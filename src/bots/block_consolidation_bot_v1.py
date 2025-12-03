#!/usr/bin/env python3
"""
Block Consolidation Bot V1

Converts 2,367 messages into 300-400 conversation blocks using semantic segmentation.
Phase 1 implementation: semantic similarity + time gaps + basic metadata.

This is the hourly bot that runs during the day to create preliminary blocks.
"""

import json
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import uuid
import sys

# Configuration
HISTORY_FILE = Path("C:/Users/user/ShearwaterAICAD/conversation_logs/current_session.jsonl")
OUTPUT_FILE = Path("C:/Users/user/ShearwaterAICAD/conversation_logs/blocks_index_v1.jsonl")

# Algorithm parameters (from research)
SIMILARITY_THRESHOLD = 0.6  # Research-backed moderate threshold
TIME_THRESHOLD = 900  # 15 minutes in seconds
MIN_BLOCK_SIZE = 5  # From TreeSeg paper
WINDOW_SIZE = 6  # Sliding window for embedding context

class BlockConsolidationBot:
    """V1 Bot: Basic semantic + time-based segmentation"""

    def __init__(self):
        self.model = None
        self.messages = []
        self.embeddings = None
        self.boundaries = []
        self.blocks = []

    def load_model(self):
        """Load sentence-transformers model"""
        print("[MODEL] Loading sentence-transformers/all-MiniLM-L6-v2...")
        try:
            self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
            print("[MODEL] ✓ Model loaded successfully")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to load model: {e}")
            return False

    def load_messages(self):
        """Load all messages from current_session.jsonl"""
        if not HISTORY_FILE.exists():
            print(f"[ERROR] {HISTORY_FILE} not found")
            return False

        print(f"[LOAD] Reading {HISTORY_FILE}...")
        count = 0
        errors = 0

        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    msg = json.loads(line.strip())
                    self.messages.append(msg)
                    count += 1
                except json.JSONDecodeError as e:
                    errors += 1
                    if errors <= 5:  # Only log first 5 errors
                        print(f"[WARN] Line {line_num}: Skipping invalid JSON")

        print(f"[LOAD] ✓ Loaded {count} messages ({errors} errors skipped)")
        return len(self.messages) > 0

    def get_message_text(self, msg, max_length=500):
        """Extract and normalize text from message"""
        try:
            if 'Message' in msg:
                content = msg['Message']
                if isinstance(content, str):
                    try:
                        content_dict = json.loads(content)
                        text = content_dict.get('message', str(content_dict))
                    except:
                        text = content
                else:
                    text = str(content)
            else:
                text = ""

            # Normalize: remove newlines, extra spaces
            text = ' '.join(text.split())[:max_length]
            return text if text else "[empty message]"

        except Exception as e:
            return "[error extracting text]"

    def parse_timestamp(self, msg):
        """Parse timestamp from message, handle multiple formats"""
        timestamp_str = msg.get('Timestamp', '')

        if not timestamp_str:
            return datetime.now()

        try:
            # Try common formats
            for fmt in ['%Y-%m-%dT%H:%M:%S.%fZ', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S']:
                try:
                    ts_clean = timestamp_str.rstrip('Z')
                    return datetime.strptime(ts_clean, fmt)
                except:
                    continue

            # Fallback
            print(f"[WARN] Could not parse timestamp: {timestamp_str}")
            return datetime.now()

        except Exception as e:
            print(f"[ERROR] Timestamp parsing failed: {e}")
            return datetime.now()

    def generate_embeddings(self):
        """Generate embeddings for all messages"""
        if not self.messages:
            print("[ERROR] No messages to embed")
            return False

        print(f"[EMBEDDING] Generating embeddings for {len(self.messages)} messages...")

        try:
            texts = [self.get_message_text(msg) for msg in self.messages]
            self.embeddings = self.model.encode(texts, show_progress_bar=True)
            print(f"[EMBEDDING] ✓ Generated {len(self.embeddings)} embeddings")
            return True

        except Exception as e:
            print(f"[ERROR] Embedding generation failed: {e}")
            return False

    def detect_boundaries(self):
        """Detect conversation boundaries using semantic similarity + time"""
        print("[BOUNDARY] Detecting boundaries...")

        if len(self.messages) < 2:
            print("[ERROR] Need at least 2 messages")
            return False

        self.boundaries = [0]  # Always start with first message
        changes_detected = 0

        for i in range(len(self.messages) - 1):
            msg_current = self.messages[i]
            msg_next = self.messages[i + 1]

            # Get timestamps
            time_current = self.parse_timestamp(msg_current)
            time_next = self.parse_timestamp(msg_next)
            time_gap = (time_next - time_current).total_seconds()

            # Check time gap first (strong signal)
            if time_gap > TIME_THRESHOLD:
                self.boundaries.append(i + 1)
                changes_detected += 1
                continue

            # Check semantic similarity
            try:
                similarity = cosine_similarity(
                    [self.embeddings[i]],
                    [self.embeddings[i + 1]]
                )[0][0]

                if similarity < SIMILARITY_THRESHOLD:
                    self.boundaries.append(i + 1)
                    changes_detected += 1

            except Exception as e:
                print(f"[WARN] Similarity computation failed at message {i}: {e}")
                continue

        self.boundaries.append(len(self.messages))  # Always end with last message

        print(f"[BOUNDARY] ✓ Detected {len(self.boundaries) - 1} boundaries ({changes_detected} changes)")
        return True

    def create_blocks(self):
        """Create block objects from boundaries"""
        print("[BLOCKS] Creating block objects...")

        if not self.boundaries:
            print("[ERROR] No boundaries detected")
            return False

        blocks_created = 0
        blocks_skipped = 0

        for i in range(len(self.boundaries) - 1):
            start_idx = self.boundaries[i]
            end_idx = self.boundaries[i + 1]

            # Skip tiny blocks
            if (end_idx - start_idx) < MIN_BLOCK_SIZE:
                blocks_skipped += 1
                continue

            try:
                block_messages = self.messages[start_idx:end_idx]

                # Extract timestamps
                timestamp_start = self.parse_timestamp(block_messages[0])
                timestamp_end = self.parse_timestamp(block_messages[-1])
                duration_seconds = (timestamp_end - timestamp_start).total_seconds()
                duration_minutes = duration_seconds / 60 if duration_seconds > 0 else 0

                # Extract metadata
                speakers = list(set(
                    msg.get('Sender', 'Unknown') for msg in block_messages
                    if msg.get('Sender')
                ))

                chains = list(set(
                    msg.get('chain_type', 'unknown') for msg in block_messages
                    if msg.get('chain_type')
                ))

                tiers = list(set(
                    msg.get('ace_tier', 'E') for msg in block_messages
                    if msg.get('ace_tier')
                ))

                # Primary chain and tier (most common)
                primary_chain = max(set(msg.get('chain_type', 'system_architecture')
                                       for msg in block_messages),
                                   key=list(msg.get('chain_type', 'system_architecture')
                                           for msg in block_messages).count)
                primary_tier = max(set(msg.get('ace_tier', 'E') for msg in block_messages),
                                  key=list(msg.get('ace_tier', 'E')
                                          for msg in block_messages).count)

                # Create block object
                block = {
                    'block_id': f"block_{datetime.utcnow().strftime('%Y%m%d')}_{len(self.blocks):04d}",
                    'timestamp_start': timestamp_start.isoformat() + 'Z',
                    'timestamp_end': timestamp_end.isoformat() + 'Z',
                    'duration_minutes': round(duration_minutes, 1),
                    'message_count': len(block_messages),
                    'message_indices': list(range(start_idx, end_idx)),
                    'speakers': speakers,
                    'primary_chain': primary_chain,
                    'secondary_chains': [c for c in chains if c != primary_chain],
                    'primary_tier': primary_tier,
                    'secondary_tiers': [t for t in tiers if t != primary_tier],
                    'keywords': self._extract_keywords(block_messages),
                    'summary': '[Summary pending - requires BART model]',
                    'confidence': self._compute_confidence(start_idx, end_idx),
                    'algorithm_version': '1.0',
                    'source': 'bot'
                }

                self.blocks.append(block)
                blocks_created += 1

            except Exception as e:
                print(f"[WARN] Block creation failed at boundary {i}: {e}")
                continue

        print(f"[BLOCKS] ✓ Created {blocks_created} blocks ({blocks_skipped} tiny blocks skipped)")
        return len(self.blocks) > 0

    def _extract_keywords(self, messages):
        """Extract keywords from block messages"""
        all_keywords = set()
        keyword_dict = {
            'photo_capture': ['photo', 'image', 'camera', 'capture', 'upload'],
            'reconstruction': ['nerf', 'gaussian', 'mesh', '3d', 'model', 'reconstruction'],
            'quality_assessment': ['quality', 'f1 score', 'artifacts', 'accuracy', 'validation'],
            'token_optimization': ['token', 'cost', 'optimization', 'efficiency', 'budget'],
            'system_architecture': ['architecture', 'design', 'framework', 'pattern'],
        }

        text = ' '.join(self.get_message_text(msg).lower() for msg in messages)

        for category, keywords in keyword_dict.items():
            for kw in keywords:
                if kw in text:
                    all_keywords.add(kw)

        return list(all_keywords)[:5]

    def _compute_confidence(self, start_idx, end_idx):
        """Compute confidence score for a block"""
        # Simple: based on average similarity within block
        if end_idx - start_idx < 2:
            return 0.5

        try:
            similarities = []
            for i in range(start_idx, end_idx - 1):
                sim = cosine_similarity(
                    [self.embeddings[i]],
                    [self.embeddings[i + 1]]
                )[0][0]
                similarities.append(sim)

            avg_similarity = np.mean(similarities) if similarities else 0.5
            # Confidence: higher similarity = more confident
            confidence = min(0.95, 0.5 + (avg_similarity * 0.5))
            return round(confidence, 2)

        except:
            return 0.75

    def save_blocks(self):
        """Save blocks to JSONL format"""
        print(f"[SAVE] Writing {len(self.blocks)} blocks to {OUTPUT_FILE}...")

        try:
            # Create directory if needed
            OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

            with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                for block in self.blocks:
                    f.write(json.dumps(block, ensure_ascii=False) + '\n')
                    f.flush()

            print(f"[SAVE] ✓ Blocks saved successfully")
            return True

        except Exception as e:
            print(f"[ERROR] Failed to save blocks: {e}")
            return False

    def print_summary(self):
        """Print summary statistics"""
        print("\n" + "=" * 80)
        print("[SUMMARY] Block Consolidation Bot V1 Complete")
        print("=" * 80)
        print(f"Input messages:     {len(self.messages)}")
        print(f"Output blocks:      {len(self.blocks)}")
        print(f"Compression ratio:  {len(self.messages) / len(self.blocks):.1f}:1")
        print(f"Average block size: {len(self.messages) / len(self.blocks):.0f} messages")

        if self.blocks:
            durations = [b['duration_minutes'] for b in self.blocks]
            print(f"Block duration:     min={min(durations):.1f}m, max={max(durations):.1f}m, avg={np.mean(durations):.1f}m")
            confidences = [b['confidence'] for b in self.blocks]
            print(f"Confidence:         avg={np.mean(confidences):.2f}")

        print(f"\nOutput file: {OUTPUT_FILE}")
        print("=" * 80 + "\n")

    def run(self):
        """Execute full pipeline"""
        print("\n" + "=" * 80)
        print("[START] Block Consolidation Bot V1")
        print("[TIME]  " + datetime.utcnow().isoformat() + "Z")
        print("=" * 80 + "\n")

        # Step 1: Load model
        if not self.load_model():
            return False

        # Step 2: Load messages
        if not self.load_messages():
            return False

        # Step 3: Generate embeddings
        if not self.generate_embeddings():
            return False

        # Step 4: Detect boundaries
        if not self.detect_boundaries():
            return False

        # Step 5: Create blocks
        if not self.create_blocks():
            return False

        # Step 6: Save blocks
        if not self.save_blocks():
            return False

        # Step 7: Print summary
        self.print_summary()

        return True


def main():
    """Main entry point"""
    bot = BlockConsolidationBot()
    success = bot.run()
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
