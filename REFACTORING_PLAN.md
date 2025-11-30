# Minimal Real-Time Voice Pipeline Refactoring Plan

## Analysis Summary

**Current State**: The `ai_receptionist` project contains a full-featured AI receptionist system with:
- Database migrations (Alembic)
- Admin tools
- Call monitoring
- Billing services
- Feature flags
- RAG/vector store integration
- Static UI components
- Multiple test suites
- Documentation and blueprints
- Sample data and scripts

**Target State**: Minimal production runtime with:
- FastAPI webhook endpoint (`/twilio/webhook`)
- Gemini Flash text→response pipeline
- Optional audio pipeline (Twilio TwiML)
- Zero latency overhead except LLM

---

## 1. Folders/Files Safe to DELETE or Move to /archive

### High Priority - DELETE or ARCHIVE Immediately

**Complete Folders:**
```
/root/antigravity_bundle/testing/ai_receptionist/.streamlit/
/root/antigravity_bundle/testing/ai_receptionist/.pytest_cache/
/root/antigravity_bundle/testing/ai_receptionist/.ruff_cache/
/root/antigravity_bundle/testing/ai_receptionist/__pycache__/
/root/antigravity_bundle/testing/ai_receptionist/alembic/
/root/antigravity_bundle/testing/ai_receptionist/data/
/root/antigravity_bundle/testing/ai_receptionist/docs/
/root/antigravity_bundle/testing/ai_receptionist/PRODUCTS/
/root/antigravity_bundle/testing/ai_receptionist/scripts/
/root/antigravity_bundle/testing/ai_receptionist/tests/
/root/antigravity_bundle/testing/ai_receptionist/tools/
```

**Within ai_receptionist/ module:**
```
/root/antigravity_bundle/testing/ai_receptionist/ai_receptionist/.pytest_cache/
/root/antigravity_bundle/testing/ai_receptionist/ai_receptionist/.ruff_cache/
/root/antigravity_bundle/testing/ai_receptionist/ai_receptionist/__pycache__/
/root/antigravity_bundle/testing/ai_receptionist/ai_receptionist/static/
/root/antigravity_bundle/testing/ai_receptionist/ai_receptionist/tests/
/root/antigravity_bundle/testing/ai_receptionist/ai_receptionist/db/
/root/antigravity_bundle/testing/ai_receptionist/ai_receptionist/workers/
/root/antigravity_bundle/testing/ai_receptionist/ai_receptionist/services/billing/
/root/antigravity_bundle/testing/ai_receptionist/ai_receptionist/services/flags/
/root/antigravity_bundle/testing/ai_receptionist/ai_receptionist/services/rag.py
/root/antigravity_bundle/testing/ai_receptionist/ai_receptionist/services/router.py
/root/antigravity_bundle/testing/ai_receptionist/ai_receptionist/app/api/admin.py
/root/antigravity_bundle/testing/ai_receptionist/ai_receptionist/api/twilio_voice.py
```

**Root-level files:**
```
/root/antigravity_bundle/testing/ai_receptionist/alembic.ini
/root/antigravity_bundle/testing/ai_receptionist/call_monitor.py
/root/antigravity_bundle/testing/ai_receptionist/start_monitor.py
/root/antigravity_bundle/testing/ai_receptionist/test_improvements.py
/root/antigravity_bundle/testing/ai_receptionist/test_voice_integration.py
/root/antigravity_bundle/testing/ai_receptionist/docker-compose.dev.yml
/root/antigravity_bundle/testing/ai_receptionist/pytest.ini
/root/antigravity_bundle/testing/ai_receptionist/COMMIT_MSG.txt
/root/antigravity_bundle/testing/ai_receptionist/EVAL_SYSTEM_README.md
/root/antigravity_bundle/testing/ai_receptionist/REFACTORING_SUMMARY.md
/root/antigravity_bundle/testing/ai_receptionist/TECHNICAL_DEBT_AUDIT.md
/root/antigravity_bundle/testing/ai_receptionist/onboarding_checklist.md
/root/antigravity_bundle/testing/ai_receptionist/pilot_agreement.md
```

### Medium Priority - Evaluate & Potentially Remove

**Agent/Conversation Logic** (if not using Gemini):
```
/root/antigravity_bundle/testing/ai_receptionist/ai_receptionist/agent/
```

**Voice Service** (hardcoded intent detection - replace with Gemini):
```
/root/antigravity_bundle/testing/ai_receptionist/ai_receptionist/services/voice/intents.py
/root/antigravity_bundle/testing/ai_receptionist/ai_receptionist/services/voice/messages.py
/root/antigravity_bundle/testing/ai_receptionist/ai_receptionist/services/voice/business_config.py
/root/antigravity_bundle/testing/ai_receptionist/ai_receptionist/services/voice/session.py
/root/antigravity_bundle/testing/ai_receptionist/ai_receptionist/services/voice/cost_tracker.py
```

**Other Projects** (not ai_receptionist):
```
/root/antigravity_bundle/testing/inventory_manager/
/root/antigravity_bundle/testing/portfolio/
```

---

## 2. Core Components to KEEP

### Essential Files

**Main Application:**
```
/root/antigravity_bundle/testing/ai_receptionist/ai_receptionist/app/main.py (simplified)
/root/antigravity_bundle/testing/ai_receptionist/ai_receptionist/app/__init__.py
/root/antigravity_bundle/testing/ai_receptionist/ai_receptionist/app/api/twilio.py
```

**Configuration:**
```
/root/antigravity_bundle/testing/ai_receptionist/ai_receptionist/config/settings.py (minimal)
/root/antigravity_bundle/testing/ai_receptionist/ai_receptionist/config/__init__.py
/root/antigravity_bundle/testing/ai_receptionist/.env (user-specific)
```

**Core Services:**
```
/root/antigravity_bundle/testing/ai_receptionist/ai_receptionist/services/telephony/telephony.py
/root/antigravity_bundle/testing/ai_receptionist/ai_receptionist/services/telephony/twilio_service.py
/root/antigravity_bundle/testing/ai_receptionist/ai_receptionist/services/telephony/__init__.py
/root/antigravity_bundle/testing/ai_receptionist/ai_receptionist/services/ai/ (NEW - Gemini integration)
```

**Models:**
```
/root/antigravity_bundle/testing/ai_receptionist/ai_receptionist/models/dtos.py (if needed)
```

**DI & Utils:**
```
/root/antigravity_bundle/testing/ai_receptionist/ai_receptionist/core/di.py
/root/antigravity_bundle/testing/ai_receptionist/ai_receptionist/utils/helpers.py (minimal)
```

**Entry Points:**
```
/root/antigravity_bundle/testing/ai_receptionist/ai_receptionist/__init__.py
/root/antigravity_bundle/testing/ai_receptionist/requirements.txt (minimal)
```

---

## 3. Recommended Final Folder Structure

```
ai_receptionist/
├── .env                          # Environment variables
├── .gitignore                    # Git ignore
├── requirements.txt              # Minimal dependencies
├── README.md                     # Simplified documentation
├── ai_receptionist/
│   ├── __init__.py
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py               # FastAPI app with /twilio/webhook
│   │   └── api/
│   │       ├── __init__.py
│   │       └── twilio.py         # Twilio webhook endpoint
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py           # Minimal Pydantic settings
│   ├── core/
│   │   ├── __init__.py
│   │   └── di.py                 # Dependency injection
│   ├── models/
│   │   ├── __init__.py
│   │   └── dtos.py               # Request/response models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ai/
│   │   │   ├── __init__.py
│   │   │   └── gemini.py         # NEW: Gemini Flash integration
│   │   └── telephony/
│   │       ├── __init__.py
│   │       ├── telephony.py      # Abstract telephony service
│   │       └── twilio_service.py # Twilio implementation
│   └── utils/
│       ├── __init__.py
│       └── helpers.py            # Minimal utilities
└── archive/                       # Moved files for reference
    ├── alembic/
    ├── docs/
    ├── tests/
    ├── scripts/
    └── ...
```

---

## 4. Diff Preview - File Removals

### Summary of Deletions

| Category | Count | Total Size (est.) |
|----------|-------|-------------------|
| Documentation | 8 files | ~200 KB |
| Tests | ~20 files | ~500 KB |
| Database/Migrations | 1 folder + config | ~100 KB |
| Admin Tools | 2 files | ~50 KB |
| Static UI | 1 folder | ~200 KB |
| Cache folders | 3 folders | ~50 MB |
| Sample data | 1 folder | ~10 KB |
| Monitoring | 3 files | ~30 KB |
| Billing/Flags | 2 folders | ~80 KB |
| Other projects | 2 folders | ~5 MB |

**Total**: ~60+ folders/files removed or archived

### Critical Files Being Removed

1. **UI Components**: `ai_receptionist/static/` - entire folder (index.html, CSS, JS)
2. **Database**: `alembic/` + `ai_receptionist/db/` - all ORM and migration logic
3. **Admin API**: `ai_receptionist/app/api/admin.py` - admin endpoints
4. **Legacy Voice**: `ai_receptionist/api/twilio_voice.py` - duplicate/legacy endpoint
5. **Call Monitor**: `call_monitor.py`, `start_monitor.py` - monitoring tools
6. **Hardcoded Intents**: `services/voice/intents.py` - replaced by Gemini
7. **RAG System**: `services/rag.py` - Pinecone vector store (optional removal)
8. **Billing**: `services/billing/billing.py` - usage tracking
9. **Workers**: `workers/tasks.py`, `workers/fallback.py` - background jobs
10. **All Tests**: `tests/`, `ai_receptionist/tests/` - entire test suite

### Files Being Modified

1. **main.py**: Remove admin router, static files mounting, UI endpoint
2. **settings.py**: Remove database, Redis, OpenAI configs; add Gemini config
3. **requirements.txt**: Strip down to 6-8 core dependencies
4. **di.py**: Remove database/Redis/billing dependencies

---

## 5. Updated requirements.txt

### Current (50+ packages)
```
fastapi==0.118.2
uvicorn==0.37.0
twilio==9.8.3
pydantic==2.12.0
pydantic-settings==2.4.0
alembic==1.13.2
SQLAlchemy==2.0.36
redis==5.0.6
streamlit==1.50.0
openai==2.2.0
httpx==0.28.1
pytest==8.4.2
... (40+ more packages)
```

### Minimal Production (6-7 packages)

```txt
# Core Web Framework
fastapi==0.118.2
uvicorn[standard]==0.37.0

# HTTP Client
httpx==0.28.1

# Twilio Integration
twilio==9.8.3

# Google Gemini AI
google-generativeai==0.8.3

# Configuration
pydantic==2.12.0
pydantic-settings==2.4.0
python-dotenv==1.1.1
```

**Alternative** (if using Vertex AI instead):
```txt
fastapi==0.118.2
uvicorn[standard]==0.37.0
httpx==0.28.1
twilio==9.8.3
google-cloud-aiplatform==1.70.0
pydantic==2.12.0
pydantic-settings==2.4.0
python-dotenv==1.1.1
```

---

## 6. Implementation Strategy

### Phase 1: Archive Non-Essential Code
```bash
# Create archive directory
mkdir -p archive

# Move folders
mv alembic archive/
mv data archive/
mv docs archive/
mv PRODUCTS archive/
mv scripts archive/
mv tests archive/
mv tools archive/
mv ai_receptionist/static archive/
mv ai_receptionist/tests archive/
mv ai_receptionist/db archive/
mv ai_receptionist/workers archive/

# Move files
mv alembic.ini archive/
mv call_monitor.py archive/
mv start_monitor.py archive/
mv test_*.py archive/
mv *.md archive/ (except README.md)
```

### Phase 2: Implement Gemini Integration

**Create**: `ai_receptionist/services/ai/gemini.py`
```python
"""Gemini Flash text→response pipeline."""

import google.generativeai as genai
from ai_receptionist.config.settings import get_settings

class GeminiService:
    def __init__(self):
        settings = get_settings()
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    async def generate_response(self, user_text: str, context: dict = None) -> str:
        """Generate response from user input."""
        prompt = self._build_prompt(user_text, context)
        response = await self.model.generate_content_async(prompt)
        return response.text
    
    def _build_prompt(self, user_text: str, context: dict = None) -> str:
        """Build minimal prompt for voice assistant."""
        system = "You are a helpful AI receptionist. Keep responses concise."
        return f"{system}\n\nUser: {user_text}\n\nAssistant:"
```

### Phase 3: Simplify main.py

**Remove**:
- Static files mounting
- Admin router
- Legacy voice router
- Complex middleware
- UI endpoints

**Keep**:
- `/health` endpoint
- `/twilio/webhook` endpoint
- Minimal logging

### Phase 4: Update Dependencies
```bash
pip freeze > old_requirements.txt
pip uninstall -y -r old_requirements.txt
pip install fastapi uvicorn[standard] httpx twilio google-generativeai pydantic pydantic-settings python-dotenv
pip freeze > requirements.txt
```

### Phase 5: Clean Cache Folders
```bash
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type d -name ".pytest_cache" -exec rm -rf {} +
find . -type d -name ".ruff_cache" -exec rm -rf {} +
```

---

## 7. Configuration Changes

### Minimal .env
```env
# App
APP_ENV=production
DEBUG=false

# Twilio
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890

# Gemini
GEMINI_API_KEY=your_gemini_api_key
```

### settings.py (simplified)
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_env: str = "production"
    debug: bool = False
    
    # Twilio
    twilio_account_sid: str
    twilio_auth_token: str
    twilio_phone_number: str
    
    # Gemini
    gemini_api_key: str
    
    class Config:
        env_file = ".env"
```

---

## 8. Performance Gains

### Before Refactoring
- **Dependencies**: 50+ packages (~500 MB)
- **Import Time**: ~2-3 seconds
- **Cold Start**: ~5 seconds
- **Memory**: ~200-300 MB
- **Webhook Latency**: 50-100ms (overhead) + LLM latency

### After Refactoring
- **Dependencies**: 7-8 packages (~100 MB)
- **Import Time**: ~0.5 seconds
- **Cold Start**: ~1 second
- **Memory**: ~50-100 MB
- **Webhook Latency**: ~10-20ms (overhead) + LLM latency

**Net Result**: ~80% reduction in overhead, approaching pure LLM latency

---

## 9. Testing Strategy (Minimal)

### Keep ONE test file for webhook
```
tests/
└── test_webhook.py  # Only test /twilio/webhook endpoint
```

### Remove
- All other tests
- Test fixtures
- Integration tests
- Evaluation scripts

---

## 10. Execution Commands

### Archive Everything
```bash
cd /root/antigravity_bundle/testing/ai_receptionist

# Create archive
mkdir -p archive/{root,module}

# Archive root-level items
mv alembic archive/root/
mv data archive/root/
mv docs archive/root/
mv PRODUCTS archive/root/
mv scripts archive/root/
mv tests archive/root/
mv tools archive/root/
mv .streamlit archive/root/
mv .pytest_cache archive/root/
mv .ruff_cache archive/root/
mv alembic.ini archive/root/
mv call_monitor.py archive/root/
mv start_monitor.py archive/root/
mv test_*.py archive/root/
mv COMMIT_MSG.txt archive/root/
mv EVAL_SYSTEM_README.md archive/root/
mv REFACTORING_SUMMARY.md archive/root/
mv TECHNICAL_DEBT_AUDIT.md archive/root/
mv onboarding_checklist.md archive/root/
mv pilot_agreement.md archive/root/
mv docker-compose.dev.yml archive/root/
mv pytest.ini archive/root/

# Archive module-level items
mv ai_receptionist/static archive/module/
mv ai_receptionist/tests archive/module/
mv ai_receptionist/db archive/module/
mv ai_receptionist/workers archive/module/
mv ai_receptionist/services/billing archive/module/
mv ai_receptionist/services/flags archive/module/
mv ai_receptionist/services/rag.py archive/module/
mv ai_receptionist/services/router.py archive/module/
mv ai_receptionist/app/api/admin.py archive/module/
mv ai_receptionist/api archive/module/

# Clean cache
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null
find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null
```

### Update Requirements
```bash
# Backup
cp requirements.txt archive/root/requirements.txt.original

# Create new minimal requirements
cat > requirements.txt << 'EOF'
# Core Web Framework
fastapi==0.118.2
uvicorn[standard]==0.37.0

# HTTP Client
httpx==0.28.1

# Twilio Integration
twilio==9.8.3

# Google Gemini AI
google-generativeai==0.8.3

# Configuration
pydantic==2.12.0
pydantic-settings==2.4.0
python-dotenv==1.1.1
EOF
```

---

## 11. Risk Assessment

### Low Risk
- Removing cache folders
- Removing documentation
- Removing tests (if not needed in production)
- Removing admin tools

### Medium Risk
- Removing database layer (ensure no production dependencies)
- Removing billing service (ensure not tracking usage)
- Removing RAG/vector store (ensure not using knowledge base)

### High Risk
- Modifying core webhook logic
- Changing Twilio integration
- Removing agent/conversation logic (if currently in use)

### Mitigation
1. Keep `archive/` folder with all removed code
2. Test webhook endpoint after changes
3. Maintain git history for rollback
4. Deploy to staging first

---

## 12. Next Steps

1. **Review this plan** - Ensure alignment with requirements
2. **Backup current state** - Create git branch or tag
3. **Execute archival** - Move non-essential code
4. **Implement Gemini** - Create ai/gemini.py service
5. **Simplify main.py** - Remove UI/admin/extras
6. **Update requirements** - Install minimal deps
7. **Test webhook** - Verify /twilio/webhook works
8. **Deploy** - Push to staging environment
9. **Monitor latency** - Verify LLM-only overhead
10. **Document** - Update README.md

---

## Appendix: File Count Summary

**Folders to Archive**: 15+
**Files to Archive**: 40+
**Files to Modify**: 4-5
**Files to Create**: 1-2
**Final Codebase**: ~15 essential files
**Dependencies**: 7-8 packages (from 50+)

**Estimated Refactoring Time**: 2-3 hours
**Estimated Testing Time**: 1 hour
**Total Time**: 3-4 hours
