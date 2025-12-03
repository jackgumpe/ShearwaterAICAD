"""
Emergent Property Tracker

Monitors and detects emergent properties in double handshake agent interactions.
Tracks:
- Solution quality improvements
- Diversity metrics
- Novelty signals
- Collaboration patterns
- Emergence indicators
"""

import json
import math
from pathlib import Path
from datetime import datetime
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Any
import re


class EmergentPropertyTracker:
    """Track and measure emergent properties in agent interactions"""

    def __init__(self, log_file: str = "conversation_logs/current_session.jsonl"):
        self.log_file = Path(log_file)
        self.messages = []
        self.interactions = []  # Agent exchanges
        self.emergence_signals = []

        # Metrics storage
        self.metrics = {
            'diversity': {},
            'novelty': {},
            'solution_quality': {},
            'collaboration': {},
            'interaction_depth': {},
            'emergence_indicators': {}
        }

    def load_messages(self):
        """Load messages from persistence log"""
        if not self.log_file.exists():
            return False

        self.messages = []
        try:
            with open(self.log_file) as f:
                for line in f:
                    try:
                        msg = json.loads(line)
                        self.messages.append(msg)
                    except:
                        pass
        except Exception as e:
            print(f"Error loading messages: {e}")
            return False

        return len(self.messages) > 0

    def extract_conversations(self):
        """Extract coherent conversations between agents"""
        conversations = []
        current_conv = []

        for msg in self.messages:
            # Look for messages with from/to fields
            if 'from' in msg and 'to' in msg:
                current_conv.append(msg)

                # New conversation starts when pattern breaks
                if len(current_conv) > 1:
                    prev = current_conv[-2]
                    curr = current_conv[-1]

                    # Check if this breaks a conversation pattern
                    if not self._is_continuation(prev, curr):
                        if len(current_conv) > 1:
                            conversations.append(current_conv[:-1])
                        current_conv = [curr]

        if current_conv:
            conversations.append(current_conv)

        self.interactions = conversations
        return conversations

    def _is_continuation(self, prev_msg: Dict, curr_msg: Dict) -> bool:
        """Check if current message continues previous conversation"""
        # Same agents but reversed direction = continuation
        return (prev_msg.get('from') == curr_msg.get('to') and
                prev_msg.get('to') == curr_msg.get('from'))

    # ========== DIVERSITY METRICS ==========

    def analyze_diversity(self) -> Dict[str, Any]:
        """Measure diversity in agent responses"""
        if not self.messages:
            return {'status': 'no_data'}

        results = {}

        # By speaker
        speaker_stats = defaultdict(int)
        for msg in self.messages:
            speaker = msg.get('SpeakerName', 'unknown')
            speaker_stats[speaker] += 1

        results['speaker_distribution'] = dict(speaker_stats)

        # Vocabulary diversity
        vocabulary = self._extract_vocabulary()
        results['vocabulary_size'] = len(vocabulary)

        # Message length diversity
        lengths = [len(str(m.get('Message', ''))) for m in self.messages]
        results['message_length'] = {
            'mean': sum(lengths) / len(lengths) if lengths else 0,
            'min': min(lengths) if lengths else 0,
            'max': max(lengths) if lengths else 0,
            'std_dev': self._std_dev(lengths)
        }

        # Concept diversity (unique topics/concepts mentioned)
        concepts = self._extract_concepts()
        results['unique_concepts'] = len(concepts)
        results['concept_entropy'] = self._calculate_entropy(list(concepts.values()))

        self.metrics['diversity'] = results
        return results

    def _extract_vocabulary(self) -> set:
        """Extract unique words from all messages"""
        vocab = set()
        for msg in self.messages:
            text = str(msg.get('Message', ''))
            words = re.findall(r'\b\w+\b', text.lower())
            vocab.update(words)
        return vocab

    def _extract_concepts(self) -> Counter:
        """Extract higher-level concepts (technical terms, patterns)"""
        concepts = Counter()
        technical_terms = [
            'api', 'database', 'cache', 'optimization', 'architecture',
            'performance', 'scalability', 'reliability', 'security', 'encryption',
            'distributed', 'concurrent', 'async', 'network', 'bandwidth',
            'latency', 'throughput', 'queue', 'pipeline', 'workflow'
        ]

        for msg in self.messages:
            text = str(msg.get('Message', '')).lower()
            for term in technical_terms:
                if term in text:
                    concepts[term] += 1

        return concepts

    # ========== NOVELTY METRICS ==========

    def analyze_novelty(self) -> Dict[str, Any]:
        """Measure novelty and creativity in solutions"""
        results = {}

        # Track new terms over time
        new_terms_over_time = self._track_new_terms()
        results['new_terms_introduction'] = new_terms_over_time

        # Unique phrasing (rare combinations)
        unique_phrases = self._find_unique_phrases()
        results['unique_phrases_count'] = len(unique_phrases)

        # Conceptual novelty (new combinations)
        novelty_score = self._calculate_novelty_score()
        results['novelty_score'] = novelty_score

        # Innovation metrics
        results['innovation_indicators'] = {
            'cross_domain_refs': self._count_cross_domain_references(),
            'new_problem_framings': self._count_problem_reframings(),
            'contradictions_resolved': self._count_contradiction_resolutions()
        }

        self.metrics['novelty'] = results
        return results

    def _track_new_terms(self) -> List[Tuple[int, str]]:
        """Track introduction of new terms over message sequence"""
        seen_terms = set()
        new_introductions = []

        for idx, msg in enumerate(self.messages):
            text = str(msg.get('Message', '')).lower()
            words = set(re.findall(r'\b\w+\b', text))

            for word in words:
                if len(word) > 5 and word not in seen_terms:
                    new_introductions.append((idx, word))
                    seen_terms.add(word)

        return new_introductions[-20:]  # Last 20 new terms

    def _find_unique_phrases(self) -> List[str]:
        """Find rare, unique phrases in conversations"""
        phrase_counts = Counter()

        for msg in self.messages:
            text = str(msg.get('Message', ''))
            # Extract 3-word phrases
            words = text.split()
            for i in range(len(words) - 2):
                phrase = ' '.join(words[i:i+3]).lower()
                if len(phrase) > 10:  # Meaningful phrases
                    phrase_counts[phrase] += 1

        # Find phrases that appear exactly once (unique)
        unique = [p for p, c in phrase_counts.items() if c == 1]
        return unique

    def _calculate_novelty_score(self) -> float:
        """Calculate overall novelty score (0-100)"""
        if not self.messages:
            return 0.0

        # Factors:
        # 1. Vocabulary diversity
        vocab_size = len(self._extract_vocabulary())
        vocab_score = min(100, (vocab_size / 500) * 100)  # 500 unique words = max

        # 2. Unique phrases
        unique_phrases = len(self._find_unique_phrases())
        phrase_score = min(100, (unique_phrases / 100) * 100)  # 100 unique = max

        # 3. Concept diversity
        concepts = self._extract_concepts()
        concept_score = min(100, (len(concepts) / 20) * 100)  # 20 concepts = max

        # Weighted average
        novelty = (vocab_score * 0.4 + phrase_score * 0.4 + concept_score * 0.2)
        return round(novelty, 2)

    def _count_cross_domain_references(self) -> int:
        """Count references to multiple technical domains"""
        domains = {
            'databases': ['sql', 'nosql', 'mongodb', 'postgres', 'database'],
            'networks': ['tcp', 'udp', 'http', 'protocol', 'socket'],
            'security': ['encryption', 'hash', 'certificate', 'auth', 'security'],
            'performance': ['latency', 'throughput', 'optimization', 'cache'],
            'architecture': ['microservice', 'monolith', 'distributed', 'architecture']
        }

        text = ' '.join(str(m.get('Message', '')) for m in self.messages).lower()
        domains_found = set()

        for domain, keywords in domains.items():
            if any(kw in text for kw in keywords):
                domains_found.add(domain)

        return len(domains_found)

    def _count_problem_reframings(self) -> int:
        """Count instances where problem is reframed"""
        reframing_signals = [
            'actually', 'but fundamentally', 'no wait', 'different angle',
            'perspective', 'reframe', 'rethink', 'instead of', 'rather than',
            'on second thought'
        ]

        text = ' '.join(str(m.get('Message', '')) for m in self.messages).lower()
        count = sum(1 for signal in reframing_signals if signal in text)

        return count

    def _count_contradiction_resolutions(self) -> int:
        """Count resolutions of contradictions between agents"""
        resolutions = 0

        for conv in self.interactions:
            if len(conv) >= 3:
                # Look for pattern: A says X, B says not X, then synthesis
                text_a = str(conv[0].get('Message', '')).lower()
                text_b = str(conv[1].get('Message', '')).lower()

                # Simple heuristic: if they disagree then agree
                if ('disagree' in text_b or 'but' in text_b) and len(conv) > 2:
                    resolutions += 1

        return resolutions

    # ========== SOLUTION QUALITY METRICS ==========

    def analyze_solution_quality(self) -> Dict[str, Any]:
        """Measure quality of proposed solutions"""
        results = {}

        # Completeness (covers multiple aspects)
        results['solution_completeness'] = self._measure_completeness()

        # Specificity (concrete details vs abstract)
        results['solution_specificity'] = self._measure_specificity()

        # Feasibility indicators
        results['feasibility_score'] = self._measure_feasibility()

        # Risk awareness
        results['risk_awareness'] = self._measure_risk_awareness()

        self.metrics['solution_quality'] = results
        return results

    def _measure_completeness(self) -> float:
        """Measure how complete solutions are"""
        aspects = {
            'implementation': ['implement', 'code', 'develop', 'build'],
            'testing': ['test', 'verify', 'validate', 'qa'],
            'deployment': ['deploy', 'release', 'production', 'launch'],
            'monitoring': ['monitor', 'alert', 'dashboard', 'metric'],
            'documentation': ['document', 'readme', 'spec', 'guide']
        }

        text = ' '.join(str(m.get('Message', '')) for m in self.messages).lower()
        covered = 0

        for aspect, keywords in aspects.items():
            if any(kw in text for kw in keywords):
                covered += 1

        completeness = (covered / len(aspects)) * 100
        return round(completeness, 2)

    def _measure_specificity(self) -> float:
        """Measure specificity of solutions (0-100)"""
        # Count specific technical references
        specific_patterns = [
            r'\d+\s*(mb|gb|ms|hours|days)',  # Numbers with units
            r'[a-z]+_[a-z]+',  # Snake_case identifiers
            r'class\s+\w+',  # Class definitions
            r'def\s+\w+',  # Function definitions
            r'\$\d+(?:,\d{3})*',  # Money amounts
        ]

        text = ' '.join(str(m.get('Message', '')) for m in self.messages)
        specific_count = 0

        for pattern in specific_patterns:
            matches = re.findall(pattern, text)
            specific_count += len(matches)

        specificity = min(100, (specific_count / 20) * 100)  # 20 specific refs = max
        return round(specificity, 2)

    def _measure_feasibility(self) -> float:
        """Measure feasibility awareness in solutions"""
        positive_signals = [
            'proven', 'mature', 'tested', 'industry standard',
            'best practice', 'well-documented', 'open source',
            'reliable', 'scalable', 'performant'
        ]

        risk_signals = [
            'risky', 'unproven', 'experimental', 'bleeding edge',
            'complex', 'difficult', 'challenging', 'new technology',
            'immature', 'unstable'
        ]

        text = ' '.join(str(m.get('Message', '')) for m in self.messages).lower()

        pos_count = sum(1 for signal in positive_signals if signal in text)
        risk_count = sum(1 for signal in risk_signals if signal in text)

        # Feasibility = positive signals - risk signals
        feasibility = ((pos_count - risk_count) / (pos_count + risk_count + 1)) * 100
        return round(max(0, feasibility), 2)

    def _measure_risk_awareness(self) -> float:
        """Measure awareness of risks and mitigation"""
        risk_keywords = [
            'risk', 'mitigation', 'fallback', 'recovery', 'contingency',
            'failure mode', 'edge case', 'bottleneck', 'limitation'
        ]

        text = ' '.join(str(m.get('Message', '')) for m in self.messages).lower()
        risk_mentions = sum(1 for kw in risk_keywords if kw in text)

        # Normalize to 0-100
        risk_score = min(100, (risk_mentions / 5) * 100)
        return round(risk_score, 2)

    # ========== COLLABORATION METRICS ==========

    def analyze_collaboration(self) -> Dict[str, Any]:
        """Measure quality of collaboration"""
        results = {}

        # Turn-taking (balanced participation)
        results['turn_balance'] = self._measure_turn_balance()

        # Building on each other
        results['iterative_improvement'] = self._measure_iterative_improvement()

        # Disagreement patterns
        results['disagreement_patterns'] = self._analyze_disagreement()

        # Question-Answer patterns
        results['q_a_effectiveness'] = self._measure_qa_effectiveness()

        self.metrics['collaboration'] = results
        return results

    def _measure_turn_balance(self) -> Dict[str, float]:
        """Measure balance in conversation turns"""
        speaker_turns = defaultdict(int)

        for msg in self.messages:
            speaker = msg.get('SpeakerName', 'unknown')
            speaker_turns[speaker] += 1

        total_turns = sum(speaker_turns.values())

        balance = {}
        for speaker, turns in speaker_turns.items():
            percentage = (turns / total_turns) * 100 if total_turns > 0 else 0
            balance[speaker] = round(percentage, 2)

        return balance

    def _measure_iterative_improvement(self) -> float:
        """Measure if solutions improve over time"""
        improvements = 0
        total_exchanges = len(self.interactions)

        for conv in self.interactions:
            if len(conv) >= 2:
                # Check for improvement indicators
                later_msg = str(conv[-1].get('Message', '')).lower()

                improvement_signals = [
                    'better', 'improved', 'enhance', 'refine', 'optimized',
                    'stronger', 'addressing', 'incorporating', 'integrated'
                ]

                if any(signal in later_msg for signal in improvement_signals):
                    improvements += 1

        improvement_ratio = (improvements / total_exchanges) if total_exchanges > 0 else 0
        return round(improvement_ratio * 100, 2)

    def _analyze_disagreement(self) -> Dict[str, Any]:
        """Analyze disagreement patterns"""
        disagreement_signals = [
            'disagree', 'but', 'however', 'although', 'instead',
            'question', 'challenge', 'contradiction', 'different view'
        ]

        disagreements = 0
        productive_disagreements = 0

        for conv in self.interactions:
            if len(conv) >= 2:
                text = str(conv[1].get('Message', '')).lower()

                if any(sig in text for sig in disagreement_signals):
                    disagreements += 1

                    # Check if followed by resolution/synthesis
                    if len(conv) > 2:
                        next_text = str(conv[2].get('Message', '')).lower()
                        if any(w in next_text for w in ['agreed', 'combined', 'hybrid', 'both']):
                            productive_disagreements += 1

        return {
            'total_disagreements': disagreements,
            'productive_disagreements': productive_disagreements,
            'disagreement_ratio': round((disagreements / len(self.interactions)) if self.interactions else 0, 2)
        }

    def _measure_qa_effectiveness(self) -> float:
        """Measure effectiveness of questions and answers"""
        questions = 0
        answered_questions = 0

        text = ' '.join(str(m.get('Message', '')) for m in self.messages)
        questions = text.count('?')

        # Simple heuristic: questions followed by detailed answers
        messages = [str(m.get('Message', '')) for m in self.messages]
        for i, msg in enumerate(messages[:-1]):
            if '?' in msg and len(messages[i+1]) > 50:  # Detailed answer
                answered_questions += 1

        effectiveness = (answered_questions / max(1, questions)) * 100 if questions > 0 else 0
        return round(min(100, effectiveness), 2)

    # ========== EMERGENCE INDICATORS ==========

    def analyze_emergence(self) -> Dict[str, Any]:
        """Detect signs of emergent properties"""
        results = {}

        # Novelty score
        results['novelty_score'] = self._calculate_novelty_score()

        # Solution quality
        quality = self.analyze_solution_quality()
        results['solution_quality_avg'] = (
            quality['solution_completeness'] +
            quality['solution_specificity'] +
            quality['feasibility_score']
        ) / 3

        # Collaboration quality
        collab = self.analyze_collaboration()
        results['collaboration_quality'] = collab['iterative_improvement']

        # Emergence confidence (0-100)
        emergence_confidence = self._calculate_emergence_confidence()
        results['emergence_confidence'] = emergence_confidence

        # Emergence signals detected
        results['detected_signals'] = self._detect_emergence_signals()

        self.metrics['emergence_indicators'] = results
        return results

    def _calculate_emergence_confidence(self) -> float:
        """Calculate confidence in presence of emergent properties"""
        factors = []

        # Factor 1: Novelty
        novelty = self._calculate_novelty_score()
        factors.append(novelty)

        # Factor 2: Collaboration quality
        for conv in self.interactions:
            if len(conv) >= 3:
                # Multi-round conversation = potential emergence
                factors.append(50)

        # Factor 3: Disagreement handled productively
        disagreement = self.analyze_collaboration()['disagreement_patterns']
        if disagreement['productive_disagreements'] > 0:
            factors.append(60)

        # Factor 4: Cross-domain thinking
        cross_domain = self._count_cross_domain_references()
        if cross_domain >= 3:
            factors.append(70)

        if not factors:
            return 0.0

        confidence = sum(factors) / len(factors)
        return round(min(100, confidence), 2)

    def _detect_emergence_signals(self) -> List[str]:
        """Detect specific signals of emergent properties"""
        signals = []
        text = ' '.join(str(m.get('Message', '')) for m in self.messages).lower()

        # Signal patterns
        patterns = {
            'novel_synthesis': r'(combining|hybrid|integrated|together|both)',
            'assumption_challenge': r'(actually|fundamentally|instead|rethink)',
            'error_correction': r'(mistake|catch|wrong|corrected|fixed)',
            'unexpected_insight': r'(surprising|unexpected|interesting|revealed)',
            'specialization': r'(stronger|weakness|complement|strength)',
            'cross_domain': r'(domain|architecture|database|network|security)',
        }

        for signal_name, pattern in patterns.items():
            if re.search(pattern, text):
                signals.append(signal_name)

        return signals

    # ========== UTILITY METHODS ==========

    def _std_dev(self, values: List[float]) -> float:
        """Calculate standard deviation"""
        if not values or len(values) < 2:
            return 0.0

        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return round(math.sqrt(variance), 2)

    def _calculate_entropy(self, values: List[int]) -> float:
        """Calculate Shannon entropy"""
        if not values:
            return 0.0

        total = sum(values)
        entropy = 0.0

        for v in values:
            if v > 0:
                p = v / total
                entropy -= p * math.log2(p)

        return round(entropy, 2)

    # ========== REPORTING ==========

    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive emergence report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'message_count': len(self.messages),
            'conversation_count': len(self.interactions),
            'metrics': {
                'diversity': self.analyze_diversity(),
                'novelty': self.analyze_novelty(),
                'solution_quality': self.analyze_solution_quality(),
                'collaboration': self.analyze_collaboration(),
                'emergence': self.analyze_emergence()
            }
        }

        return report

    def print_summary(self):
        """Print human-readable summary"""
        report = self.generate_report()

        print("\n" + "="*80)
        print("  EMERGENT PROPERTY ANALYSIS REPORT")
        print("="*80)
        print(f"\nTimestamp: {report['timestamp']}")
        print(f"Messages Analyzed: {report['message_count']}")
        print(f"Conversations: {report['conversation_count']}")

        emergence = report['metrics']['emergence']
        print(f"\n[EMERGENCE INDICATORS]")
        print(f"  Novelty Score: {emergence['novelty_score']}/100")
        print(f"  Solution Quality: {emergence['solution_quality_avg']:.1f}/100")
        print(f"  Collaboration Quality: {emergence['collaboration_quality']:.1f}/100")
        print(f"  Emergence Confidence: {emergence['emergence_confidence']:.1f}/100")
        print(f"  Detected Signals: {', '.join(emergence['detected_signals']) or 'None'}")

        diversity = report['metrics']['diversity']
        print(f"\n[DIVERSITY]")
        print(f"  Vocabulary Size: {diversity['vocabulary_size']}")
        print(f"  Unique Concepts: {diversity['unique_concepts']}")
        print(f"  Concept Entropy: {diversity['concept_entropy']}")

        collab = report['metrics']['collaboration']
        print(f"\n[COLLABORATION]")
        for speaker, percentage in collab['turn_balance'].items():
            print(f"  {speaker}: {percentage}%")
        print(f"  Iterative Improvement: {collab['iterative_improvement']:.1f}%")
        print(f"  Productive Disagreements: {collab['disagreement_patterns']['productive_disagreements']}")

        print("\n" + "="*80)


if __name__ == "__main__":
    tracker = EmergentPropertyTracker()

    if tracker.load_messages():
        tracker.extract_conversations()
        tracker.print_summary()

        # Save detailed report
        report = tracker.generate_report()
        output_file = Path("reports/emergence_analysis.json")
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\nDetailed report saved to: {output_file}")
    else:
        print("No messages found. Make sure persistence log exists.")
