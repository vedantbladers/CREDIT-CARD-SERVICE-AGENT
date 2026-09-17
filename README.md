# Agentic AI Platform for Single-Interaction Credit Card Resolution, Real-Time Execution, and Verifiable Auditing

[![Go Version](https://img.shields.io/badge/Go-1.23-00ADD8?style=flat&logo=go)](https://golang.org)
[![Python Version](https://img.shields.io/badge/Python-3.12-3776AB?style=flat&logo=python)](https://python.org)
[![LangGraph](https://img.shields.io/badge/Orchestrator-LangGraph-FF6F00?style=flat)](https://langchain-ai.github.io/langgraph/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=flat&logo=react)](https://react.dev)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=flat&logo=postgresql)](https://www.postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat&logo=docker)](https://www.docker.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An enterprise-grade agentic financial service platform designed to provide **single-interaction customer resolution** with **deterministic banking safety guardrails**, **ACID-compliant database execution**, and **verifiable audit trails**. 

Built with a modular microservice architecture decoupling non-deterministic LLM reasoning from critical business policy decisions and direct database mutations.

---

## 📑 Table of Contents

1. [High-Level Architecture](#-high-level-architecture)
2. [Key Principles & Features](#-key-principles--features)
3. [Completed Milestones & Roadmap](#-completed-milestones--roadmap)
4. [Technology Stack](#-technology-stack)
5. [Repository Structure](#-repository-structure)
6. [Quick Start & Setup](#-quick-start--setup)
7. [Testing & Verification Guide](#-testing--verification-guide)
8. [Security & Isolation Model](#-security--isolation-model)
9. [Author & Academic Context](#-author--academic-context)

---

## 🏛 High-Level Architecture

```
                                  ┌────────────────────────┐
                                  │    React Frontend      │ (Port 5173)
                                  │  - Customer Chat UI    │
                                  │  - Test Scenarios      │
                                  └───────────┬────────────┘
                                              │ HTTP POST /api/chat
                                              │ (Bearer JWT Auth)
                                              ▼
                                  ┌────────────────────────┐
                                  │   Go API Gateway       │ (Port 8080)
                                  │  - Chi v5 Ingress      │
                                  │  - JWT & IDOR Checks   │
                                  │  - Security Headers    │
                                  └───────────┬────────────┘
                                              │ HTTP POST /chat
                                              ▼
                                  ┌────────────────────────┐
                                  │  FastAPI Orchestrator  │ (Port 8000)
                                  │  - LangGraph State     │
                                  │  - OpenRouter AI (LLM) │
                                  │  - Slot Extraction     │
                                  └───────────┬────────────┘
                                              │
                                              ▼
                                  ┌────────────────────────┐
                                  │ Deterministic Policy   │ (Zero-LLM Safety Layer)
                                  │  - Rule Guardrails     │
                                  │  - APPROVE / REJECT /  │
                                  │    NEEDS_ESCALATION    │
                                  └───────────┬────────────┘
                                              │ Verified Approval Only
                                              ▼
                                  ┌────────────────────────┐
                                  │   MCP Server Proxy     │ (Port 8001)
                                  │  - Tool Sandbox        │
                                  │  - Strict Parameters   │
                                  └───────────┬────────────┘
                                              │
                       ┌──────────────────────┴──────────────────────┐
                       ▼                                             ▼
        ┌─────────────────────────────┐               ┌─────────────────────────────┐
        │     PostgreSQL 16 DB        │               │   Elasticsearch Cluster     │
        │  - ACID Transactions        │               │  - Immutable Audit Logs     │
        │  - Row-Level Locking        │               │  - (Scheduled Phase 5)      │
        └─────────────────────────────┘               └─────────────────────────────┘
```

---

## 💡 Key Principles & Features

- **Decoupled Non-Deterministic Reasoning**: The Large Language Model (configured via OpenRouter with native reasoning support) is exclusively responsible for **intent classification** and **slot extraction**. It never executes commands or writes to the database directly.
- **Zero-LLM Deterministic Policy Engine**: Hard business rules (waiver limits, tenure constraints, delinquency checks, credit line adjustment caps) are evaluated deterministically in pure Python code without probabilistic model interference.
- **Model Context Protocol (MCP) Isolation**: All database mutations (`waive_fee`, `adjust_credit_limit`, `replace_card`) are sandboxed inside an isolated microservice that rejects execution unless accompanied by an explicit, auditable policy approval.
- **ACID Integrity & Audit Ledger**: Every transaction runs with strict PostgreSQL row-level locking (`SELECT ... FOR UPDATE`), atomic balance checks, and commits before/after state into the `audit_transactions` ledger table.
- **Edge Ingress Defense**: A high-performance Go API Gateway powered by Chi v5 verifies JWT authentication, prevents Insecure Direct Object References (IDOR), sets strict security response headers, and routes traffic cleanly.

---

## 🚀 Completed Milestones & Roadmap

- [x] **Phase 1 — End-to-End Microservice Skeleton**
  - Fully containerized 4-tier stack (React, Go Gateway, FastAPI, PostgreSQL).
  - Wired synchronous request-response flow for the foundational `fee_waiver` intent.
- [x] **Phase 2 — LangGraph Orchestration & Slot Parsing**
  - State graph managing conversational flow (`classify_intent` ➔ `extract_slots`).
  - Supported intents: `fee_waiver`, `credit_limit_increase`, `card_replacement`, and `unclear`.
  - Automatic clarification triggers for missing essential parameters (e.g. replacement reason).
  - OpenRouter API integration with fallback to a deterministic offline regex/keyword engine.
- [x] **Phase 3 — Standalone Deterministic Policy Engine**
  - Standardized rule codes: `POL-FW-001` through `POL-FW-004`, `POL-CLI-001` through `POL-CLI-004`, and `POL-CR-001` through `POL-CR-003`.
  - Three-tier verdicts: `APPROVED`, `REJECTED`, or `NEEDS_ESCALATION` with auditable reasoning.
- [x] **Phase 4 — Model Context Protocol (MCP) & ACID Transactions**
  - Standalone MCP execution service on port `8001`.
  - Tools: `execute_waive_fee`, `execute_adjust_credit_limit`, and `execute_replace_card`.
  - Pessimistic locking, transaction rollback safety, and immediate before/after state diffing in UI.
- [x] **Security Hardening (SEC-01 – SEC-11 Remediation)**
  - Hardened JWT subject cross-verification preventing IDOR across cardholder accounts.
  - Secret sanitization: All API keys and model parameters strictly read from `.env`.
  - Strict CORS origin allowlists and standard HTTP security defense headers (`X-Frame-Options`, `CSP`, `HSTS`, `X-Content-Type-Options`).
  - Input boundary enforcement (rejection of zero and negative financial amounts).
- [ ] **Phase 5 — Asynchronous Immutable Audit Logging (Elasticsearch)**
- [ ] **Phase 6 — Ingress Token Bucket Rate Limiting per Cardholder**

---

## 🛠 Technology Stack

| Component | Technology | Responsibility |
| :--- | :--- | :--- |
| **Frontend** | React 18, Vite, CSS3 | Customer banking portal, real-time audit inspector, interactive scenario runner |
| **Edge Gateway** | Go 1.23, Chi v5, `golang-jwt` | Ingress validation, JWT authentication, IDOR enforcement, security headers |
| **AI Orchestrator** | Python 3.12, FastAPI, LangGraph | Conversational state graph, intent classification, parameter slot extraction |
| **LLM Inference** | OpenRouter (OpenAI SDK) | Flexible model routing with native reasoning capabilities enabled |
| **Policy Engine** | Pure Python 3.12 | Deterministic corporate rule evaluation, safety checks, limit enforcement |
| **Tool Sandbox** | FastAPI, MCP Server Architecture | Sandboxed database execution tools with transaction rollback safety |
| **Core Database** | PostgreSQL 16 Alpine, `psycopg2` | Mock core banking accounts, ACID transaction commits, audit transaction logging |
| **DevOps** | Docker, Docker Compose | Multi-container orchestration, health-checking, container networking |

---

## 📂 Repository Structure

```
CREDIT-CARD SERVICE/
├── docker-compose.yml              # Complete 5-tier container orchestration
├── .env.example                    # Template for environment variables and secrets
├── .gitignore                      # Git exclusion rules
│
├── fastapi-agent/                  # Tier 2: AI Orchestrator & Policy Engine
│   ├── app/
│   │   ├── api/                    # FastAPI route handlers (/chat, /accounts)
│   │   ├── core/config.py          # Configuration loader (strictly loads .env)
│   │   ├── models/schemas.py       # Pydantic schemas for state, slots, and requests
│   │   ├── policy/                 # Standalone Deterministic Policy Engine
│   │   │   ├── engine.py           # Evaluator returning APPROVED, REJECTED, ESCALATED
│   │   │   └── rules.py            # Financial guardrails and banking rules
│   │   └── services/
│   │       ├── graph_orchestrator.py # LangGraph workflow graph definition
│   │       ├── llm_factory.py      # OpenRouter client with reasoning & offline fallback
│   │       └── mcp_client.py       # HTTP client connecting Orchestrator to MCP server
│   ├── tests/                      # Pytest suite (Phase 2, Phase 3, Phase 4 suites)
│   ├── Dockerfile
│   └── requirements.txt
│
├── go-gateway/                     # Tier 1: High-Performance Go Ingress Proxy
│   ├── cmd/server/main.go          # Gateway server entry point
│   ├── internal/
│   │   ├── config/config.go        # Environment loader
│   │   ├── handler/                # Route handlers (/health, /api/token, /api/chat)
│   │   ├── middleware/             # Chi JWT auth, IDOR validation, security headers
│   │   ├── response/               # Consistent JSON response utilities
│   │   └── router/router.go        # Chi router and route definitions
│   ├── Dockerfile
│   └── go.mod
│
├── mcp-server/                     # Tier 3: Model Context Protocol Tool Proxy
│   ├── server.py                   # FastAPI MCP endpoints (/tools/list, /tools/execute)
│   ├── tools.py                    # ACID banking mutations (waive, adjust, replace)
│   ├── db.py                       # PostgreSQL transactional context manager
│   ├── Dockerfile
│   └── requirements.txt
│
├── postgres/                       # Tier 4: Core Banking Database
│   └── init.sql                    # Initial schema: accounts, audit_transactions, seed data
│
└── react-ui/                       # Tier 0: Customer Interface & Scenario Runner
    ├── src/
    │   ├── App.jsx                 # Dynamic UI with timeline, status badges, and controls
    │   └── index.css               # Modern banking design system styling
    ├── Dockerfile
    └── package.json
```

---

## ⚡ Quick Start & Setup

### 1. Prerequisites
- **Docker** & **Docker Compose** installed
- **Git**
- *(Optional for local dev)*: Go 1.23+, Python 3.12+, Node.js 20+

### 2. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Edit `.env` to supply your configuration:
```env
# Database Configuration
POSTGRES_DB=banking_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgrespassword
POSTGRES_PORT=5433

# Go Gateway Configuration
PORT=8080
JWT_SECRET=academic-project-secret-key-2026
AGENT_SERVICE_URL=http://fastapi-agent:8000

# OpenRouter AI Configuration
OPENROUTER_API_KEY=your-openrouter-api-key-here
OPENROUTER_MODEL=inclusionai/ling-3.0-flash-vl:free
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

# React UI Configuration
VITE_GATEWAY_URL=http://localhost:8080
```

> **Note**: If `OPENROUTER_API_KEY` is not provided, the orchestrator automatically falls back to its built-in deterministic NLP pattern matcher so the platform remains fully functional offline!

### 3. Launch with Docker Compose
Start all 5 microservices in detached mode:
```bash
docker compose up -d --build
```

Check running container status:
```bash
docker compose ps
```

Once running, access the web portal at:
👉 **[http://localhost:5173](http://localhost:5173)**

---

## 🧪 Testing & Verification Guide

### 1. Automated Test Suites

#### FastAPI Agent & Policy Suite (22 Unit & Integration Tests)
```bash
source .venv/bin/activate
PYTHONPATH=fastapi-agent pytest fastapi-agent/tests/test_phase2.py fastapi-agent/tests/test_phase3_policy.py
```

#### Go API Gateway Compilation & Build Check
```bash
cd go-gateway
go build ./...
```

---

### 2. End-to-End Verification via cURL

#### Step 1: Ingress Health Check
```bash
curl -s http://localhost:8080/health
```
*Expected*: `{"router":"chi/v5","service":"go-gateway","status":"ok",...}`

#### Step 2: Obtain Signed Test JWT
```bash
TOKEN=$(curl -s "http://localhost:8080/api/token/test?account_id=ACC-1001" | grep -o '"token":"[^"]*' | cut -d'"' -f4)
```

#### Step 3: Test Policy Approval & Real-Time MCP Execution
Issue a legitimate card replacement request for account `ACC-1001`:
```bash
curl -s -X POST http://localhost:8080/api/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "My credit card was stolen, please dispatch a replacement card"}'
```
*Expected Response*:
```json
{
  "intent": "card_replacement",
  "confidence_score": 0.98,
  "slots": {"delivery_type": "standard", "reason": "stolen"},
  "policy_decision": "APPROVED",
  "policy_rule": "POL-CR-001:ActiveCardReplacement",
  "execution_result": {
    "status": "SUCCESS",
    "tool_called": "replace_card"
  },
  "status": "executed"
}
```

#### Step 4: Test IDOR Authorization Barrier
Attempt to execute actions against `ACC-1002` using a token signed for `ACC-1001`:
```bash
curl -s -i -X POST http://localhost:8080/api/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Waive my fee", "account_id": "ACC-1002"}'
```
*Expected Response*:
`HTTP/1.1 403 Forbidden` with `Access denied: cannot perform actions for account 'ACC-1002' with credentials for 'ACC-1001'`.

---

## 🔒 Security & Isolation Model

The platform enforces multiple defense-in-depth layers:

1. **Insecure Direct Object Reference (IDOR) Mitigation**:
   - The Go Gateway intercepts incoming requests, decodes the JWT subject (`sub`), and strictly compares it against client-provided payload IDs. Any discrepancy triggers an immediate `403 Forbidden` prior to hitting internal services.
2. **Deterministic Guardrails**:
   - LLMs are never granted direct write privileges or SQL capabilities.
   - Even if the LLM hallucinated an approval, the Python Policy Engine evaluates conditions against live PostgreSQL account data and will reject unauthorized actions.
3. **Defense-in-Depth Tool Validation**:
   - The MCP tool endpoints independently verify account status (e.g. refusing card replacement if account is `suspended` or flagged with `fraud_alert`).
4. **Hardened HTTP Response Headers**:
   - The Gateway applies `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `Content-Security-Policy`, and strict CORS policies.

---

## 👨‍💻 Author & Academic Context

- **Author**: Vedant Desai ([@vedantbladers](https://github.com/vedantbladers))
- **Project Title**: *An Agentic AI Platform for Single-Interaction Credit Card Resolution, Real-Time Execution, and Verifiable Auditing*
- **Focus**: Agentic AI Workflows, Deterministic Safety Architectures, Microservices, and Verifiable Financial Transactions.
