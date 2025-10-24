from typing import Optional
import os

try:
    # Preferred in Pydantic v2
    from pydantic_settings import BaseSettings, SettingsConfigDict  # type: ignore

    class Settings(BaseSettings):
        """Application settings loaded from environment variables or .env file."""

        app_env: str = "local"

        # Twilio (example placeholders)
        twilio_account_sid: Optional[str] = None
        twilio_auth_token: Optional[str] = None
        twilio_phone_number: Optional[str] = None

        model_config = SettingsConfigDict(env_file=".env", env_prefix="", case_sensitive=False)

except Exception:  # pragma: no cover - fallback when pydantic-settings not available
    # Lightweight fallback to avoid import errors if dependency isn't installed yet.
    from pydantic import BaseModel

    class Settings(BaseModel):
        app_env: str = os.getenv("APP_ENV", "local")
        twilio_account_sid: Optional[str] = os.getenv("TWILIO_ACCOUNT_SID")
        twilio_auth_token: Optional[str] = os.getenv("TWILIO_AUTH_TOKEN")
        twilio_phone_number: Optional[str] = os.getenv("TWILIO_PHONE_NUMBER")

