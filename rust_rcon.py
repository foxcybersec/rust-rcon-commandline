# Import required libraries
import websocket
import json
import argparse
import sys
import logging


# Custom exception for RCON-related errors
class RustRCONError(Exception):
    pass

# Main RCON client class
class RustRCONClient:
    def __init__(self, host, port, password, verbose=False):
        """
        Initialize the RustRCONClient.

        :param host: Server hostname or IP address
        :param port: Server RCON port
        :param password: RCON password
        :param verbose: Enable verbose logging if True
        """
        self.host = host
        self.port = port
        self.password = password
        self.verbose = verbose
        self.ws = None
        self.request_id = 0

        # Set up logging
        level = logging.DEBUG if verbose else logging.INFO
        logging.basicConfig(format='%(levelname)s: %(message)s', level=level)
        self.logger = logging.getLogger(__name__)

    def connect(self):
        """
        Establish a WebSocket connection to the RCON server.

        :raises RustRCONError: If connection fails
        """
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
        """Close the WebSocket connection if it exists."""
        if self.ws:
            self.ws.close()
            self.logger.debug("Disconnected from server")

    def send_command(self, command):
        """
        Send a command to the RCON server and return the response.

        :param command: The command to send
        :return: JSON response from the server
        :raises RustRCONError: If sending the command fails
        """
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
    """Main function to handle command-line interface and execute RCON commands."""
    # Set up command-line argument parser
    parser = argparse.ArgumentParser(description="RCON client for Rust using WebSockets")
    parser.add_argument("-H", "--host", required=True, help="Server hostname or IP address")
    parser.add_argument("-P", "--port", type=int, required=True, help="Server RCON port")
    parser.add_argument("-p", "--password", required=True, help="RCON password")
    parser.add_argument("-c", "--command", nargs='+', required=True, help="Command to execute (use quotes for commands with spaces)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("--raw", action="store_true", help="Print raw JSON response")
    
    # Parse command-line arguments
    try:
        args = parser.parse_args()
    except argparse.ArgumentError as e:
        print(f"Argument error: {str(e)}")
        sys.exit(1)

    # Create RCON client instance
    client = RustRCONClient(args.host, args.port, args.password, args.verbose)

    try:
        # Connect to the server
        client.connect()
        
        # Join command arguments and send the command
        full_command = " ".join(args.command)
        response = client.send_command(full_command)
        
        # Print the response
        if args.raw:
            print(json.dumps(response, indent=2))
        else:
            print("Server response:")
            print(response.get('Message', 'No message in response'))
    
    except RustRCONError as e:
        print(f"RCON Error: {str(e)}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nOperation interrupted by user.")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        sys.exit(1)
    finally:
        # Ensure disconnect is called even if an error occurs
        client.disconnect()

# Entry point of the script
if __name__ == "__main__":
    main()