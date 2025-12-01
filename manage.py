import argparse
import os
import subprocess
import time
from dotenv import load_dotenv # Add load_dotenv

# Load environment variables early
load_dotenv()

SERVICES = {
    "broker": {
        "command": ["python", "-m", "brokers.pub_hub"],
        "cwd": "src",
        "pid": None,
    },
    "persistence_daemon": {
        "command": ["python", "-m", "persistence.persistence_daemon"],
        "cwd": "src",
        "pid": None,
    },
    # "bff": {
    #     "command": ["python", "-m", "uvicorn", "bff.main:app", "--host", "0.0.0.0", "--port", "8000"],
    #     "cwd": "src",
    #     "pid": None,
    # },
    "claude_client": {
        "command": ["python", "-m", "monitors.claude_client"],
        "cwd": "src",
        "pid": None,
    },
    "gemini_client": {
        "command": ["python", "-m", "monitors.gemini_client"],
        "cwd": "src",
        "pid": None,
    },
}

PID_FILE_DIR = "C:/Users/user/.gemini/tmp/70c2ccb1a3fa29727b06715e8ec63ce30494f3f0ac421de7b8bd38a4c973039a/pids"
os.makedirs(PID_FILE_DIR, exist_ok=True)

def get_pid_file(service_name):
    """Returns the path to the PID file for a given service."""
    return os.path.join(PID_FILE_DIR, f"{service_name}.pid")

def start_services(args):
    """Starts all defined services as background processes."""
    print("Starting Synaptic Core services...")
    
    # CRITICAL SECURITY RISK: Keys are hardcoded due to .env loading issues.
    # DO NOT COMMIT THIS FILE TO VERSION CONTROL.
    claude_api_key = "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"
    gemini_api_key = "AIzaSyBjDGtyntnQrMxPLZNiIGe3nZ6urQeb63s" # Replace with your actual key

    # Validate that keys exist before starting services
    if not claude_api_key or "YOUR_CLAUDE_API_KEY" in claude_api_key:
        print("\nERROR: ANTHROPIC_API_KEY is not set in manage.py. Cannot start claude_client.")
        return
    if not gemini_api_key or "YOUR_GOOGLE_API_KEY" in gemini_api_key:
        print("\nERROR: GOOGLE_API_KEY is not set in manage.py. Cannot start gemini_client.")
        return
        
    # Update command with API keys, num_messages, and model names before launching
    SERVICES["claude_client"]["command"].extend(["--api-key", claude_api_key, "--model-name", args.claude_model])
    SERVICES["gemini_client"]["command"].extend(["--api-key", gemini_api_key, "--num-messages", str(args.num_messages), "--model-name", args.gemini_model])

    for name, config in SERVICES.items():
        pid_file = get_pid_file(name)
        if os.path.exists(pid_file):
            print(f"- {name} is already running.")
            continue
        try:
            # Use Popen to run services in the background
            process = subprocess.Popen(config["command"], cwd=config["cwd"])
            config["pid"] = process.pid
            with open(pid_file, "w") as f:
                f.write(str(process.pid))
            print(f"- Started {name} (PID: {process.pid})")
            # Give persistence daemon extra time to initialize
            if name == "persistence_daemon":
                time.sleep(2)
            else:
                time.sleep(1)  # Stagger launches to make logs more readable
        except Exception as e:
            print(f"Error starting {name}: {e}")
    print("\nAll services launched.")

def stop_services(args):
    """Stops all running services."""
    print("Stopping Synaptic Mesh services...")
    for name in SERVICES.keys():
        pid_file = get_pid_file(name)
        if not os.path.exists(pid_file):
            print(f"- {name} is not running.")
            continue
        try:
            with open(pid_file, "r") as f:
                pid = int(f.read().strip())
            
            # Use taskkill on Windows to forcefully terminate the process
            subprocess.run(["taskkill", "/F", "/PID", str(pid)], check=True, capture_output=True)
            print(f"- Stopped {name} (PID: {pid})")
            
            os.remove(pid_file)
        except FileNotFoundError:
             print(f"- {name} is not running (PID file not found).")
        except (ValueError, subprocess.CalledProcessError) as e:
            # This can happen if the process is already gone but the pid file remains
            print(f"- Could not stop {name}. It may have already terminated.")
            if os.path.exists(pid_file):
                os.remove(pid_file) # Clean up stale PID file
        except Exception as e:
            print(f"Error stopping {name}: {e}")

    # Optional: A final check to ensure all known python processes are gone if needed
    # This is aggressive and should be used with caution
    subprocess.run(["taskkill", "/F", "/IM", "python.exe"], capture_output=True)
    print("Force-stopped any remaining Python processes.")


def status_services(args):
    """Checks the status of all services."""
    print("Checking status of Synaptic Mesh services...")
    for name in SERVICES.keys():
        pid_file = get_pid_file(name)
        if os.path.exists(pid_file):
            try:
                with open(pid_file, "r") as f:
                    pid = f.read().strip()
                # Simple check if pid file exists. A more robust check would
                # query the OS to see if the process is actually running.
                print(f"- {name}: Running (PID: {pid})")
            except Exception as e:
                print(f"- {name}: Status unknown ({e})")
        else:
            print(f"- {name}: Stopped")

def run_analytics(args):
    """Placeholder for running performance and data analysis."""
    print("Running analytics...")
    # Here we will add calls to the analytics and logging scripts.
    # For example:
    # from src.utilities import conversation_analytics_engine
    # conversation_analytics_engine.main()
    print("Analytics placeholder complete. Future implementation goes here.")


def main():
    """Main function to parse arguments and call the appropriate handler."""
    parser = argparse.ArgumentParser(description="ShearwaterAICAD Management Utility")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Start command
    start_parser = subparsers.add_parser("start", help="Start all services.")
    start_parser.add_argument("--num-messages", type=int, default=10, help="Number of recent messages for Gemini's context.")
    start_parser.add_argument("--gemini-model", type=str, default="gemini-pro", help="The Gemini model to use.")
    start_parser.add_argument("--claude-model", type=str, default="claude-3-haiku-20240307", help="The Claude model to use.")
    start_parser.set_defaults(func=start_services)

    # Stop command
    stop_parser = subparsers.add_parser("stop", help="Stop all services.")
    stop_parser.set_defaults(func=stop_services)

    # Status command
    status_parser = subparsers.add_parser("status", help="Check the status of all services.")
    status_parser.set_defaults(func=status_services)

    # Analytics command
    analytics_parser = subparsers.add_parser("run-analytics", help="Run data and performance analytics.")
    analytics_parser.set_defaults(func=run_analytics)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
