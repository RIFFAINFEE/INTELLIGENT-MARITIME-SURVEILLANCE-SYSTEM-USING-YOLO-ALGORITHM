import os
import asyncio
import logging

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.websocket_manager import ws_manager

from app.api import camera_routes
from app.api import zone_routes
from app.api import alert_routes
from app.api import stream_routes


# --------------------------------------------------
# Logger
# --------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

logger = logging.getLogger("main")


# --------------------------------------------------
# FastAPI App
# --------------------------------------------------

app = FastAPI(
    title="Maritime Surveillance System",
    version="1.0.0",
    description="AI Powered Maritime Surveillance Backend"
)

logger.info("====================================")
logger.info("Maritime Surveillance Backend Starting")
logger.info("====================================")


# --------------------------------------------------
# Register FastAPI Event Loop (IMPORTANT)
# --------------------------------------------------

@app.on_event("startup")
async def startup_event():

    ws_manager.loop = asyncio.get_running_loop()

    logger.info("[SYSTEM] WebSocket event loop registered")


# --------------------------------------------------
# CORS (Frontend Access)
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("[SYSTEM] CORS Middleware Enabled")


# --------------------------------------------------
# API Routers
# --------------------------------------------------

logger.info("[SYSTEM] Loading API Routes")

app.include_router(camera_routes.router)
logger.info("[ROUTE] Camera Routes Loaded")

app.include_router(zone_routes.router)
logger.info("[ROUTE] Zone Routes Loaded")

app.include_router(alert_routes.router)
logger.info("[ROUTE] Alert Routes Loaded")

app.include_router(stream_routes.router)
logger.info("[ROUTE] Stream Routes Loaded")


# --------------------------------------------------
# Static Files (Alert Snapshots)
# --------------------------------------------------

if os.path.exists("alerts"):

    app.mount(
        "/alert-snapshots",
        StaticFiles(directory="alerts"),
        name="alerts-snapshots"
    )

    logger.info("[SYSTEM] Static alerts directory mounted at /alert-snapshots")

else:

    logger.warning(
        "[WARNING] Alerts directory 'alerts' not found, static mounting skipped"
    )


# --------------------------------------------------
# Root Endpoint
# --------------------------------------------------

@app.get("/")
def root():

    logger.info("[API] Root endpoint called")

    return {
        "status": "running",
        "service": "Maritime Surveillance Backend"
    }


# --------------------------------------------------
# Health Check
# --------------------------------------------------

@app.get("/health")
def health():

    logger.info("[API] Health check requested")

    return {
        "status": "ok"
    }


# --------------------------------------------------
# WebSocket Endpoint
# --------------------------------------------------

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):

    await ws_manager.connect(websocket)

    logger.info("[WebSocket] Client connected")

    try:

        while True:

            # keep connection alive
            data = await websocket.receive_text()

            logger.info(f"[WebSocket] Received message: {data}")

    except WebSocketDisconnect:

        ws_manager.disconnect(websocket)

        logger.info("[WebSocket] Client disconnected")

    except Exception as e:


        logger.error(f"[WebSocket] Error: {e}")