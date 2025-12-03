#!/usr/bin/env python3
"""
Persistence Launcher - Auto-starts persistence when agent connects

This is the entry point that:
1. Detects when an agent (Claude/Gemini) connects to the project
2. Starts persistence daemon in background
3. Shows interactive checkpoint menu
4. Returns control to agent
"""

import subprocess
import time
import sys
import os
from pathlib import Path
from persistence_cli import PersistenceCLI
import logging

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] {%(levelname)s} - %(message)s'
)
logger = logging.getLogger('persistence_launcher')
logger.addHandler(logging.StreamHandler())


class PersistenceLauncher:
    """Manages persistence service lifecycle"""

    def __init__(self):
        self.daemon_process = None
        self.cli = PersistenceCLI()

    def on_agent_connected(self, agent_name: str = "agent"):
        """Called when agent connects to project"""
        print("\n" + "=" * 70)
        print(f"  PERSISTENCE SYSTEM DETECTED")
        print("=" * 70)

        logger.info(f"Agent '{agent_name}' connected to project")

        # 1. Start persistence daemon in background
        if self._start_daemon():
            logger.info("Persistence daemon started successfully")

            # Give daemon time to initialize
            time.sleep(1)

            # 2. Show checkpoint menu to user
            logger.info("Showing checkpoint selection menu")
            self._show_checkpoint_menu()
        else:
            logger.error("Failed to start persistence daemon")
            print("  [!] Warning: Persistence daemon failed to start")
            print("      Continuing without persistence...\n")

        print("=" * 70)
        logger.info("Persistence launcher returning control to agent")

    def _start_daemon(self) -> bool:
        """Start persistence daemon as background subprocess"""
        print("--- in _start_daemon ---")
        logger.info("Attempting to start persistence daemon...")
        try:
            # Change to src directory
            src_path = Path(__file__).parent
            logger.info(f"Launcher CWD: {os.getcwd()}")
            logger.info(f"Daemon CWD: {src_path}")
            logger.info(f"Python executable: {sys.executable}")

            # Start daemon
            self.daemon_process = subprocess.Popen(
                [sys.executable, "-m", "persistence.persistence_daemon"],
                cwd=src_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
            )

            logger.info(f"Persistence daemon started (PID: {self.daemon_process.pid})")
            return True

        except Exception as e:
            logger.error(f"Failed to start persistence daemon: {e}")
            # Log stdout and stderr for debugging
            if self.daemon_process:
                stdout, stderr = self.daemon_process.communicate()
                logger.error(f"Daemon stdout: {stdout.decode()}")
                logger.error(f"Daemon stderr: {stderr.decode()}")
            return False

    def _show_checkpoint_menu(self):
        """Show interactive checkpoint selection menu"""
        print()
        self.cli.show_main_menu()

    def on_agent_disconnected(self):
        """Called when agent disconnects"""
        logger.info("Agent disconnected")

        # Create emergency checkpoint
        print("\n  Saving session checkpoint...")
        try:
            self.cli.checkpoint_store.checkpoint_store.create_checkpoint(
                "session_end_snapshot"
            )
            logger.info("Emergency checkpoint created")
        except Exception as e:
            logger.error(f"Failed to create checkpoint: {e}")

        # Gracefully stop daemon
        self._stop_daemon()

    def _stop_daemon(self):
        """Gracefully stop persistence daemon"""
        if self.daemon_process:
            try:
                logger.info(f"Stopping persistence daemon (PID: {self.daemon_process.pid})")

                # Send termination signal
                if os.name == 'nt':
                    # Windows
                    self.daemon_process.terminate()
                else:
                    # Unix
                    os.kill(self.daemon_process.pid, 15)  # SIGTERM

                # Wait for graceful shutdown
                self.daemon_process.wait(timeout=5)
                logger.info("Persistence daemon stopped gracefully")

            except subprocess.TimeoutExpired:
                logger.warning("Daemon did not stop gracefully, forcing...")
                self.daemon_process.kill()
                self.daemon_process.wait()
            except Exception as e:
                logger.error(f"Error stopping daemon: {e}")


def main():
    """
    Entry point - automatically called when agent starts

    Can be used two ways:
    1. Direct: python persistence.py (starts launcher)
    2. From agent: launcher.on_agent_connected()
    """
    launcher = PersistenceLauncher()

    try:
        # Auto-detect agent
        agent_name = sys.argv[1] if len(sys.argv) > 1 else "agent"

        # Start persistence
        launcher.on_agent_connected(agent_name)

        # Keep launcher running in background
        # Daemon continues in background
        # Agent continues execution

        return launcher

    except KeyboardInterrupt:
        print("\n\n  [!] Interrupted")
        launcher.on_agent_disconnected()
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
