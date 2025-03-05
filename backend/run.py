import uvicorn
from api.main import app
from config.logging_config import setup_logging

# Configure logging
logger = setup_logging()
logger.info("Starting MPCrew application")

if __name__ == "__main__":
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
    logger.info("Application shutdown") 