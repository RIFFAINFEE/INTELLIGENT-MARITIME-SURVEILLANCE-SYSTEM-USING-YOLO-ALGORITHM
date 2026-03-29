import logging
from fastapi import WebSocket

# --------------------------------------------------
# Logger Configuration
# --------------------------------------------------

logger = logging.getLogger("websocket_manager")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)


# --------------------------------------------------
# WebSocket Manager
# --------------------------------------------------

class WebSocketManager:

    def __init__(self):

        # active websocket connections
        self.connections = []

        # FastAPI event loop (set at startup)
        self.loop = None

        logger.info("[WebSocketManager] Initialized")

    # --------------------------------------------------

    async def connect(self, websocket: WebSocket):

        try:

            await websocket.accept()

            self.connections.append(websocket)

            logger.info(
                f"[WebSocket] Client connected | "
                f"Total clients: {len(self.connections)}"
            )

        except Exception as e:

            logger.error(f"[WebSocket] Connection failed: {e}")

    # --------------------------------------------------

    def disconnect(self, websocket: WebSocket):

        try:

            if websocket in self.connections:

                self.connections.remove(websocket)

                logger.info(
                    f"[WebSocket] Client disconnected | "
                    f"Remaining clients: {len(self.connections)}"
                )

        except Exception as e:

            logger.error(f"[WebSocket] Disconnect error: {e}")

    # --------------------------------------------------

    async def broadcast(self, message: dict):

        if not self.connections:

            logger.debug("[WebSocket] No active clients to broadcast")

            return

        logger.info(
            f"[WebSocket] Broadcasting message to "
            f"{len(self.connections)} clients"
        )

        disconnected = []

        for conn in self.connections:

            try:

                await conn.send_json(message)

            except Exception as e:

                logger.warning(
                    f"[WebSocket] Failed to send message, "
                    f"marking client for removal: {e}"
                )

                disconnected.append(conn)

        # cleanup broken connections
        for conn in disconnected:

            self.disconnect(conn)

    # --------------------------------------------------

    def connection_count(self):

        return len(self.connections)


# --------------------------------------------------
# Singleton Instance
# --------------------------------------------------

ws_manager = WebSocketManager()