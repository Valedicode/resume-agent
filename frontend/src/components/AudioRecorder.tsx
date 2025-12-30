'use client';

import { useState, useRef, useCallback, useEffect } from 'react';
import { translateAudio, APIError, getErrorMessage } from '@/lib/api';
import type { TranslationRequest, TranslationResponse } from '@/types';

interface AudioRecorderProps {
  onTranscriptionComplete?: (text: string) => void;
  onTranscriptionResult?: (result: TranslationResponse, mode: 'translate', model?: string) => void;
  onError?: (error: string) => void;
  className?: string;
}

type RecordingState = 'idle' | 'recording' | 'processing' | 'completed';

export const AudioRecorder = ({
  onTranscriptionComplete,
  onTranscriptionResult,
  onError,
  className = '',
}: AudioRecorderProps) => {
  const [recordingState, setRecordingState] = useState<RecordingState>('idle');
  const [isRecording, setIsRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [transcription, setTranscription] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [recordingTime, setRecordingTime] = useState(0);
  const [audioLevel, setAudioLevel] = useState(0);
  const [prompt, setPrompt] = useState('');

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const streamRef = useRef<MediaStream | null>(null);
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const animationFrameRef = useRef<number | null>(null);

  // Fixed values - always translate with whisper-1
  const selectedModel = 'whisper-1';
  const selectedMode = 'translate';

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (audioUrl) {
        URL.revokeObjectURL(audioUrl);
      }
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
      cleanupAudioVisualization();
    };
  }, [audioUrl]);

  // Setup audio visualization
  const setupAudioVisualization = useCallback((stream: MediaStream) => {
    try {
      audioContextRef.current = new AudioContext();
      analyserRef.current = audioContextRef.current.createAnalyser();
      analyserRef.current.fftSize = 256;
      analyserRef.current.smoothingTimeConstant = 0.8;
      
      const source = audioContextRef.current.createMediaStreamSource(stream);
      source.connect(analyserRef.current);
      
      const bufferLength = analyserRef.current.frequencyBinCount;
      const dataArray = new Uint8Array(bufferLength);
      
      const updateAudioLevel = () => {
        if (analyserRef.current && isRecording) {
          analyserRef.current.getByteFrequencyData(dataArray);
          
          // Calculate average volume
          const average = dataArray.reduce((a, b) => a + b) / bufferLength;
          const normalized = Math.min(average / 128, 1); // Normalize to 0-1
          
          setAudioLevel(normalized);
          animationFrameRef.current = requestAnimationFrame(updateAudioLevel);
        }
      };
      
      updateAudioLevel();
    } catch (err) {
      console.error('Error setting up audio visualization:', err);
    }
  }, [isRecording]);

  // Cleanup audio visualization
  const cleanupAudioVisualization = useCallback(() => {
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
      animationFrameRef.current = null;
    }
    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }
    analyserRef.current = null;
    setAudioLevel(0);
  }, []);

  const startRecording = useCallback(async () => {
    try {
      setError(null);
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;

      // Setup audio visualization
      setupAudioVisualization(stream);

      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus',
      });

      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const blob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        setAudioBlob(blob);
        const url = URL.createObjectURL(blob);
        setAudioUrl(url);
        setIsRecording(false);
        setRecordingState('idle');
        if (timerRef.current) {
          clearInterval(timerRef.current);
          timerRef.current = null;
        }
        setRecordingTime(0);
        cleanupAudioVisualization();
      };

      mediaRecorder.start();
      setIsRecording(true);
      setRecordingState('recording');

      // Start timer
      let time = 0;
      timerRef.current = setInterval(() => {
        time += 1;
        setRecordingTime(time);
      }, 1000);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to start recording';
      setError(`Microphone access denied: ${errorMessage}`);
      if (onError) {
        onError(errorMessage);
      }
    }
  }, [onError, setupAudioVisualization, cleanupAudioVisualization]);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
        streamRef.current = null;
      }
      cleanupAudioVisualization();
    }
  }, [isRecording, cleanupAudioVisualization]);

  const handleFileUpload = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validate file type
    const validTypes = ['audio/mpeg', 'audio/mp3', 'audio/mp4', 'audio/wav', 'audio/webm', 'audio/m4a', 'audio/mpga'];
    const validExtensions = ['.mp3', '.mp4', '.mpeg', '.mpga', '.m4a', '.wav', '.webm'];
    const fileExt = '.' + file.name.split('.').pop()?.toLowerCase();

    if (!validTypes.includes(file.type) && !validExtensions.includes(fileExt)) {
      setError(`Unsupported file format. Supported: ${validExtensions.join(', ')}`);
      return;
    }

    // Validate file size (25MB)
    const maxSize = 25 * 1024 * 1024;
    if (file.size > maxSize) {
      setError(`File size (${(file.size / (1024 * 1024)).toFixed(2)}MB) exceeds maximum of 25MB`);
      return;
    }

    setError(null);
    setAudioBlob(file);
    const url = URL.createObjectURL(file);
    setAudioUrl(url);
    setTranscription(null);
  }, []);

  const processAudio = useCallback(async () => {
    if (!audioBlob) return;

    setRecordingState('processing');
    setError(null);

    try {
      // Convert blob to File
      const file = new File([audioBlob], 'audio.webm', { type: audioBlob.type });

      const request: TranslationRequest = {
        file,
        model: 'whisper-1',
        response_format: 'text',
      };

      if (prompt.trim()) {
        request.prompt = prompt.trim();
      }

      const response = await translateAudio(request);

      if (response.success && response.text) {
        // Trim to remove trailing newlines
        const cleanedText = response.text.trimEnd();
        setTranscription(cleanedText);
        setRecordingState('completed');
        if (onTranscriptionResult) {
          onTranscriptionResult(response, selectedMode, selectedModel);
        }
      } else {
        throw new Error(response.message || 'Translation failed');
      }
    } catch (err) {
      const errorMessage = getErrorMessage(err);
      setError(errorMessage);
      setRecordingState('idle');
      if (onError) {
        onError(errorMessage);
      }
    }
  }, [audioBlob, selectedModel, selectedMode, prompt, onTranscriptionResult, onError]);

  const reset = useCallback(() => {
    setRecordingState('idle');
    setIsRecording(false);
    setAudioBlob(null);
    if (audioUrl) {
      URL.revokeObjectURL(audioUrl);
    }
    setAudioUrl(null);
    setTranscription(null);
    setError(null);
    setRecordingTime(0);
    setPrompt('');
    cleanupAudioVisualization();
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  }, [audioUrl, cleanupAudioVisualization]);

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // Audio Visualization Component
  const AudioVisualization = ({ level }: { level: number }) => {
    const circles = [0, 1, 2, 3];
    
    return (
      <div className="relative flex items-center justify-center h-32 w-32">
        {circles.map((index) => {
          const scale = 1 + level * (0.4 + index * 0.15);
          const opacity = 0.08 + level * 0.15 * (1 - index * 0.2);
          
          return (
            <div
              key={index}
              className="absolute rounded-full bg-indigo-500 dark:bg-indigo-400 transition-all duration-75"
              style={{
                width: `${60 + index * 18}px`,
                height: `${60 + index * 18}px`,
                transform: `scale(${scale})`,
                opacity,
              }}
            />
          );
        })}
        {/* Center microphone icon */}
        <div className="relative z-10 flex items-center justify-center h-16 w-16 rounded-full bg-indigo-600 shadow-lg dark:bg-indigo-500">
          <svg className="h-8 w-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
          </svg>
        </div>
      </div>
    );
  };

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Info Badge */}
      <div className="flex items-center gap-2 rounded-lg bg-indigo-50 border border-indigo-100 px-3 py-2 dark:bg-indigo-900/20 dark:border-indigo-800">
        <svg className="h-4 w-4 text-indigo-600 dark:text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span className="text-xs text-indigo-700 dark:text-indigo-300">
          Voice input will be automatically translated to English
        </span>
      </div>

      {/* Prompt Input */}
      <div>
        <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
          Optional Context (helps improve accuracy)
        </label>
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="e.g., This is about job applications and resumes..."
          className="w-full rounded-lg border border-slate-300 bg-slate-50 px-3 py-2 text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:border-slate-600 dark:bg-slate-700 dark:text-slate-100 dark:placeholder-slate-500"
          rows={2}
        />
      </div>

      {/* Recording State Display */}
      {isRecording && (
        <div className="flex flex-col items-center gap-4 py-6 bg-slate-50 dark:bg-slate-800/50 rounded-xl">
          <AudioVisualization level={audioLevel} />
          <div className="flex items-center gap-2">
            <div className="h-2.5 w-2.5 rounded-full bg-red-500 animate-pulse"></div>
            <span className="text-sm font-medium text-slate-700 dark:text-slate-300">
              {formatTime(recordingTime)}
            </span>
          </div>
          <button
            onClick={stopRecording}
            className="rounded-lg bg-red-600 px-6 py-2.5 text-sm font-medium text-white transition-colors hover:bg-red-700 shadow-md"
          >
            Stop Recording
          </button>
        </div>
      )}

      {/* Recording Controls */}
      {!isRecording && !audioBlob && (
        <div className="flex flex-col sm:flex-row items-center gap-3">
          <button
            onClick={startRecording}
            className="flex items-center justify-center gap-2 rounded-lg bg-indigo-600 px-6 py-3 text-sm font-medium text-white transition-colors hover:bg-indigo-700 shadow-md hover:shadow-lg w-full sm:w-auto dark:bg-indigo-500 dark:hover:bg-indigo-600"
          >
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
            </svg>
            Start Recording
          </button>
          <span className="text-sm text-slate-500 dark:text-slate-400">or</span>
          <button
            onClick={() => fileInputRef.current?.click()}
            className="flex items-center justify-center gap-2 rounded-lg border border-slate-300 bg-white px-6 py-3 text-sm font-medium text-slate-700 transition-colors hover:bg-slate-50 shadow-sm w-full sm:w-auto dark:border-slate-600 dark:bg-slate-700 dark:text-slate-300 dark:hover:bg-slate-600"
          >
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
            Upload Audio File
          </button>
          <input
            ref={fileInputRef}
            type="file"
            accept="audio/*,.mp3,.mp4,.mpeg,.mpga,.m4a,.wav,.webm"
            onChange={handleFileUpload}
            className="hidden"
          />
        </div>
      )}

      {/* Audio Preview & Process */}
      {audioBlob && !isRecording && recordingState !== 'processing' && (
        <div className="space-y-3">
          {audioUrl && (
            <div className="rounded-lg border border-slate-200 bg-slate-50 p-3 dark:border-slate-700 dark:bg-slate-800/50">
              <audio src={audioUrl} controls className="w-full" />
            </div>
          )}
          <div className="flex items-center gap-3">
            <button
              onClick={processAudio}
              className="flex-1 rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-medium text-white transition-colors hover:bg-indigo-700 shadow-md dark:bg-indigo-500 dark:hover:bg-indigo-600"
            >
              Translate to English
            </button>
            <button
              onClick={reset}
              className="rounded-lg border border-slate-300 bg-white px-4 py-2.5 text-sm font-medium text-slate-700 transition-colors hover:bg-slate-50 dark:border-slate-600 dark:bg-slate-700 dark:text-slate-300 dark:hover:bg-slate-600"
            >
              Reset
            </button>
          </div>
        </div>
      )}

      {/* Processing State */}
      {recordingState === 'processing' && (
        <div className="flex items-center justify-center gap-3 py-6 text-sm text-slate-600 dark:text-slate-400">
          <svg className="h-5 w-5 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span className="font-medium">Translating to English...</span>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="rounded-lg bg-red-50 border border-red-200 p-3 text-sm text-red-700 dark:bg-red-950/20 dark:border-red-800 dark:text-red-400">
          {error}
        </div>
      )}

      {/* Translation Result */}
      {transcription && (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-medium text-slate-700 dark:text-slate-300">
              Translation (English)
            </h3>
            <button
              onClick={() => {
                if (onTranscriptionComplete) {
                  onTranscriptionComplete(transcription);
                }
              }}
              className="text-sm font-medium text-indigo-600 hover:text-indigo-700 dark:text-indigo-400 dark:hover:text-indigo-300"
            >
              Use in Chat →
            </button>
          </div>
          <div className="rounded-lg border border-slate-200 bg-slate-50 p-4 text-sm text-slate-900 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100">
            {transcription}
          </div>
        </div>
      )}
    </div>
  );
};

