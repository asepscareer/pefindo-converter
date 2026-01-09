from fastapi import FastAPI
from middleware_kit import ObservabilityMiddleware, LoggerConfigurator

import uvicorn
import logging

from api.v1 import SmartSearchIndvRouter, GetCustomReportRouter, GetPdfReportRouter, GetOtherReportRouter
from config import lifespan, settings


LoggerConfigurator().setup()
logger = logging.getLogger(__name__)

def create_app() -> FastAPI:
    app = FastAPI(title="Pefindo Converter API",debug=settings.debug,lifespan=lifespan,)

    app.add_middleware(ObservabilityMiddleware)
    app.include_router(SmartSearchIndvRouter,prefix="/pefindo",tags=["Pefindo"])
    app.include_router(GetCustomReportRouter,prefix="/pefindo",tags=["Pefindo"])
    app.include_router(GetPdfReportRouter,prefix="/pefindo",tags=["Pefindo"])
    app.include_router(GetOtherReportRouter,prefix="/pefindo",tags=["Pefindo"])
    return app


app = create_app()

@app.get("/", description="Root endpoint", tags=["Root"])
async def index():
    logger.info("Root endpoint accessed")
    return {"message": "Welcome to the Pefindo API Integration!"}

@app.get("/health", description="Health check endpoint", tags=["Root"])
async def health_check():
    return {"status": "healthy"}

@app.get("/ready", description="Ready check endpoint", tags=["Root"])
async def ready_check():
    return {"status": "ready"}

if __name__ == "__main__":
    uvicorn.run(app, host=settings.host, port=settings.port)