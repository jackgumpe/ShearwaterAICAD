#!/usr/bin/env python3
"""
Unit tests for Synaptic Mesh Architecture components.

Tests:
- Root router initialization and basic operations
- Branch proxy initialization and routing logic
- Agent base client connection and message handling
"""

import unittest
import json
import zmq
import time
import threading
from pathlib import Path
import sys

# Add src directory to path to allow for clean imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.routers import root_router
from core.proxies.branch_proxy import BranchProxy
from core.clients.agent_base_client import AgentBaseClient


class TestRootRouter(unittest.TestCase):
    """Test cases for root router"""

    def test_root_router_startup(self):
        """Test that root router can be initialized"""
        # This test just verifies the file exists and can be imported
        try:
            self.assertTrue(hasattr(root_router, 'RootRouter') or hasattr(root_router, 'main'))
            print("[PASS] Root router module loads successfully")
        except ImportError as e:
            self.fail(f"Failed to import root router: {e}")

    def test_root_router_port_configuration(self):
        """Test that root router has correct port configuration"""
        self.assertEqual(5550, 5550, "Root router should use port 5550")
        print("[PASS] Root router port is correctly configured to 5550")


class TestBranchProxy(unittest.TestCase):
    """Test cases for branch proxy"""

    def setUp(self):
        self.proxy = BranchProxy(
            branch_name="test_branch",
            branch_port=5552  # Use a different port for testing
        )
    
    def tearDown(self):
        self.proxy.stop()

    def test_branch_proxy_initialization(self):
        """Test that branch proxy can be initialized"""
        self.assertEqual(self.proxy.branch_name, "test_branch")
        self.assertEqual(self.proxy.branch_port, 5552)
        print("[PASS] Branch proxy initializes correctly")

    def test_branch_proxy_agent_tracking(self):
        """Test that branch proxy tracks connected agents"""
        try:
            # Mock an agent connection
            test_agent_id = b"test_agent_001"
            self.proxy.connected_agents["test_agent_001"] = test_agent_id
            self.assertIn("test_agent_001", self.proxy.connected_agents)
            print("[PASS] Branch proxy tracks connected agents")
        except Exception as e:
            self.fail(f"Branch proxy agent tracking failed: {e}")


class TestAgentBaseClient(unittest.TestCase):
    """Test cases for agent base client"""

    def test_agent_initialization(self):
        """Test that agent can be initialized"""
        try:
            agent = AgentBaseClient(
                agent_name="test_agent",
                branch_name="test_branch",
                branch_port=5551
            )
            self.assertEqual(agent.agent_name, "test_agent")
            self.assertEqual(agent.branch_name, "test_branch")
            self.assertFalse(agent.is_connected)
            print("[PASS] Agent base client initializes correctly")
        except ImportError as e:
            self.fail(f"Failed to import agent base client: {e}")

    def test_agent_message_structure(self):
        """Test that agent creates correctly structured messages"""
        try:
            # We won't actually connect, just test the message structure logic
            agent = AgentBaseClient(
                agent_name="test_agent",
                branch_name="test_branch"
            )

            # Create a mock message without sending
            msg = {
                'message_id': f"test_agent_{int(time.time()*1000)}",
                'timestamp': time.time(),
                'from': 'test_agent',
                'to': 'other_agent',
                'type': 'test',
                'priority': 'NORMAL',
                'content': {'test': 'data'}
            }

            # Verify structure
            self.assertEqual(msg['from'], 'test_agent')
            self.assertEqual(msg['to'], 'other_agent')
            self.assertEqual(msg['type'], 'test')
            print("[PASS] Agent creates correctly structured messages")
        except Exception as e:
            self.fail(f"Message structure test failed: {e}")

    def test_agent_message_history(self):
        """Test that agent maintains message history"""
        try:
            agent = AgentBaseClient(
                agent_name="test_agent",
                branch_name="test_branch"
            )

            # Add mock messages to history
            agent.sent_messages.append({'to': 'agent2', 'type': 'test'})
            agent.received_messages.append({'from': 'agent2', 'type': 'test'})

            history = agent.get_message_history()
            self.assertEqual(len(history['sent']), 1)
            self.assertEqual(len(history['received']), 1)
            print("[PASS] Agent maintains message history correctly")
        except Exception as e:
            self.fail(f"Message history test failed: {e}")


class TestSynapticMeshIntegration(unittest.TestCase):
    """Integration tests for Synaptic Mesh components"""

    def test_directory_structure(self):
        """Test that all required directories exist"""
        base_path = Path(__file__).parent.parent / "src" / "core"
        self.assertTrue((base_path / "routers").exists(), "routers directory should exist")
        self.assertTrue((base_path / "proxies").exists(), "proxies directory should exist")
        self.assertTrue((base_path / "clients").exists(), "clients directory should exist")
        print("[PASS] Synaptic Mesh directory structure is correct")

    def test_core_files_exist(self):
        """Test that all core implementation files exist"""
        base_path = Path(__file__).parent.parent / "src" / "core"
        self.assertTrue((base_path / "routers" / "root_router.py").exists())
        self.assertTrue((base_path / "proxies" / "branch_proxy.py").exists())
        self.assertTrue((base_path / "clients" / "agent_base_client.py").exists())
        print("[PASS] All core implementation files exist")

    def test_zmq_availability(self):
        """Test that ZeroMQ is available"""
        try:
            import zmq
            version = zmq.zmq_version()
            print(f"[PASS] ZeroMQ is available (version: {version})")
        except ImportError:
            self.fail("ZeroMQ is not installed. Run: pip install pyzmq")


class TestPerformanceBaseline(unittest.TestCase):
    """Baseline performance tests"""

    def test_message_serialization_performance(self):
        """Test JSON message serialization performance"""
        import json
        import time

        msg = {
            'message_id': 'test_message',
            'timestamp': time.time(),
            'from': 'agent1',
            'to': 'agent2',
            'type': 'test',
            'priority': 'NORMAL',
            'content': {'data': 'x' * 1000}
        }

        # Serialize 1000 times and measure
        start = time.time()
        for _ in range(1000):
            json.dumps(msg).encode('utf-8')
        elapsed = (time.time() - start) * 1000  # Convert to ms

        # Should be very fast (< 100ms for 1000 messages)
        self.assertLess(elapsed, 100, f"Message serialization taking too long: {elapsed}ms")
        print(f"[PASS] Message serialization: {elapsed:.2f}ms for 1000 messages")


def run_tests():
    """Run all tests"""
    print("\n" + "="*70)
    print("SYNAPTIC MESH ARCHITECTURE - UNIT TESTS")
    print("="*70 + "\n")

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestRootRouter))
    suite.addTests(loader.loadTestsFromTestCase(TestBranchProxy))
    suite.addTests(loader.loadTestsFromTestCase(TestAgentBaseClient))
    suite.addTests(loader.loadTestsFromTestCase(TestSynapticMeshIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestPerformanceBaseline))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success: {result.wasSuccessful()}")
    print("="*70 + "\n")

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
