#!/usr/bin/env python3
"""
Backend-for-Frontend (BFF) for the Shearwater Control Panel

This FastAPI server provides a simple REST API for the Svelte UI to
interact with the underlying `manage.py` script and control the services.
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import uvicorn
import asyncio
import zmq
import zmq.asyncio
from contextlib import asynccontextmanager

# --- Lifespan Management ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Lifespan startup: Starting log broadcaster...")
    task = asyncio.create_task(log_broadcaster())
    yield
    # Shutdown
    print("Lifespan shutdown: Cancelling log broadcaster...")
    task.cancel()

app = FastAPI(lifespan=lifespan)
context = zmq.asyncio.Context()


# --- CORS Middleware ---
# This allows the Svelte frontend (running on a different port) to talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # The default Svelte dev server port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- WebSocket Connection Manager ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

# --- Background Task for Broadcasting Logs ---
async def log_broadcaster():
    """Subscribes to the ZMQ broker and broadcasts logs to WebSocket clients."""
    sub_socket = context.socket(zmq.SUB)
    sub_socket.connect("tcp://localhost:5556") # Connect to the broker's XPUB port
    sub_socket.setsockopt_string(zmq.SUBSCRIBE, "") # Subscribe to all topics

    print("Log broadcaster started. Listening to ZMQ broker...")
    # Send a ready ping every 3 seconds to let the frontend know we are alive
    async def ready_pinger():
        while True:
            await manager.broadcast(json.dumps({"status": "READY"}))
            await asyncio.sleep(3)

    ping_task = asyncio.create_task(ready_pinger())

    while True:
        try:
            topic, message = await sub_socket.recv_multipart()
            await manager.broadcast(message.decode('utf-8'))
        except Exception as e:
            print(f"Error in log broadcaster: {e}")
            await asyncio.sleep(1) # Avoid tight loop on error

def run_manage_py_command(command: str) -> str:
    """Helper function to run a command via the manage.py script."""
    try:
        process = subprocess.Popen(
            ["python", "manage.py", command],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate(timeout=30)
        if process.returncode != 0:
            return f"Error running '{command}':\n{stderr}"
        return stdout
    except FileNotFoundError:
        return "Error: manage.py not found."
    except subprocess.TimeoutExpired:
        return f"Error: Timeout running '{command}'."
    except Exception as e:
        return f"An unexpected error occurred: {e}"

@app.get("/api/services/status")
async def get_status():
    """Endpoint to get the status of all services."""
    output = run_manage_py_command("status")
    return {"output": output}

@app.post("/api/services/start")
async def start_services():
    """Endpoint to start all services."""
    output = run_manage_py_command("start")
    return {"output": output}

@app.post("/api/services/stop")
async def stop_services():
    """Endpoint to stop all services."""
    output = run_manage_py_command("stop")
    return {"output": output}

@app.websocket("/ws/log")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep the connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("Client disconnected from WebSocket.")

if __name__ == "__main__":
    print("Starting Shearwater BFF Server...")
    print("API available at http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
