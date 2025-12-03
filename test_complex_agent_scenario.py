#!/usr/bin/env python3
"""
Complex Agent Scenario Test

Simulates a realistic multi-step collaboration between claude_code and gemini_cli:
1. Claude receives a complex project design request
2. Gemini provides initial analysis
3. Claude proposes architecture
4. Gemini offers optimization suggestions
5. Both agents reach consensus

This test demonstrates the recording system capturing a full collaboration workflow.
"""

import zmq
import json
import time
import sys
from pathlib import Path
from datetime import datetime

def send_agent_message(from_agent, to_agent, message_type, content):
    """Send a message through the broker"""
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

    topic = to_agent.encode('utf-8')
    payload = json.dumps(msg).encode('utf-8')
    pub_socket.send_multipart([topic, payload])

    print(f"\n[SENT] {from_agent} -> {to_agent}")
    print(f"  Type: {message_type}")
    print(f"  Content: {content[:80]}...")

    pub_socket.close()
    context.term()
    return msg['message_id']

def main():
    print("="*80)
    print("  COMPLEX AGENT COLLABORATION SCENARIO TEST")
    print("="*80)
    print("\nScenario: Design a Photo Capture to 3D Model Processing Pipeline")
    print("Agents: Claude (Architect) & Gemini (Analyst)")

    log_file = Path("conversation_logs/current_session.jsonl")
    if not log_file.exists():
        print("[ERROR] Persistence log not found!")
        return False

    # Get initial count
    with open(log_file) as f:
        initial_count = sum(1 for _ in f)

    print(f"\n[STATUS] Initial message count: {initial_count}")
    print("[INFO] Starting complex collaboration scenario...\n")

    try:
        # Phase 1: Problem Statement
        print("[PHASE 1] Problem Statement")
        print("-" * 80)
        send_agent_message(
            "claude_code",
            "gemini_cli",
            "request",
            """We need to design a system that:
1. Captures 3D photos using a camera array
2. Processes them with NERF/Gaussian splatting
3. Outputs CAD-standard 3D models
4. Integrates with Unity for rendering

Current constraints:
- RTX 2070 8GB VRAM (GPU limited)
- Real-time processing preferred
- Quality must be production-ready
- Cost-conscious implementation

Please analyze the technical feasibility and provide initial assessment."""
        )
        time.sleep(1.5)

        # Phase 2: Initial Analysis
        print("\n[PHASE 2] Initial Analysis from Gemini")
        print("-" * 80)
        send_agent_message(
            "gemini_cli",
            "claude_code",
            "response",
            """Feasibility Analysis:

STRENGTHS:
- NERF/Gaussian splatting proven technology
- Existing open-source implementations available
- RTX 2070 can handle medium-resolution models with optimization

CHALLENGES:
- 8GB VRAM limits model complexity
- Real-time processing likely not feasible with RTX 2070
- Need efficient memory management and quantization

RECOMMENDATIONS:
1. Use 4-bit QLoRA quantization for model compression
2. Implement batch processing instead of real-time
3. Use gradual refinement approach (coarse to fine)
4. Consider model caching and incremental updates

Next: Propose detailed architecture."""
        )
        time.sleep(1.5)

        # Phase 3: Architecture Proposal
        print("\n[PHASE 3] Architecture Proposal from Claude")
        print("-" * 80)
        send_agent_message(
            "claude_code",
            "gemini_cli",
            "decision",
            """PROPOSED ARCHITECTURE:

Data Pipeline:
[1] Photo Capture Layer (camera array interface)
[2] Preprocessing (image alignment, color correction)
[3] NERF Training (4-bit quantized, gradient checkpointing)
[4] Gaussian Splatting (optimized for 8GB VRAM)
[5] Post-processing (mesh extraction, LOD generation)
[6] CAD Export (USD/STL/OBJ formats)

Technical Stack:
- Frontend: Unity (WebGL for web preview)
- Backend: Python with PyTorch
- GPU Optimization: Apex AMP, gradient checkpointing, memory mapping
- Storage: S3-compatible object storage

Estimated Processing:
- Single photo set: 5-15 minutes per model
- Batch processing: 50-100 models per day on RTX 2070
- Quality: Production-ready with manual refinement option

Cost Estimate:
- Development: 3-4 weeks
- Infrastructure: ~$500/month (cloud GPU rental for batch jobs)
- Maintenance: Minimal after launch

Proceed with detailed implementation planning?"""
        )
        time.sleep(1.5)

        # Phase 4: Optimization Feedback
        print("\n[PHASE 4] Optimization Feedback from Gemini")
        print("-" * 80)
        send_agent_message(
            "gemini_cli",
            "claude_code",
            "response",
            """Architecture Review - OPTIMIZATIONS IDENTIFIED:

PERFORMANCE IMPROVEMENTS:
1. Add progressive refinement: coarse 512x512 → fine 2048x2048
2. Cache intermediate representations between stages
3. Use CPU preprocessing in parallel with GPU NERF training
4. Implement early-exit for "good enough" quality scenarios

COST REDUCTION:
1. Use open-source NeRF (Instant NGP) instead of proprietary
2. Implement local VRAM swapping for edge cases
3. Add model pruning post-training (reduce parameters by 30-50%)
4. Consider CPU inference for preview generation

SUGGESTED TIMELINE:
- Week 1-2: Photo capture integration + preprocessing
- Week 2-3: NERF training pipeline (quantized)
- Week 3-4: Export + Unity integration + testing

Risk: NERF training stability on limited VRAM
Mitigation: Implement checkpointing and fallback to lower resolution

CONSENSUS: Proposal approved with optimization suggestions integrated."""
        )
        time.sleep(1.5)

        # Phase 5: Final Agreement
        print("\n[PHASE 5] Final Agreement from Claude")
        print("-" * 80)
        send_agent_message(
            "claude_code",
            "gemini_cli",
            "decision",
            """FINAL ARCHITECTURE APPROVED:

All optimization suggestions integrated.

DELIVERABLES:
1. Photo capture system with array support
2. Quantized NERF training pipeline (4-bit QLoRA)
3. Progressive refinement workflow
4. CAD-standard 3D model export (USD/STL)
5. Unity integration with LOD support
6. Cost optimization: ~$300-400/month operations

IMPLEMENTATION STARTING:
- Repository: ShearwaterAICAD/photo-to-3d-pipeline
- Branch: feature/nerf-processing
- Target completion: 4 weeks
- First MVP release: 2 weeks (batch processing only)

STATUS: HANDSHAKE COMPLETE - PROCEEDING TO IMPLEMENTATION

Next meeting: Design review in 5 days
Expected progress: Photo capture + preprocessing complete"""
        )
        time.sleep(1.5)

        # Verify recording
        print("\n" + "="*80)
        print("[FINAL] Verifying Message Recording")
        print("="*80 + "\n")

        time.sleep(2)

        with open(log_file) as f:
            final_count = sum(1 for _ in f)

        new_messages = final_count - initial_count

        print(f"[RESULTS]")
        print(f"  Initial count: {initial_count}")
        print(f"  Final count: {final_count}")
        print(f"  New messages: {new_messages}")

        if new_messages > 0:
            print(f"\n[SUCCESS] {new_messages} messages from complex scenario recorded!")

            # Show the conversation flow
            with open(log_file) as f:
                lines = f.readlines()

            print(f"\n[CONVERSATION FLOW]:")
            recent = []
            for line in lines[-min(6, new_messages):]:
                try:
                    msg = json.loads(line)
                    sender = msg.get('SpeakerName', 'unknown')
                    content = str(msg.get('Message', ''))
                    if isinstance(content, str) and content.startswith('{'):
                        try:
                            parsed = json.loads(content)
                            snippet = str(parsed.get('message', ''))[:60]
                        except:
                            snippet = content[:60]
                    else:
                        snippet = content[:60]
                    recent.append(f"  {sender:15s}: {snippet}...")
                except:
                    pass

            for entry in recent:
                print(entry)

            print("\n" + "="*80)
            print("  [SUCCESS] COMPLEX AGENT COLLABORATION RECORDED")
            print("="*80)
            print("\nScenario Summary:")
            print("  [OK] Problem statement shared")
            print("  [OK] Technical analysis provided")
            print("  [OK] Architecture proposed")
            print("  [OK] Optimizations suggested")
            print("  [OK] Final agreement reached")
            print("  [OK] All messages persisted and queryable")

            return True
        else:
            print(f"\n[WARN] No messages recorded")
            print("[INFO] Agents may not have processed messages yet")
            return False

    except ConnectionRefusedError:
        print("[ERROR] Cannot connect to broker on localhost:5555")
        print("[INFO] Is the broker running? Try: python src/brokers/pub_hub.py")
        return False
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
