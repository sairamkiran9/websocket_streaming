#!/usr/bin/env python
import asyncio
import websockets
import json
import logging
import argparse
import sys
from datetime import datetime

# Configure logging
logging.basicConfig(
    format="%(asctime)s %(message)s",
    level=logging.INFO,
)

async def receive_messages(uri, limit=None):
    """
    Connect to a WebSocket server and receive messages.
    
    Args:
        uri: WebSocket server URI
        limit: Optional limit of messages to receive before disconnecting
    """
    counter = 0
    
    try:
        logging.info(f"Connecting to {uri}...")
        async with websockets.connect(uri) as websocket:
            logging.info("Connected!")
            
            # Infinite loop to receive messages (or until limit reached)
            while limit is None or counter < limit:
                try:
                    # Wait for a message
                    message = await websocket.recv()
                    counter += 1
                    
                    # Parse and display the message
                    data = json.loads(message)
                    timestamp = data.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3])
                    
                    # Print a formatted message
                    print(f"[{counter}] Message received at {timestamp}")
                    print(json.dumps(data, indent=2))
                    print("-" * 50)
                    
                    # If we've reached the limit, exit
                    if limit is not None and counter >= limit:
                        logging.info(f"Received {limit} messages. Disconnecting.")
                        break
                        
                except websockets.exceptions.ConnectionClosed:
                    logging.error("Connection closed by server")
                    break
                    
    except websockets.exceptions.ConnectionError:
        logging.error(f"Failed to connect to {uri}")
        return
    except KeyboardInterrupt:
        logging.info("Client stopped by user")
        return

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="WebSocket Client for Data Streaming")
    parser.add_argument("--uri", default="ws://localhost:8765",
                        help="WebSocket server URI (default: ws://localhost:8765)")
    parser.add_argument("--limit", type=int, default=None,
                        help="Limit number of messages to receive before disconnecting")
    
    args = parser.parse_args()
    
    # Start the client
    try:
        asyncio.run(receive_messages(args.uri, args.limit))
    except KeyboardInterrupt:
        logging.info("Client stopped by user")
        sys.exit(0)

if __name__ == "__main__":
    main()
