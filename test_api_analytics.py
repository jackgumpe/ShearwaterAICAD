#!/usr/bin/env python3
"""
API Analytics Test

Simulates agent communication and tracks:
1. Tokens used (Claude API vs Gemini API)
2. Bandwidth consumed (request/response sizes)
3. Latency metrics (message send time)
4. API call costs estimation
5. Data transfer statistics
"""

import zmq
import json
import time
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict


class APIAnalytics:
    """Track API usage metrics across agent communications"""

    def __init__(self):
        self.metrics = {
            'claude': {
                'api_calls': 0,
                'tokens_sent': 0,
                'tokens_received': 0,
                'total_tokens': 0,
                'bandwidth_sent': 0,  # bytes
                'bandwidth_received': 0,  # bytes
                'total_bandwidth': 0,
                'latencies': [],
                'estimated_cost': 0.0
            },
            'gemini': {
                'api_calls': 0,
                'tokens_sent': 0,
                'tokens_received': 0,
                'total_tokens': 0,
                'bandwidth_sent': 0,
                'bandwidth_received': 0,
                'total_bandwidth': 0,
                'latencies': [],
                'estimated_cost': 0.0
            }
        }
        # Pricing (as of 2024)
        self.pricing = {
            'claude': {
                'input_per_million': 3.00,      # $3 per 1M input tokens
                'output_per_million': 15.00      # $15 per 1M output tokens
            },
            'gemini': {
                'input_per_million': 0.075,      # $0.075 per 1M input tokens
                'output_per_million': 0.3        # $0.3 per 1M output tokens
            }
        }

    def estimate_tokens(self, text):
        """Rough estimation: ~1 token per 4 characters"""
        return max(1, len(text) // 4)

    def record_api_call(self, api_name, request_text, response_text, latency_ms):
        """Record metrics for an API call"""
        if api_name not in self.metrics:
            return

        m = self.metrics[api_name]

        # Count API calls
        m['api_calls'] += 1

        # Estimate tokens
        request_tokens = self.estimate_tokens(request_text)
        response_tokens = self.estimate_tokens(response_text)

        m['tokens_sent'] += request_tokens
        m['tokens_received'] += response_tokens
        m['total_tokens'] += request_tokens + response_tokens

        # Track bandwidth (in bytes)
        request_bytes = len(request_text.encode('utf-8'))
        response_bytes = len(response_text.encode('utf-8'))

        m['bandwidth_sent'] += request_bytes
        m['bandwidth_received'] += response_bytes
        m['total_bandwidth'] += request_bytes + response_bytes

        # Track latency
        m['latencies'].append(latency_ms)

        # Calculate cost
        input_cost = (m['tokens_sent'] / 1_000_000) * self.pricing[api_name]['input_per_million']
        output_cost = (m['tokens_received'] / 1_000_000) * self.pricing[api_name]['output_per_million']
        m['estimated_cost'] = input_cost + output_cost

    def get_summary(self):
        """Generate summary report"""
        summary = {
            'timestamp': datetime.now().isoformat(),
            'apis': {}
        }

        for api_name, metrics in self.metrics.items():
            avg_latency = sum(metrics['latencies']) / len(metrics['latencies']) if metrics['latencies'] else 0

            summary['apis'][api_name] = {
                'api_calls': metrics['api_calls'],
                'total_tokens': metrics['total_tokens'],
                'tokens_sent': metrics['tokens_sent'],
                'tokens_received': metrics['tokens_received'],
                'bandwidth': {
                    'sent_bytes': metrics['bandwidth_sent'],
                    'received_bytes': metrics['bandwidth_received'],
                    'total_bytes': metrics['total_bandwidth'],
                    'sent_mb': round(metrics['bandwidth_sent'] / (1024*1024), 4),
                    'received_mb': round(metrics['bandwidth_received'] / (1024*1024), 4),
                    'total_mb': round(metrics['total_bandwidth'] / (1024*1024), 4)
                },
                'latency': {
                    'avg_ms': round(avg_latency, 2),
                    'min_ms': round(min(metrics['latencies']), 2) if metrics['latencies'] else 0,
                    'max_ms': round(max(metrics['latencies']), 2) if metrics['latencies'] else 0,
                    'calls_measured': len(metrics['latencies'])
                },
                'cost': {
                    'estimated_usd': round(metrics['estimated_cost'], 4),
                    'input_tokens': metrics['tokens_sent'],
                    'output_tokens': metrics['tokens_received']
                }
            }

        # Aggregate totals
        total_calls = sum(m['api_calls'] for m in self.metrics.values())
        total_tokens = sum(m['total_tokens'] for m in self.metrics.values())
        total_bandwidth = sum(m['total_bandwidth'] for m in self.metrics.values())
        total_cost = sum(m['estimated_cost'] for m in self.metrics.values())

        summary['totals'] = {
            'api_calls': total_calls,
            'total_tokens': total_tokens,
            'total_bandwidth_bytes': total_bandwidth,
            'total_bandwidth_mb': round(total_bandwidth / (1024*1024), 4),
            'total_estimated_cost_usd': round(total_cost, 4)
        }

        return summary

    def print_report(self, summary):
        """Pretty print the analytics report"""
        print("\n" + "="*80)
        print("  API USAGE ANALYTICS REPORT")
        print("="*80)
        print(f"\nTimestamp: {summary['timestamp']}\n")

        for api_name, metrics in summary['apis'].items():
            print(f"[{api_name.upper()} API]")
            print(f"  API Calls Made: {metrics['api_calls']}")
            print(f"  Total Tokens: {metrics['total_tokens']:,}")
            print(f"    - Input tokens: {metrics['tokens_sent']:,}")
            print(f"    - Output tokens: {metrics['tokens_received']:,}")
            print(f"  Bandwidth:")
            print(f"    - Sent: {metrics['bandwidth']['sent_bytes']:,} bytes ({metrics['bandwidth']['sent_mb']} MB)")
            print(f"    - Received: {metrics['bandwidth']['received_bytes']:,} bytes ({metrics['bandwidth']['received_mb']} MB)")
            print(f"    - Total: {metrics['bandwidth']['total_bytes']:,} bytes ({metrics['bandwidth']['total_mb']} MB)")
            print(f"  Latency (Round-trip):")
            print(f"    - Average: {metrics['latency']['avg_ms']} ms")
            print(f"    - Min: {metrics['latency']['min_ms']} ms")
            print(f"    - Max: {metrics['latency']['max_ms']} ms")
            print(f"    - Samples: {metrics['latency']['calls_measured']}")
            print(f"  Estimated Cost: ${metrics['cost']['estimated_usd']}")
            print()

        totals = summary['totals']
        print("[TOTALS ACROSS ALL APIS]")
        print(f"  Total API Calls: {totals['api_calls']}")
        print(f"  Total Tokens Used: {totals['total_tokens']:,}")
        print(f"  Total Bandwidth: {totals['total_bandwidth_bytes']:,} bytes ({totals['total_bandwidth_mb']} MB)")
        print(f"  Total Estimated Cost: ${totals['total_estimated_cost_usd']}")
        print("\n" + "="*80)


def send_agent_message(from_agent, to_agent, message_type, content, analytics=None):
    """Send a message and track API usage"""
    context = zmq.Context()
    pub_socket = context.socket(zmq.PUB)
    pub_socket.connect("tcp://localhost:5555")
    time.sleep(0.1)

    msg = {
        'message_id': f"{from_agent}_{int(time.time()*1000)}",
        'timestamp': datetime.now().isoformat(),
        'from': from_agent,
        'to': to_agent,
        'type': message_type,
        'priority': 'HIGH',
        'content': {'message': content}
    }

    # Measure API call metrics
    api_name = 'claude' if from_agent == 'claude_code' else 'gemini'

    start_time = time.time()

    topic = to_agent.encode('utf-8')
    payload = json.dumps(msg).encode('utf-8')
    pub_socket.send_multipart([topic, payload])

    latency_ms = (time.time() - start_time) * 1000

    # Record metrics
    if analytics:
        analytics.record_api_call(
            api_name,
            json.dumps(msg),  # Request
            content,          # Response
            latency_ms
        )

    print(f"[SENT] {from_agent} -> {to_agent} ({api_name.upper()} API)")
    print(f"  Type: {message_type}")
    print(f"  Size: {len(content)} chars, ~{analytics.estimate_tokens(content) if analytics else 0} tokens")
    print(f"  Latency: {latency_ms:.2f}ms\n")

    pub_socket.close()
    context.term()
    return msg['message_id']


def main():
    print("="*80)
    print("  API ANALYTICS TEST - Agent Communication with Metrics")
    print("="*80)
    print("\nTracking: Tokens, Bandwidth, Latency, and Cost")

    analytics = APIAnalytics()

    log_file = Path("conversation_logs/current_session.jsonl")
    if not log_file.exists():
        print("[ERROR] Persistence log not found!")
        return False

    with open(log_file) as f:
        initial_count = sum(1 for _ in f)

    print(f"\n[STATUS] Initial message count: {initial_count}")
    print("[INFO] Starting API analytics scenario...\n")

    try:
        # Test 1: Simple Query-Response (Claude)
        print("[TEST 1] Simple Claude API Call")
        print("-" * 80)
        send_agent_message(
            "claude_code",
            "gemini_cli",
            "request",
            "What is the best approach to implement a caching strategy for a distributed system?",
            analytics
        )
        time.sleep(1)

        # Test 2: Detailed Analysis (Gemini)
        print("[TEST 2] Detailed Gemini API Response")
        print("-" * 80)
        send_agent_message(
            "gemini_cli",
            "claude_code",
            "response",
            """For a distributed caching strategy, consider:

1. Cache Invalidation Strategies:
   - TTL-based expiration (simple but wasteful)
   - Event-driven invalidation (complex but accurate)
   - Hybrid approach (best for most cases)

2. Data Consistency:
   - Eventual consistency (high performance, low accuracy)
   - Strong consistency (low performance, high accuracy)
   - Causal consistency (balanced approach)

3. Implementation Tools:
   - Redis (in-memory, fast)
   - Memcached (distributed, lightweight)
   - Apache Ignite (query-capable cache)

4. Bandwidth Optimization:
   - Compress cached data
   - Use binary protocols instead of JSON
   - Implement delta updates for large objects

5. Monitoring:
   - Cache hit ratio
   - Memory usage patterns
   - Network throughput
   - Query latency metrics

Recommendation: Use Redis with event-driven invalidation and monitoring""",
            analytics
        )
        time.sleep(1)

        # Test 3: Code Review Request (Claude)
        print("[TEST 3] Code Review Request via Claude API")
        print("-" * 80)
        send_agent_message(
            "claude_code",
            "gemini_cli",
            "request",
            """Please review this Python code for performance and security issues:

```python
def process_user_data(user_ids):
    results = []
    for uid in user_ids:
        user = db.query(User).filter(User.id == uid).first()
        if user:
            processed = transform_user_data(user)
            results.append(processed)
            cache.set(f"user_{uid}", processed, ttl=3600)
    return results
```

Focus on: N+1 queries, security vulnerabilities, caching effectiveness""",
            analytics
        )
        time.sleep(1)

        # Test 4: Extended Analysis (Gemini)
        print("[TEST 4] Extended Gemini API Analysis")
        print("-" * 80)
        send_agent_message(
            "gemini_cli",
            "claude_code",
            "response",
            """Code Review Results:

PERFORMANCE ISSUES (Critical):
1. N+1 Query Problem:
   - Loops making individual DB queries
   - Should use batch fetch: User.query.filter(User.id.in_(user_ids))
   - Performance impact: Linear with user count

2. Inefficient Caching:
   - Cache set happens synchronously (blocking)
   - Should use background task queue
   - TTL of 3600s may be too short for batch operations

SECURITY ISSUES (High):
1. SQL Injection Risk:
   - Not directly vulnerable due to ORM, but parameterization is good

2. Data Leakage:
   - Caching user data in plain text
   - Should encrypt sensitive fields
   - PII exposure in logs possible

3. Race Conditions:
   - Concurrent updates could cause cache staleness
   - Implement version-based cache validation

RECOMMENDATIONS:
1. Use batch queries with JOIN
2. Implement async caching with Celery/RQ
3. Add encryption for sensitive fields
4. Implement cache versioning
5. Add monitoring for cache hit rates
6. Use database connection pooling
7. Implement proper error handling

Estimated performance improvement: 10-50x faster for large user lists""",
            analytics
        )
        time.sleep(1)

        # Test 5: Decision (Claude)
        print("[TEST 5] Final Decision via Claude API")
        print("-" * 80)
        send_agent_message(
            "claude_code",
            "gemini_cli",
            "decision",
            """APPROVED: Implementing all recommendations.

Action Plan:
1. Refactor query logic to use batch operations (Week 1)
2. Add encryption layer for PII (Week 1)
3. Migrate caching to async with Celery (Week 2)
4. Implement monitoring and alerting (Week 2)
5. Load testing to verify 10x performance improvement (Week 3)

Budget: ~40 hours engineering time
Expected ROI: 50% reduction in database load""",
            analytics
        )
        time.sleep(2)

        # Verify recording and generate analytics
        print("\n" + "="*80)
        print("[FINAL] Verifying Recording and Generating Analytics")
        print("="*80 + "\n")

        with open(log_file) as f:
            final_count = sum(1 for _ in f)

        new_messages = final_count - initial_count

        print(f"[RESULTS]")
        print(f"  Initial message count: {initial_count}")
        print(f"  Final message count: {final_count}")
        print(f"  New messages recorded: {new_messages}")

        # Generate and display analytics report
        summary = analytics.get_summary()
        analytics.print_report(summary)

        # Save detailed report to file
        report_file = Path("reports/api_analytics_report.json")
        report_file.parent.mkdir(parents=True, exist_ok=True)

        with open(report_file, 'w') as f:
            json.dump(summary, f, indent=2)

        print(f"\n[INFO] Detailed report saved to: {report_file}")

        if new_messages > 0:
            print(f"\n[SUCCESS] Test completed!")
            print(f"  - {new_messages} messages recorded")
            print(f"  - API analytics captured")
            print(f"  - Cost analysis complete")
            return True
        else:
            print(f"\n[WARN] No new messages recorded")
            print("[INFO] Check if broker is running on localhost:5555")
            return False

    except ConnectionRefusedError:
        print("[ERROR] Cannot connect to broker on localhost:5555")
        print("[INFO] Start broker with: cd src && python -m brokers.pub_hub")
        return False
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
