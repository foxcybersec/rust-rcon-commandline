import websocket
import json
import argparse
import sys
import logging
from typing import Dict, Any

class RustRCONError(Exception):
    pass

class RustRCONClient:
    def __init__(self, host: str, port: int, password: str, verbose: bool = False):
        self.host = host
        self.port = port
        self.password = password
        self.verbose = verbose
        self.ws = None
        self.request_id = 0

        level = logging.DEBUG if verbose else logging.INFO
        logging.basicConfig(format='%(levelname)s: %(message)s', level=level)
        self.logger = logging.getLogger(__name__)

    def connect(self):
        url = f"ws://{self.host}:{self.port}/{self.password}"
        try:
            self.ws = websocket.create_connection(url, timeout=10)
            self.logger.debug(f"Connected to {self.host}:{self.port}")
        except websocket.WebSocketTimeoutException:
            raise RustRCONError("Connection timed out. Check your host and port.")
        except websocket.WebSocketBadStatusException as e:
            if e.status_code == 401:
                raise RustRCONError("Authentication failed. Check your password.")
            else:
                raise RustRCONError(f"Connection failed with status code: {e.status_code}")
        except Exception as e:
            raise RustRCONError(f"Failed to connect: {str(e)}")

    def disconnect(self):
        if self.ws:
            self.ws.close()
            self.logger.debug("Disconnected from server")
            self.ws = None

    def send_command(self, command: str) -> Dict[str, Any]:
        if not self.ws:
            raise RustRCONError("Not connected to server. Call connect() first.")

        self.request_id += 1
        message = json.dumps({
            "Identifier": self.request_id,
            "Message": command,
            "Name": "WebRcon"
        })
        
        try:
            self.logger.debug(f"Sending command: {command}")
            self.ws.send(message)
            response = self.ws.recv()
            self.logger.debug(f"Received response: {response}")
            return json.loads(response)
        except websocket.WebSocketTimeoutException:
            raise RustRCONError("Server did not respond in time.")
        except json.JSONDecodeError:
            raise RustRCONError("Received invalid JSON response from server.")
        except Exception as e:
            raise RustRCONError(f"Error sending command: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description="RCON client for Rust using WebSockets")
    parser.add_argument("-H", "--host", required=True, help="Server hostname or IP address")
    parser.add_argument("-P", "--port", type=int, required=True, help="Server RCON port")
    parser.add_argument("-p", "--password", required=True, help="RCON password")
    parser.add_argument("-c", "--command", nargs='+', required=True, help="Command to execute (use quotes for commands with spaces)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("--raw", action="store_true", help="Print raw JSON response")
    parser.add_argument("--retry", type=int, default=3, help="Number of connection retry attempts")
    
    try:
        args = parser.parse_args()
    except argparse.ArgumentError as e:
        print(f"Argument error: {str(e)}")
        sys.exit(1)

    client = RustRCONClient(args.host, args.port, args.password, args.verbose)

    for attempt in range(args.retry):
        try:
            client.connect()
            full_command = " ".join(args.command)
            response = client.send_command(full_command)
            
            if args.raw:
                print(json.dumps(response, indent=2))
            else:
                print("Server response:")
                print(response.get('Message', 'No message in response'))
            break
        except RustRCONError as e:
            print(f"RCON Error (Attempt {attempt + 1}/{args.retry}): {str(e)}")
            if attempt == args.retry - 1:
                sys.exit(1)
        except KeyboardInterrupt:
            print("\nOperation interrupted by user.")
            break
        except Exception as e:
            print(f"An unexpected error occurred: {str(e)}")
            sys.exit(1)
        finally:
            client.disconnect()

if __name__ == "__main__":
    main()
