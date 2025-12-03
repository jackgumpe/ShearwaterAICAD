#!/usr/bin/env python3
"""
Test Emergent Property Tracker

Analyzes current conversation logs for signs of emergent properties
and generates detailed metrics on collaboration and innovation.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from utilities.emergent_property_tracker import EmergentPropertyTracker


def main():
    print("="*80)
    print("  EMERGENT PROPERTY TRACKER - Analysis")
    print("="*80)
    print("\nScanning conversation logs for emergent properties...")
    print("(Analyzing patterns of collaboration, novelty, and innovation)\n")

    tracker = EmergentPropertyTracker()

    # Load and analyze
    if not tracker.load_messages():
        print("[ERROR] Could not load messages from persistence log")
        print("[INFO] Make sure conversation_logs/current_session.jsonl exists")
        return False

    print(f"[OK] Loaded {len(tracker.messages)} messages")

    # Extract conversations
    convs = tracker.extract_conversations()
    print(f"[OK] Extracted {len(convs)} conversations")

    # Run all analyses
    print("\n[ANALYSIS] Running emergence detection...\n")

    # Diversity analysis
    diversity = tracker.analyze_diversity()
    print("[DIVERSITY ANALYSIS]")
    print(f"  Vocabulary size: {diversity['vocabulary_size']} unique words")
    print(f"  Unique concepts: {diversity['unique_concepts']}")
    print(f"  Concept entropy: {diversity['concept_entropy']}")
    print(f"  Message length variance: {diversity['message_length']['std_dev']}")

    # Novelty analysis
    novelty = tracker.analyze_novelty()
    print("\n[NOVELTY ANALYSIS]")
    print(f"  Novelty score: {novelty['novelty_score']}/100")
    print(f"  Cross-domain references: {novelty['innovation_indicators']['cross_domain_refs']}")
    print(f"  Problem reframings: {novelty['innovation_indicators']['new_problem_framings']}")
    print(f"  Contradiction resolutions: {novelty['innovation_indicators']['contradictions_resolved']}")

    # Solution quality
    quality = tracker.analyze_solution_quality()
    print("\n[SOLUTION QUALITY]")
    print(f"  Completeness: {quality['solution_completeness']:.1f}%")
    print(f"  Specificity: {quality['solution_specificity']:.1f}%")
    print(f"  Feasibility: {quality['feasibility_score']:.1f}%")
    print(f"  Risk awareness: {quality['risk_awareness']:.1f}%")

    # Collaboration
    collab = tracker.analyze_collaboration()
    print("\n[COLLABORATION PATTERNS]")
    for speaker, pct in collab['turn_balance'].items():
        print(f"  {speaker}: {pct}% of turns")
    print(f"  Iterative improvement: {collab['iterative_improvement']:.1f}%")
    print(f"  Disagreement ratio: {collab['disagreement_patterns']['disagreement_ratio']:.2f}")
    print(f"  Productive disagreements: {collab['disagreement_patterns']['productive_disagreements']}")
    print(f"  Q&A effectiveness: {collab['q_a_effectiveness']:.1f}%")

    # Emergence
    emergence = tracker.analyze_emergence()
    print("\n[EMERGENCE INDICATORS]")
    print(f"  Novelty component: {emergence['novelty_score']:.1f}/100")
    print(f"  Solution quality component: {emergence['solution_quality_avg']:.1f}/100")
    print(f"  Collaboration component: {emergence['collaboration_quality']:.1f}/100")
    print(f"  *** EMERGENCE CONFIDENCE: {emergence['emergence_confidence']:.1f}/100 ***")
    print(f"\n  Detected signals:")
    if emergence['detected_signals']:
        for signal in emergence['detected_signals']:
            print(f"    - {signal}")
    else:
        print("    (None detected)")

    # Summary and interpretation
    print("\n" + "="*80)
    print("  INTERPRETATION")
    print("="*80)

    confidence = emergence['emergence_confidence']

    if confidence >= 70:
        print("\n[HIGH EMERGENCE POTENTIAL] >>>")
        print("  Strong signs of emergent properties detected.")
        print("  - Agents are collaborating effectively")
        print("  - Novel solutions are being explored")
        print("  - Complex interactions producing valuable insights")
    elif confidence >= 40:
        print("\n[MODERATE EMERGENCE] **")
        print("  Some signs of emergent behavior detected.")
        print("  - Agents demonstrate collaboration")
        print("  - Some novel thinking present")
        print("  - Room for deeper interaction")
    else:
        print("\n[LOW EMERGENCE] ==")
        print("  Limited signs of emergent properties.")
        print("  - Agents mostly exchanging information")
        print("  - Less novel collaboration visible")
        print("  - Consider deeper interaction patterns")

    # Key findings
    print("\n[KEY FINDINGS]")

    findings = []

    if emergence['detected_signals']:
        findings.append(f"Detected {len(emergence['detected_signals'])} types of emergence signals")

    if collab['disagreement_patterns']['productive_disagreements'] > 0:
        findings.append("Agents productively resolve disagreements")

    if novelty['innovation_indicators']['cross_domain_refs'] >= 3:
        findings.append("Strong cross-domain thinking present")

    if collab['iterative_improvement'] > 50:
        findings.append("Clear pattern of iterative improvement")

    if diversity['concept_entropy'] > 2.0:
        findings.append("High diversity in concepts explored")

    for i, finding in enumerate(findings, 1):
        print(f"  {i}. {finding}")

    if not findings:
        print("  No major patterns detected")

    # Recommendations
    print("\n[RECOMMENDATIONS FOR NEXT PHASE]")

    recommendations = []

    if confidence < 50:
        recommendations.append("Increase interaction depth - more back-and-forth rounds")
        recommendations.append("Encourage explicit disagreement and debate")

    if quality['solution_completeness'] < 60:
        recommendations.append("Push for more complete solutions addressing implementation")

    if collab['q_a_effectiveness'] < 70:
        recommendations.append("Structure more Q&A patterns for better knowledge transfer")

    if novelty['innovation_indicators']['new_problem_framings'] == 0:
        recommendations.append("Encourage problem reframing to find novel angles")

    for i, rec in enumerate(recommendations, 1):
        print(f"  {i}. {rec}")

    # Generate full report
    print("\n" + "="*80)
    print("  GENERATING FULL REPORT")
    print("="*80 + "\n")

    report = tracker.generate_report()

    # Save report
    report_file = Path("reports/emergence_analysis.json")
    report_file.parent.mkdir(parents=True, exist_ok=True)

    import json
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"[OK] Full report saved to: {report_file}")
    print(f"[OK] Contains detailed metrics on:")
    print(f"    - Diversity analysis")
    print(f"    - Novelty metrics")
    print(f"    - Solution quality assessment")
    print(f"    - Collaboration patterns")
    print(f"    - Emergence indicators")

    print("\n" + "="*80)
    print("  ANALYSIS COMPLETE")
    print("="*80)

    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
