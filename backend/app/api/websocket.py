"""WebSocket handlers."""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()


class ConnectionManager:
    """Manage WebSocket connections."""

    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, job_id: str):
        """Accept and register a WebSocket connection."""
        await websocket.accept()
        if job_id not in self.active_connections:
            self.active_connections[job_id] = []
        self.active_connections[job_id].append(websocket)

    def disconnect(self, websocket: WebSocket, job_id: str):
        """Remove a WebSocket connection."""
        if job_id in self.active_connections:
            self.active_connections[job_id].remove(websocket)
            if not self.active_connections[job_id]:
                del self.active_connections[job_id]

    async def broadcast_to_job(self, job_id: str, message: dict):
        """Broadcast a message to all connections for a job."""
        if job_id in self.active_connections:
            for connection in self.active_connections[job_id]:
                await connection.send_json(message)


manager = ConnectionManager()


@router.websocket("/ws/generation/{job_id}")
async def generation_progress_websocket(websocket: WebSocket, job_id: str):
    """WebSocket endpoint for real-time generation progress."""
    # TODO: Validate job_id and user authentication
    await manager.connect(websocket, job_id)
    try:
        while True:
            # Keep connection open, waiting for client messages or disconnect
            data = await websocket.receive_text()
            # Handle ping/pong or other client messages
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(websocket, job_id)
