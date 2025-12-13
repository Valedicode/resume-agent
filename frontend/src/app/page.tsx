'use client';

import { Header } from '@/components/Header';
import { ResumeUpload } from '@/components/ResumeUpload';
import { JobInput } from '@/components/JobInput';
import { HowItWorks } from '@/components/HowItWorks';
import { ChatContainer } from '@/components/Chat/ChatContainer';
import { useTheme } from '@/hooks/useTheme';
import { useFileUpload } from '@/hooks/useFileUpload';
import { useJobInput } from '@/hooks/useJobInput';
import { useSession } from '@/hooks/useSession';
import { useChat } from '@/hooks/useChat';

export default function Home() {
  const { isDark, toggleTheme } = useTheme();
  
  // Initialize session
  const {
    sessionId,
    sessionState,
    isInitializing,
    error: sessionError,
    updateSessionState,
  } = useSession();
  
  // File upload with backend integration
  const {
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
  } = useFileUpload();
  
  // Job input with backend integration
  const {
    jobText,
    setJobText,
    jobData,
    isProcessing: isJobProcessing,
    error: jobError,
    submitJob,
    clearError: clearJobError,
    clearJob,
  } = useJobInput();
  
  // Chat with supervisor agent
  const {
    messages,
    inputText,
    setInputText,
    isLoading,
    error: chatError,
    textareaRef,
    messagesEndRef,
    handleSendMessage,
    handleKeyDown,
  } = useChat({
    sessionId,
    cvData,
    onSessionStateUpdate: updateSessionState,
  });

  return (
    <div className="flex min-h-screen flex-col bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 dark:from-slate-950 dark:via-slate-900 dark:to-slate-950">
      <Header isDark={isDark} toggleTheme={toggleTheme} />

      {/* Main Content Area */}
      <main className="container mx-auto flex flex-1 flex-col gap-6 p-6">
        {/* Session Error Banner */}
        {sessionError && (
          <div className="rounded-lg border border-red-200 bg-red-50 p-4 dark:border-red-900/50 dark:bg-red-950/30">
            <div className="flex items-start gap-3">
              <svg
                className="h-5 w-5 flex-shrink-0 text-red-600 dark:text-red-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <div className="flex-1">
                <h3 className="font-semibold text-red-900 dark:text-red-100">
                  Connection Error
                </h3>
                <p className="mt-1 text-sm text-red-700 dark:text-red-400">
                  {sessionError}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Session Initializing */}
        {isInitializing && (
          <div className="rounded-lg border border-blue-200 bg-blue-50 p-4 dark:border-blue-900/50 dark:bg-blue-950/30">
            <div className="flex items-center gap-3">
              <div className="h-5 w-5 animate-spin rounded-full border-2 border-blue-600 border-t-transparent dark:border-blue-400"></div>
              <p className="text-sm text-blue-700 dark:text-blue-300">
                Initializing AI session...
              </p>
            </div>
          </div>
        )}

        <div className="flex flex-1 flex-col gap-6 lg:flex-row">
          {/* Left Sidebar - Upload Section */}
          <aside className="flex flex-col gap-4 lg:w-80">
            <ResumeUpload
              uploadedFile={uploadedFile}
              isDragging={isDragging}
              uploadError={uploadError}
              isUploading={isUploading}
              cvData={cvData}
              needsClarification={needsClarification}
              clarificationQuestions={clarificationQuestions}
              fileInputRef={fileInputRef}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onFileInputChange={handleFileInputChange}
              onClickUpload={handleClickUpload}
              onRemoveFile={handleRemoveFile}
            />
            <JobInput
              jobText={jobText}
              setJobText={setJobText}
              jobData={jobData}
              isProcessing={isJobProcessing}
              error={jobError}
              onSubmit={submitJob}
              onClear={clearJob}
            />
            <HowItWorks />
          </aside>

          {/* Main Chat Area */}
          <div className="flex flex-1 flex-col gap-4">
            <ChatContainer
              messages={messages}
              inputText={inputText}
              isLoading={isLoading}
              textareaRef={textareaRef}
              messagesEndRef={messagesEndRef}
              onInputChange={setInputText}
              onKeyDown={handleKeyDown}
              onSendMessage={handleSendMessage}
              onClickUpload={handleClickUpload}
              sessionReady={!!sessionId && !isInitializing}
            />
          </div>
        </div>
      </main>
    </div>
  );
}
