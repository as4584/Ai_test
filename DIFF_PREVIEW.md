# File Removal Diff Preview
# Refactoring: Minimal Real-Time Voice Pipeline
# Date: November 30, 2025

## Summary Statistics

BEFORE Refactoring:
- Total folders: ~30
- Total Python files: ~119
- Total dependencies: 50+
- Estimated codebase size: ~5 MB
- Cache/temp size: ~50 MB

AFTER Refactoring:
- Total folders: ~8
- Total Python files: ~15
- Total dependencies: 7-8
- Estimated codebase size: ~200 KB
- Cache/temp size: 0

REDUCTION:
- Folders: 73% reduction
- Python files: 87% reduction
- Dependencies: 85% reduction
- Codebase size: 96% reduction

================================================================================
FOLDERS TO DELETE/ARCHIVE
================================================================================

❌ DELETE - Cache & Temporary Files
────────────────────────────────────────────────────────────────────────────────
[-] .streamlit/                          # Streamlit UI config (not used)
[-] .pytest_cache/                       # Pytest cache
[-] .ruff_cache/                         # Ruff linter cache
[-] __pycache__/                         # Python bytecode (root)
[-] ai_receptionist/.pytest_cache/       # Pytest cache (module)
[-] ai_receptionist/.ruff_cache/         # Ruff cache (module)
[-] ai_receptionist/__pycache__/         # Python bytecode (module)

📦 ARCHIVE - Infrastructure & Tooling
────────────────────────────────────────────────────────────────────────────────
[-] alembic/                             # Database migrations
    ├── env.py
    ├── script.py.mako
    └── versions/
        └── *.py                         # All migration files
[-] scripts/                             # Helper scripts
    ├── generate_changelog.py
    └── migrations_helper.py
[-] tools/                               # Admin tools
    └── adminctl.py
[-] tests/                               # Root-level tests
    ├── test_migrations.py
    ├── test_generate_changelog.py
    ├── test_eval_blueprint.py
    ├── test_voice_webhook.py
    ├── tests_test_adminctl.py
    ├── test_calendar_stub.py
    └── conftest.py

📚 ARCHIVE - Documentation & Specs
────────────────────────────────────────────────────────────────────────────────
[-] docs/                                # Documentation folder
    ├── EVAL_SYSTEM_README.md
    └── samples/
[-] PRODUCTS/                            # Product specifications
    └── VERSIONS.md

💾 ARCHIVE - Data & Samples
────────────────────────────────────────────────────────────────────────────────
[-] data/                                # Sample data
    └── appointments.json

🎨 ARCHIVE - UI Components
────────────────────────────────────────────────────────────────────────────────
[-] ai_receptionist/static/              # Static web assets
    ├── index.html                       # ChatGPT-style UI
    ├── style.css
    └── app.js

🧪 ARCHIVE - Testing Infrastructure
────────────────────────────────────────────────────────────────────────────────
[-] ai_receptionist/tests/               # Module-level tests
    ├── test_health.py
    ├── test_feature_flag_service.py
    ├── test_twilio_webhook.py
    ├── test_billing.py
    ├── test_rag.py
    ├── test_router.py
    ├── test_voice_endpoints.py
    ├── test_fallback.py
    └── conftest.py

🗄️ ARCHIVE - Database Layer
────────────────────────────────────────────────────────────────────────────────
[-] ai_receptionist/db/                  # Database repositories
    ├── __init__.py
    └── repositories.py

⚙️ ARCHIVE - Background Workers
────────────────────────────────────────────────────────────────────────────────
[-] ai_receptionist/workers/             # Background job workers
    ├── __init__.py
    ├── tasks.py
    └── fallback.py

💰 ARCHIVE - Business Logic Services
────────────────────────────────────────────────────────────────────────────────
[-] ai_receptionist/services/billing/    # Billing/usage tracking
    ├── __init__.py
    └── billing.py
[-] ai_receptionist/services/flags/      # Feature flags
    ├── __init__.py
    └── service.py

🔍 ARCHIVE - RAG/Vector Store
────────────────────────────────────────────────────────────────────────────────
[-] ai_receptionist/services/rag.py      # RAG with Pinecone (120 lines)
[-] ai_receptionist/services/router.py   # Request routing logic

🤖 ARCHIVE - Legacy Agent/Voice Logic
────────────────────────────────────────────────────────────────────────────────
[-] ai_receptionist/agent/               # Conversation bot (replaced by Gemini)
    ├── __init__.py
    └── conversation_bot.py              # 396 lines - hardcoded logic

🎙️ EVALUATE - Voice Service (may keep simplified version)
────────────────────────────────────────────────────────────────────────────────
[?] ai_receptionist/services/voice/      # Voice conversation handlers
    ├── endpoints.py                     # 247 lines - Twilio TwiML generation
    ├── intents.py                       # 150 lines - hardcoded intent detection (REPLACE with Gemini)
    ├── messages.py                      # Static message templates
    ├── business_config.py               # Business-specific config
    ├── session.py                       # Call session management
    └── cost_tracker.py                  # Cost tracking

🌐 ARCHIVE - Admin API & Legacy Endpoints
────────────────────────────────────────────────────────────────────────────────
[-] ai_receptionist/app/api/admin.py     # Admin dashboard endpoints
[-] ai_receptionist/api/                 # Legacy API folder
    └── twilio_voice.py                  # Duplicate/legacy Twilio endpoint

================================================================================
FILES TO DELETE/ARCHIVE (Root Level)
================================================================================

⚙️ Configuration Files
────────────────────────────────────────────────────────────────────────────────
[-] alembic.ini                          # Alembic configuration
[-] docker-compose.dev.yml               # Development docker compose
[-] pytest.ini                           # Pytest configuration

📝 Documentation Files
────────────────────────────────────────────────────────────────────────────────
[-] COMMIT_MSG.txt                       # Commit message template
[-] EVAL_SYSTEM_README.md                # Evaluation system docs
[-] REFACTORING_SUMMARY.md               # Previous refactoring notes
[-] TECHNICAL_DEBT_AUDIT.md              # Technical debt documentation
[-] onboarding_checklist.md              # Onboarding guide
[-] pilot_agreement.md                   # Pilot program agreement

🧪 Test Files
────────────────────────────────────────────────────────────────────────────────
[-] test_improvements.py                 # Test improvement script
[-] test_voice_integration.py            # Voice integration tests

🔧 Monitoring & Debug Tools
────────────────────────────────────────────────────────────────────────────────
[-] call_monitor.py                      # Call monitoring tool
[-] start_monitor.py                     # Monitor startup script

================================================================================
FILES TO KEEP & SIMPLIFY
================================================================================

✅ Core Application Files
────────────────────────────────────────────────────────────────────────────────
[K] ai_receptionist/app/main.py          # FastAPI app (SIMPLIFY - remove UI/admin)
[K] ai_receptionist/app/__init__.py
[K] ai_receptionist/app/api/__init__.py
[K] ai_receptionist/app/api/twilio.py    # /twilio/webhook endpoint (KEEP)
[K] ai_receptionist/app/middleware.py    # Minimal logging (SIMPLIFY)

✅ Configuration
────────────────────────────────────────────────────────────────────────────────
[K] ai_receptionist/config/settings.py   # Settings (SIMPLIFY - remove DB/Redis/OpenAI)
[K] ai_receptionist/config/__init__.py
[K] .env                                 # Environment variables (user-specific)
[K] .gitignore

✅ Core Services
────────────────────────────────────────────────────────────────────────────────
[K] ai_receptionist/services/__init__.py
[K] ai_receptionist/services/telephony/__init__.py
[K] ai_receptionist/services/telephony/telephony.py      # Abstract service
[K] ai_receptionist/services/telephony/twilio_service.py # Twilio implementation
[N] ai_receptionist/services/ai/__init__.py              # NEW - AI services
[N] ai_receptionist/services/ai/gemini.py                # NEW - Gemini integration

✅ Data Models
────────────────────────────────────────────────────────────────────────────────
[K] ai_receptionist/models/__init__.py
[K] ai_receptionist/models/dtos.py       # Request/response models (if needed)

✅ Core Utilities
────────────────────────────────────────────────────────────────────────────────
[K] ai_receptionist/core/__init__.py
[K] ai_receptionist/core/di.py           # Dependency injection (SIMPLIFY)
[K] ai_receptionist/utils/__init__.py
[K] ai_receptionist/utils/helpers.py     # Minimal helpers (SIMPLIFY)

✅ Entry Points
────────────────────────────────────────────────────────────────────────────────
[K] ai_receptionist/__init__.py
[K] ai_receptionist/pyproject.toml       # Package metadata (SIMPLIFY)
[K] requirements.txt                     # REPLACE with requirements.minimal.txt
[K] README.md                            # SIMPLIFY documentation

================================================================================
DEPENDENCY CHANGES (requirements.txt)
================================================================================

❌ REMOVED Dependencies (43 packages):
────────────────────────────────────────────────────────────────────────────────
[-] alembic==1.13.2                      # Database migrations
[-] SQLAlchemy==2.0.36                   # ORM
[-] redis==5.0.6                         # Redis client
[-] streamlit==1.50.0                    # UI framework
[-] altair==5.5.0                        # Streamlit dependency
[-] pillow==11.3.0                       # Streamlit dependency
[-] numpy==2.2.6                         # Streamlit dependency
[-] pandas==2.3.3                        # Streamlit dependency
[-] pyarrow==21.0.0                      # Streamlit dependency
[-] pydeck==0.9.1                        # Streamlit dependency
[-] tornado==6.5.2                       # Streamlit dependency
[-] watchdog==6.0.0                      # Streamlit dependency
[-] openai==2.2.0                        # OpenAI SDK (replaced by Gemini)
[-] pytest==8.4.2                        # Testing framework
[-] pytest-json-report==1.5.0            # Test reporting
[-] pytest-metadata==3.1.1               # Test metadata
[-] GitPython==3.1.45                    # Git integration
[-] gitdb==4.0.12                        # Git database
[-] smmap==5.0.2                         # Git dependency
[-] Mako==1.3.10                         # Alembic dependency
[-] greenlet==3.2.4                      # SQLAlchemy dependency
[-] aiohttp==3.13.0                      # HTTP client (use httpx instead)
[-] aiohttp-retry==2.9.1
[-] aiohappyeyeballs==2.6.1
[-] aiosignal==1.4.0
[-] async-timeout==5.0.1
[-] frozenlist==1.8.0
[-] multidict==6.7.0
[-] propcache==0.4.1
[-] yarl==1.22.0
[-] jsonschema==4.25.1                   # Not needed for core
[-] jsonschema-specifications==2025.9.1
[-] referencing==0.36.2
[-] rpds-py==0.27.1
[-] narwhals==2.7.0                      # Pandas dependency
[-] protobuf==6.32.1                     # Not needed without gRPC
[-] PyJWT==2.10.1                        # JWT tokens (not used)
[-] Pygments==2.19.2                     # Syntax highlighting
[-] tenacity==9.1.2                      # Retry logic (built-in to httpx)
[-] toml==0.10.2                         # TOML parser (not needed)
[-] tomli==2.2.1                         # TOML parser
[-] tqdm==4.67.1                         # Progress bars
[-] cachetools==6.2.0                    # Caching utilities

✅ KEPT Dependencies (7-8 packages):
────────────────────────────────────────────────────────────────────────────────
[K] fastapi==0.118.2                     # Web framework
[K] uvicorn==0.37.0                      # ASGI server
[K] httpx==0.28.1                        # HTTP client
[K] twilio==9.8.3                        # Twilio SDK
[N] google-generativeai==0.8.3           # NEW - Gemini Flash
[K] pydantic==2.12.0                     # Data validation
[K] pydantic-settings==2.4.0             # Settings management
[K] python-dotenv==1.1.1                 # Environment variables

📊 Transitive Dependencies (auto-installed):
────────────────────────────────────────────────────────────────────────────────
[*] starlette                            # FastAPI dependency
[*] anyio                                # Async I/O
[*] sniffio                              # Async detection
[*] h11                                  # HTTP/1.1
[*] httpcore                             # HTTP core
[*] click                                # CLI (uvicorn)
[*] typing-extensions                    # Type hints
[*] annotated-types                      # Pydantic dependency
[*] pydantic-core                        # Pydantic core
[*] certifi                              # SSL certificates
[*] idna                                 # Domain names
[*] urllib3                              # HTTP client
[*] requests                             # Twilio dependency
[*] PyJWT                                # Twilio dependency
[*] python-dateutil                      # Date handling
[*] pytz                                 # Timezone handling

================================================================================
CODE MODIFICATION PREVIEW
================================================================================

📝 ai_receptionist/app/main.py (BEFORE):
────────────────────────────────────────────────────────────────────────────────
```python
from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import logging

from ai_receptionist.config.settings import Settings, get_settings
from ai_receptionist.app.api.twilio import router as twilio_router
from ai_receptionist.app.api.admin import router as admin_router           # ❌ REMOVE
from ai_receptionist.api.twilio_voice import router as twilio_voice_router # ❌ REMOVE
from ai_receptionist.services.voice.endpoints import router as voice_router# ❌ REMOVE
from ai_receptionist.app.middleware import configure_logging, request_context_middleware

logger = logging.getLogger(__name__)

app = FastAPI(title="AI Receptionist", version="0.1.0")

# Get static directory path
BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"

# Mount static files                                                        # ❌ REMOVE
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/health")
def health(settings: Settings = Depends(get_settings)):
    return {"status": "ok", "env": settings.app_env}

# Serve the ChatGPT-style UI at root                                        # ❌ REMOVE
@app.get("/")
def root():
    html_path = STATIC_DIR / "index.html"
    if html_path.exists():
        return FileResponse(str(html_path))
    return JSONResponse({"name": "ai-receptionist", "version": "0.1.0"})

# Mount routers
app.include_router(twilio_router)
app.include_router(admin_router)                                            # ❌ REMOVE
app.include_router(twilio_voice_router)                                     # ❌ REMOVE
app.include_router(voice_router)                                            # ❌ REMOVE

# Observability: attach request id and tenant id to context and logs
configure_logging()
app.middleware("http")(request_context_middleware)
```

📝 ai_receptionist/app/main.py (AFTER):
────────────────────────────────────────────────────────────────────────────────
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

# Mount Twilio webhook router
app.include_router(twilio_router)

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

────────────────────────────────────────────────────────────────────────────────

📝 ai_receptionist/config/settings.py (BEFORE - 163 lines):
────────────────────────────────────────────────────────────────────────────────
```python
class Settings(BaseSettings):
    # Application Environment
    app_env: str = "local"
    debug: bool = False
    
    # Twilio Configuration
    twilio_account_sid: Optional[str] = None
    twilio_auth_token: Optional[str] = None
    twilio_phone_number: Optional[str] = None
    
    # Database Configuration                                                # ❌ REMOVE
    database_url: Optional[str] = None
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "ai_receptionist"
    postgres_user: Optional[str] = None
    postgres_password: Optional[str] = None
    
    # Redis Configuration                                                   # ❌ REMOVE
    redis_url: Optional[str] = None
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    
    # OpenAI Configuration                                                  # ❌ REMOVE
    openai_api_key: Optional[str] = None
    
    # ... (many more config options)
```

📝 ai_receptionist/config/settings.py (AFTER - ~40 lines):
────────────────────────────────────────────────────────────────────────────────
```python
"""Minimal configuration for voice pipeline."""

from typing import Optional
from pydantic_settings import BaseSettings

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

_settings: Optional[Settings] = None

def get_settings() -> Settings:
    """Get cached settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
```

────────────────────────────────────────────────────────────────────────────────

📝 NEW FILE: ai_receptionist/services/ai/gemini.py
────────────────────────────────────────────────────────────────────────────────
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
        logger.info(f"Initialized Gemini with model: {settings.gemini_model}")
    
    async def generate_response(
        self,
        user_text: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate AI response from user input.
        
        Args:
            user_text: User's spoken input (transcribed)
            context: Optional conversation context
        
        Returns:
            Generated response text
        """
        prompt = self._build_prompt(user_text, context)
        
        try:
            response = await self.model.generate_content_async(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
            return "I apologize, I'm having trouble processing that right now."
    
    def _build_prompt(
        self,
        user_text: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Build prompt for Gemini."""
        system_prompt = (
            "You are a helpful AI receptionist for a business. "
            "Respond concisely and professionally to phone calls. "
            "Keep responses under 3 sentences when possible."
        )
        
        if context:
            # Add context if provided (e.g., business name, hours, services)
            business_info = context.get("business_info", "")
            if business_info:
                system_prompt += f"\n\nBusiness Information:\n{business_info}"
        
        return f"{system_prompt}\n\nCaller: {user_text}\n\nReceptionist:"


# Singleton instance
_gemini_service: Optional[GeminiService] = None


def get_gemini_service() -> GeminiService:
    """Get or create Gemini service instance."""
    global _gemini_service
    if _gemini_service is None:
        _gemini_service = GeminiService()
    return _gemini_service
```

================================================================================
FINAL STRUCTURE VISUALIZATION
================================================================================

ai_receptionist/
├── .env                          ✅ KEEP (user-specific)
├── .gitignore                    ✅ KEEP
├── README.md                     ✅ KEEP (simplified)
├── requirements.txt              ✅ REPLACE with minimal version
├── requirements.minimal.txt      ✅ NEW (backup)
├── REFACTORING_PLAN.md           ✅ NEW (this document)
├── archive/                      ✅ NEW (all removed code)
│   ├── root/
│   │   ├── alembic/
│   │   ├── data/
│   │   ├── docs/
│   │   ├── scripts/
│   │   ├── tests/
│   │   ├── tools/
│   │   └── *.md, *.ini, *.py
│   └── module/
│       ├── static/
│       ├── tests/
│       ├── db/
│       ├── workers/
│       └── services/billing/, flags/, rag.py, router.py
└── ai_receptionist/
    ├── __init__.py               ✅ KEEP
    ├── app/
    │   ├── __init__.py           ✅ KEEP
    │   ├── main.py               ✅ SIMPLIFY (30 lines → 15 lines)
    │   └── api/
    │       ├── __init__.py       ✅ KEEP
    │       └── twilio.py         ✅ KEEP (core webhook)
    ├── config/
    │   ├── __init__.py           ✅ KEEP
    │   └── settings.py           ✅ SIMPLIFY (163 lines → 40 lines)
    ├── core/
    │   ├── __init__.py           ✅ KEEP
    │   └── di.py                 ✅ SIMPLIFY (remove DB/Redis deps)
    ├── models/
    │   ├── __init__.py           ✅ KEEP
    │   └── dtos.py               ✅ KEEP (if needed)
    ├── services/
    │   ├── __init__.py           ✅ KEEP
    │   ├── ai/
    │   │   ├── __init__.py       ✅ NEW
    │   │   └── gemini.py         ✅ NEW (Gemini integration)
    │   └── telephony/
    │       ├── __init__.py       ✅ KEEP
    │       ├── telephony.py      ✅ KEEP (abstract service)
    │       └── twilio_service.py ✅ KEEP (Twilio implementation)
    └── utils/
        ├── __init__.py           ✅ KEEP
        └── helpers.py            ✅ SIMPLIFY (minimal utilities)

FINAL TOTALS:
- Folders: 8 (down from 30+)
- Python files: ~15 (down from 119)
- Lines of code: ~500 (down from ~5000+)
- Dependencies: 7-8 (down from 50+)

================================================================================
DEPLOYMENT IMPACT
================================================================================

Container Size:
  BEFORE: ~800 MB (base image + 50 dependencies)
  AFTER:  ~200 MB (base image + 7 dependencies)
  SAVINGS: 75%

Cold Start Time:
  BEFORE: ~5 seconds (import time + initialization)
  AFTER:  ~1 second (minimal imports)
  IMPROVEMENT: 80%

Memory Usage:
  BEFORE: ~200-300 MB (all services loaded)
  AFTER:  ~50-100 MB (only webhook + Gemini)
  SAVINGS: 60-75%

Request Latency Breakdown:
  BEFORE:
    - FastAPI overhead: 10-20ms
    - Middleware/logging: 10-20ms
    - DB connection pool: 5-10ms
    - Redis lookup: 5-10ms
    - Feature flag check: 5-10ms
    - LLM call: 500-2000ms
    - TOTAL: 535-2070ms

  AFTER:
    - FastAPI overhead: 10-20ms
    - Minimal logging: 2-5ms
    - LLM call: 500-2000ms
    - TOTAL: 512-2025ms

  IMPROVEMENT: ~25-45ms reduction (approaching pure LLM latency)

================================================================================
LEGEND
================================================================================

[-] DELETE/ARCHIVE   - Remove from active codebase
[K] KEEP             - Essential file, keep as-is
[S] SIMPLIFY         - Keep but reduce complexity
[N] NEW              - Create new file
[?] EVALUATE         - Determine if needed based on use case
[*] AUTO             - Automatically installed as dependency

================================================================================
