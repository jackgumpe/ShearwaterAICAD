#!/usr/bin/env python3
"""
Defragmentation Engine for Conversation Analytics

This engine processes raw, fragmented message logs (JSONL) and reconstructs
them into coherent conversational threads based on ContextId and time-based sessioning.
"""

import json
from pathlib import Path
from datetime import datetime, timedelta, timezone
from collections import defaultdict
import logging
from typing import List, Dict, Any

try:
    import pyarrow as pa
    import pyarrow.parquet as pq
    import pandas as pd
    ARROW_SUPPORT = True
except ImportError:
    ARROW_SUPPORT = False

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] {%(levelname)s} - %(message)s'
)
logger = logging.getLogger('DefragmentationEngine')

class DefragmentationEngine:
    """
    Groups individual message events into logical sessions or threads.
    """

    def __init__(self, raw_log_file: str, output_file: str, min_messages: int = 2, min_duration: int = 5, max_session_gap_minutes: int = 5):
        self.raw_log_path = Path(raw_log_file)
        self.output_path = Path(output_file)
        self.parquet_output_path = self.output_path.with_suffix('.parquet') # New path for Parquet file
        self.max_session_gap = timedelta(minutes=max_session_gap_minutes)
        self.min_messages = min_messages
        self.min_duration = min_duration
        self.messages = []

    def _load_raw_logs(self) -> bool:
        """Loads and sorts messages from the raw JSONL file."""
        if not self.raw_log_path.exists():
            logger.error(f"Raw log file not found: {self.raw_log_path}")
            return False

        with open(self.raw_log_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    msg = json.loads(line)
                    # Ensure timestamp is a valid ISO format string
                    if 'Timestamp' in msg and isinstance(msg['Timestamp'], str):
                        self.messages.append(msg)
                except json.JSONDecodeError:
                    logger.warning(f"Skipping invalid JSON line in {self.raw_log_path}")

        # Sort messages chronologically, which is crucial for sessioning
        self.messages.sort(key=lambda m: m['Timestamp'])
        logger.info(f"Loaded and sorted {len(self.messages)} messages from {self.raw_log_path}")
        return True

    def _parse_and_normalize_timestamp(self, ts_str: str) -> datetime:
        """Parses an ISO timestamp string and returns an offset-naive UTC datetime object."""
        try:
            # Handle 'Z' for Zulu time (UTC), which fromisoformat doesn't like before Python 3.11
            if ts_str.endswith('Z'):
                ts_str = ts_str[:-1] + '+00:00'
            dt = datetime.fromisoformat(ts_str)
            # If it's timezone-aware, convert to UTC and then make it naive for calculations
            if dt.tzinfo:
                return dt.astimezone(timezone.utc).replace(tzinfo=None)
            return dt  # It's already naive
        except (ValueError, TypeError):
            logger.warning(f"Could not parse timestamp: '{ts_str}'. Using epoch.")
            return datetime.min

    def _group_by_context_id(self) -> tuple[dict, list]:
        """Groups messages into threads using 'ContextId' as the primary key."""
        threads = defaultdict(list)
        unassigned = []

        for msg in self.messages:
            context_id = msg.get('ContextId')
            if context_id and context_id != 'unknown':
                threads[context_id].append(msg)
            else:
                unassigned.append(msg)

        logger.info(f"Grouped messages into {len(threads)} threads by ContextId.")
        logger.info(f"{len(unassigned)} messages have no ContextId and will be processed by time-based sessioning.")
        return threads, unassigned

    def _group_by_time(self, messages: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Groups remaining messages into sessions based on time gaps."""
        if not messages:
            return {}

        sessions = []
        current_session = [messages[0]]

        for i in range(1, len(messages)):
            prev_msg_time = self._parse_and_normalize_timestamp(messages[i-1]['Timestamp'])
            current_msg_time = self._parse_and_normalize_timestamp(messages[i]['Timestamp'])

            if (current_msg_time - prev_msg_time) > self.max_session_gap:
                sessions.append(current_session)
                current_session = [messages[i]]
            else:
                current_session.append(messages[i])
        
        sessions.append(current_session)  # Add the last session

        # Convert to dictionary with generated session IDs
        session_dict = {f"session_{i+1}": s for i, s in enumerate(sessions)}
        logger.info(f"Grouped {len(messages)} unassigned messages into {len(session_dict)} time-based sessions.")
        return session_dict

    def _summarize_thread(self, thread_id: str, thread_messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Creates a summary for a given thread."""
        if not thread_messages:
            return {}

        start_time_str = thread_messages[0]['Timestamp']
        end_time_str = thread_messages[-1]['Timestamp']

        start_dt = self._parse_and_normalize_timestamp(start_time_str)
        end_dt = self._parse_and_normalize_timestamp(end_time_str)
        
        duration_seconds = (end_dt - start_dt).total_seconds()
        participants = sorted(list(set(msg.get('SpeakerName', 'unknown') for msg in thread_messages)))
        context_shifts = self._analyze_context_shifts(thread_messages)
        
        # Extract final status from SHL tags if available
        final_status = "Completed"
        for msg in reversed(thread_messages):
             tags = msg.get('Metadata', {}).get('shl_tags', [])
             if any("Status-Blocked" in tag for tag in tags):
                 final_status = "Blocked"
                 break
             if any("Status-Ready" in tag for tag in tags):
                 final_status = "Ready"
                 break

        return {
            "thread_id": thread_id,
            "start_time": start_time_str,
            "end_time": end_time_str,
            "duration_seconds": duration_seconds,
            "message_count": len(thread_messages),
            "participants": participants,
            "final_status": final_status,
            "context_shifts": context_shifts, # New field for context transformations
            "messages": thread_messages
        }

    def _analyze_context_shifts(self, messages: List[Dict[str, Any]], stability_threshold: int = 2) -> List[Dict[str, Any]]:
        """Analyzes the sequence of messages to find points where the conversation topic changes."""
        if len(messages) < stability_threshold:
            return []

        shifts = []
        current_context = messages[0].get('Metadata', {}).get('chain_type', 'unknown')
        
        for i in range(1, len(messages) - stability_threshold + 1):
            new_context = messages[i].get('Metadata', {}).get('chain_type', 'unknown')

            if new_context != current_context:
                # Look ahead to see if the new context is stable
                is_stable_shift = all(
                    m.get('Metadata', {}).get('chain_type', 'unknown') == new_context
                    for m in messages[i : i + stability_threshold]
                )

                if is_stable_shift:
                    shifts.append({
                        "from_topic": current_context,
                        "to_topic": new_context,
                        "message_index": i
                    })
                    current_context = new_context
        
        return shifts

    def _write_to_parquet(self, threads: List[Dict[str, Any]]):
        """Writes the list of summarized threads to a Parquet file."""
        if not ARROW_SUPPORT:
            logger.warning("Apache Arrow/PyArrow not installed. Skipping Parquet output.")
            logger.warning("Install it with: pip install pyarrow pandas")
            return
        
        try:
            # For Parquet, complex types like list-of-dicts are best stored as JSON strings
            df_data = []
            for thread in threads:
                thread_copy = thread.copy()
                thread_copy['messages'] = json.dumps(thread_copy['messages'])
                thread_copy['participants'] = json.dumps(thread_copy['participants'])
                thread_copy['context_shifts'] = json.dumps(thread_copy['context_shifts'])
                df_data.append(thread_copy)

            df = pd.DataFrame(df_data)
            table = pa.Table.from_pandas(df)
            pq.write_table(table, self.parquet_output_path)
            logger.info(f"Successfully wrote {len(threads)} threads to Parquet file: {self.parquet_output_path}")

        except Exception as e:
            logger.error(f"Failed to write to Parquet file: {e}")

    def run(self):
        """Executes the full defragmentation process."""
        logger.info("Starting defragmentation process...")
        if not self._load_raw_logs():
            return

        context_threads, unassigned_messages = self._group_by_context_id()
        time_based_sessions = self._group_by_time(unassigned_messages)

        all_threads = {**context_threads, **time_based_sessions}
        
        summarized_threads = [self._summarize_thread(tid, msgs) for tid, msgs in all_threads.items()]

        # Phase 1: Significance Filtering
        initial_thread_count = len(summarized_threads)
        significant_threads = [
            thread for thread in summarized_threads
            if thread['message_count'] >= self.min_messages and thread['duration_seconds'] >= self.min_duration
        ]
        filtered_count = initial_thread_count - len(significant_threads)
        logger.info(f"Filtered out {filtered_count} insignificant threads based on min_messages={self.min_messages} and min_duration={self.min_duration}s.")

        # Sort threads by start time
        significant_threads.sort(key=lambda t: t['start_time'])

        try:
            self.output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.output_path, 'w', encoding='utf-8') as f:
                for thread in significant_threads:
                    f.write(json.dumps(thread, ensure_ascii=False) + '\n')
            logger.info(f"Successfully wrote {len(significant_threads)} defragmented threads to {self.output_path}")
        except IOError as e:
            logger.error(f"Failed to write output file: {e}")
        
        # Write to Parquet format as well
        self._write_to_parquet(significant_threads)

def main():
    """CLI entry point for running the engine directly."""
    raw_log = "conversation_logs/current_session.jsonl"
    defragmented_log = "conversation_logs/defragmented_sessions.jsonl"
    
    engine = DefragmentationEngine(raw_log_file=raw_log, output_file=defragmented_log)
    engine.run()

if __name__ == "__main__":
    main()