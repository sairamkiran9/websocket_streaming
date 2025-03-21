#!/usr/bin/env python
import asyncio
import json
import logging
import websockets
import random
import time
from datetime import datetime

# Configure logging
logging.basicConfig(
    format="%(asctime)s %(message)s",
    level=logging.INFO,
)

# Keep track of all connected clients
CLIENTS = set()

async def register(websocket):
    """Register a new client."""
    CLIENTS.add(websocket)
    logging.info(f"New client connected. Total clients: {len(CLIENTS)}")

async def unregister(websocket):
    """Unregister a client."""
    CLIENTS.remove(websocket)
    logging.info(f"Client disconnected. Total clients: {len(CLIENTS)}")

async def generate_data():
    """Generate random data for streaming."""
    while True:
        # Current timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        
        # Generate random data points
        data = {
            "timestamp": timestamp,
            "value": random.uniform(0, 100),
            "category": random.choice(["A", "B", "C", "D"]),
            "status": random.choice(["active", "idle", "error"]),
            "metrics": {
                "cpu": random.uniform(0, 100),
                "memory": random.uniform(0, 100),
                "network": random.uniform(0, 1000)
            }
        }
        
        # Convert to JSON and broadcast to all clients
        message = json.dumps(data)
        
        if CLIENTS:  # Only try to send if there are connected clients
            websockets.broadcast(CLIENTS, message)
        
        # Sleep for a short interval
        await asyncio.sleep(1)

async def handle_client(websocket):
    """Handle a connection and dispatch data to the client."""
    await register(websocket)
    try:
        await websocket.wait_closed()
    finally:
        await unregister(websocket)

async def main():
    """Start the WebSocket server and data generator."""
    # Start the data generator task
    data_generator = asyncio.create_task(generate_data())
    
    # Start the WebSocket server
    async with websockets.serve(
        handle_client, 
        "localhost", 
        8765,
        ping_interval=30,  # Send ping every 30 seconds
        ping_timeout=10    # Wait 10 seconds for pong before timeout
    ):
        logging.info("WebSocket server started at ws://localhost:8765")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Server stopped by user")
