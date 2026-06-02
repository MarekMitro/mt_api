#Robot-controlled server for Photoneo Maintenance Tool

import socket
import sys
from phoxi_api import MaintenanceTool
from phoxi_api.exceptions import PhoXiError

SERVER_HOST = "0.0.0.0"
SERVER_PORT = 2222


def cleanup_device(device):
    #Safely disconnect and release the device if it exists.
    if device is not None:
        try:
            # Attempt to call disconnect() if the method exists
            if hasattr(device, "disconnect"):
                device.disconnect()
        except Exception as e:
            print(f"Error during device disconnect: {e}")
        # Let go of the reference
        device = None
    return None


def handle_client(conn, addr, mt):
    #Handle all commands from a single client connection.
    device = None
    print(f"Connected by {addr}")

    try:
        conn.settimeout(5.0)  # timeout for recv

        while True:
            try:
                data = conn.recv(1024)
                if not data:
                    print("Client disconnected.")
                    break

                command_line = data.decode("utf-8").strip()
                if not command_line:
                    continue
                print(f"Received: {command_line}")

                parts = command_line.split()
                cmd = parts[0].upper()
                response = None

                # ---------- Command handling ----------
                if cmd == "START_CALIBRATION":
                    if len(parts) < 2:
                        response = "NOK:Missing serial number"
                    else:
                        serial = parts[1]
                        if device is not None:
                            response = "NOK:Calibration already active (send STOP_CALIBRATION first)"
                        else:
                            try:
                                device = mt.connect(serial, "./", "./ValidationTarget-M.json")
                                response = "OK"
                                print(f"Device {serial} connected.")
                            except PhoXiError as e:
                                response = f"NOK:{e}"
                                device = None

                elif cmd == "ADJUST_POWER":
                    if device is None:
                        response = "NOK:No active calibration (send START_CALIBRATION first)"
                    else:
                        try:
                            device.adjust_power()
                            response = "OK"
                            print("Power adjustment succeeded.")
                        except PhoXiError as e:
                            response = f"NOK:{e}"

                elif cmd == "TRIGGER":
                    if device is None:
                        response = "NOK:No active calibration"
                    else:
                        try:
                            result = device.trigger()
                            response = f"OK, markers recognized: {result.count_of_recognized_marker_points}"
                            print(f"Trigger OK: frames={result.count_of_acquired_scans}, markers={result.count_of_recognized_marker_points}")
                        except PhoXiError as e:
                            response = f"NOK:{e}"

                elif cmd == "ANALYZE":
                    if device is None:
                        response = "NOK:No active calibration"
                    else:
                        try:
                            score = device.analyze()
                            response = f"OK, area occupancy score: {score:.6f}"
                            print(f"Analysis OK, occupancy score: {score:.6f}")
                        except PhoXiError as e:
                            response = f"NOK:{e}"

                elif cmd == "PATCH":
                    if device is None:
                        response = "NOK:No active calibration"
                    else:
                        try:
                            device.patch()
                            response = "OK"
                            print("Patch applied successfully.")
                            # Patch automatically disconnects the device
                            device = None
                        except PhoXiError as e:
                            response = f"NOK:{e}"

                elif cmd == "STOP_CALIBRATION":
                    if device is not None:
                        device = cleanup_device(device)
                    response = "OK"
                    print("Calibration stopped.")

                else:
                    response = f"NOK:Unknown command '{cmd}'"

                # Send response
                conn.sendall((response + "\n").encode("utf-8"))
                print(f"Sent: {response}")

            except socket.timeout:
                # No data, but connection still alive – continue
                continue
            except ConnectionResetError:
                print("Client reset the connection.")
                break
            except Exception as e:
                print(f"Unexpected error in client loop: {e}")
                break

    finally:
        # Ensure device is cleaned up when this client disconnects
        cleanup_device(device)
        conn.close()
        print("Connection closed and device released.")


def main():
    print("=" * 60)
    print("  Photoneo Maintenance Tool Server (Robot client control)")
    print("=" * 60)

    mt = MaintenanceTool()
    server_socket = None

    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((SERVER_HOST, SERVER_PORT))
        server_socket.listen(5)   # allow backlog
        print(f"Server listening on {SERVER_HOST}:{SERVER_PORT}")
        print("Waiting for robot clients (Ctrl+C to stop)...")

        while True:
            conn, addr = server_socket.accept()
            handle_client(conn, addr, mt)

    except KeyboardInterrupt:
        print("\nServer stopped by user.")
    except Exception as e:
        print(f"Fatal server error: {e}")
        return 1
    finally:
        if server_socket:
            server_socket.close()
        print("Server shutdown complete.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
