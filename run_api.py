#!/usr/bin/env python3
"""Script to run the RetailAssist API."""

import uvicorn
from retail_assist.infra.settings import settings
from retail_assist.infra.logging import logger

if __name__ == "__main__":
    logger.info("Starting RetailAssist API server...")
    logger.info(f"Server will run on {settings.API_HOST}:{settings.API_PORT}")
    
    uvicorn.run(
        "retail_assist.api.app:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        workers=settings.API_WORKERS,
        reload=True,
        log_level=settings.LOG_LEVEL.lower(),
    )
