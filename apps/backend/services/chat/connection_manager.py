from fastapi import WebSocket
from typing import Dict, List

class ConnectionManager:
    def __init__(self):
        # This will store active connections for each chat thread (topic)
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, topic: str):
        await websocket.accept()
        if topic not in self.active_connections:
            self.active_connections[topic] = []
        self.active_connections[topic].append(websocket)

    def disconnect(self, websocket: WebSocket, topic: str):
        if topic in self.active_connections:
            self.active_connections[topic].remove(websocket)

    async def broadcast(self, message: str, topic: str):
        if topic in self.active_connections:
            for connection in self.active_connections[topic]:
                await connection.send_text(message)

manager = ConnectionManager()
