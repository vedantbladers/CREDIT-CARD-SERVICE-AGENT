# Engineering Process & Build Log
## Project: Agentic AI Platform for Single-Interaction Credit Card Resolution, Real-Time Execution, and Verifiable Auditing

> **Purpose of this document**: This file tracks the step-by-step evolution, architectural decisions, implementation details, verification records, and known simplifications across all project phases. It serves as a continuous record for academic review, report writing, and project defense.

---

## 1. High-Level Architecture Overview

```
                          ┌───────────────────────┐
                          │   React Chat UI       │ (Port 5173)
                          └──────────┬────────────┘
                                     │ HTTP POST /api/chat
                                     │ (Bearer JWT)
                                     ▼
                          ┌───────────────────────┐
                          │   Go API Gateway      │ (Port 8080)
                          │  - JWT Verification  │
                          │  - Rate Limiting     │
                          └──────────┬────────────┘
                                     │ HTTP POST /chat
                                     ▼
                          ┌───────────────────────┐
                          │  FastAPI Orchestrator │ (Port 8000)
                          │  - LangGraph State    │
                          │  - Intent & Slots     │
                          └──────────┬────────────┘
                                     │
                                     ▼
                          ┌───────────────────────┐
                          │ Deterministic Policy  │ (Python Safety Layer - No LLM)
                          │ - Rule Guardrails     │
                          └──────────┬────────────┘
                                     │
                                     ▼
                          ┌───────────────────────┐
                          │      MCP Server       │ (Isolation Layer)
                          │ - Approved Tools Only │
                          └──────────┬────────────┘
                                     │
                    ┌────────────────┴────────────────┐
                    ▼                                 ▼
         ┌─────────────────────┐           ┌─────────────────────┐
         │ PostgreSQL Core DB  │           │   Elasticsearch     │
         │ (ACID Transactions) │           │ (Immutable Auditing)│
         └─────────────────────┘           └─────────────────────┘
```

---

## 2. Phase-by-Phase Build History

### Phase 1: Minimal Skeleton & Thin End-to-End Slice (Completed)

#### Objective
Establish a runnable, containerized multi-service skeleton wired end-to-end to prove the request/response pipeline across services for a single intent: **"fee waiver"**. Intelligence is intentionally mocked (no LLM, no database mutation yet).

#### Services Implemented (Modularized & Refactored)

1. **PostgreSQL Core Banking Database (`postgres`)**
   - **File**: `postgres/init.sql`
   - **Image**: `postgres:16-alpine`
   - **Database Name**: `banking_db`
   - **Ports**: `5433:5432` (Host `5433` mapped to container `5432` to avoid host collision)
   - **Table**: `accounts (id, account_number, name, balance, fees_waived_this_quarter, created_at)`
   - **Seed Data**: `ACC-1001` (Alice Johnson), `ACC-1002` (Bob Smith), `ACC-1003` (Charlie Brown)

2. **Go API Gateway (`go-gateway`) — Powered by Chi Router (`v5`)**
   - **Architecture Pattern**: Standard Go layout (`cmd/`, `internal/`)
   - **Files**:
     - `cmd/server/main.go` — Clean server entry point
     - `internal/config/config.go` — Environment and configuration management
     - `internal/middleware/auth.go` — Chi JWT validation middleware (HMAC-SHA256)
     - `internal/response/response.go` — Shared JSON response and error utility
     - `internal/handler/health.go` — Health check endpoint (`GET /health`)
     - `internal/handler/token.go` — Signed mock JWT generator (`GET|POST /api/token/test`)
     - `internal/handler/chat.go` — Protected proxy handler (`POST /api/chat`)
     - `internal/router/router.go` — Chi router, CORS, logger, recoverer, and route groups
   - **Port**: `8080`

3. **FastAPI Agent Orchestrator (`fastapi-agent`) — Clean Layered Python**
   - **Architecture Pattern**: Layered Python domain architecture
   - **Files**:
     - `main.py` — Entry point delegating to modular application factory
     - `app/main.py` — FastAPI app instantiation, CORS, and router registration
     - `app/core/config.py` — Application settings & database connection string
     - `app/models/schemas.py` — Pydantic request/response validation schemas
     - `app/services/intent_matcher.py` — Isolated keyword intent classifier (ready to swap with LangGraph in Phase 2)
     - `app/api/health.py` — Health router (`GET /health`)
     - `app/api/chat.py` — Chat router (`POST /chat`)
     - `app/api/router.py` — Aggregated top-level API router
   - **Port**: `8000`

4. **React Chat Frontend (`react-ui`) — Modular Component Tree**
   - **Architecture Pattern**: Component-based UI with decoupled services layer
   - **Files**:
     - `src/services/api.js` — Dedicated API client for Go Gateway communication
     - `src/components/Header.jsx` — Project banner & phase badge
     - `src/components/AuthBar.jsx` — Cardholder information, JWT status, and test controls
     - `src/components/ChatMessages.jsx` — Scrollable conversation stream with metadata pills
     - `src/components/Suggestions.jsx` — Pre-configured testing chips
     - `src/components/ChatInput.jsx` — Textbox and submit button
     - `src/App.jsx` — Central state coordinator
     - `src/App.css` / `src/index.css` — Styling tokens & layout
   - **Port**: `5173`

5. **Container Orchestration (`docker-compose.yml`)**
   - Coordinates all 4 services on bridge network `platform-net`
   - PostgreSQL health check ensures database readiness before depending services start
   - Persistent volume `postgres_data` for database durability

---

## 3. How to Run and Test the System

### Starting All Services (Single Command)
```bash
docker compose up -d --build
```

### Starting Services in Separate Terminals (Multi-Terminal Mode)

If you prefer to see live, real-time logs for each service in dedicated terminal tabs:

#### Option 1: Start All in Background, Tail Each in Its Own Terminal (Best Practice)
When you run `docker compose up <service>` without `-d`, it runs attached in the foreground, meaning pressing `Ctrl+C` shuts down the container.

To keep services running in the background and use individual terminals for viewing live logs:

1. Start all containers in detached mode (`-d`):
   ```bash
   docker compose up -d
   ```
2. Open 4 separate terminal tabs to follow live logs for each service (pressing `Ctrl+C` will only close the log stream, not kill the server):
   - **Terminal 1 (PostgreSQL logs)**:
     ```bash
     docker compose logs -f postgres
     ```
   - **Terminal 2 (FastAPI Orchestrator logs)**:
     ```bash
     docker compose logs -f fastapi-agent
     ```
   - **Terminal 3 (Go API Gateway logs)**:
     ```bash
     docker compose logs -f go-gateway
     ```
   - **Terminal 4 (React UI logs)**:
     ```bash
     docker compose logs -f react-ui
     ```

#### Option 2: Running Services Natively on Host (with Docker Postgres)
- **Terminal 1 (PostgreSQL Docker)**:
  ```bash
  docker compose up postgres
  ```
- **Terminal 2 (FastAPI Orchestrator)**:
  ```bash
  cd fastapi-agent
  python3 -m venv venv && source venv/bin/activate
  pip install -r requirements.txt
  uvicorn main:app --host 0.0.0.0 --port 8000 --reload
  ```
- **Terminal 3 (Go API Gateway)**:
  ```bash
  cd go-gateway
  export AGENT_SERVICE_URL="http://localhost:8000"
  export PORT="8080"
  go run main.go
  ```
- **Terminal 4 (React Frontend)**:
  ```bash
  cd react-ui
  npm install
  npm run dev
  ```

### Checking Container Health
```bash
docker compose ps
```

### Verification Tests

#### Test 1: Check Database Seeding
```bash
docker compose exec postgres psql -U postgres -d banking_db -c "SELECT * FROM accounts;"
```

#### Test 2: Verify Go Gateway 401 Unauthorized Behavior
```bash
curl -s -i -X POST http://localhost:8080/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Please waive my fee"}' | head -n 12
```
*Expected: HTTP/1.1 401 Unauthorized with message `missing Authorization header`.*

#### Test 3: Verify Authenticated Request Routing
```bash
TOKEN=$(curl -s http://localhost:8080/api/token/test | grep -o '"token":"[^"]*' | cut -d'"' -f4)

curl -s -X POST http://localhost:8080/api/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Please waive my late fee"}'
```
*Expected: HTTP 200 OK with `intent: "fee_waiver"` and `status: "success"`.*

#### Test 4: Web Browser UI Verification
1. Navigate to `http://localhost:5173` in a web browser.
2. Click `"Please waive my credit card annual fee"`: agent responds with `intent: fee_waiver`.
3. Click `"Clear Token (Test 401)"` and send a message: red error banner displays Gateway 401 rejection.
4. Click `"Refresh Test Token"` and test an unhandled prompt: agent responds with `intent: unknown`.

---

### Phase 2: Real LLM Intent Classification & Slot Extraction (LangGraph) (Completed)

#### Objective
Replace the Phase 1 keyword heuristics in FastAPI with a compiled **LangGraph State Graph** that performs structured intent classification, entity slot extraction, and clarification routing for 3 credit card intents + out-of-scope handling.

#### Architecture Implemented
1. **LangGraph State Graph (`fastapi-agent/app/services/graph_orchestrator.py`)**:
   - `AgentState`: Tracks `message`, `intent`, `confidence_score`, `slots`, `needs_clarification`, `clarification_prompt`, `response_message`, and `status`.
   - Sequential Nodes:
     - **Node 1: `classify_intent`** — Classifies into `fee_waiver`, `credit_limit_increase`, `card_replacement`, or `unclear`.
     - **Node 2: `extract_slots`** — Extracts structured parameters (`fee_type`, `amount`, `requested_limit`, `reason`, `delivery_type`).
     - **Node 3: `route_decision`** — Enforces slot completeness and confidence thresholds (`< 0.70`), routing to a clarification response instead of guessing.
2. **LLM Factory (`fastapi-agent/app/services/llm_factory.py`)**:
   - Exclusively configured for **Fireworks AI** (`accounts/fireworks/models/deepseek-v4-flash-0731` via `https://api.fireworks.ai/inference/v1`).
   - Removed all dependencies and references to OpenAI, Anthropic, and Ollama.
   - Built-in deterministic NLP fallback ensuring the LangGraph graph runs and passes all tests offline if the remote key is unauthorized or offline.
3. **Pydantic Schemas (`fastapi-agent/app/models/schemas.py`)**:
   - Added `confidence_score: float`, `slots: Dict[str, Any]`, `needs_clarification: bool`, and `clarification_prompt`.
4. **Automated Pytest Suite (`fastapi-agent/tests/test_phase2.py`)**:
   - 6 test cases verifying all 3 intents, full slot extraction, missing slot clarification triggers, and ambiguous queries.
5. **React UI Updates (`react-ui/`)**:
   - Visual slots breakdown chips displaying parameter names and values.
   - AI confidence score pills (`95% confidence`).
   - Clarification alert box when `needs_clarification` is active.
   - Interactive suggestion chips for all 4 scenarios.

---

## 3. How to Run and Test the System

### Starting All Services (Single Command)
```bash
docker compose up -d --build
```

### Running Phase 2 Automated Pytests
```bash
docker compose exec fastapi-agent pytest tests/test_phase2.py -v
```

### Testing All 4 Scenarios via Go API Gateway
```bash
TOKEN=$(curl -s http://localhost:8080/api/token/test | grep -o '"token":"[^"]*' | cut -d'"' -f4)

# 1. Fee Waiver
curl -s -X POST http://localhost:8080/api/chat -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{"message": "Can you please waive my $95 annual fee?"}' | jq .

# 2. Credit Limit Increase (Complete)
curl -s -X POST http://localhost:8080/api/chat -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{"message": "Raise my credit limit to $15,000"}' | jq .

# 3. Card Replacement (Missing Slot -> Clarify)
curl -s -X POST http://localhost:8080/api/chat -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{"message": "Send me a replacement card"}' | jq .

# 4. Out-of-Scope (Clarify)
curl -s -X POST http://localhost:8080/api/chat -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{"message": "Can you help me apply for a used car loan?"}' | jq .
```

---

---

### Phase 3: Deterministic Policy Engine (Completed)

#### Objective
Build a standalone, LLM-free Python policy engine that sits between the LangGraph orchestrator and database execution. It enforces hard corporate banking guardrails, safety constraints, and business limits, evaluating intent and extracted slots deterministically into `APPROVED`, `REJECTED`, or `NEEDS_ESCALATION` verdicts with auditable reasoning.

#### Architecture Implemented
1. **Domain Models (`fastapi-agent/app/policy/models.py`)**:
   - `PolicyDecision`: Enum with values `APPROVED`, `REJECTED`, `NEEDS_ESCALATION`.
   - `AccountProfile`: Entity containing `account_number`, `name`, `balance`, `credit_limit`, `fees_waived_this_quarter`, `tenure_months`, `is_active`, `status`.
   - `PolicyResult`: Audit model capturing `decision`, `rule_name`, `reason`, `details`, `evaluated_at`.
2. **Deterministic Rules Engine (`fastapi-agent/app/policy/rules.py`)**:
   - **Fee Waiver Rules**:
     - `POL-FW-001`: Max 1 waiver per calendar quarter (`fees_waived_this_quarter >= 1` ➔ `REJECTED`).
     - `POL-FW-002`: High-value fee escalation threshold (`amount > $150.00` ➔ `NEEDS_ESCALATION`).
     - Account standing verification (`status != "active"` ➔ `REJECTED`).
   - **Credit Limit Increase Rules**:
     - `POL-CLI-001`: Increase <= 20% of current limit and tenure >= 6 months ➔ `APPROVED`.
     - `POL-CLI-002`: Account tenure < 6 months ➔ `REJECTED`.
     - `POL-CLI-003`: Increase between 20% and 50% ➔ `NEEDS_ESCALATION` (Manual Underwriting).
     - `POL-CLI-004`: Increase > 50% cap ➔ `REJECTED` (Excessive Risk).
     - Requested limit <= current limit ➔ `REJECTED`.
   - **Card Replacement Rules**:
     - `POL-CR-001`: Active account ➔ `APPROVED` (stolen, lost, damaged, expired).
     - `POL-CR-002`: Fraud alert hold (`status == "fraud_alert"` ➔ `NEEDS_ESCALATION`).
     - Suspended or inactive accounts ➔ `REJECTED`.
3. **Account Store & Lookup (`fastapi-agent/app/policy/repository.py`)**:
   - In-memory repository seeded with 4 cardholder test profiles:
     - `ACC-1001` (Alice Johnson): Active, 0 waivers, 18mo tenure, $10k limit (All approvals & high-limit tests).
     - `ACC-1002` (Bob Smith): Active, 1 waiver, 3mo tenure, $5k limit (Waiver limit and tenure rejection tests).
     - `ACC-1003` (Charlie Brown): Suspended, 2 waivers, 24mo tenure, $15k limit (Suspended account tests).
     - `ACC-1004` (Dana Scully): Fraud Alert, 0 waivers, 14mo tenure, $7.5k limit (Fraud escalation tests).
4. **Pipeline Integration (`fastapi-agent/app/api/chat.py` & `schemas.py`)**:
   - FastAPI `/chat` passes structured LangGraph output directly into `evaluate_policy()`.
   - `ChatResponse` enriched with `policy_decision`, `policy_rule`, `policy_reason`, and `policy_details`.
5. **Gateway Upgrades (`go-gateway/`)**:
   - `GET|POST /api/token/test?account_id=ACC-XXXX` supports issuing JWTs for any seeded test cardholder.
   - Forwarding timeout expanded to 60 seconds to support LLM reasoning headroom.
   - `GET /api/accounts` proxies account profile queries to FastAPI.
6. **React UI Updates (`react-ui/`)**:
   - Interactive Cardholder dropdown in `AuthBar.jsx` for 1-click profile switching.
   - Policy verdict cards rendering green `APPROVED`, red `REJECTED`, and amber `NEEDS ESCALATION` cards with rule IDs, reasons, and metric breakdown chips.
   - Suggestions suite containing test buttons for all policy paths.
7. **Automated Unit & Integration Test Suite (`fastapi-agent/tests/test_phase3_policy.py`)**:
   - 16 isolated pytest cases + 6 Phase 2 regression tests = **22 passing tests in 0.2s**.

---

## 4. How to Verify Phase 3

### 1. Automated Test Suite
```bash
cd fastapi-agent
PYTHONPATH=. ../.venv/bin/pytest tests/test_phase3_policy.py tests/test_phase2.py -v
```
*Result: 22 passed.*

### 2. Live API Testing via Go Gateway
```bash
# 1. Fee Waiver Approved (Alice - 0 waivers)
TOKEN_ALICE=$(curl -s "http://localhost:8080/api/token/test?account_id=ACC-1001" | grep -o '"token":"[^"]*' | cut -d'"' -f4)
curl -s -X POST http://localhost:8080/api/chat -H "Authorization: Bearer $TOKEN_ALICE" -H "Content-Type: application/json" \
  -d '{"message": "Can you please waive my $95 annual fee?"}' | jq .

# 2. Fee Waiver Rejected (Bob - 1 waiver already used)
TOKEN_BOB=$(curl -s "http://localhost:8080/api/token/test?account_id=ACC-1002" | grep -o '"token":"[^"]*' | cut -d'"' -f4)
curl -s -X POST http://localhost:8080/api/chat -H "Authorization: Bearer $TOKEN_BOB" -H "Content-Type: application/json" \
  -d '{"message": "Please waive my late fee of $35"}' | jq .

# 3. Credit Limit Increase Escalated (Alice - +40% increase)
curl -s -X POST http://localhost:8080/api/chat -H "Authorization: Bearer $TOKEN_ALICE" -H "Content-Type: application/json" \
  -d '{"message": "Please increase my credit limit to $14,000"}' | jq .

# 4. Card Replacement Rejected (Charlie - Suspended Account)
TOKEN_CHARLIE=$(curl -s "http://localhost:8080/api/token/test?account_id=ACC-1003" | grep -o '"token":"[^"]*' | cut -d'"' -f4)
curl -s -X POST http://localhost:8080/api/chat -H "Authorization: Bearer $TOKEN_CHARLIE" -H "Content-Type: application/json" \
  -d '{"message": "My card was stolen, send me a replacement"}' | jq .
```

### 3. Visual Verification Artifacts
- Browser screenshot captured via Chrome Devtools MCP tool: `phase3_verified_website.png`
- Shows live cardholder switching (`ACC-1002 - Bob Smith`), `❌ POLICY REJECTED` verdict card with rule `POL-FW-001:QuarterlyFeeWaiverLimit`, and previous `⚠️ NEEDS ESCALATION` verdict card with rule `POL-CLI-003:ManualUnderwritingEscalation`.

---

## 5. Simplifications & Academic Report Notes (Known Limitations)

| Area | Current Phase 3 Implementation | Production / Enterprise Standard | Report Rationale |
|---|---|---|---|
| **Policy Engine** | Standalone Python module with pure deterministic rule functions | Distributed Drools, Open Policy Agent (OPA), or specialized rule engine with dynamic rule deployment | Keeps rule execution deterministic, sub-millisecond, and fully testable without introducing complex rule engine infrastructure. |
| **Account Store** | In-memory repository with test seeds matching PostgreSQL schema | Direct query to read-replica core banking DB with transaction isolation | Direct DB access is intentionally restricted until Phase 4 MCP server isolation layer is introduced. |
| **Audit Log** | Structured in-memory response models returned through gateway | Immutable, write-once append log in Elasticsearch | Full async Elasticsearch audit trail is planned for Phase 5. |

---

## 6. Next Steps / Project Roadmap

- [x] **Phase 1**: Skeleton & one thin end-to-end slice (fee waiver keyword match)
- [x] **Phase 2**: Real LLM intent classification + slot extraction (LangGraph state graph: 3 intents + clarify fallback)
- [x] **Phase 3**: Deterministic Python Policy Engine (unit-tested rule functions: max 1 waiver/quarter, 20% credit increase limit)
- [ ] **Phase 4**: MCP server + ACID transaction execution against PostgreSQL
- [ ] **Phase 5**: Async immutable audit logging via Elasticsearch
- [ ] **Phase 6**: Go API Gateway hardening (real JWT issuance, rate limiting per cardholder)
- [ ] **Phase 7**: React UI polish (multi-turn conversation flow, escalation/rejection cards)
- [ ] **Phase 8**: Final testing pass, architecture documentation, and 5-minute evaluation demo script

