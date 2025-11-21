## Resume Architect Agent

An autonomous **human-in-the-loop AI agent** that takes your **generic PDF resume** and a **specific Job Description URL**, then iteratively rewrites and optimizes your resume until it tightly matches the job requirements and passes your personal approval.

---

## Concept

You provide:

- **Generic resume** as a PDF file
- **Job Description** as a URL (or pasted text, depending on the interface)

The agent:

- Scrapes and parses the job description
- Parses your existing resume from PDF
- Runs a **gap analysis** between JD requirements and your current resume
- Iteratively **rewrites and optimizes** bullets, summary, and skills
- **Pauses for your review and feedback** (human-in-the-loop)
- Incorporates your feedback into the next iteration
- Outputs a **clean, professional, targeted PDF resume**

---

## The Architecture Loop

At the core of this project is an optimization loop with an explicit human checkpoint:

- **Ingestion**
  - **Job Description scraping**: Fetch and structure the JD from a URL.
  - **Resume parsing**: Extract sections (summary, experience, projects, skills, education) from your PDF.

- **Gap Analysis**
  - Compare JD entities (skills, tools, responsibilities, keywords) with your parsed resume.
  - Identify:
    - Missing or weak skills/keywords  
    - Under-emphasized experience  
    - Misaligned framing or tone
  - Example: **JD requires `LangGraph`, resume only mentions `Python`**.

- **Drafting**
  - Rewrite:
    - Summary / headline
    - Experience bullets
    - Skills section
  - Goals:
    - Close identified gaps
    - Mirror relevant JD language (without keyword stuffing)
    - Preserve factual accuracy and your authentic profile

- **Human Intervention (The Hook)**
  - Execution pauses and the system:
    - Shows **before vs after** bullets/sections
    - Explains which JD requirements each change targets
  - You can:
    - Approve / reject individual changes
    - Give qualitative feedback, e.g.:
      - “This looks too formal, make it punchier.”
      - “Shorten this.”
      - “Tone down the buzzwords.”
  - The agent ingests your feedback, updates style/constraints, and loops back to **Drafting**.

- **Publication**
  - Once you click **Approve**:
    - The agent generates a final, **professionally formatted PDF**
    - (Optionally) exports other formats (DOCX / Markdown) depending on the implementation

---

## Example Workflow

1. Upload your **base resume PDF**.
2. Provide a **JD URL** (or paste the job description text).
3. The agent:
   - Scrapes/parses the JD  
   - Parses your resume  
   - Runs gap analysis and generates a first tailored draft  
4. Review a **diff view** of proposed changes:
   - Original vs rewritten bullets and sections  
   - Notes on which JD requirements are being satisfied  
5. Give feedback like:
   - “This looks too formal, make it punchier.”
6. The agent regenerates the draft with your style preferences.
7. When satisfied, click **Approve**.
8. Download your **targeted PDF resume**.

---

## Project Structure (Planned)

tbc.
---

## Getting Started

### Prerequisites

- [Conda](https://docs.conda.io/en/latest/miniconda.html) or [Miniconda](https://docs.conda.io/en/latest/miniconda.html) installed
- Python 3.11+ (managed by conda)

### Setup

1. **Clone the repo**

```bash
git clone https://github.com/Valedicode/resume-architect-agent.git
cd resume-architect-agent
```

2. **Create and activate conda environment**

```bash
conda env create -f environment.yml
conda activate resume-architect-agent
```

3. **Install additional dependencies** (as you add them to your project)

```bash
pip install <package-name>
# Then update environment.yml or create requirements.txt
```

4. **Configure environment variables**

Create a `.env` file in the project root:

```bash
# .env
OPENAI_API_KEY=your_api_key_here
# Add other API keys and configuration as needed
OUTPUT_DIR=./output
```

### Alternative: Using venv (if you prefer)

If you'd rather use Python's built-in `venv` instead of conda:

```bash
python -m venv .venv
.venv\Scripts\activate  # On Windows
# or
source .venv/bin/activate  # On macOS/Linux
pip install -r requirements.txt
```

---

## Design Principles

- **Human agency first**: You always see what changed and approve the final result.
- **No fabrication**: The agent reframes and optimizes; it does not invent experience or credentials.
- **Transparency**: Each change can be traced back to specific JD requirements.
- **ATS-aware**: Output is optimized for both humans and applicant tracking systems.

---
