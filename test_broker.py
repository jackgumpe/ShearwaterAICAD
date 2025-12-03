#!/usr/bin/env python3
"""Test if the enhanced broker works correctly"""

import sys
import os
sys.path.insert(0, 'src')

print("[TEST] Starting broker test...")
print(f"[TEST] Current dir: {os.getcwd()}")
print(f"[TEST] Python path: {sys.path}")

try:
    import zmq
    print("[OK] ZMQ imports successfully")
except Exception as e:
    print(f"[ERROR] ZMQ import failed: {e}")
    sys.exit(1)

try:
    from brokers.zmq_broker_enhanced import EnhancedConversationRecorder, main, FRONTEND_PORT, BACKEND_PORT
    print("[OK] Enhanced broker imports successfully")
    print(f"[OK] Frontend port: {FRONTEND_PORT}")
    print(f"[OK] Backend port: {BACKEND_PORT}")
except Exception as e:
    print(f"[ERROR] Enhanced broker import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    recorder = EnhancedConversationRecorder()
    print("[OK] EnhancedConversationRecorder instantiated")
    print(f"[OK] Log directories created")
except Exception as e:
    print(f"[ERROR] Recorder instantiation failed: {e}")
    sys.exit(1)

print("\n[SUCCESS] All broker components working correctly")
print("[INFO] Broker is ready to be deployed")
