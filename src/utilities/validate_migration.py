#!/usr/bin/env python3
"""
Validate migrated data integrity and quality.

This script:
1. Checks all required fields are present
2. Verifies JSON validity
3. Counts distribution across chain types, tiers, sources
4. Identifies any errors or missing data
5. Reports comprehensive statistics
"""

import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime

def validate_migration():
    output_file = Path("conversation_logs/migrated_history.jsonl")

    if not output_file.exists():
        print("[ERROR] Migrated file not found: {}".format(output_file))
        return False

    stats = {
        'total_records': 0,
        'valid_records': 0,
        'missing_fields': defaultdict(int),
        'chain_types': defaultdict(int),
        'ace_tiers': defaultdict(int),
        'sources': defaultdict(int),
        'errors': []
    }

    print("[VALIDATE] Starting migration validation...")
    print("[FILE] {}".format(output_file))
    print()

    with open(output_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            stats['total_records'] += 1

            try:
                record = json.loads(line.strip())

                # Check required fields
                required = ['Id', 'Timestamp', 'SpeakerName', 'Message', 'chain_type', 'ace_tier']
                record_valid = True
                for field in required:
                    if field not in record:
                        stats['missing_fields'][field] += 1
                        record_valid = False

                if record_valid:
                    stats['valid_records'] += 1

                # Count chain types
                chain = record.get('chain_type', 'unknown')
                stats['chain_types'][chain] += 1

                # Count ACE tiers
                tier = record.get('ace_tier', 'E')
                stats['ace_tiers'][tier] += 1

                # Count sources
                source = record.get('zmq_metadata', {}).get('source_system', 'unknown')
                stats['sources'][source] += 1

                # Report every 1000 records
                if line_num % 1000 == 0:
                    print("[PROGRESS] Validated {} records...".format(line_num))

            except json.JSONDecodeError as e:
                stats['errors'].append("Line {}: {}".format(line_num, str(e)[:80]))
                if len(stats['errors']) <= 10:  # Show first 10 errors
                    print("[ERROR] Line {}: Invalid JSON: {}".format(line_num, str(e)[:50]))

    # Print results
    print("\n" + "=" * 80)
    print("[VALIDATION RESULTS]")
    print("=" * 80)
    print("Total Records:           {:,}".format(stats['total_records']))
    print("Valid Records:           {:,}".format(stats['valid_records']))
    print("Validation Rate:         {:.1f}%".format(
        (stats['valid_records'] / stats['total_records'] * 100) if stats['total_records'] > 0 else 0
    ))

    if stats['missing_fields']:
        print("\n[MISSING FIELDS]")
        for field, count in sorted(stats['missing_fields'].items(), key=lambda x: x[1], reverse=True):
            print("  {}: {} records".format(field, count))

    print("\n[CHAIN TYPE DISTRIBUTION]")
    total = sum(stats['chain_types'].values())
    for chain in sorted(stats['chain_types'].keys()):
        count = stats['chain_types'][chain]
        pct = (count / total * 100) if total > 0 else 0
        print("  {}: {:,} ({:.1f}%)".format(chain, count, pct))

    print("\n[ACE TIER DISTRIBUTION]")
    total = sum(stats['ace_tiers'].values())
    for tier in ['A', 'C', 'E']:
        count = stats['ace_tiers'].get(tier, 0)
        pct = (count / total * 100) if total > 0 else 0
        print("  {}-Tier: {:,} ({:.1f}%)".format(tier, count, pct))

    print("\n[SOURCE DISTRIBUTION]")
    total = sum(stats['sources'].values())
    for source in sorted(stats['sources'].keys(), key=lambda x: stats['sources'][x], reverse=True):
        count = stats['sources'][source]
        pct = (count / total * 100) if total > 0 else 0
        print("  {}: {:,} ({:.1f}%)".format(source, count, pct))

    if stats['errors']:
        print("\n[ERRORS] {} errors during validation".format(len(stats['errors'])))
        for error in stats['errors'][:10]:  # Show first 10
            print("  {}".format(error))

    print("=" * 80)
    success = len(stats['errors']) == 0 and stats['valid_records'] == stats['total_records']
    print("[RESULT] {}".format('PASSED' if success else 'FAILED'))
    print("=" * 80)

    return success


if __name__ == "__main__":
    import sys
    success = validate_migration()
    sys.exit(0 if success else 1)
