import { Message, DownloadableFile } from '@/types';
import { DownloadButton } from './DownloadButton';

interface ChatMessageProps {
  message: Message;
  generatedFiles?: DownloadableFile[] | null;
}

export const ChatMessage = ({ message, generatedFiles }: ChatMessageProps) => {
  // Simple markdown-like formatting for plain text
  // Converts ## headers, **text** to bold, *text* to italic, and preserves line breaks
  const formatText = (text: string) => {
    // Split by line breaks to preserve structure
    return text.split('\n').map((line, lineIndex) => {
      // Check if line is a header (## Header text)
      const headerMatch = line.match(/^##\s+(.+)$/);
      if (headerMatch) {
        return (
          <h3 key={lineIndex} className="mt-4 mb-2 text-base font-semibold text-slate-900 dark:text-slate-100 first:mt-0">
            {headerMatch[1]}
          </h3>
        );
      }
      
      // Simple formatting: **bold** and *italic*
      const parts: (string | React.ReactElement)[] = [];
      let lastIndex = 0;
      let key = 0;
      
      // Match **bold** and *italic* patterns
      const boldRegex = /\*\*([^*]+)\*\*/g;
      const italicRegex = /(?<!\*)\*([^*]+)\*(?!\*)/g;
      
      // Find all matches
      const matches: Array<{ start: number; end: number; type: 'bold' | 'italic'; text: string }> = [];
      
      let match;
      while ((match = boldRegex.exec(line)) !== null) {
        matches.push({ start: match.index, end: match.index + match[0].length, type: 'bold', text: match[1] });
      }
      while ((match = italicRegex.exec(line)) !== null) {
        // Check if not part of a bold match
        const isPartOfBold = matches.some(m => match!.index >= m.start && match!.index < m.end);
        if (!isPartOfBold) {
          matches.push({ start: match.index, end: match.index + match[0].length, type: 'italic', text: match[1] });
        }
      }
      
      // Sort matches by position
      matches.sort((a, b) => a.start - b.start);
      
      // Build parts array
      matches.forEach((m) => {
        // Add text before match
        if (m.start > lastIndex) {
          parts.push(line.substring(lastIndex, m.start));
        }
        // Add formatted match
        if (m.type === 'bold') {
          parts.push(<strong key={key++}>{m.text}</strong>);
        } else {
          parts.push(<em key={key++}>{m.text}</em>);
        }
        lastIndex = m.end;
      });
      
      // Add remaining text
      if (lastIndex < line.length) {
        parts.push(line.substring(lastIndex));
      }
      
      // If no matches, return original line
      if (parts.length === 0) {
        parts.push(line);
      }
      
      return (
        <span key={lineIndex}>
          {parts}
          {lineIndex < text.split('\n').length - 1 && <br />}
        </span>
      );
    });
  };

  return (
    <div
      className={`flex gap-4 ${
        message.role === 'user' ? 'justify-end' : 'justify-start'
      }`}
    >
      {message.role === 'assistant' && (
        <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-indigo-600 to-blue-600 dark:from-indigo-500 dark:to-blue-500">
          <svg className="h-5 w-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
        </div>
      )}
      <div
        className={`max-w-[80%] rounded-2xl px-4 py-3 ${
          message.role === 'user'
            ? 'bg-indigo-600 text-white dark:bg-indigo-500'
            : 'bg-slate-100 text-slate-900 dark:bg-slate-700 dark:text-slate-100'
        }`}
      >
        <div className="text-sm leading-relaxed whitespace-pre-wrap">
          {formatText(message.content)}
        </div>
        {message.role === 'assistant' && generatedFiles && generatedFiles.length > 0 && (
          <div className="mt-3 pt-3 border-t border-slate-200 dark:border-slate-600">
            <div className="space-y-2">
              {generatedFiles.map((file, index) => (
                <DownloadButton key={index} file={file} />
              ))}
            </div>
          </div>
        )}
      </div>
      {message.role === 'user' && (
        <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-slate-200 dark:bg-slate-700">
          <svg className="h-5 w-5 text-slate-600 dark:text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
        </div>
      )}
    </div>
  );
};


