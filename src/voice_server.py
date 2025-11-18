"""
Twilio Voice API Server Entry Point
Uvicorn server for the Haircut Concierge Voice API
"""

import os
import logging
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def setup_application():
    """Initialize application components"""
    # Ensure data directory and files exist
    from src.calendar_handler import ensure_data_file
    ensure_data_file()
    
    # Validate environment variables
    required_vars = ['TWILIO_ACCOUNT_SID', 'TWILIO_AUTH_TOKEN', 'TWILIO_PHONE_NUMBER']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars and os.getenv('TEST_MODE') != 'true':
        logger.warning(f"Missing environment variables: {missing_vars}")
        logger.warning("Some features may not work correctly without proper configuration")
    
    logger.info("Application setup complete")

# Import the FastAPI app

# Setup on import
setup_application()

if __name__ == "__main__":
    import uvicorn
    
    # Development server configuration
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', '8000'))
    
    logger.info(f"Starting Haircut Concierge Voice API on {host}:{port}")
    logger.info("Available endpoints:")
    logger.info("  GET/POST /twilio/voice - Twilio voice webhook entry point")
    logger.info("  POST /twilio/handle - Handle speech input")
    logger.info("  GET /health - Health check")
    
    # Command to run: uvicorn src.voice_server:app --host 0.0.0.0 --port 8000
    uvicorn.run(
        "src.twilio_handler:app",
        host=host,
        port=port,
        reload=True,  # Enable auto-reload in development
        log_level="info"
    )