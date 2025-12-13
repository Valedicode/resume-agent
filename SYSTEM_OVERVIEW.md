# JobWriterAI System Overview

A visual guide to understanding how the system works.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER BROWSER                             │
│                    http://localhost:3000                        │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                    NEXT.JS FRONTEND                        │ │
│  │                                                            │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │ │
│  │  │  Components  │  │    Hooks     │  │     API      │   │ │
│  │  │              │  │              │  │   Service    │   │ │
│  │  │ • Upload UI  │→ │ • useSession │→ │              │   │ │
│  │  │ • Chat UI    │  │ • useUpload  │  │ • uploadCV() │   │ │
│  │  │ • Download   │  │ • useChat    │  │ • sendMsg()  │   │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘   │ │
│  │                                              ↓            │ │
│  │                                     /api/* requests       │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                              ↓                  │
│                                    Next.js Proxy               │
│                              /api/* → :8000/api/*              │
└─────────────────────────────────────────────────────────────────┘
                                     ↓
                              HTTP Requests
                                     ↓
┌─────────────────────────────────────────────────────────────────┐
│                       FASTAPI BACKEND                           │
│                    http://localhost:8000                        │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                      API ROUTERS                           │ │
│  │                                                            │ │
│  │  /api/supervisor  │  /api/cv  │  /api/job  │  /api/writer│ │
│  │        ↓                ↓            ↓             ↓       │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                ↓                                │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                   LANGCHAIN AGENTS                         │ │
│  │                                                            │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │ │
│  │  │  Supervisor  │  │   CV Agent   │  │  Job Agent   │   │ │
│  │  │    Agent     │  │              │  │              │   │ │
│  │  │              │  │ • Extract    │  │ • Scrape URL │   │ │
│  │  │ • Coordinate │  │ • Clarify    │  │ • Parse Text │   │ │
│  │  │ • Route      │  │ • Validate   │  │ • Research   │   │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘   │ │
│  │                                                            │ │
│  │                    ┌──────────────┐                       │ │
│  │                    │Writer Agent  │                       │ │
│  │                    │              │                       │ │
│  │                    │ • Align      │                       │ │
│  │                    │ • Tailor     │                       │ │
│  │                    │ • Generate   │                       │ │
│  │                    └──────────────┘                       │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                ↓                                │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                      LLM PROVIDER                          │ │
│  │                    (OpenAI GPT-4)                          │ │
│  └───────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## User Journey

```
                    START
                      ↓
         ┌────────────────────────┐
         │  User Opens Browser    │
         │  http://localhost:3000 │
         └────────────────────────┘
                      ↓
         ┌────────────────────────┐
         │  Session Initializes   │
         │  (Auto, in background) │
         └────────────────────────┘
                      ↓
         ┌────────────────────────┐
         │  Welcome Message       │
         │  "Hello! I'm your..."  │
         └────────────────────────┘
                      ↓
                 ╔═══════╗
                 ║ READY ║
                 ╚═══════╝
                      ↓
         ┌────────────────────────┐
         │  User Uploads PDF      │
         │  (Drag & Drop / Click) │
         └────────────────────────┘
                      ↓
         ┌────────────────────────┐
         │  CV Extracted          │
         │  "Resume processed     │
         │   successfully!"       │
         └────────────────────────┘
                      ↓
         ┌────────────────────────┐
         │  User Chats            │
         │  "Here's a job URL..." │
         └────────────────────────┘
                      ↓
         ┌────────────────────────┐
         │  Job Analyzed          │
         │  "I've analyzed the    │
         │   job requirements"    │
         └────────────────────────┘
                      ↓
         ┌────────────────────────┐
         │  User Requests CV      │
         │  "Generate tailored CV"│
         └────────────────────────┘
                      ↓
         ┌────────────────────────┐
         │  CV Generated          │
         │  "Your tailored CV is  │
         │   ready for download"  │
         └────────────────────────┘
                      ↓
         ┌────────────────────────┐
         │  User Downloads        │
         │  john_doe_cv.pdf       │
         └────────────────────────┘
                      ↓
                    END
```

---

## Data Flow

### 1. CV Upload Flow

```
User                Frontend              Backend                LLM
 │                     │                    │                     │
 │  Upload PDF         │                    │                     │
 ├────────────────────>│                    │                     │
 │                     │  POST /cv/upload   │                     │
 │                     ├───────────────────>│                     │
 │                     │                    │  Extract data       │
 │                     │                    ├────────────────────>│
 │                     │                    │                     │
 │                     │                    │  CV Data + Questions│
 │                     │                    │<────────────────────┤
 │                     │  CV Data Response  │                     │
 │                     │<───────────────────┤                     │
 │  Success Message    │                    │                     │
 │<────────────────────┤                    │                     │
```

### 2. Chat Flow

```
User                Frontend              Backend                Supervisor
 │                     │                    │                     │
 │  Type message       │                    │                     │
 ├────────────────────>│                    │                     │
 │                     │  POST /session/msg │                     │
 │                     ├───────────────────>│                     │
 │                     │                    │  Process message    │
 │                     │                    ├────────────────────>│
 │                     │                    │                     │
 │                     │                    │  Response + State   │
 │                     │                    │<────────────────────┤
 │                     │  AI Response       │                     │
 │                     │<───────────────────┤                     │
 │  Display response   │                    │                     │
 │<────────────────────┤                    │                     │
```

### 3. CV Generation Flow

```
User                Frontend              Backend                Writer Agent
 │                     │                    │                     │
 │  Request CV         │                    │                     │
 ├────────────────────>│                    │                     │
 │                     │  POST /generate-cv │                     │
 │                     ├───────────────────>│                     │
 │                     │                    │  Align & Generate   │
 │                     │                    ├────────────────────>│
 │                     │                    │                     │
 │                     │                    │  PDF File Path      │
 │                     │                    │<────────────────────┤
 │                     │  File Path         │                     │
 │                     │<───────────────────┤                     │
 │  Download link      │                    │                     │
 │<────────────────────┤                    │                     │
 │                     │                    │                     │
 │  Click download     │                    │                     │
 ├────────────────────>│  GET /files/...    │                     │
 │                     ├───────────────────>│                     │
 │                     │  PDF Blob          │                     │
 │                     │<───────────────────┤                     │
 │  File downloads     │                    │                     │
 │<────────────────────┤                    │                     │
```

---

## Component Hierarchy

```
App (page.tsx)
│
├─ Header
│  └─ ThemeToggle
│
├─ SessionErrorBanner (conditional)
│
├─ SessionInitializing (conditional)
│
└─ MainContent
   │
   ├─ Sidebar
   │  ├─ ResumeUpload
   │  │  ├─ FileInput (hidden)
   │  │  ├─ DropZone
   │  │  ├─ UploadProgress (conditional)
   │  │  ├─ SuccessMessage (conditional)
   │  │  ├─ ClarificationWarning (conditional)
   │  │  └─ ErrorMessage (conditional)
   │  │
   │  └─ HowItWorks
   │
   └─ ChatArea
      └─ ChatContainer
         ├─ EmptyState (when no messages)
         │  ├─ ChatInput
         │  └─ QuickSuggestions
         │
         └─ MessagesView (when has messages)
            ├─ ChatMessage (for each message)
            ├─ LoadingIndicator (conditional)
            └─ ChatInput
```

---

## Hook Dependencies

```
page.tsx
│
├─ useTheme()
│  └─ Theme state (local)
│
├─ useSession()
│  ├─ sessionId
│  ├─ sessionState
│  └─ API: startSupervisorSession()
│
├─ useFileUpload()
│  ├─ uploadedFile
│  ├─ cvData
│  └─ API: uploadCV()
│
└─ useChat({ sessionId, cvData })
   ├─ messages
   ├─ isLoading
   └─ API: sendSupervisorMessage()
```

---

## State Management

### Session State
```javascript
{
  sessionId: "uuid-string",
  sessionState: {
    session_stage: "collecting_job",
    has_cv_data: true,
    has_job_data: false,
    needs_clarification: false,
    ready_for_writer: false,
    current_agent: "supervisor"
  },
  isInitializing: false,
  error: null
}
```

### Upload State
```javascript
{
  uploadedFile: File,
  cvData: {
    name: "John Doe",
    email: "john@example.com",
    phone: "+1234567890",
    skills: ["Python", "JavaScript"],
    education: ["BS Computer Science"],
    experience: ["Software Engineer at..."]
  },
  isUploading: false,
  uploadError: null,
  needsClarification: false,
  clarificationQuestions: []
}
```

### Chat State
```javascript
{
  messages: [
    {
      id: "1",
      role: "assistant",
      content: "Hello! I'm your Resume AI Agent...",
      timestamp: Date
    },
    {
      id: "2",
      role: "user",
      content: "Here's a job posting...",
      timestamp: Date
    }
  ],
  inputText: "",
  isLoading: false,
  error: null
}
```

---

## Error Handling Flow

```
Error Occurs
    ↓
┌─────────────────────┐
│   API Layer         │
│   (lib/api.ts)      │
│                     │
│   • Network error   │
│   • HTTP error      │
│   • Parse error     │
└─────────────────────┘
    ↓
  Throw APIError
    ↓
┌─────────────────────┐
│   Hook Layer        │
│   (useXXX)          │
│                     │
│   try/catch block   │
│   set error state   │
└─────────────────────┘
    ↓
  Update State
    ↓
┌─────────────────────┐
│  Component Layer    │
│  (React Component)  │
│                     │
│  Render error UI    │
│  Show user message  │
└─────────────────────┘
    ↓
User Sees Error
```

---

## File Structure

```
JobWriterAI/
│
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app
│   │   ├── api/                 # API endpoints
│   │   ├── agents/              # LangChain agents
│   │   ├── models/              # Pydantic schemas
│   │   └── services/            # Business logic
│   ├── data/                    # Generated files
│   ├── uploads/                 # Uploaded CVs
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── app/                 # Next.js pages
│   │   ├── components/          # React components
│   │   ├── hooks/               # Custom hooks
│   │   ├── lib/                 # Utilities
│   │   └── types/               # TypeScript types
│   ├── package.json
│   └── next.config.ts           # Proxy config
│
└── Documentation/
    ├── START.md                 # Quick start
    ├── INTEGRATION_GUIDE.md     # Full guide
    ├── INTEGRATION_STATUS.md    # Status report
    ├── SYSTEM_OVERVIEW.md       # This file
    └── DEVELOPMENT_CHECKLIST.md # Testing guide
```

---

## API Endpoint Map

```
Backend                          Frontend
http://localhost:8000           http://localhost:3000

/api/supervisor/session/start   → /api (proxied)
/api/supervisor/session/message
/api/cv/upload
/api/cv/clarify
/api/job/extract-url
/api/job/extract-text
/api/job/research-company
/api/writer/analyze-alignment
/api/writer/generate-cv
/api/writer/generate-cover-letter
/api/files/{filename}
/health
/docs                           Direct access
```

---

## Typical Session Timeline

```
T+0s    User opens app
T+1s    Session initialized
T+2s    Welcome message shown
        ═══ USER READY ═══
T+5s    User uploads PDF
T+7s    CV extracted
T+10s   User provides job URL
T+15s   Job analyzed
T+20s   User requests CV
T+45s   CV generated
T+46s   User downloads CV
        ═══ COMPLETE ═══
```

---

## Performance Targets

| Operation | Target | Actual* |
|-----------|--------|---------|
| Session Init | < 2s | ~1s |
| CV Upload | < 5s | ~3-5s |
| Chat Response | < 10s | ~5-15s |
| CV Generation | < 30s | ~20-40s |
| File Download | Instant | ~1s |

*Actual times depend on LLM API response times

---

## Key Technologies

### Frontend Stack
```
Next.js 16
  ├── React 19
  ├── TypeScript 5
  └── Tailwind CSS 4
```

### Backend Stack
```
FastAPI
  ├── Python 3.11+
  ├── LangChain
  ├── OpenAI API
  └── WeasyPrint
```

---

## Quick Reference

### Start Application
```bash
# Terminal 1
cd backend && python -m uvicorn app.main:app --reload

# Terminal 2  
cd frontend && npm run dev
```

### Access Points
- **App:** http://localhost:3000
- **API:** http://localhost:8000
- **Docs:** http://localhost:8000/docs

### Common Tasks
- **Upload CV:** Drag PDF to left sidebar
- **Chat:** Type in chat input, press Enter
- **Download:** Click generated file link

---

## Summary

JobWriterAI is a full-stack AI application that:
1. Extracts data from PDF resumes
2. Analyzes job requirements
3. Generates tailored CVs and cover letters
4. Provides an interactive chat interface
