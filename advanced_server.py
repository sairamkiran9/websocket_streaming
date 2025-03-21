#!/usr/bin/env python
import asyncio
import json
import logging
import websockets
import random
import time
import math
from datetime import datetime
import argparse

# Configure logging
logging.basicConfig(
    format="%(asctime)s %(message)s",
    level=logging.INFO,
)

# Keep track of all connected clients with their subscriptions
CLIENTS = {}

# Available data streams
STREAMS = {
    "random": "Random fluctuating values",
    "sine": "Sine wave pattern",
    "system": "Simulated system metrics",
    "events": "Random events and alerts"
}

class DataGenerator:
    """Generate different types of streaming data."""
    
    def __init__(self):
        self.counter = 0
        self.sine_offset = 0
        self.last_event = time.time()
    
    def get_timestamp(self):
        """Get current timestamp string."""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    
    def random_data(self):
        """Generate random fluctuating data."""
        return {
            "stream": "random",
            "timestamp": self.get_timestamp(),
            "value": random.uniform(0, 100),
            "direction": random.choice(["up", "down", "stable"]),
            "delta": random.uniform(-5, 5)
        }
    
    def sine_wave(self):
        """Generate sine wave pattern data."""
        self.sine_offset += 0.1
        value = 50 + 40 * math.sin(self.sine_offset)
        
        return {
            "stream": "sine",
            "timestamp": self.get_timestamp(),
            "value": value,
            "phase": self.sine_offset,
            "frequency": 0.1
        }
    
    def system_metrics(self):
        """Generate simulated system metrics."""
        # Simulate daily patterns with some randomness
        hour = datetime.now().hour
        # CPU usage higher during work hours
        cpu_base = 30 + 20 * math.sin(hour / 24 * 2 * math.pi)
        
        return {
            "stream": "system",
            "timestamp": self.get_timestamp(),
            "metrics": {
                "cpu": max(0, min(100, cpu_base + random.uniform(-10, 10))),
                "memory": max(0, min(100, 50 + random.uniform(-20, 20))),
                "disk": max(0, min(100, 60 + random.uniform(-5, 5))),
                "network": max(0, min(1000, 200 + random.uniform(-100, 100))),
                "temperature": max(0, min(100, 40 + random.uniform(-5, 5)))
            },
            "status": random.choices(
                ["healthy", "warning", "critical"],
                weights=[0.8, 0.15, 0.05],
                k=1
            )[0]
        }
    
    def random_events(self):
        """Generate random events and alerts."""
        current_time = time.time()
        
        # Only generate a new event every ~5-15 seconds
        if current_time - self.last_event < random.uniform(5, 15):
            return None
        
        self.last_event = current_time
        
        event_types = [
            "user_login", "user_logout", "api_call", "database_query",
            "error", "warning", "info", "security_alert"
        ]
        
        severity_levels = ["low", "medium", "high", "critical"]
        
        return {
            "stream": "events",
            "timestamp": self.get_timestamp(),
            "event_type": random.choice(event_types),
            "severity": random.choice(severity_levels),
            "message": f"Event #{self.counter} occurred",
            "source": random.choice(["server", "client", "database", "network"]),
            "id": self.counter
        }

async def register(websocket, streams=None):
    """Register a new client with optional stream subscriptions."""
    if streams is None:
        # Default to all streams
        streams = list(STREAMS.keys())
    
    CLIENTS[websocket] = streams
    logging.info(f"New client connected. Subscribed to: {', '.join(streams)}. Total clients: {len(CLIENTS)}")

async def unregister(websocket):
    """Unregister a client."""
    if websocket in CLIENTS:
        del CLIENTS[websocket]
        logging.info(f"Client disconnected. Total clients: {len(CLIENTS)}")

async def generate_and_send_data():
    """Generate and send data to subscribed clients."""
    generator = DataGenerator()
    counter = 0
    
    while True:
        counter += 1
        generator.counter = counter
        
        # Generate data for each stream type
        data_random = generator.random_data()
        data_sine = generator.sine_wave()
        data_system = generator.system_metrics()
        data_events = generator.random_events()
        
        # Map of stream types to their data
        stream_data = {
            "random": data_random,
            "sine": data_sine,
            "system": data_system,
            "events": data_events
        }
        
        # Send data to each client based on their subscriptions
        for websocket, streams in list(CLIENTS.items()):
            try:
                for stream in streams:
                    data = stream_data.get(stream)
                    if data is not None:  # Skip None data (like infrequent events)
                        await websocket.send(json.dumps(data))
            except websockets.exceptions.ConnectionClosed:
                # Will be removed by the handler, just skip for now
                continue
        
        # Sleep for a short interval
        await asyncio.sleep(1)

async def handle_client(websocket):
    """Handle a client connection and their subscription messages."""
    # Default subscription to all streams
    await register(websocket)
    
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                
                # Handle subscription message
                if "subscribe" in data:
                    streams = data["subscribe"]
                    # Validate streams
                    valid_streams = [s for s in streams if s in STREAMS]
                    CLIENTS[websocket] = valid_streams
                    logging.info(f"Client updated subscriptions to: {', '.join(valid_streams)}")
                    
                    # Send confirmation
                    await websocket.send(json.dumps({
                        "type": "subscription_update",
                        "subscribed": valid_streams
                    }))
                
                # Handle metadata request
                elif data.get("type") == "get_streams":
                    await websocket.send(json.dumps({
                        "type": "streams_list",
                        "streams": STREAMS
                    }))
                
            except json.JSONDecodeError:
                logging.warning(f"Received invalid JSON: {message}")
                
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        await unregister(websocket)

async def main(host="localhost", port=8765):
    """Start the WebSocket server and data generator."""
    # Start the data generator task
    data_generator = asyncio.create_task(generate_and_send_data())
    
    # Start the WebSocket server
    async with websockets.serve(
        handle_client, 
        host, 
        port,
        ping_interval=30,
        ping_timeout=10
    ):
        logging.info(f"WebSocket server started at ws://{host}:{port}")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Advanced WebSocket streaming server")
    parser.add_argument("--host", default="localhost", help="Host address to bind to")
    parser.add_argument("--port", type=int, default=8765, help="Port to listen on")
    
    args = parser.parse_args()
    
    try:
        asyncio.run(main(args.host, args.port))
    except KeyboardInterrupt:
        logging.info("Server stopped by user")
