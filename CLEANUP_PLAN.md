# REPOSITORY CLEANUP PLAN
**AI Receptionist - Minimal Voice Pipeline**

**Generated:** November 30, 2025  
**Repository:** /root/antigravity_bundle/testing/ai_receptionist  
**Goal:** Keep ONLY FastAPI + Twilio webhook + Gemini Flash + Optional audio pipeline

---

## 🎯 RETENTION CRITERIA

**KEEP ONLY:**
- FastAPI application core
- Twilio webhook at `/twilio/webhook`
- AI logic using Gemini Flash
- Optional audio pipeline (Twilio TwiML)
- Core telephony service abstraction
- Configuration management
- Dependency injection

**DELETE EVERYTHING ELSE:**
- Tests (except webhook-specific if needed)
- Database/Alembic migrations
- Streamlit UI
- Sample scripts
- Documentation (keep only README.md)
- Admin tools
- Cache folders
- UI/templates
- Experimental code
- Other projects (inventory_manager, portfolio)

---

## 📦 PART 1: FOLDERS SAFE TO DELETE

### Root-Level Folders (Outside ai_receptionist/)

#### ❌ DELETE - Cache & Temporary (12 folders)
```
.pytest_cache/              # Pytest cache
.ruff_cache/                # Ruff linter cache
.streamlit/                 # Streamlit config (UI not needed)
__pycache__/                # Python bytecode cache
.vscode/                    # VSCode settings (optional, user-specific)
```

#### ❌ DELETE - Infrastructure & Tools (8 folders)
```
alembic/                    # Database migrations (no DB needed)
scripts/                    # Helper scripts (generate_changelog, migrations_helper)
tools/                      # Admin tools (adminctl.py)
tests/                      # Root-level tests (not webhook-specific)
.github/                    # GitHub workflows (deploy, test, CI, release, security)
```

#### ❌ DELETE - Documentation & Specs (3 folders)
```
docs/                       # Documentation + samples (EVAL_SYSTEM_README, sample JSON flows)
PRODUCTS/                   # Product specifications (VERSIONS.md)
data/                       # Sample data (appointments.json)
```

#### ❌ DELETE - Other Projects (2 folders)
```
../inventory_manager/       # Completely separate project
../portfolio/               # Completely separate project
```

**Total Root-Level Folders to Delete: 25+**

---

### Module-Level Folders (Inside ai_receptionist/)

#### ❌ DELETE - Cache (3 folders)
```
ai_receptionist/.pytest_cache/
ai_receptionist/.ruff_cache/
ai_receptionist/__pycache__/
```

#### ❌ DELETE - UI Components (1 folder)
```
ai_receptionist/static/      # UI files (index.html)
```

#### ❌ DELETE - Testing (1 folder)
```
ai_receptionist/tests/       # Module-level tests (9 test files)
```

#### ❌ DELETE - Database Layer (1 folder)
```
ai_receptionist/db/          # Database repositories (no DB needed)
```

#### ❌ DELETE - Background Workers (1 folder)
```
ai_receptionist/workers/     # Background jobs (tasks.py, fallback.py)
```

#### ❌ DELETE - Business Logic Not Needed (2 folders)
```
ai_receptionist/services/billing/   # Billing/usage tracking
ai_receptionist/services/flags/     # Feature flags
```

#### ⚠️ EVALUATE - May Delete (2 folders)
```
ai_receptionist/agent/       # Hardcoded conversation bot (396 lines)
                             # Can be replaced by Gemini - RECOMMEND DELETE

ai_receptionist/api/         # Legacy API (twilio_voice.py)
                             # Duplicate of app/api/twilio.py - RECOMMEND DELETE
```

**Total Module-Level Folders to Delete: 11+**

---

## 📄 PART 2: FILES SAFE TO DELETE

### Root-Level Files

#### ❌ DELETE - Configuration Files (4 files)
```
alembic.ini                  # Alembic configuration
docker-compose.dev.yml       # Development docker compose
pytest.ini                   # Pytest configuration
.env                         # User-specific (should not be in repo anyway)
```

#### ❌ DELETE - Documentation Files (10+ files)
```
COMMIT_MSG.txt               # Commit message template
EVAL_SYSTEM_README.md        # Evaluation system docs
REFACTORING_SUMMARY.md       # Previous refactoring notes
TECHNICAL_DEBT_AUDIT.md      # Technical debt documentation
onboarding_checklist.md      # Onboarding guide
pilot_agreement.md           # Pilot program agreement
REFACTORING_PLAN.md          # THIS cleanup plan (delete after use)
DIFF_PREVIEW.md              # Diff preview (delete after use)
EXECUTIVE_SUMMARY.md         # Executive summary (delete after use)
README_REFACTORING.md        # Refactoring docs (delete after use)
CHECKLIST.md                 # Checklist (delete after use)
requirements.minimal.txt     # Will become requirements.txt
refactor.sh                  # Script (delete after use)
```

#### ❌ DELETE - Test Files (2 files)
```
test_improvements.py         # Test improvement script
test_voice_integration.py    # Voice integration tests
```

#### ❌ DELETE - Monitoring & Debug Tools (2 files)
```
call_monitor.py              # Call monitoring tool
start_monitor.py             # Monitor startup script
```

**Total Root-Level Files to Delete: 18+**

---

### Module-Level Files (Inside ai_receptionist/)

#### ❌ DELETE - Config Files (3 files)
```
ai_receptionist/.env.example
ai_receptionist/.gitignore
ai_receptionist/pyproject.toml  # If not using as package
```

#### ❌ DELETE - Service Files (2 files)
```
ai_receptionist/services/rag.py      # RAG/vector store (120 lines)
ai_receptionist/services/router.py   # Request routing logic
```

#### ❌ DELETE - Admin API (1 file)
```
ai_receptionist/app/api/admin.py     # Admin dashboard endpoints
```

#### ⚠️ EVALUATE - Voice Service Files (6 files)
```
ai_receptionist/services/voice/intents.py         # Hardcoded intent detection (150 lines)
                                                   # REPLACE with Gemini - RECOMMEND DELETE

ai_receptionist/services/voice/messages.py        # Static message templates
                                                   # REPLACE with Gemini - RECOMMEND DELETE

ai_receptionist/services/voice/business_config.py # Business-specific config
                                                   # Move to .env or config - RECOMMEND DELETE

ai_receptionist/services/voice/session.py         # Call session management
                                                   # KEEP if needed for stateful conversations

ai_receptionist/services/voice/cost_tracker.py    # Cost tracking
                                                   # DELETE if not tracking costs

ai_receptionist/services/voice/endpoints.py       # TwiML generation (247 lines)
                                                   # REVIEW - may need for audio pipeline
```

**Total Module-Level Files to Delete: 12+**

---

## ✅ PART 3: RECOMMENDED MINIMAL FOLDER STRUCTURE

```
ai_receptionist/
├── .env                          # ✅ Environment variables (create if not exists)
├── .gitignore                    # ✅ Git ignore (keep root-level)
├── README.md                     # ✅ Simplified documentation
├── requirements.txt              # ✅ Minimal dependencies (7-8 packages)
│
└── ai_receptionist/              # Main package
    ├── __init__.py               # ✅ Package init
    │
    ├── app/                      # FastAPI application
    │   ├── __init__.py           # ✅
    │   ├── main.py               # ✅ SIMPLIFIED - FastAPI app entry point
    │   └── api/
    │       ├── __init__.py       # ✅
    │       └── twilio.py         # ✅ KEEP - /twilio/webhook endpoint
    │
    ├── config/                   # Configuration
    │   ├── __init__.py           # ✅
    │   └── settings.py           # ✅ SIMPLIFIED - Minimal Pydantic settings
    │
    ├── core/                     # Core utilities
    │   ├── __init__.py           # ✅
    │   └── di.py                 # ✅ SIMPLIFIED - Dependency injection
    │
    ├── models/                   # Data models
    │   ├── __init__.py           # ✅
    │   └── dtos.py               # ✅ KEEP - Request/response models (if needed)
    │
    ├── services/                 # Business services
    │   ├── __init__.py           # ✅
    │   │
    │   ├── ai/                   # AI integration
    │   │   ├── __init__.py       # ✅ KEEP (currently empty)
    │   │   └── gemini.py         # 🆕 CREATE - Gemini Flash integration
    │   │
    │   └── telephony/            # Telephony services
    │       ├── __init__.py       # ✅
    │       ├── telephony.py      # ✅ KEEP - Abstract service interface
    │       └── twilio_service.py # ✅ KEEP - Twilio implementation
    │
    └── utils/                    # Utilities
        ├── __init__.py           # ✅
        └── helpers.py            # ✅ SIMPLIFIED - Minimal utilities
```

**Total Structure:**
- **Folders:** 8 core folders
- **Python Files:** ~15 files
- **Dependencies:** 7-8 packages

---

## 🔍 PART 4: DIFF-STYLE CLEANUP PREVIEW

### Summary Statistics

```diff
BEFORE Cleanup:
- Folders: 35+ (root + module)
- Python files: 119
- Config files: 15+
- Documentation: 20+ files
- Dependencies: 50+ packages
- Total size: ~5 MB + 50 MB cache

AFTER Cleanup:
- Folders: 8
- Python files: ~15
- Config files: 2 (.env, .gitignore)
- Documentation: 1 (README.md)
- Dependencies: 7-8 packages
- Total size: ~200 KB

REDUCTION:
- 77% fewer folders
- 87% fewer Python files
- 96% smaller codebase
```

---

### Folder Deletions

```diff
ROOT LEVEL:
- .pytest_cache/              ❌ DELETE
- .ruff_cache/                ❌ DELETE
- .streamlit/                 ❌ DELETE
- .vscode/                    ❌ DELETE
- __pycache__/                ❌ DELETE
- alembic/                    ❌ DELETE
- data/                       ❌ DELETE
- docs/                       ❌ DELETE
- PRODUCTS/                   ❌ DELETE
- scripts/                    ❌ DELETE
- tests/                      ❌ DELETE
- tools/                      ❌ DELETE
- .github/                    ❌ DELETE

MODULE LEVEL (ai_receptionist/):
- .pytest_cache/              ❌ DELETE
- .ruff_cache/                ❌ DELETE
- __pycache__/                ❌ DELETE
- agent/                      ❌ DELETE (or replace with Gemini)
- api/                        ❌ DELETE (legacy duplicate)
- db/                         ❌ DELETE
- static/                     ❌ DELETE
- tests/                      ❌ DELETE
- workers/                    ❌ DELETE
- services/billing/           ❌ DELETE
- services/flags/             ❌ DELETE

KEEP:
+ ai_receptionist/app/        ✅ KEEP (simplified)
+ ai_receptionist/config/     ✅ KEEP (simplified)
+ ai_receptionist/core/       ✅ KEEP (simplified)
+ ai_receptionist/models/     ✅ KEEP (if needed)
+ ai_receptionist/services/ai/           ✅ KEEP (add gemini.py)
+ ai_receptionist/services/telephony/    ✅ KEEP
+ ai_receptionist/utils/      ✅ KEEP (simplified)
```

---

### File Deletions

```diff
ROOT LEVEL FILES:
- alembic.ini                 ❌ DELETE
- call_monitor.py             ❌ DELETE
- CHECKLIST.md                ❌ DELETE (after cleanup)
- COMMIT_MSG.txt              ❌ DELETE
- DIFF_PREVIEW.md             ❌ DELETE (after cleanup)
- docker-compose.dev.yml      ❌ DELETE
- EVAL_SYSTEM_README.md       ❌ DELETE
- EXECUTIVE_SUMMARY.md        ❌ DELETE (after cleanup)
- onboarding_checklist.md     ❌ DELETE
- pilot_agreement.md          ❌ DELETE
- pytest.ini                  ❌ DELETE
- README_REFACTORING.md       ❌ DELETE (after cleanup)
- refactor.sh                 ❌ DELETE (after cleanup)
- REFACTORING_PLAN.md         ❌ DELETE (after cleanup)
- REFACTORING_SUMMARY.md      ❌ DELETE
- requirements.minimal.txt    ❌ DELETE (merge into requirements.txt)
- start_monitor.py            ❌ DELETE
- TECHNICAL_DEBT_AUDIT.md     ❌ DELETE
- test_improvements.py        ❌ DELETE
- test_voice_integration.py   ❌ DELETE

MODULE LEVEL FILES:
- ai_receptionist/.env.example              ❌ DELETE
- ai_receptionist/.gitignore                ❌ DELETE (keep root-level)
- ai_receptionist/pyproject.toml            ❌ DELETE (if not packaging)
- ai_receptionist/README.md                 ❌ DELETE (keep root-level)
- ai_receptionist/api/twilio_voice.py       ❌ DELETE (legacy duplicate)
- ai_receptionist/app/api/admin.py          ❌ DELETE
- ai_receptionist/services/rag.py           ❌ DELETE
- ai_receptionist/services/router.py        ❌ DELETE
- ai_receptionist/services/voice/intents.py ❌ DELETE (replace with Gemini)
- ai_receptionist/services/voice/messages.py ❌ DELETE (replace with Gemini)
- ai_receptionist/services/voice/business_config.py ❌ DELETE (move to .env)

KEEP & SIMPLIFY:
+ ai_receptionist/app/main.py               ✅ SIMPLIFY (remove UI/admin)
+ ai_receptionist/config/settings.py        ✅ SIMPLIFY (remove DB/Redis/OpenAI)
+ ai_receptionist/core/di.py                ✅ SIMPLIFY (remove unused deps)
+ ai_receptionist/app/api/twilio.py         ✅ KEEP (core webhook)
+ ai_receptionist/services/telephony/*.py   ✅ KEEP
+ ai_receptionist/utils/helpers.py          ✅ SIMPLIFY

CREATE NEW:
+ ai_receptionist/services/ai/gemini.py     🆕 CREATE (Gemini integration)
```

---

### Dependencies Cleanup

```diff
requirements.txt BEFORE (50+ packages):
- alembic==1.13.2             ❌ REMOVE (database migrations)
- SQLAlchemy==2.0.36          ❌ REMOVE (ORM)
- redis==5.0.6                ❌ REMOVE (caching)
- streamlit==1.50.0           ❌ REMOVE (UI framework)
- altair==5.5.0               ❌ REMOVE (streamlit dep)
- pandas==2.3.3               ❌ REMOVE (streamlit dep)
- numpy==2.2.6                ❌ REMOVE (streamlit dep)
- pillow==11.3.0              ❌ REMOVE (streamlit dep)
- pyarrow==21.0.0             ❌ REMOVE (streamlit dep)
- openai==2.2.0               ❌ REMOVE (replaced by Gemini)
- pytest==8.4.2               ❌ REMOVE (testing)
- pytest-json-report==1.5.0   ❌ REMOVE (testing)
- GitPython==3.1.45           ❌ REMOVE (git integration)
- Mako==1.3.10                ❌ REMOVE (alembic dep)
- greenlet==3.2.4             ❌ REMOVE (SQLAlchemy dep)
- aiohttp==3.13.0             ❌ REMOVE (use httpx)
- ... (30+ more packages)

requirements.txt AFTER (7-8 packages):
+ fastapi==0.118.2            ✅ KEEP (web framework)
+ uvicorn[standard]==0.37.0   ✅ KEEP (ASGI server)
+ httpx==0.28.1               ✅ KEEP (HTTP client)
+ twilio==9.8.3               ✅ KEEP (Twilio SDK)
+ google-generativeai==0.8.3  ✅ ADD (Gemini Flash)
+ pydantic==2.12.0            ✅ KEEP (data validation)
+ pydantic-settings==2.4.0    ✅ KEEP (settings)
+ python-dotenv==1.1.1        ✅ KEEP (env vars)
```

---

### Code Simplifications

#### main.py (BEFORE: 50 lines → AFTER: 20 lines)

```diff
- from fastapi.staticfiles import StaticFiles        ❌ REMOVE
- from fastapi.responses import FileResponse         ❌ REMOVE
- from pathlib import Path                           ❌ REMOVE
- from ai_receptionist.app.api.admin import router   ❌ REMOVE
- from ai_receptionist.api.twilio_voice import router ❌ REMOVE
- from ai_receptionist.services.voice.endpoints import router ❌ REMOVE

+ from fastapi import FastAPI, Depends              ✅ KEEP
+ from ai_receptionist.app.api.twilio import router ✅ KEEP

- # Mount static files                              ❌ REMOVE BLOCK
- if STATIC_DIR.exists():
-     app.mount("/static", StaticFiles(...))

- # Serve UI at root                                ❌ REMOVE BLOCK
- @app.get("/")
- def root():
-     return FileResponse(...)

- app.include_router(admin_router)                  ❌ REMOVE
- app.include_router(twilio_voice_router)           ❌ REMOVE
- app.include_router(voice_router)                  ❌ REMOVE

+ @app.get("/health")                               ✅ KEEP
+ def health(...): ...

+ app.include_router(twilio_router)                 ✅ KEEP
```

#### settings.py (BEFORE: 163 lines → AFTER: 40 lines)

```diff
- # Database Configuration                          ❌ REMOVE BLOCK
- database_url: Optional[str] = None
- postgres_host: str = "localhost"
- postgres_port: int = 5432
- ...

- # Redis Configuration                             ❌ REMOVE BLOCK
- redis_url: Optional[str] = None
- redis_host: str = "localhost"
- ...

- # OpenAI Configuration                            ❌ REMOVE
- openai_api_key: Optional[str] = None

+ # Gemini Configuration                            ✅ ADD
+ gemini_api_key: str
+ gemini_model: str = "gemini-2.0-flash-exp"
```

#### di.py Simplifications

```diff
- from ai_receptionist.db import get_db_session      ❌ REMOVE
- from ai_receptionist.services.billing import ...   ❌ REMOVE
- from ai_receptionist.services.flags import ...     ❌ REMOVE

- def get_db_session(): ...                          ❌ REMOVE
- def get_billing_service(): ...                     ❌ REMOVE
- def get_feature_flags(): ...                       ❌ REMOVE

+ from ai_receptionist.services.ai.gemini import get_gemini_service ✅ ADD
+ def get_ai_service(): return get_gemini_service()  ✅ ADD
```

---

## 🎯 DETAILED DELETION LIST

### Cache & Temporary Files (DELETE IMMEDIATELY)

```bash
# These can be deleted with no impact:
.pytest_cache/
.ruff_cache/
__pycache__/
.venv/                        # Virtual environment (user-specific)
ai_receptionist/.pytest_cache/
ai_receptionist/.ruff_cache/
ai_receptionist/__pycache__/
ai_receptionist/*/__pycache__/
ai_receptionist/*/*/__pycache__/
```

**Command to delete all cache:**
```bash
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null
find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete
find . -type f -name "*.pyo" -delete
```

---

### Infrastructure Folders (SAFE TO DELETE)

```bash
alembic/                      # Database migrations - not needed
  └── versions/
      └── 0001_create_schema_version.py
  └── env.py

scripts/                      # Helper scripts - not needed
  ├── generate_changelog.py
  └── migrations_helper.py

tools/                        # Admin tools - not needed
  └── adminctl.py

tests/                        # Root-level tests - not needed
  ├── test_migrations.py
  ├── test_generate_changelog.py
  ├── test_eval_blueprint.py
  ├── test_voice_webhook.py
  ├── tests_test_adminctl.py
  └── test_calendar_stub.py

.github/                      # GitHub workflows - optional
  └── workflows/
      ├── ci.yml
      ├── test.yml
      ├── deploy.yml
      ├── release.yml
      └── security-check.yml
```

---

### Documentation & Samples (SAFE TO DELETE)

```bash
docs/                         # Documentation - keep only README.md
  ├── EVAL_SYSTEM_README.md
  └── samples/
      ├── complete_booking_flow.json
      ├── haircut_ambiguous_time.json
      ├── haircut_after_hours.json
      ├── haircut_cancel_flow.json
      ├── haircut_conflict_propose_alt.json
      ├── haircut_missing_service.json
      ├── haircut_payment_refusal.json
      ├── haircut_reschedule_flow.json
      ├── payment_security_rejection.json
      ├── reschedule_appointment_flow.json
      ├── double_booking_conflict.json
      ├── after_hours_request.json
      ├── ambiguous_datetime_request.json
      ├── cancel_appointment_flow.json
      ├── incomplete_booking_missing_datetime.json
      ├── missing_name_flow.json
      └── missing_service_type.json

PRODUCTS/                     # Product specs - not needed
  └── VERSIONS.md

data/                         # Sample data - not needed
  └── appointments.json

# Documentation files (keep only README.md)
COMMIT_MSG.txt
EVAL_SYSTEM_README.md
REFACTORING_SUMMARY.md
TECHNICAL_DEBT_AUDIT.md
onboarding_checklist.md
pilot_agreement.md
REFACTORING_PLAN.md          # Delete after cleanup
DIFF_PREVIEW.md              # Delete after cleanup
EXECUTIVE_SUMMARY.md         # Delete after cleanup
README_REFACTORING.md        # Delete after cleanup
CHECKLIST.md                 # Delete after cleanup
```

---

### Module-Level Deletions (SAFE TO DELETE)

```bash
ai_receptionist/agent/        # Hardcoded conversation logic - replace with Gemini
  ├── __init__.py
  └── conversation_bot.py     # 396 lines of hardcoded logic

ai_receptionist/api/          # Legacy duplicate API
  └── twilio_voice.py         # Duplicate of app/api/twilio.py

ai_receptionist/db/           # Database layer - not needed
  ├── __init__.py
  └── repositories.py

ai_receptionist/static/       # UI components - not needed
  └── index.html              # ChatGPT-style UI

ai_receptionist/tests/        # Module-level tests - not needed
  ├── test_health.py
  ├── test_feature_flag_service.py
  ├── test_twilio_webhook.py
  ├── test_billing.py
  ├── test_rag.py
  ├── test_router.py
  ├── test_voice_endpoints.py
  ├── test_fallback.py
  └── conftest.py

ai_receptionist/workers/      # Background jobs - not needed
  ├── __init__.py
  ├── tasks.py
  └── fallback.py

ai_receptionist/services/billing/  # Billing - not needed
  ├── __init__.py
  └── billing.py

ai_receptionist/services/flags/    # Feature flags - not needed
  ├── __init__.py
  └── service.py

# Service files to delete
ai_receptionist/services/rag.py     # RAG/vector store - not needed
ai_receptionist/services/router.py  # Request routing - not needed

# Admin API
ai_receptionist/app/api/admin.py    # Admin endpoints - not needed

# Config files (redundant)
ai_receptionist/.env.example
ai_receptionist/.gitignore          # Keep root-level only
ai_receptionist/pyproject.toml      # If not packaging
ai_receptionist/README.md           # Keep root-level only
```

---

### Voice Service Files (EVALUATE)

```bash
ai_receptionist/services/voice/
  ├── intents.py            # ❌ DELETE - Hardcoded intent detection
                            # Replace with Gemini natural language understanding
  
  ├── messages.py           # ❌ DELETE - Static message templates
                            # Replace with Gemini response generation
  
  ├── business_config.py    # ⚠️ EVALUATE - Business configuration
                            # Move values to .env or keep if complex
  
  ├── session.py            # ⚠️ KEEP IF - Call session management
                            # Keep if maintaining stateful conversations
  
  ├── cost_tracker.py       # ❌ DELETE - Cost tracking
                            # Delete if not tracking costs in production
  
  └── endpoints.py          # ⚠️ REVIEW - TwiML generation (247 lines)
                            # May need for audio pipeline - review carefully
```

---

### Other Projects (DELETE ENTIRELY)

```bash
../inventory_manager/         # ❌ DELETE - Separate project
../portfolio/                 # ❌ DELETE - Separate project
```

---

## 📋 EXECUTION CHECKLIST

### Phase 1: Safety Backup
- [ ] Commit all current changes to git
- [ ] Create backup branch: `git checkout -b pre-cleanup-backup`
- [ ] Tag current state: `git tag pre-cleanup-$(date +%Y%m%d)`

### Phase 2: Delete Cache (No Risk)
- [ ] Delete `.pytest_cache/`
- [ ] Delete `.ruff_cache/`
- [ ] Delete `__pycache__/` (all locations)
- [ ] Delete `ai_receptionist/.pytest_cache/`
- [ ] Delete `ai_receptionist/.ruff_cache/`

### Phase 3: Delete Infrastructure (Low Risk)
- [ ] Delete `alembic/` folder
- [ ] Delete `scripts/` folder
- [ ] Delete `tools/` folder
- [ ] Delete `tests/` folder
- [ ] Delete `.github/` folder (if not using CI/CD)
- [ ] Delete `.streamlit/` folder
- [ ] Delete `.vscode/` folder (user-specific)

### Phase 4: Delete Documentation (Low Risk)
- [ ] Delete `docs/` folder
- [ ] Delete `PRODUCTS/` folder
- [ ] Delete `data/` folder
- [ ] Delete all `.md` files except `README.md`

### Phase 5: Delete Module Components (Medium Risk)
- [ ] Delete `ai_receptionist/agent/`
- [ ] Delete `ai_receptionist/api/` (legacy)
- [ ] Delete `ai_receptionist/db/`
- [ ] Delete `ai_receptionist/static/`
- [ ] Delete `ai_receptionist/tests/`
- [ ] Delete `ai_receptionist/workers/`
- [ ] Delete `ai_receptionist/services/billing/`
- [ ] Delete `ai_receptionist/services/flags/`

### Phase 6: Delete Service Files (Medium Risk)
- [ ] Delete `ai_receptionist/services/rag.py`
- [ ] Delete `ai_receptionist/services/router.py`
- [ ] Delete `ai_receptionist/app/api/admin.py`

### Phase 7: Evaluate Voice Service (High Risk - Review First)
- [ ] Review `ai_receptionist/services/voice/endpoints.py`
- [ ] Delete `ai_receptionist/services/voice/intents.py`
- [ ] Delete `ai_receptionist/services/voice/messages.py`
- [ ] Decide on `ai_receptionist/services/voice/business_config.py`
- [ ] Decide on `ai_receptionist/services/voice/session.py`
- [ ] Delete `ai_receptionist/services/voice/cost_tracker.py`

### Phase 8: Delete Config Files (Low Risk)
- [ ] Delete `alembic.ini`
- [ ] Delete `docker-compose.dev.yml`
- [ ] Delete `pytest.ini`
- [ ] Delete monitoring scripts (`call_monitor.py`, `start_monitor.py`)
- [ ] Delete test files (`test_*.py`)

### Phase 9: Simplify Code (High Risk - Test After Each Change)
- [ ] Simplify `ai_receptionist/app/main.py`
- [ ] Simplify `ai_receptionist/config/settings.py`
- [ ] Simplify `ai_receptionist/core/di.py`
- [ ] Create `ai_receptionist/services/ai/gemini.py`

### Phase 10: Update Dependencies
- [ ] Replace `requirements.txt` with minimal version
- [ ] Test: `pip install -r requirements.txt`

### Phase 11: Validation
- [ ] Test imports: `python -c "from ai_receptionist.app.main import app"`
- [ ] Test server: `uvicorn ai_receptionist.app.main:app`
- [ ] Test webhook: `curl http://localhost:8000/twilio/webhook`
- [ ] Check file count: `find ai_receptionist -name "*.py" | wc -l` (should be ~15)
- [ ] Check dependencies: `pip list | wc -l` (should be ~20-30)

---

## ⚠️ WARNINGS & PRECAUTIONS

### DO NOT DELETE (without careful review):

1. **ai_receptionist/app/api/twilio.py** - Core webhook endpoint
2. **ai_receptionist/services/telephony/** - Twilio integration layer
3. **ai_receptionist/config/settings.py** - Configuration (simplify, don't delete)
4. **ai_receptionist/core/di.py** - Dependency injection (simplify, don't delete)
5. **.env** - Environment variables (user-specific, should not be in git)
6. **.gitignore** - Git ignore file
7. **README.md** - Main documentation

### HIGH RISK Files (Review Before Deleting):

1. **ai_receptionist/services/voice/endpoints.py** - May contain TwiML logic needed for audio
2. **ai_receptionist/services/voice/session.py** - May be needed for stateful conversations
3. **ai_receptionist/app/main.py** - Simplify, don't delete
4. **ai_receptionist/app/middleware.py** - Check if any critical middleware remains

---

## 📊 EXPECTED RESULTS

### Before Cleanup:
```
Total folders: 35+
Total files: 150+
Python files: 119
Dependencies: 50+
Codebase size: ~5 MB
Container size: ~800 MB
```

### After Cleanup:
```
Total folders: 8
Total files: ~20
Python files: ~15
Dependencies: 7-8
Codebase size: ~200 KB
Container size: ~200 MB
```

### Improvement:
```
Folders: -77%
Files: -87%
Code size: -96%
Container: -75%
```

---

## 🚀 NEXT STEPS AFTER CLEANUP

1. Create `ai_receptionist/services/ai/gemini.py` with Gemini integration
2. Update `requirements.txt` to minimal dependencies
3. Simplify `main.py`, `settings.py`, `di.py`
4. Test webhook endpoint
5. Deploy to staging
6. Monitor latency (should approach pure LLM latency)

---

**END OF CLEANUP PLAN**

This is a **PLAN ONLY** - no deletions have been performed.
Review carefully before executing any deletions.
