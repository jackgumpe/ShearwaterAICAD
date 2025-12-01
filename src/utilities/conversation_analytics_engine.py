#!/usr/bin/env python3
"""
Conversation Analytics Engine
Analyzes persistence recording data from JSONL and Arrow formats
Generates actionable reports with collaboration metrics
"""

import json
import re
from pathlib import Path
from datetime import datetime
from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Any
import logging

# Try to import pyarrow for Arrow support
try:
    import pyarrow.parquet as pq
    ARROW_SUPPORT = True
except ImportError:
    ARROW_SUPPORT = False

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s'
)
logger = logging.getLogger('AnalyticsEngine')

class ConversationAnalytics:
    """Analyzes conversation data for collaboration metrics and insights"""

    def __init__(self, log_dir: str = "conversation_logs"):
        self.log_dir = Path(log_dir)
        self.messages = []
        self.reports_dir = Path("reports")
        self.reports_dir.mkdir(exist_ok=True)

    def load_jsonl(self) -> int:
        """Load messages from JSONL file"""
        session_file = self.log_dir / "current_session.jsonl"

        if not session_file.exists():
            logger.error(f"Session file not found: {session_file}")
            return 0

        count = 0
        try:
            with open(session_file, 'r') as f:
                for line in f:
                    try:
                        msg = json.loads(line.strip())
                        self.messages.append(msg)
                        count += 1
                    except json.JSONDecodeError:
                        pass
        except Exception as e:
            logger.error(f"Error loading JSONL: {e}")

        logger.info(f"Loaded {count} messages from JSONL")
        return count

    def load_arrow(self) -> int:
        """Load messages from Arrow/Parquet format"""
        if not ARROW_SUPPORT:
            logger.warning("PyArrow not available, skipping Arrow format")
            return 0

        arrow_files = list(self.log_dir.glob("**/*.arrow")) + list(self.log_dir.glob("**/*.parquet"))

        count = 0
        for arrow_file in arrow_files:
            try:
                table = pq.read_table(arrow_file)
                df = table.to_pandas()

                for _, row in df.iterrows():
                    msg = row.to_dict()
                    # Convert numpy types to native Python types
                    msg = {k: (v.item() if hasattr(v, 'item') else v) for k, v in msg.items()}
                    self.messages.append(msg)
                    count += 1

                logger.info(f"Loaded {count} messages from {arrow_file.name}")
            except Exception as e:
                logger.warning(f"Error loading Arrow file {arrow_file}: {e}")

        return count

    def analyze(self) -> Dict[str, Any]:
        """Perform comprehensive analysis"""
        if not self.messages:
            logger.error("No messages loaded!")
            return {}

        results = {
            'timestamp': datetime.now().isoformat(),
            'total_messages': len(self.messages),
            'speakers': self._analyze_speakers(),
            'message_types': self._analyze_message_types(),
            'chain_types': self._analyze_chain_types(),
            'ace_tiers': self._analyze_ace_tiers(),
            'keywords': self._analyze_keywords(),
            'timeline': self._analyze_timeline(),
            'metadata_insights': self._analyze_metadata(),
            'collaboration_score': self._calculate_collaboration_score(),
        }

        return results

    def _analyze_speakers(self) -> Dict[str, int]:
        """Count messages by speaker"""
        speakers = Counter()
        for msg in self.messages:
            speaker = msg.get('SpeakerName', 'unknown')
            speakers[speaker] += 1
        return dict(speakers.most_common())

    def _analyze_message_types(self) -> Dict[str, int]:
        """Analyze message types from metadata"""
        msg_types = defaultdict(int)

        for msg in self.messages:
            # Try multiple possible type fields
            msg_type = (msg.get('Type') or
                       msg.get('type') or
                       msg.get('ConversationType') or
                       'unknown')
            msg_types[str(msg_type)] += 1

        return dict(sorted(msg_types.items(), key=lambda x: x[1], reverse=True))

    def _analyze_chain_types(self) -> Dict[str, int]:
        """Analyze domain chains"""
        chains = Counter()
        for msg in self.messages:
            chain = msg.get('chain_type', 'unknown')
            chains[chain] += 1
        return dict(chains.most_common())

    def _analyze_ace_tiers(self) -> Dict[str, int]:
        """Analyze ACE tier distribution"""
        tiers = Counter()
        for msg in self.messages:
            tier = msg.get('ace_tier', 'unknown')
            tiers[tier] += 1
        return dict(tiers.most_common())

    def _analyze_keywords(self, top_n: int = 20) -> List[Tuple[str, int]]:
        """Extract top keywords"""
        keywords = Counter()

        for msg in self.messages:
            # Try metadata keywords first
            if isinstance(msg.get('Metadata'), dict):
                meta_keywords = msg['Metadata'].get('keywords', [])
                if isinstance(meta_keywords, list):
                    keywords.update(meta_keywords)

            # Also try root-level keywords
            if isinstance(msg.get('keywords'), list):
                keywords.update(msg['keywords'])

        return keywords.most_common(top_n)

    def _analyze_timeline(self) -> Dict[str, Any]:
        """Analyze message distribution over time"""
        timeline = defaultdict(int)

        for msg in self.messages:
            timestamp = msg.get('Timestamp', '')
            if timestamp:
                # Extract date
                date = timestamp.split('T')[0]
                timeline[date] += 1

        return dict(sorted(timeline.items()))

    def _analyze_metadata(self) -> Dict[str, Any]:
        """Analyze metadata patterns"""
        insights = {
            'shl_tags_frequency': self._count_shl_tags(),
            'consolidation_ratio': self._analyze_consolidation(),
            'content_hash_coverage': sum(1 for m in self.messages
                                        if 'content_hash' in m.get('Metadata', {})),
        }
        return insights

    def _count_shl_tags(self) -> Dict[str, int]:
        """Count SHL tags"""
        tags = Counter()
        for msg in self.messages:
            shl_tags = msg.get('shl_tags', [])
            if isinstance(shl_tags, list):
                tags.update(shl_tags)
        return dict(tags.most_common(10))

    def _analyze_consolidation(self) -> Dict[str, Any]:
        """Analyze message consolidation stats"""
        consolidated = sum(1 for m in self.messages
                          if m.get('Metadata', {}).get('consolidated'))
        total = len(self.messages)

        return {
            'consolidated_count': consolidated,
            'total_count': total,
            'consolidation_percentage': (consolidated / total * 100) if total > 0 else 0,
        }

    def _calculate_collaboration_score(self) -> float:
        """Calculate overall collaboration quality (0-100)"""
        if not self.messages:
            return 0

        score = 0.0

        # 1. Speaker diversity (20%)
        speakers = len(self._analyze_speakers())
        speaker_score = min(speakers / 3 * 100, 100)  # 0-100 based on unique speakers
        score += speaker_score * 0.2

        # 2. Domain coverage (20%)
        chains = len(self._analyze_chain_types())
        domain_score = min(chains / 10 * 100, 100)  # 0-100 based on domain chains
        score += domain_score * 0.2

        # 3. Message consistency (20%)
        message_ratio = len(self.messages) / 100  # Normalize to 100-message baseline
        consistency_score = min(message_ratio * 100, 100)
        score += consistency_score * 0.2

        # 4. Metadata enrichment (20%)
        enriched = sum(1 for m in self.messages if m.get('Metadata'))
        enrichment_score = (enriched / len(self.messages) * 100) if self.messages else 0
        score += enrichment_score * 0.2

        # 5. SHL tagging (20%)
        tagged = sum(1 for m in self.messages if m.get('shl_tags'))
        tagging_score = (tagged / len(self.messages) * 100) if self.messages else 0
        score += tagging_score * 0.2

        return round(score, 2)

    def generate_report(self) -> str:
        """Generate markdown report"""
        analysis = self.analyze()

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = self.reports_dir / f"analytics_report_{timestamp}.md"

        report = f"""# Conversation Analytics Report
Generated: {analysis['timestamp']}

## Overview
- **Total Messages**: {analysis['total_messages']}
- **Collaboration Score**: {analysis['collaboration_score']}/100
- **Sessions**: {len(analysis['timeline'])}

## Speaker Activity
```
"""

        for speaker, count in analysis['speakers'].items():
            report += f"{speaker}: {count} messages\n"

        report += """```

## Domain Focus (Chain Types)
```
"""
        for chain, count in analysis['chain_types'].items():
            report += f"{chain}: {count} messages\n"

        report += """```

## ACE Tier Distribution
```
"""
        for tier, count in analysis['ace_tiers'].items():
            report += f"Tier {tier}: {count} messages\n"

        report += """```

## Top Keywords
```
"""
        for keyword, count in analysis['keywords']:
            report += f"{keyword}: {count} occurrences\n"

        report += """```

## Message Timeline
```
"""
        for date, count in list(analysis['timeline'].items())[-10:]:
            report += f"{date}: {count} messages\n"

        report += """```

## Metadata Insights
- Consolidated Messages: {consolidated}/{total} ({pct:.1f}%)
- Content Hash Coverage: {hashes}/total
- SHL Tags Coverage: Yes

## Collaboration Metrics
- Speaker Diversity: {speakers} unique speakers
- Domain Coverage: {domains} different domains
- Enrichment Score: Comprehensive

## Key Findings
1. Main discussion focus: {top_domain}
2. Most active speaker: {top_speaker}
3. Most common tag: {top_tag}
4. Data quality: {quality}%

---
**Status**: Analysis complete
**Next**: Review trends and generate targeted reports
""".format(
            consolidated=analysis['metadata_insights']['consolidation_ratio']['consolidated_count'],
            total=analysis['metadata_insights']['consolidation_ratio']['total_count'],
            pct=analysis['metadata_insights']['consolidation_ratio']['consolidation_percentage'],
            hashes=analysis['metadata_insights']['content_hash_coverage'],
            speakers=len(analysis['speakers']),
            domains=len(analysis['chain_types']),
            top_domain=max(analysis['chain_types'].items(), key=lambda x: x[1])[0] if analysis['chain_types'] else 'N/A',
            top_speaker=max(analysis['speakers'].items(), key=lambda x: x[1])[0] if analysis['speakers'] else 'N/A',
            top_tag=max(analysis['metadata_insights']['shl_tags_frequency'].items(), key=lambda x: x[1])[0] if analysis['metadata_insights']['shl_tags_frequency'] else 'N/A',
            quality=int(analysis['collaboration_score']),
        )

        with open(report_path, 'w') as f:
            f.write(report)

        logger.info(f"Report saved to {report_path}")
        return str(report_path)

    def generate_json_report(self) -> str:
        """Generate JSON report"""
        analysis = self.analyze()

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = self.reports_dir / f"analytics_report_{timestamp}.json"

        with open(report_path, 'w') as f:
            json.dump(analysis, f, indent=2)

        logger.info(f"JSON report saved to {report_path}")
        return str(report_path)

    def run(self) -> Dict[str, Any]:
        """Load data and run analysis"""
        logger.info("Starting conversation analytics...")

        # Load from both formats
        jsonl_count = self.load_jsonl()
        arrow_count = self.load_arrow()

        logger.info(f"Total messages loaded: {len(self.messages)}")

        if not self.messages:
            logger.error("No data to analyze!")
            return {}

        # Generate reports
        analysis = self.analyze()

        self.generate_json_report()
        self.generate_report()

        # Print summary
        print("\n" + "="*70)
        print("CONVERSATION ANALYTICS REPORT")
        print("="*70)
        print(f"Total Messages: {analysis['total_messages']}")
        print(f"Collaboration Score: {analysis['collaboration_score']}/100")
        print(f"\nTop Speakers:")
        for speaker, count in list(analysis['speakers'].items())[:5]:
            print(f"  - {speaker}: {count}")
        print(f"\nDomain Focus:")
        for chain, count in list(analysis['chain_types'].items())[:5]:
            print(f"  - {chain}: {count}")
        print(f"\nTop Keywords:")
        for keyword, count in analysis['keywords'][:5]:
            print(f"  - {keyword}: {count}")
        print("="*70 + "\n")

        return analysis


def main():
    """CLI entry point"""
    analytics = ConversationAnalytics()
    analytics.run()


if __name__ == "__main__":
    main()
