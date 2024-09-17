# Rust RCON Command-line Tool

![Rust](https://img.shields.io/badge/game-Rust-red)
![Python](https://img.shields.io/badge/language-Python-blue)
![License](https://img.shields.io/badge/license-MIT-green)

A powerful and user-friendly command-line interface for interacting with Rust game servers using the RCON (Remote Console) protocol.

## Features

- 🚀 Easy-to-use command-line interface
- 🔐 Secure WebSocket-based RCON communication
- 🛠 Support for custom commands
- 📊 Optional verbose output for debugging
- 🖨 Raw JSON response printing capability

## Prerequisites

- Python 3.6+
- `websocket-client` library

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/rust-rcon-commandline.git
   cd rust-rcon-commandline
   ```

2. Install the required dependencies:
   ```
   pip install websocket-client
   ```

## Usage

Run the script with the following command-line arguments:

```
python rust_rcon_client.py -H <host> -P <port> -p <password> -c <command> [options]
```

### Arguments

- `-H, --host`: Server hostname or IP address (required)
- `-P, --port`: Server RCON port (required)
- `-p, --password`: RCON password (required)
- `-c, --command`: Command to execute (use quotes for commands with spaces) (required)
- `-v, --verbose`: Enable verbose output (optional)
- `--raw`: Print raw JSON response (optional)

### Examples

1. Get server information:
   ```
   python rust_rcon_client.py -H 127.0.0.1 -P 28016 -p mypassword -c "serverinfo"
   ```

2. Broadcast a message to all players:
   ```
   python rust_rcon_client.py -H 127.0.0.1 -P 28016 -p mypassword -c "say Hello, players!"
   ```

3. Get a list of all connected players with verbose output:
   ```
   python rust_rcon_client.py -H 127.0.0.1 -P 28016 -p mypassword -c "players" -v
   ```

4. Print the raw JSON response:
   ```
   python rust_rcon_client.py -H 127.0.0.1 -P 28016 -p mypassword -c "serverinfo" --raw
   ```

## Error Handling

The script includes robust error handling for common issues:

- Connection timeouts
- Authentication failures
- Invalid JSON responses
- Unexpected errors

Error messages are displayed with clear descriptions to help troubleshoot issues.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This tool is not affiliated with, maintained, authorized, endorsed, or sponsored by Facepunch Studios or any of its affiliates. This is an independent and unofficial project.
