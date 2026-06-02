"""
Simple localhost test client for Photoneo Maintenance Tool Server.
Connects to 127.0.0.1:2222 and lets you send commands interactively.
"""

import socket

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 2222

HELP_TEXT = """
Available commands:
  START_CALIBRATION <serial>   Connect and start calibration for a device
  ADJUST_POWER                 Adjust device power
  TRIGGER                      Trigger a scan and report recognized markers
  ANALYZE                      Analyze scan and report area occupancy score
  PATCH                        Apply patch (automatically disconnects device)
  STOP_CALIBRATION             Stop calibration and release device

Local commands:
  help                         Show this help message
  quit / exit                  Disconnect and exit
"""

def main():
    print("=" * 60)
    print("  Photoneo Maintenance Tool – Test Client")
    print("=" * 60)
    print(f"Connecting to {SERVER_HOST}:{SERVER_PORT} ...")

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((SERVER_HOST, SERVER_PORT))
            sock.settimeout(50.0)
            print("Connected. Type 'help' for a list of commands.\n")

            while True:
                try:
                    raw = input("cmd> ").strip()
                except EOFError:
                    break

                if not raw:
                    continue

                if raw.lower() in ("quit", "exit"):
                    print("Disconnecting.")
                    break

                if raw.lower() == "help":
                    print(HELP_TEXT)
                    continue

                # Send command to server
                sock.sendall((raw + "\n").encode("utf-8"))

                # Read response (server always ends with \n)
                try:
                    response = ""
                    while not response.endswith("\n"):
                        chunk = sock.recv(4096).decode("utf-8")
                        if not chunk:
                            print("Server closed the connection.")
                            return
                        response += chunk
                    print(f"<<  {response.strip()}\n")
                except socket.timeout:
                    print("(!) Timed out waiting for a response.\n")

    except ConnectionRefusedError:
        print(f"ERROR: Could not connect to {SERVER_HOST}:{SERVER_PORT}. Is the server running?")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    main()
