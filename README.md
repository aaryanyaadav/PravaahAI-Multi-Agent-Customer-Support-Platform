# Stateful Multi-Agent Customer Support Orchestrator

Pravaah AI is a production-grade, stateful, multi-agent customer support orchestration system. Built using **LangGraph** and **FastAPI**, it dynamically routes customer queries through specialized domain agents, enforces rigorous safety and grounding guardrails, integrates voice-to-text input, and provides a premium operational telemetry dashboard with real-time token tracking.

---

## Tech Stack & Technologies

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=FastAPI&logoColor=white)
![React](https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB)
![TailwindCSS](https://img.shields.io/badge/tailwindcss-%2338B2AC.svg?style=for-the-badge&logo=tailwind-css&logoColor=white)
![Supabase](https://img.shields.io/badge/Supabase-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-f55a42?style=for-the-badge&logo=groq&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white)

---

## What the Project Solves & Core Capabilities

Enterprise customer support suffers from disconnected data, slow response times, and high human agent workloads. Pravaah AI solves these issues by acting as a **stateful, autonomous routing gateway** that resolves queries immediately or escalates with detailed context:

*   **Context-Aware Dialog Memory**: Preserves customer context and `account_id` across multi-turn follow-up questions in the same chat session.
*   **Dual-Guardrail Safety Layer**: Intercepts toxic/injection inputs and verifies output grounding against retrieved documents to prevent LLM hallucinations.
*   **Intelligent Escalation**: Verifies support relevance (ignoring spam/greetings) and creates PostgreSQL support tickets only for genuine requests, generating an L2 handoff summary.
*   **Direct Telemetry Dashboard**: Provides live KPIs (ticket distribution, daily trend graphs, and active workload) and a step-by-step observability trace drawer.
*   **Voice Input Capability**: Supports live microphone transcription with a pulsing voice waveform and an interactive stop-and-edit workflow.

---

## System Architecture

The following diagram illustrates the complete routing flow, API gateways, database mappings, and specialized agent nodes.

```mermaid
graph TD
    classDef client fill:#0f172a,stroke:#38bdf8,stroke-width:2px,color:#f8fafc;
    classDef api fill:#1e1b4b,stroke:#818cf8,stroke-width:2px,color:#f8fafc;
    classDef orchestrator fill:#1e293b,stroke:#a78bfa,stroke-width:2px,color:#f8fafc;
    classDef agent fill:#311042,stroke:#d946ef,stroke-width:2px,color:#f8fafc;
    classDef db fill:#064e3b,stroke:#34d399,stroke-width:2px,color:#f8fafc;

    subgraph Client ["Client (React SPA)"]
        ChatUI["Chat Interface (Voice + Text)"]:::client
        DashUI["Operations Dashboard"]:::client
        TraceUI["Trace Inspector Drawer"]:::client
    end

    subgraph API ["API Layer (FastAPI REST)"]
        Gate["API Gateway / Rate Limiter"]:::api
        ChatEnd["/api/chat (POST)"]:::api
        HistEnd["/api/history/{id} (GET/DELETE)"]:::api
        StatsEnd["/api/dashboard/stats (GET)"]:::api
    end

    subgraph Graph ["LangGraph Orchestration State Machine"]
        LoadMem["1. load_memory Node (Input Guardrails)"]:::orchestrator
        RouterNode["2. router Node (LLM Router)"]:::orchestrator
        ExecAgents["3. Agent Nodes (CRM, Billing, Ticket, RAG, Refund)"]:::orchestrator
        EscNode["4. escalation Node (lightweight check + ticket creation)"]:::orchestrator
        FinalNode["5. final_response Node (Merge & Output Guardrails)"]:::orchestrator
    end

    subgraph Agents ["ReAct Domain Agents"]
        CRM["CRM Agent"]:::agent
        Billing["Billing Agent"]:::agent
        Ticket["Ticket Agent"]:::agent
        RAG["Knowledge Agent (RAG)"]:::agent
        Refund["Refund Agent"]:::agent
    end

    subgraph DB ["Data Layer (Supabase Postgres)"]
        Supabase["Supabase DB Client"]:::db
        T_Accounts["accounts Table"]:::db
        T_Tickets["tickets Table"]:::db
        T_Invoices["invoices Table"]:::db
        T_Audit["audit_log Table (Conversation logs)"]:::db
        RAG_Store["FAQ & Policy JSON (BM25 Retriever)"]:::db
    end

    %% Routing Flow Connections %%
    ChatUI <-->|JSON Requests| Gate
    DashUI <-->|KPI Requests| StatsEnd
    TraceUI <-->|Trace Requests| HistEnd
    
    Gate --> ChatEnd
    Gate --> HistEnd
    Gate --> StatsEnd

    ChatEnd -->|InitialState| LoadMem
    HistEnd <-->|Retrieve Logs| Supabase
    StatsEnd <-->|Telemetry Query| Supabase

    LoadMem -->|Redacted Query & Session context| RouterNode
    RouterNode -->|Route Decision| ExecAgents
    RouterNode -->|Escalate| EscNode
    RouterNode -->|Direct Final| FinalNode

    ExecAgents --> CRM
    ExecAgents --> Billing
    ExecAgents --> Ticket
    ExecAgents --> RAG
    ExecAgents --> Refund

    CRM <-->|Query Profile| Supabase
    Billing <-->|Query Invoices| Supabase
    Ticket <-->|Query Tickets| Supabase
    RAG <-->|Local Search| RAG_Store
    Refund <-->|Check Status| Supabase

    CRM --> RouterNode
    Billing --> RouterNode
    Ticket --> RouterNode
    RAG --> RouterNode
    Refund --> RouterNode

    EscNode -->|Create SQL Ticket| Supabase
    FinalNode -->|Validate Output| RouterNode
    FinalNode -->|Log Audits| Supabase
```

---

## End-to-End Sequence Flow

This sequence trace details the sequence of execution when a user submits a query through the frontend chat workspace.

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant UI as React UI (Frontend)
    participant API as FastAPI Backend
    participant Graph as LangGraph Orchestrator
    participant Guard as Guardrails (Input/Output)
    participant Agent as Specialized Agent (e.g. Billing)
    participant DB as Supabase PostgreSQL

    User->>UI: Input query (via Voice or Text)
    UI->>API: POST /api/chat {query, session_id}
    API->>Graph: invoke(initial_state)
    
    rect rgb(15, 23, 42)
        note right of Graph: 1. load_memory & Input Checks
        Graph->>Guard: validate_input(query)
        Guard-->>Graph: Safe (PII Redacted)
        Graph->>DB: Lookup session memory (audit_log & accounts)
        DB-->>Graph: Return historical context & account_id
    end

    rect rgb(30, 27, 75)
        note right of Graph: 2. Central Router Node
        Graph->>Graph: Evaluate routing criteria
        Graph-->>Graph: Route to Billing Agent
    end

    rect rgb(49, 16, 66)
        note right of Graph: 3. ReAct Domain execution
        Graph->>Agent: Invoke BillingAgent(query)
        Agent->>DB: Query account invoice details
        DB-->>Agent: Invoice line items data
        Agent-->>Graph: Return domain context (Invoices output)
    end

    rect rgb(6, 78, 59)
        note right of Graph: 4. final_response & Grounding
        Graph->>Graph: Merge contexts via LLM response generator
        Graph->>Guard: validate_output(generated_response, agent_contexts)
        Guard-->>Graph: Grounded & Relevant (Passed)
        Graph->>DB: Save session logs & token metrics to audit_log
        DB-->>Graph: Confirmed
    end

    Graph-->>API: Return FinalState result
    API-->>UI: Return ChatResponse JSON
    UI-->>User: Display polished response & update telemetry
```

---

## ReAct Base Agent Execution Loop

Each specialized domain agent operates inside a **Reasoning and Acting (ReAct)** state loop configured to invoke database retrieval tools before deciding on a final answer.

```mermaid
graph TD
    classDef startNode fill:#1e293b,stroke:#94a3b8,stroke-width:2px,color:#f8fafc;
    classDef actionNode fill:#0f172a,stroke:#38bdf8,stroke-width:2px,color:#f8fafc;
    classDef toolNode fill:#1e1b4b,stroke:#818cf8,stroke-width:2px,color:#f8fafc;
    classDef decisionNode fill:#581c87,stroke:#c084fc,stroke-width:2px,color:#f8fafc;
    classDef endNode fill:#064e3b,stroke:#34d399,stroke-width:2px,color:#f8fafc;

    Start["1. Entry Point: Initialize State"]:::startNode --> Reason["2. reason Node (LLM Prompting)"]:::actionNode
    
    Reason --> Decision{"3. should_continue Edge"}:::decisionNode
    
    Decision -->|LLM action='tool' AND iteration < 5| Tool["4. tool Node (Execute Tool)"]:::toolNode
    Decision -->|LLM action='final' OR iteration >= 5| End["5. Output final_answer to Shared State"]:::endNode
    
    Tool -->|Append Result & Add Tokens| Reason
```

---

## Module Breakdown

*   **`src/main.py`**: The core FastAPI REST server hosting the endpoint routing gateway, CORS configurations, dynamic DB stats aggregator, and rate-limiting middleware.
*   **`src/agents/orchestrator.py`**: The Central State Orchestration node compiling the LangGraph network, managing safe input deflection, and executing conditional state updates.
*   **`src/agents/base/`**: Holds parent classes (`base_agent.py`, `nodes.py`, `graph_builder.py`) compiling the internal ReAct loop for domain agents.
*   **`src/guardrails/`**: Implements safety validators (`input_guard.py`, `output_guard.py`) conducting toxic keyword filtering, regex PII scrubbing, and grounding checks.
*   **`src/rag/`**: Powers policy FAQ lookups using local `BM25Retriever` indexing (`bm25_retriever.py`, `knowledge_services.py`).
*   **`database/`**: Configures PostgreSQL connection parameters and table schemas (`connections.py`), repositories (`repositories/`), and seed scripts (`seeder/`).
*   **`frontend/`**: Contains core browser resources (`app.js`, `index.html`) managing the UI, waveform renderers, stats cards, and ApexCharts.

---

## Technical Features & Mechanisms

### 1. Multi-Agent Orchestration
Multi-agent coordination is powered by a central orchestrator. When a user submits a query, the **Central Support Orchestrator** router node reads the input and decides which agent should process it next. The graph supports multi-turn execution: if a user asks for both billing details and cancellation policy, the orchestrator routes to the CRM agent first, then to the Knowledge agent, aggregating their data in a **shared context** before formulating a single consolidated response.

### 2. Session Memory & Context Retention
Maintaining state is crucial. When a query is received:
*   A unique `session_id` is assigned or extracted.
*   The system searches the database's `audit_log` table for prior entries under that `session_id`.
*   If found, the associated `account_id` is retrieved and populated into the active state, preserving user context even if follow-up queries do not specify account numbers.
*   The conversational logs are appended to the model's history to retain full message context.

### 3. Voice Input Integration
Spoken requests are captured dynamically using the browser's native **Web Speech API**. While speaking:
*   A premium visual waveform consisting of multiple pulsing bars (`.voice-wave-bar`) animated with custom CSS keyframes is displayed.
*   The user clicks a stop toggle ("cross") to halt listening, loading the transcribed text into a `<textarea>`.
*   The user is free to review, correct typos, and click send.

### 4. Support Query Verification & Database Setup
The system connects to a **Supabase PostgreSQL** database. The database contains the following tables:
*   `accounts`: Stores seat limits, plan tiers, statuses, and monthly revenues.
*   `users`: Company owner, admin, and member account details.
*   `subscriptions`: Active contract terms and renewal timelines.
*   `invoices` & `invoice_line_items`: Details individual billing records.
*   `tickets`: Tracks support cases.
*   `audit_log`: Stores session IDs, queries, responses, and token telemetry.

To prevent database spam:
Before routing to the `escalation` node and creating a ticket row in the `tickets` table, a validation LLM verifies if the user query is a **genuine support request** (related to billing, refunds, accounts, or policies). If it is a greeting or gibberish, ticket creation is bypassed, and a polite response is returned.

---

## API Endpoint References

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/chat` | `POST` | Submits a query. Returns redacted inputs, final response, routing steps trace, and token usage. |
| `/api/history/{session_id}` | `GET` | Retrieves chronological history and linked `account_id` context. |
| `/api/history/{session_id}` | `DELETE` | Deletes audit log entries matching the session ID. |
| `/api/dashboard/stats` | `GET` | Fetches aggregated KPIs, daily trends, active tickets, and token usage. |
| `/api/ping` | `GET` | Connectivity check. Returns `{"ping": "pong"}`. |
| `/api/health` | `GET` | Returns operational health status of the API. |

---

## Visual Showcase

Explore the customer-facing interface and the real-time operations dashboard.

### 1. Customer Chat Workspace

The Customer Chat Workspace is a stateful, interactive portal designed to handle customer queries over multiple turns.

#### A. Chat Initial State
![Chat Initial State](./docs/screenshots/chat_initial.png)
*   **Conversational History Sidebar (Left):** Maintains a clean chronological list of past support sessions (e.g., "Billing Inquiry", "Refund Inquiry") linked to the user's active session.
*   **Stateful Memory Context:** When a user requests invoices or profile info, the system resolves historical context to retrieve their `account_id` automatically.
*   **Ticket Confirmation Alerts:** Displays clear, system-generated notification cards whenever an inquiry is escalated and a new ticket is written to the database.

#### B. Voice Dictation Mode
![Voice Dictation Mode](./docs/screenshots/chat_voice_listening.png)
*   **Web Speech API Integration:** Enables live microphone recording. The status bar displays a pulsing red `REC` badge along with custom CSS-animated soundwave frequencies.
*   **Safe Edit Workflow:** Users can record their speech, press the red cancel (`X`) button to halt listening, and edit the transcribed text manually before submission.
*   **Chip Suggestions:** Provides quick-click query suggestions for common actions (e.g., querying billing history, account details, testing safety deflections).

#### C. Multi-Agent Conversation & Trace
![Chat Conversation](./docs/screenshots/chat_conversation.png)
*   **Active Agent Flow:** Displays a multi-turn session where a refund query is parsed and handled by the system.
*   **Observability Sidebar (Right):** The panel slides out to reveal the step-by-step reasoning steps of the central orchestrator (Input Guardrail status, router confidence, agent tool executions, and final response synthesis).

---

### 2. Operations & Telemetry Dashboard

The Operations Dashboard provides support administrators with complete real-time visibility into active workloads, AI deflection rates, and agent-level telemetry.

#### A. Telemetry Dashboard Overview
![Telemetry Dashboard Overview](./docs/screenshots/dashboard_overview.png)
*   **Interactive Period Filters:** Allows administrators to filter metrics by Today, Last 7 Days, Last 30 Days, or All Time.
*   **Key Performance Indicators (KPIs):**
    *   **Total Tickets Raised / Active / Resolved:** Live indicators pulling directly from PostgreSQL.
    *   **AI Resolution Rate:** Displays a 100% deflection rate, representing cases handled fully by autonomous agents.
*   **Telemetry Trends & Workloads:**
    *   **Incoming Daily Volume (Left):** Real-time chart displaying volumetric trends of incoming conversations vs. escalations.
    *   **Agent Workload (Right):** Visual bar chart counting invocations per specialized agent (CRM, Billing, Knowledge, etc.) to evaluate resource allocation.

#### B. Observability Trace Inspector Drawer
![Observability Trace Inspector](./docs/screenshots/observability_trace_drawer.png)
*   **Step-by-Step Execution Logs:** Displays the exact routing path taken by the orchestrator:
    1.  **Input Guardrail:** Confirms input is safe and checks for PII/injections.
    2.  **Routing Decision:** Router evaluates query and selects the CRM agent (95% confidence).
    3.  **Agent Execution:** Preview of data returned by database query tools (company info, renewal timeline, seat count, monthly revenue).
    4.  **Final Response:** Router determines CRM context is complete and routes to the final response node.

---

## System Evaluation & Benchmark

The platform includes an **industry-grade automated evaluation framework** located in the [`evaluation/`](./evaluation/) directory. The framework tests and benchmarks multi-agent routing decisions, factual groundedness, escalation accuracy, ticket creation/suppression behavior, latency, and token efficiency against a **100-query ground-truth dataset** derived directly from the system's database entities (`accounts.csv`, `invoices.csv`, `tickets.csv`, `users.csv`, `subscriptions.csv`, and support policy documents).

### Framework Architecture

```
evaluation/
├── datasets/
│   ├── benchmark_100.json        # 100 curated ground-truth test queries
│   ├── benchmark_100.csv         # Tabular export for data science workflows
│   └── generate_datasets.py      # Automated ground-truth generator from DB CSVs
├── metrics/
│   ├── routing_metrics.py        # Top-1 Accuracy, Precision, Recall, F1, Confusion Matrix
│   ├── answer_metrics.py         # Keyword coverage, semantic answer accuracy, grounding rate
│   ├── escalation_metrics.py     # Escalation Precision/Recall, False Positive Rate, FNR
│   └── latency_metrics.py        # p50/p90/p99 latency percentiles, duration, token usage
├── runners/
│   └── batch_runner.py           # Rate-limit aware batch executor with full telemetry
├── reports/
│   ├── generator.py              # Report generation engine
│   └── runs/                     # Timestamped run directories (raw_results, summary, report)
└── cli.py                        # Unified command-line interface
```

### Benchmark Results Summary (100 Queries)

**Latest Benchmark Run**: `run_20260825_224623` | **Total Queries**: `100` | **Model**: `openai/gpt-oss-120b`

#### 1. Executive KPI Summary

| Benchmark Metric | Score | Description |
| :--- | :---: | :---: | :---: | :--- |
| **Routing Accuracy** | **73.0%** | Correct primary domain agent assigned |
| **Escalation Accuracy** | **94.0%** | Correct identification of human handoff needs |
| **Ticket Accuracy (Suppression & Creation)** | **94.0%** | Accurate DB ticket creation vs suppression |
| **Conversational Ticket Suppression** | **100.0%** | 0 false tickets generated for greetings/gibberish |
| **Answer / Factual Accuracy** | **71.0%** | Correct factual details present in response |
| **Average Keyword Coverage** | **64.66%** | Key ground-truth entities mentioned |

#### 2. Latency & Token Telemetry

| Metric | Measured Value |
| :--- | :--- |
| **Median Latency (p50)** | `1.539s` |
| **90th Percentile Latency (p90)** | `47.434s` |
| **99th Percentile Latency (p99)** | `64.262s` |
| **Average Response Duration** | `12.633s` (Min: `0.339s`, Max: `64.262s`) |
| **Total Tokens Consumed** | `177,305` tokens |
| **Average Tokens per Query** | `1,773.0` tokens |

#### 3. Category-wise Performance Breakdown

| Category | Queries | Routing Acc | Escalation Acc | Ticket Acc | Answer Acc |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **CRM & Accounts** | 20 | **95.0%** | **95.0%** | **95.0%** | 75.0% |
| **Billing & Invoices** | 20 | **95.0%** | **95.0%** | **95.0%** | 70.0% |
| **Support Tickets** | 15 | **100.0%** | **100.0%** | **100.0%** | 66.7% |
| **Conversational / Smalltalk** | 8 | **100.0%** | **100.0%** | **100.0%** | **100.0%** |
| **Guardrails & Safety** | 2 | **100.0%** | **100.0%** | **100.0%** | **100.0%** |
| **Knowledge Base & Policies** | 15 | 40.0% | **100.0%** | **100.0%** | 53.3% |
| **Escalations & Disputes** | 10 | 40.0% | 60.0% | 60.0% | 40.0% |
| **Refunds** | 10 | 0.0% | **100.0%** | **100.0%** | **100.0%** |

#### 4. Agent Routing Performance & Confusion Matrix

| Agent | Support | Precision | Recall | F1-Score |
| :--- | :---: | :---: | :---: | :---: |
| **CRM Agent** | 20 | 82.61% | 95.0% | **88.37%** |
| **Billing Agent** | 20 | 55.88% | 95.0% | **70.37%** |
| **Ticket Agent** | 15 | 88.24% | 100.0% | **93.75%** |
| **Input Guard (Safety & Conversational)** | 10 | 100.0% | 100.0% | **100.0%** |
| **Knowledge Agent** | 15 | 54.55% | 40.0% | 46.15% |
| **Escalation Agent** | 10 | 100.0% | 40.0% | 57.14% |
| **Refund Agent** | 10 | 0.0% | 0.0% | 0.0% |

**Confusion Matrix (Rows = Expected, Columns = Predicted):**

| Expected \ Actual | billing | crm | escalation | input_guard | knowledge | refund | ticket |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **billing** | 19 | 0 | 0 | 0 | 1 | 0 | 0 |
| **crm** | 0 | 19 | 0 | 0 | 1 | 0 | 0 |
| **escalation** | 2 | 1 | 4 | 0 | 3 | 0 | 0 |
| **input_guard** | 0 | 0 | 0 | 10 | 0 | 0 | 0 |
| **knowledge** | 3 | 3 | 0 | 0 | 6 | 1 | 2 |
| **refund** | 10 | 0 | 0 | 0 | 0 | 0 | 0 |
| **ticket** | 0 | 0 | 0 | 0 | 0 | 0 | 15 |

---

### Running the Evaluation Suite

To run the automated benchmark runner:

```bash
# Run complete 100-query benchmark
python -m evaluation.cli

# Run on a limited subset (e.g. 10 queries)
python -m evaluation.cli --limit 10

# Run evaluation for a specific domain category
python -m evaluation.cli --category crm --limit 5
python -m evaluation.cli --category billing --limit 5
python -m evaluation.cli --category conversational

# Save artifacts to a custom directory
python -m evaluation.cli --output-dir evaluation/reports/custom_run
```

Each run automatically persists timestamped artifacts in `evaluation/reports/runs/run_<timestamp>/`:
*   `summary_metrics.json`: Machine-readable KPI scores, latency percentiles, and confusion matrix.
*   `raw_results.json`: Full execution traces, actual vs. expected routing decisions, token counts, and error logs per query.
*   `evaluation_report.md`: Markdown summary report with KPI tables and breakdown.

---

## Setup & Installation

### Requirements
*   Python 3.10 or 3.11
*   Supabase Account & Postgres Database
*   Groq API Key (Llama 3.1 model access)

### 1. Setup Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Create a `.env` file in the project root:
```env
SUPABASE_URL=https://your-supabase-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
DB_USER=postgres
DB_PASSWORD=your-db-password
DB_HOST=db.your-supabase.supabase.co
DB_PORT=5432
DB_NAME=postgres
GROQ_API_KEY=gsk_your_groq_api_key
```

### 3. Seed Database tables
Populate your database with mock accounts, invoices, subscriptions, and tickets:
```bash
python database/seeder/seeder.py
python database/seeder/upload_csv_to_database.py
```

### 4. Launch Services
Run the FastAPI backend server:
```bash
python -m uvicorn src.main:app --host 127.0.0.1 --port 8000
```
Run the frontend web server (using python server, node, or liveserver):
```bash
python -m http.server 3000 --directory frontend
```
Open `http://127.0.0.1:3000` in your web browser.

---

## Author

*   **Aryan Yadav**
    *   **Email:** [aryanyadav051206@gmail.com](mailto:aryanyadav051206@gmail.com)
    *   **GitHub:** [@aaryanyaadav](https://github.com/aaryanyaadav)

