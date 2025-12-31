/**
 * Hook for handling file uploads with backend integration
 */

import { useState, useRef, useCallback } from 'react';
import { validateFile } from '@/lib/utils';
import { uploadCV, isAPIError, getErrorMessage } from '@/lib/api';
import type { ResumeInfo } from '@/types';

interface UseFileUploadProps {
  sessionId: string | null;
  onCVUploaded?: () => void;
}

interface UseFileUploadReturn {
  uploadedFile: File | null;
  cvData: ResumeInfo | null;
  isDragging: boolean;
  uploadError: string | null;
  isUploading: boolean;
  needsClarification: boolean;
  clarificationQuestions: string[] | null;
  fileInputRef: React.RefObject<HTMLInputElement | null>;
  handleDragOver: (e: React.DragEvent) => void;
  handleDragLeave: (e: React.DragEvent) => void;
  handleDrop: (e: React.DragEvent) => void;
  handleFileInputChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  handleClickUpload: () => void;
  handleRemoveFile: () => void;
  retryUpload: () => Promise<void>;
  processUploadedFile: () => Promise<void>;
}

export const useFileUpload = ({ sessionId, onCVUploaded }: UseFileUploadProps): UseFileUploadReturn => {
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [cvData, setCvData] = useState<ResumeInfo | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [needsClarification, setNeedsClarification] = useState(false);
  const [clarificationQuestions, setClarificationQuestions] = useState<string[] | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const uploadFileToBackend = useCallback(async (file: File) => {
    setIsUploading(true);
    setUploadError(null);
    setCvData(null);
    setNeedsClarification(false);
    setClarificationQuestions(null);

    try {
      const response = await uploadCV(file);

      if (response.success) {
        setCvData(response.cv_data || null);
        setNeedsClarification(response.needs_clarification);
        setClarificationQuestions(response.questions || null);
        
        if (response.needs_clarification && response.questions) {
          console.log('Clarification needed:', response.questions);
        }
        
        // Notify parent component
        if (response.cv_data) {
          onCVUploaded?.();
        }
      } else {
        setUploadError(response.message || 'Failed to process CV');
      }
    } catch (error) {
      const errorMessage = getErrorMessage(error);
      setUploadError(errorMessage);
      
      // Log error with multiple formats for better debugging
      console.error('CV upload error - Message:', errorMessage);
      console.error('CV upload error - Raw error:', error);
      console.error('CV upload error - Error type:', error instanceof Error ? error.constructor.name : typeof error);
      
      if (error instanceof Error) {
        console.error('CV upload error - Error name:', error.name);
        console.error('CV upload error - Error stack:', error.stack);
      }
      
      if (isAPIError(error)) {
        console.error('CV upload error - API Status:', error.status);
        console.error('CV upload error - API Detail:', error.detail);
      }
      
      console.error('CV upload error - File info:', {
        name: file.name,
        size: file.size,
        type: file.type
      });
    } finally {
      setIsUploading(false);
    }
  }, [sessionId, onCVUploaded]);

  const handleFileSelect = useCallback(async (file: File) => {
    setUploadError(null);
    const error = validateFile(file);
    
    if (error) {
      setUploadError(error);
      return;
    }
    
    setUploadedFile(file);
    
    // Don't automatically upload - wait for manual trigger
    // await uploadFileToBackend(file);
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      handleFileSelect(files[0]);
    }
  }, [handleFileSelect]);

  const handleFileInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFileSelect(files[0]);
    }
  }, [handleFileSelect]);

  const handleClickUpload = useCallback(() => {
    fileInputRef.current?.click();
  }, []);

  const handleRemoveFile = useCallback(() => {
    setUploadedFile(null);
    setCvData(null);
    setUploadError(null);
    setNeedsClarification(false);
    setClarificationQuestions(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  }, []);

  const retryUpload = useCallback(async () => {
    if (uploadedFile) {
      await uploadFileToBackend(uploadedFile);
    }
  }, [uploadedFile, uploadFileToBackend]);

  const processUploadedFile = useCallback(async () => {
    if (uploadedFile && !cvData && !isUploading) {
      await uploadFileToBackend(uploadedFile);
    }
  }, [uploadedFile, cvData, isUploading, uploadFileToBackend]);

  return {
    uploadedFile,
    cvData,
    isDragging,
    uploadError,
    isUploading,
    needsClarification,
    clarificationQuestions,
    fileInputRef,
    handleDragOver,
    handleDragLeave,
    handleDrop,
    handleFileInputChange,
    handleClickUpload,
    handleRemoveFile,
    retryUpload,
    processUploadedFile,
  };
};
