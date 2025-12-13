'use client';

import { useState } from 'react';

interface StepData {
  number: number;
  title: string;
  description: string;
}

const steps: StepData[] = [
  {
    number: 1,
    title: 'Upload your resume PDF',
    description:
      'Drag and drop your existing resume or click to browse. Our AI will extract your skills, experience, and qualifications. If any information is unclear, we\'ll ask clarifying questions to ensure accuracy.',
  },
  {
    number: 2,
    title: 'Paste job description or URL',
    description:
      'Share the job posting by pasting the job description text directly or providing a URL. Our AI analyzes the requirements, identifies key skills, and understands what the employer is looking for.',
  },
  {
    number: 3,
    title: 'Review AI suggestions',
    description:
      'Our AI compares your resume with the job requirements and provides personalized recommendations. You can chat with the AI to refine the suggestions, ask questions, or request specific changes before generating your tailored resume.',
  },
  {
    number: 4,
    title: 'Download optimized resume',
    description:
      'Once you\'re satisfied with the tailored resume, download your professionally formatted PDF. You can also generate a matching cover letter that highlights your relevant experience and aligns with the job requirements.',
  },
];

export const HowItWorks = () => {
  const [expandedSteps, setExpandedSteps] = useState<Set<number>>(new Set());

  const toggleStep = (stepNumber: number) => {
    setExpandedSteps((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(stepNumber)) {
        newSet.delete(stepNumber);
      } else {
        newSet.add(stepNumber);
      }
      return newSet;
    });
  };

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-800">
      <h3 className="mb-6 text-lg font-semibold text-indigo-900 dark:text-indigo-300">
        How it works
      </h3>
      <ol className="space-y-4">
        {steps.map((step) => {
          const isExpanded = expandedSteps.has(step.number);
          return (
            <li key={step.number} className="flex gap-4">
              <span className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-indigo-100 text-base font-semibold text-indigo-700 dark:bg-indigo-900/50 dark:text-indigo-400">
                {step.number}
              </span>
              <div className="flex-1">
                <button
                  onClick={() => toggleStep(step.number)}
                  className="flex w-full items-center justify-between gap-2 text-left transition-colors hover:text-indigo-600 dark:hover:text-indigo-400"
                >
                  <h4 className="font-semibold text-slate-900 dark:text-slate-100">
                    {step.title}
                  </h4>
                  <svg
                    className={`h-5 w-5 flex-shrink-0 text-slate-400 transition-transform ${
                      isExpanded ? 'rotate-180' : ''
                    }`}
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M19 9l-7 7-7-7"
                    />
                  </svg>
                </button>
                {isExpanded && (
                  <p className="mt-2 text-sm text-slate-600 dark:text-slate-400">
                    {step.description}
                  </p>
                )}
              </div>
            </li>
          );
        })}
      </ol>
    </div>
  );
};


