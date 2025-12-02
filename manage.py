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

    # Load API keys from environment variables (NOT hardcoded)
    claude_api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    gemini_api_key = os.getenv("GOOGLE_API_KEY", "").strip()

    # Validate that keys exist before starting services
    if not claude_api_key:
        print("\nERROR: ANTHROPIC_API_KEY not set in environment variables.")
        print("  Set it with: export ANTHROPIC_API_KEY='your-key-here'")
        print("  Or create a .env file with: ANTHROPIC_API_KEY=your-key-here")
        return
    if not gemini_api_key:
        print("\nERROR: GOOGLE_API_KEY not set in environment variables.")
        print("  Set it with: export GOOGLE_API_KEY='your-key-here'")
        print("  Or create a .env file with: GOOGLE_API_KEY=your-key-here")
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
    try:
        from src.utilities.conversation_analytics_engine import ConversationAnalytics
        analytics = ConversationAnalytics(
            defragmented_log_file="conversation_logs/defragmented_sessions.jsonl"
        )
        analytics.run()
    except ImportError:
        print("Could not import analytics engine. Make sure it's in src/utilities.")
    except Exception as e:
        print(f"An error occurred during analytics: {e}")

def run_defragmentation(args):
    """Runs the conversation defragmentation engine."""
    print("Running conversation defragmentation...")
    try:
        from src.utilities import defragmentation_engine
        engine = defragmentation_engine.DefragmentationEngine(
            raw_log_file="conversation_logs/current_session.jsonl",
            output_file="conversation_logs/defragmented_sessions.jsonl",
            min_messages=args.min_messages,
            min_duration=args.min_duration
        )
        engine.run()
        print("Defragmentation complete.")
    except ImportError:
        print("Could not import defragmentation engine. Make sure it's in src/utilities.")
    except Exception as e:
        print(f"An error occurred during defragmentation: {e}")


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

    # Defragment command
    defragment_parser = subparsers.add_parser("defragment", help="Reconstruct conversation threads from raw logs.")
    defragment_parser.add_argument("--min-messages", type=int, default=2, help="Minimum messages for a significant thread.")
    defragment_parser.add_argument("--min-duration", type=int, default=5, help="Minimum duration in seconds for a significant thread.")
    defragment_parser.set_defaults(func=run_defragmentation)

    # Superthread analysis command
    superthread_parser = subparsers.add_parser("create-superthreads", help="Cluster conversation threads into superthreads using NLP.")
    superthread_parser.add_argument("--num-threads", type=int, default=20, help="The target number of superthreads to create.")
    superthread_parser.set_defaults(func=run_superthread_analysis)

    args = parser.parse_args()
    args.func(args)
    
def run_superthread_analysis(args):
    """Runs the superthread analysis engine."""
    print("Running superthread analysis...")
    try:
        from src.utilities import superthread_analyzer
        analyzer = superthread_analyzer.SuperthreadAnalyzer(
            defragmented_file="conversation_logs/defragmented_sessions.parquet",
            output_file="conversation_logs/superthreads.json",
            n_superthreads=args.num_threads
        )
        analyzer.run()
        print("Superthread analysis complete.")
    except ImportError:
        print("Could not import superthread_analyzer. Make sure it's in src/utilities.")
    except Exception as e:
        print(f"An error occurred during superthread analysis: {e}")

if __name__ == "__main__":
    main()
