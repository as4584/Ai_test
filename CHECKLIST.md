# REFACTORING CHECKLIST
## Minimal Real-Time Voice Pipeline

**Date:** November 30, 2025  
**Project:** AI Receptionist  
**Goal:** Reduce to minimal FastAPI + Twilio + Gemini pipeline

---

## 📋 Pre-Refactoring

- [ ] Read `EXECUTIVE_SUMMARY.md`
- [ ] Read `REFACTORING_PLAN.md`
- [ ] Read `DIFF_PREVIEW.md`
- [ ] Understand what will be removed (60+ items)
- [ ] Backup current state:
  ```bash
  git add -A
  git commit -m "Pre-refactoring snapshot"
  git tag pre-refactoring-$(date +%Y%m%d)
  ```
- [ ] Verify `.env` file exists with Twilio credentials
- [ ] Have Gemini API key ready

---

## 🗑️ Phase 1: Archival (Automated)

- [ ] Make refactor.sh executable: `chmod +x refactor.sh`
- [ ] Run: `./refactor.sh`
- [ ] Verify archive/ folder created:
  - [ ] `archive/root/` - root-level items
  - [ ] `archive/module/` - module-level items
  - [ ] `archive/config/` - config files
  - [ ] `archive/docs/` - documentation
  - [ ] `archive/ARCHIVE_SUMMARY.txt` - summary file

### Items Archived by Script:

**Folders:**
- [ ] `.streamlit/`
- [ ] `.pytest_cache/`, `.ruff_cache/`, `__pycache__/`
- [ ] `alembic/`
- [ ] `data/`
- [ ] `docs/`
- [ ] `PRODUCTS/`
- [ ] `scripts/`
- [ ] `tests/`
- [ ] `tools/`
- [ ] `ai_receptionist/static/`
- [ ] `ai_receptionist/tests/`
- [ ] `ai_receptionist/db/`
- [ ] `ai_receptionist/workers/`
- [ ] `ai_receptionist/services/billing/`
- [ ] `ai_receptionist/services/flags/`
- [ ] `ai_receptionist/agent/`
- [ ] `ai_receptionist/api/` (legacy)

**Files:**
- [ ] `alembic.ini`
- [ ] `docker-compose.dev.yml`
- [ ] `pytest.ini`
- [ ] `call_monitor.py`, `start_monitor.py`
- [ ] `test_*.py` files
- [ ] Documentation `.md` files (except README)
- [ ] `services/rag.py`, `services/router.py`
- [ ] `app/api/admin.py`

**Dependencies:**
- [ ] `requirements.txt` backed up to `archive/root/requirements.txt.original`
- [ ] New minimal `requirements.txt` created (7-8 packages)

---

## 🆕 Phase 2: New Gemini Integration

- [ ] Create directory: `mkdir -p ai_receptionist/services/ai`
- [ ] Create `ai_receptionist/services/ai/__init__.py`:
  ```python
  """AI services for LLM integration."""
  from .gemini import GeminiService, get_gemini_service
  __all__ = ["GeminiService", "get_gemini_service"]
  ```
- [ ] Create `ai_receptionist/services/ai/gemini.py`:
  ```python
  """Gemini Flash integration for text→response pipeline."""
  import logging
  from typing import Optional, Dict, Any
  import google.generativeai as genai
  from ai_receptionist.config.settings import get_settings
  
  logger = logging.getLogger(__name__)
  
  class GeminiService:
      """Service for generating responses using Gemini Flash."""
      
      def __init__(self):
          """Initialize Gemini client with API key from settings."""
          settings = get_settings()
          genai.configure(api_key=settings.gemini_api_key)
          self.model = genai.GenerativeModel(settings.gemini_model)
          logger.info(f"Initialized Gemini: {settings.gemini_model}")
      
      async def generate_response(
          self,
          user_text: str,
          context: Optional[Dict[str, Any]] = None
      ) -> str:
          """Generate AI response from user input."""
          prompt = self._build_prompt(user_text, context)
          try:
              response = await self.model.generate_content_async(prompt)
              return response.text.strip()
          except Exception as e:
              logger.error(f"Gemini generation failed: {e}")
              return "I apologize, I'm having trouble right now."
      
      def _build_prompt(
          self,
          user_text: str,
          context: Optional[Dict[str, Any]] = None
      ) -> str:
          """Build prompt for Gemini."""
          system = (
              "You are a helpful AI receptionist for a business. "
              "Respond concisely and professionally to phone calls. "
              "Keep responses under 3 sentences when possible."
          )
          if context:
              business_info = context.get("business_info", "")
              if business_info:
                  system += f"\n\nBusiness Info:\n{business_info}"
          return f"{system}\n\nCaller: {user_text}\n\nReceptionist:"
  
  _gemini_service: Optional[GeminiService] = None
  
  def get_gemini_service() -> GeminiService:
      """Get or create Gemini service instance."""
      global _gemini_service
      if _gemini_service is None:
          _gemini_service = GeminiService()
      return _gemini_service
  ```

---

## ✏️ Phase 3: Simplify main.py

- [ ] Open `ai_receptionist/app/main.py`
- [ ] **REMOVE** these imports:
  ```python
  from fastapi.responses import JSONResponse, FileResponse  # Remove FileResponse
  from fastapi.staticfiles import StaticFiles  # Remove entire line
  from pathlib import Path  # Remove entire line
  from ai_receptionist.app.api.admin import router as admin_router  # Remove
  from ai_receptionist.api.twilio_voice import router as twilio_voice_router  # Remove
  from ai_receptionist.services.voice.endpoints import router as voice_router  # Remove
  from ai_receptionist.app.middleware import configure_logging, request_context_middleware  # Simplify
  ```
- [ ] **REMOVE** static files mounting:
  ```python
  # Remove these lines:
  BASE_DIR = Path(__file__).resolve().parent.parent
  STATIC_DIR = BASE_DIR / "static"
  if STATIC_DIR.exists():
      app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
  ```
- [ ] **REMOVE** UI root endpoint:
  ```python
  # Remove this entire endpoint:
  @app.get("/")
  def root():
      html_path = STATIC_DIR / "index.html"
      if html_path.exists():
          return FileResponse(str(html_path))
      return JSONResponse({"name": "ai-receptionist", "version": "0.1.0"})
  ```
- [ ] **REMOVE** extra routers:
  ```python
  # Remove these lines:
  app.include_router(admin_router)
  app.include_router(twilio_voice_router)
  app.include_router(voice_router)
  ```
- [ ] **SIMPLIFY** middleware:
  ```python
  # Remove these lines:
  configure_logging()
  app.middleware("http")(request_context_middleware)
  
  # Replace with basic logging:
  logging.basicConfig(
      level=logging.INFO,
      format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
  )
  ```
- [ ] **VERIFY** final main.py looks like this:
  ```python
  """Minimal FastAPI application for Twilio webhook and Gemini integration."""
  from fastapi import FastAPI, Depends
  import logging
  from ai_receptionist.config.settings import Settings, get_settings
  from ai_receptionist.app.api.twilio import router as twilio_router
  
  logger = logging.getLogger(__name__)
  
  app = FastAPI(
      title="AI Receptionist Voice Pipeline",
      version="0.2.0",
      description="Minimal real-time voice pipeline with Twilio and Gemini Flash"
  )
  
  @app.get("/health")
  def health(settings: Settings = Depends(get_settings)):
      """Health check endpoint."""
      return {
          "status": "ok",
          "env": settings.app_env,
          "service": "voice-pipeline"
      }
  
  app.include_router(twilio_router)
  
  logging.basicConfig(
      level=logging.INFO,
      format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
  )
  ```

---

## ✏️ Phase 4: Simplify settings.py

- [ ] Open `ai_receptionist/config/settings.py`
- [ ] **REMOVE** these fields from Settings class:
  ```python
  # Database Configuration
  database_url: Optional[str] = None
  postgres_host: str = "localhost"
  postgres_port: int = 5432
  postgres_db: str = "ai_receptionist"
  postgres_user: Optional[str] = None
  postgres_password: Optional[str] = None
  
  # Redis Configuration
  redis_url: Optional[str] = None
  redis_host: str = "localhost"
  redis_port: int = 6379
  redis_db: int = 0
  
  # OpenAI Configuration
  openai_api_key: Optional[str] = None
  ```
- [ ] **ADD** these fields for Gemini:
  ```python
  # Gemini Configuration
  gemini_api_key: str
  gemini_model: str = "gemini-2.0-flash-exp"
  ```
- [ ] **VERIFY** final Settings class looks like this:
  ```python
  class Settings(BaseSettings):
      """Application settings loaded from environment variables."""
      
      # Application
      app_env: str = "production"
      debug: bool = False
      
      # Twilio
      twilio_account_sid: str
      twilio_auth_token: str
      twilio_phone_number: str
      
      # Gemini
      gemini_api_key: str
      gemini_model: str = "gemini-2.0-flash-exp"
      
      class Config:
          env_file = ".env"
          env_file_encoding = "utf-8"
  ```

---

## ✏️ Phase 5: Simplify di.py

- [ ] Open `ai_receptionist/core/di.py`
- [ ] **REMOVE** imports for:
  ```python
  # Remove any database-related imports
  # Remove any Redis-related imports
  # Remove any billing service imports
  # Remove any feature flag imports
  ```
- [ ] **REMOVE** dependency injection functions for:
  ```python
  # Remove get_db_session() or similar
  # Remove get_redis_client() or similar
  # Remove get_billing_service() or similar
  # Remove get_feature_flags() or similar
  ```
- [ ] **KEEP** only:
  ```python
  # Keep get_telephony_service()
  # Keep get_tenant_mapping()
  ```
- [ ] **ADD** (if integrating Gemini into webhook):
  ```python
  from ai_receptionist.services.ai.gemini import get_gemini_service
  
  def get_ai_service():
      return get_gemini_service()
  ```

---

## 🔧 Phase 6: Update .env

- [ ] Open `.env` file
- [ ] **REMOVE** (if present):
  ```
  DATABASE_URL=...
  POSTGRES_HOST=...
  POSTGRES_PORT=...
  POSTGRES_DB=...
  POSTGRES_USER=...
  POSTGRES_PASSWORD=...
  REDIS_URL=...
  REDIS_HOST=...
  REDIS_PORT=...
  REDIS_DB=...
  OPENAI_API_KEY=...
  ```
- [ ] **ADD** Gemini configuration:
  ```
  GEMINI_API_KEY=your_gemini_api_key_here
  GEMINI_MODEL=gemini-2.0-flash-exp
  ```
- [ ] **VERIFY** .env contains only:
  ```
  # App
  APP_ENV=production
  DEBUG=false
  
  # Twilio
  TWILIO_ACCOUNT_SID=your_account_sid
  TWILIO_AUTH_TOKEN=your_auth_token
  TWILIO_PHONE_NUMBER=+1234567890
  
  # Gemini
  GEMINI_API_KEY=your_gemini_api_key
  GEMINI_MODEL=gemini-2.0-flash-exp
  ```

---

## 📦 Phase 7: Install Dependencies

- [ ] **Option A: Fresh Virtual Environment (Recommended)**
  ```bash
  deactivate
  rm -rf .venv
  python3 -m venv .venv
  source .venv/bin/activate
  pip install --upgrade pip
  pip install -r requirements.txt
  ```

- [ ] **Option B: Upgrade Existing Environment**
  ```bash
  pip uninstall -y -r archive/root/requirements.txt.original
  pip install -r requirements.txt
  ```

- [ ] Verify installed packages:
  ```bash
  pip list
  ```
  Should show only ~20-30 packages (7-8 direct + transitive dependencies)

---

## 🧪 Phase 8: Testing

### 8.1 Test Health Endpoint
- [ ] Start server:
  ```bash
  uvicorn ai_receptionist.app.main:app --reload --port 8000
  ```
- [ ] Test health:
  ```bash
  curl http://localhost:8000/health
  ```
  Expected response:
  ```json
  {
    "status": "ok",
    "env": "production",
    "service": "voice-pipeline"
  }
  ```

### 8.2 Test Webhook Endpoint
- [ ] Test webhook with mock data:
  ```bash
  curl -X POST http://localhost:8000/twilio/webhook \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "From=+1234567890" \
    -d "To=+0987654321" \
    -d "CallSid=test-call-sid-123"
  ```
- [ ] Check server logs for:
  - [ ] No import errors
  - [ ] No database connection errors
  - [ ] No Redis connection errors
  - [ ] Webhook processed successfully

### 8.3 Test Gemini Integration (if integrated into webhook)
- [ ] Modify webhook to call Gemini (if needed)
- [ ] Test with real Twilio webhook (use ngrok for local testing):
  ```bash
  # In another terminal:
  ngrok http 8000
  
  # Update Twilio webhook URL to: https://<ngrok-id>.ngrok.io/twilio/webhook
  ```
- [ ] Make test call to your Twilio number
- [ ] Verify Gemini response in logs

### 8.4 Verify No Errors
- [ ] Check for import errors:
  ```bash
  python -c "from ai_receptionist.app.main import app; print('OK')"
  ```
- [ ] Check for missing dependencies:
  ```bash
  pip check
  ```

---

## 📊 Phase 9: Validation

### Performance Metrics
- [ ] Measure cold start time:
  ```bash
  time python -c "from ai_receptionist.app.main import app"
  ```
  Should be < 2 seconds

- [ ] Measure memory usage:
  ```bash
  # Start server, then in another terminal:
  ps aux | grep uvicorn
  ```
  Should be < 150 MB

- [ ] Measure webhook latency (excluding LLM):
  ```bash
  curl -X POST http://localhost:8000/twilio/webhook \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "From=+1234567890" \
    -d "To=+0987654321" \
    -d "CallSid=test-call-sid-123" \
    -w "\nTime: %{time_total}s\n"
  ```
  Should be < 0.1 seconds (100ms)

### Code Metrics
- [ ] Count Python files:
  ```bash
  find ai_receptionist -name "*.py" | wc -l
  ```
  Should be ~15 files

- [ ] Count dependencies:
  ```bash
  pip list --format=freeze | wc -l
  ```
  Should be ~20-30 packages total

- [ ] Check codebase size:
  ```bash
  du -sh ai_receptionist/
  ```
  Should be < 500 KB

---

## 🚀 Phase 10: Deployment

- [ ] Update `README.md` with new minimal setup
- [ ] Create/update `Dockerfile` (if using Docker):
  ```dockerfile
  FROM python:3.11-slim
  WORKDIR /app
  COPY requirements.txt .
  RUN pip install --no-cache-dir -r requirements.txt
  COPY ai_receptionist/ ai_receptionist/
  COPY .env .
  CMD ["uvicorn", "ai_receptionist.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
  ```
- [ ] Test Docker build:
  ```bash
  docker build -t ai-receptionist:minimal .
  docker images | grep ai-receptionist
  ```
  Should be < 300 MB

- [ ] Deploy to staging environment
- [ ] Run smoke tests on staging
- [ ] Monitor latency metrics
- [ ] Deploy to production (if staging successful)

---

## 🧹 Phase 11: Cleanup

- [ ] Remove `requirements.minimal.txt` (already merged into requirements.txt)
- [ ] Review `archive/` folder - decide if keeping or moving to backup storage
- [ ] Update `.gitignore` to exclude `archive/` if desired
- [ ] Commit final state:
  ```bash
  git add -A
  git commit -m "Refactored to minimal voice pipeline - removed 87% of codebase"
  git tag post-refactoring-$(date +%Y%m%d)
  ```

---

## ✅ Success Criteria

Refactoring is successful when ALL of these are true:

- [x] Archival completed (60+ items in archive/)
- [ ] Gemini integration created and working
- [ ] main.py simplified (no UI/admin)
- [ ] settings.py simplified (no DB/Redis)
- [ ] di.py simplified (no unused deps)
- [ ] Dependencies reduced to 7-8 direct packages
- [ ] `/health` endpoint returns 200 OK
- [ ] `/twilio/webhook` endpoint returns 200 OK
- [ ] No import errors
- [ ] No dependency errors
- [ ] Webhook latency < 50ms (excluding LLM)
- [ ] Cold start < 2 seconds
- [ ] Memory usage < 150 MB
- [ ] Container size < 300 MB
- [ ] Python files count ~15
- [ ] Codebase size < 500 KB

---

## 🆘 Troubleshooting

### Issue: Import errors after archival
**Solution:** Check if you archived a file that's still imported somewhere
```bash
grep -r "from ai_receptionist.services.billing" ai_receptionist/
grep -r "from ai_receptionist.services.flags" ai_receptionist/
grep -r "from ai_receptionist.db" ai_receptionist/
```

### Issue: Missing environment variables
**Solution:** Verify .env has all required fields
```bash
python -c "from ai_receptionist.config.settings import get_settings; s = get_settings(); print('OK')"
```

### Issue: Gemini API errors
**Solution:** Verify API key is correct
```bash
python -c "import google.generativeai as genai; genai.configure(api_key='your_key'); print('OK')"
```

### Issue: Webhook returns 500 error
**Solution:** Check logs for specific error
```bash
uvicorn ai_receptionist.app.main:app --log-level debug
```

### Issue: Want to restore archived code
**Solution:** Move back from archive
```bash
# Example: restore billing service
mv archive/module/billing ai_receptionist/services/
```

---

## 📝 Notes

- All archived code is in `archive/` folder - safe to restore if needed
- Original requirements.txt saved as `archive/root/requirements.txt.original`
- Git history preserved - can revert if needed
- This checklist assumes you're using the automated `refactor.sh` script
- Manual modifications (Phases 2-5) must be done after running the script

---

## 📞 Support

If stuck, refer to:
1. `EXECUTIVE_SUMMARY.md` - High-level overview
2. `REFACTORING_PLAN.md` - Detailed step-by-step guide
3. `DIFF_PREVIEW.md` - Before/after code examples
4. `archive/ARCHIVE_SUMMARY.txt` - What was archived

---

**END OF CHECKLIST**

Print this and check off items as you complete them!
