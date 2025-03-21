# WebSocket Streaming Proof of Concept

A simple demonstration of real-time data streaming using WebSockets in Python.

## Features

- Real-time data streaming from server to clients
- Multiple client options (web browser and command line)
- Data visualization with Chart.js
- Multiple data stream types (random, sine wave, system metrics, events)
- Customizable data generation

## Requirements

- Python 3.7+
- WebSockets library for Python
- Modern web browser for web client

## Quick Start

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Start the server:
   ```
   python advanced_server.py
   ```

3. Connect with a client:
   - Open `index.html` in a web browser
   - OR run `python ws_client.py`

## Available Servers

- `ws_server.py` - Basic server with single data stream
- `advanced_server.py` - Enhanced server with multiple data streams

## Available Clients

- `index.html` - Web browser client with data visualization
- `advanced_client.html` - Enhanced web client for multiple streams
- `ws_client.py` - Command line client

## Command Line Options

```
python ws_client.py --uri ws://localhost:8765 --limit 10
```

- `--uri` - WebSocket server URL
- `--limit` - Number of messages to receive before disconnecting

## License

MIT# websocket_streaming
