# 🛡️ Autonomous QA Automation & Security Audit Agentic Pipeline

A production-grade, multi-agent continuous integration security and quality assurance validation system. This project leverages an autonomous agent network to programmatically analyze application structures, design boundary regression test suites, execute vulnerability scans (via OWASP ZAP and built-in specialized Python tests), persist audit memories to a SQLite database, and compile publication-ready executive Word documents.

This project satisfies all criteria for the **QA / Testing / Security track mini-project**, providing a complete, runnable, and robust codebase designed for academic evaluation.

---

## 1. Project Overview

Modern DevSecOps demands continuous functional validation and proactive vulnerability assessment. Traditional testing systems are siloed and rigid. This project introduces an **Autonomous Agentic Pipeline** that simulates a team of senior QA architects and Security engineers working in sync.

### Key Capabilities:
- **Autonomous DOM Scraping**: Dynamically navigates target URLs using a headless Playwright engine, mapping interactive forms, inputs, and structure parameters.
- **Behavior-Driven Development (BDD) Feature Design**: Converts functional test requirements into standard Gherkin/Cucumber feature files (`Given-When-Then`) for seamless business-to-development alignment.
- **Asynchronous Playwright Automation Code Builder**: Automatically generates ready-to-run, high-quality, async Python Playwright automation script blocks matching designed test cases and locator IDs.
- **QA & Security Coverage Gap Analyzer**: Cross-references scraped elements, designed test suites, and discovered security issues to identify uncovered application paths and deliver structured risk remediations.
- **Hybrid Security Auditing**: Uses a dual-mode Security Scan Agent executing checks for OWASP Top 10 vulnerabilities (SQL Injection, XSS, exposed configurations, insecure protocols, open ports) natively or through an OWASP ZAP API daemon connection.
- **Long & Short-Term Memory Orchestration**: Synchronizes multi-agent handshakes and test logs inside a SQLite database memory model (`memory/memory.db`) for permanent historical tracking and cross-agent context sharing.
- **Publication-Ready Word Reporting**: Compiles and exports beautiful corporate/academic-grade reports with custom coloring, statistical threat distribution tables, and remediation roadmaps using `python-docx`.

---

## 2. Architecture & Multi-Agent Collaboration Workflow

```
                        +------------------------------------+
                        |       Streamlit Frontend Dashboard  |
                        +-----------------+------------------+
                                          | Input URL & Requirements
                                          v
                        +------------------------------------+
                        |       Multi-Agent Orchestrator     |
                        +--------+------------------+--------+
                                 |                  |
            +--------------------+                  +---------------------+
            | (State Handoff)                       | (State Handoff)     |
            v                                       v                     v
+-----------------------+               +-----------------------+   +-------------------+
|  Test Case Agent      |               |  Security Scan Agent  |   | SQLite Memory DB  |
+-----------------------+               +-----------------------+   +-------------------+
|  Role: QA Lead Architect               |  Role: Lead Pentester  |   | - scan_history    |
|  Tool: Playwright DOM Scraper         |  Tool: Hybrid Scanner |   | - test_cases      |
|  Task: Designs Positive, Negative,    |  Task: Runs XSS, SQLi, |   | - vulnerabilities |
|        & Boundary test suites.        |        ports, header checks|   | - agent_interactions
+-----------+-----------+               +-----------+-----------+   +-------------------+
            |                                       |                     ^
            +--------------------+  +---------------+                     |
                                 v  v                                     | Writes Output
                        +--------+--------------+                         |
                        |  Report Compiler Agent |-------------------------+
                        +-----------------------+
                        |  Role: Tech Writer / CISO Consultant
                        |  Tool: python-docx Report Builder
                        |  Task: Consolidates outputs, generates Executive
                        |        Summaries, writes physical DOCX report.
                        +-------------------------------------------------+
```

### End-to-End Orchestrated Steps:
1. **Initialize Session Memory**: The orchestrator registers a new session ID in the SQLite database `scan_history` table with a status of `IN_PROGRESS`.
2. **DOM Analysis & Test Design**:
   - The **Test Case Agent** invokes the Playwright engine (`tools/playwright_tool.py`) to scrape the target URL.
   - The elements (inputs, action forms, submit triggers) are compiled and sent to the LLM to design structured functional regression testing suites.
   - Handoff logs are written into the short-term agent interaction memory.
3. **Vulnerability Scans**:
   - The **Security Scan Agent** takes over. It deploys port scanners, SQL Injection payload checkers, XSS fuzzer payloads, directory fuzzers (checking for exposed `.git`, `.env` files), and inspects HTTP headers for missing clickjacking or CSP rules.
   - Discovered raw findings are enriched using LLM intelligence, mapping them to official OWASP Top 10 vulnerabilities with precise remediation guidance.
4. **Report Compilation & Persistence**:
   - The **Report Compiler Agent** aggregates all generated data, updates the SQLite long-term database tables, and computes statistics.
   - It queries the LLM to synthesize a highly professional Executive Summary suitable for CTO/CISO audit presentation.
   - Finally, it formats a polished, corporate Word document and saves the file in `/reports`.

---

## 3. Folder Structure

```
agentic-pipeline/
│
├── agents/
│   ├── __init__.py
│   ├── base_agent.py          # Base Agent utilizing OpenAI/Groq API with retry checks
│   ├── test_agent.py          # QA Automation Architect generating functional tests
│   ├── security_agent.py      # Security Penetration Testing Agent mapping OWASP Top 10
│   ├── report_agent.py        # Reporter agent persisting database and compiling results
│   └── extended_features_agent.py # BDD Generator, Playwright script compiler, and Coverage analyzer
│
├── memory/
│   ├── __init__.py
│   ├── database.py            # SQLite schema initialization and CRUD methods
│   └── memory.db              # Database file (auto-generated on first run)
│
├── tools/
│   ├── __init__.py
│   ├── playwright_tool.py     # Headless browser page scraper (falls back to BeautifulSoup)
│   ├── zap_tool.py            # OWASP ZAP API client + Native Python scanner
│   └── report_tool.py         # Word (.docx) styling and file generation utility
│
├── ui/
│   ├── __init__.py
│   ├── app.py                 # Premium Streamlit UI Dashboard Interface
│   └── styles.py              # CSS styling rules for modern premium white/light-mode UI
│
├── reports/                   # Saved Word (.docx) Audit reports (auto-generated)
├── requirements.txt           # Python package requirements
├── README.md                  # Project manual and instruction guide
├── main.py                    # Orchestrator CLI entrypoint
└── test_app.py                # Built-in vulnerable mock application for demo runs
```

---

## 4. Installation Steps

Ensure you have **Python 3.8+** installed on your Windows machine.

### Step 1: Clone or Open Workspace
Ensure the project files are located in your workspace directory:
```bash
c:\Users\susmi\Desktop\Capstone Full Agent Pipeline
```

### Step 2: Create a Virtual Environment (Recommended)
Open a command prompt (or PowerShell) in the workspace directory and execute:
```powershell
python -m venv venv
.\venv\Scripts\activate
```

### Step 3: Install Required Dependencies
Install the required packages listed in `requirements.txt`:
```powershell
pip install -r requirements.txt
```

### Step 4: Install Playwright Browsers
To enable the high-fidelity Playwright browser web scraping engine, initialize its browser binaries:
```powershell
playwright install
```

### Step 5: Configure OpenAI API Key
Add your OpenAI API key to the `.env` file in the project root directory:
```env
OPENAI_API_KEY=your_actual_key_here
```

---

## 5. Execution Commands

### 1. Run the Vulnerable Mock Target Server (Highly Recommended for Demos!)
We have included a completely self-contained, vulnerable web application (`test_app.py`) written using only standard libraries. It purposefully lacks security headers, exposes raw SQL Injection database error streams, allows reflected XSS scripts, and exposes sensitive configurations. 

Start the mock target application in a **separate terminal window**:
```powershell
python test_app.py
```
*The mock application will start running on **`http://localhost:5000`**.*

### 2. Run the Streamlit Dashboard UI
Launch the interactive visual dashboard in your primary terminal window:
```powershell
streamlit run ui/app.py
```
*This command will automatically open your web browser to **`http://localhost:8501`**.*

### 3. Run via CLI Orchestrator Directly
If you prefer running the pipeline directly from the command-line console, execute:
```powershell
python main.py --url http://localhost:5000
```

---

## 6. Comprehensive Demo Presentation Walkthrough

Follow these steps to perform a flawless live demonstration of the pipeline for academic grading:

### Step 1: Launch the Local Infrastructure
1. Open terminal 1 and run the mock vulnerable app: `python test_app.py`.
2. Open terminal 2 and run the Streamlit UI: `streamlit run ui/app.py`.
3. Verify that your browser loads the dashboard on `http://localhost:8501`.

### Step 2: Configure Credentials & Target
1. In the sidebar of the Streamlit dashboard:
   - Paste your **OpenAI API Key** (if not already set in environment variables).
   - Verify the **Application URL** target is set to `http://localhost:5000` (pointing to your running mock app).
   - Leave ZAP Proxy unchecked to run the custom high-fidelity native scanner, which checks for SQLi, XSS, headers, exposed `.env` and `.git`, and open ports.

### Step 3: Perform Database Initialization
1. In the sidebar, click the **Initialize SQLite Memory** button. This will build the SQLite schema and prepare the memory databases.

### Step 4: Execute the Autonomous Scan
1. Navigate to the **"Run Agentic Pipeline"** tab.
2. In the specification box, type custom requirements to guide the QA Agent:
   > *"The user must be able to fill the login form. The system should block blank passwords. Users should be able to search for items and lookup reviews by index."*
3. Click the **"Trigger Full Multi-Agent Audit"** button.
4. Watch the progress bar advance. The interface will display live status logs as the orchestrator coordinates:
   - Playwright scraping the inputs/forms on `http://localhost:5000`.
   - The **QA SDET Agent** designing test suites.
   - The **Security Scan Agent** executing real fuzzer payloads against the search and feedback inputs.
   - The **Report Compiler Agent** logging entries, creating an Executive Summary, and building the Word DOCX report.

### Step 5: Explore the Findings, Automation Scripts, & Audit Trails
1. **Enjoy the Premium Bright UI**: Notice the stunning, modern white/light-mode dashboard aesthetic which provides high readability and slate-toned contrast tags for visual excellence.
2. **Navigate to "BDD Test Cases" Tab**: Click the **"🥒 Generate Gherkin BDD Feature Suite"** button to instantly compile your functional tests into Cucumber/Gherkin specifications, and download the finished `.feature` file.
3. **Navigate to "Playwright Scripts" Tab**: Click the **"🎭 Compile Playwright Automation Script"** button. The *Extended QA Suite Agent* will analyze input elements and output a fully functional, async Python Playwright automation script ready for deployment! You can download the completed script via the download button.
4. **Navigate to "Coverage Gap Analysis" Tab**: Click the **"📊 Perform QA & Security Coverage Audit"** button to perform a rigorous coverage depth evaluation. Review the detailed metric distributions, vulnerability impact mapping, and remediation checklists inside the card.
5. **Navigate to "Security Vulnerability Portal" Tab**: Point out the High and Medium severity vulnerabilities discovered:
   - *Reflected Cross-Site Scripting (XSS)* on the `/search` parameter.
   - *SQL Injection* triggering a SQLite database syntax error on the `/feedback` parameter.
   - *Exposed Sensitive Paths* showing the exposed `/.env` configuration and Git repository files.
   - *Missing Security Headers* checking for HSTS and Clickjacking guards.
   - Note the **Secure Coding Remediation Strategies** containing actual code blocks to fix each threat!
6. **Navigate to "Multi-Agent Audit Log" Tab**: Showcase the collaborative handshake logs showing the exact times and short-term messages passed across agents.
7. **Download Consolidated Report**: After completing a scan, the **Download Consolidated DOCX Audit Report** button will appear in the **"Run Agentic Pipeline"** tab. Click it to retrieve the highly professional compiled Word Document. Open and present the document's structured layouts, tables, and colors.

---

## 7. Future Enhancements

1. **Static Code Analysis (SAST)**: Equip a new *SAST Agent* to read local source files directly and audit raw Python/JS code blocks for vulnerabilities using AST parsing.
2. **Interactive Playwright Test Execution**: Implement a browser crawler tool that executes the generated test scenarios automatically on the target site to record pass/fail results.
3. **CI/CD Integration**: Build GitHub Actions or Jenkins plugins that fail builds if the Security Agent records High or Critical vulnerabilities.
