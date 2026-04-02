from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import time
import asyncio
import os
from core.db import Base, get_engine
from services.candles import fetch_candles
from core.settings import get_app_name, get_environment, get_debug
from core.logging import setup_logging, get_logger
from services.candles import candle_loop
from api.indicator_routes import router

# Prometheus метрики
from prometheus_client import Counter, Histogram, generate_latest, REGISTRY
from starlette.responses import Response

setup_logging()

logger = get_logger(__name__)

# ----- PROMETHEUS МЕТРИКИ -----
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Контекстный менеджер для жизненного цикла приложения"""
    logger.info(f"Starting {get_app_name()}")
    logger.info(f"Environment: {get_environment()}")
    logger.info(f"Debug mode: {get_debug()}")
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        logger.info(f"Successfully create database")

    asyncio.create_task(candle_loop())
    logger.info(f"Candle loop started")
    yield
    logger.info(f"Shutting down {get_app_name()}")


app = FastAPI(
    title=get_app_name(),
    debug=get_debug(),
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.middleware("http")
async def log_and_metrics(request: Request, call_next):
    """Middleware для логирования и сбора метрик"""
    logger_api = get_logger("api")

    start_time = time.time()

    logger_api.info(f"Request: {request.method} {request.url.path}")

    try:
        response = await call_next(request)

        process_time = time.time() - start_time

        # Логирование
        logger_api.info(
            f"Response: {request.method} {request.url.path} | "
            f"Status: {response.status_code} | "
            f"Time: {process_time:.3f}s"
        )

        # Prometheus метрики
        http_requests_total.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()

        http_request_duration.labels(
            method=request.method,
            endpoint=request.url.path
        ).observe(process_time)

        return response

    except Exception as e:
        logger_api.error(
            f"Error processing request: {request.method} {request.url.path} | {str(e)}",
            exc_info=True
        )
        raise


@app.get("/health")
async def health_check():
    """Проверка здоровья приложения"""
    logger.debug("Health check requested")
    return {"status": "healthy"}


@app.get("/metrics")
async def get_metrics():
    """Эндпоинт для Prometheus метрик"""
    return Response(generate_latest(REGISTRY), media_type="text/plain")