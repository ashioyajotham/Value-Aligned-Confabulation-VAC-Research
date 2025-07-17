"""
Basic tests for the VAC evaluation framework.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.evaluation.vac_evaluator import ValueAlignedConfabulationEvaluator, Domain, EvaluationContext
from src.evaluation.benchmarks.medical_scenarios import MedicalScenarios
from src.evaluation.metrics.alignment_metrics import AlignmentMetrics
from src.evaluation.metrics.truthfulness_metrics import TruthfulnessMetrics
from src.evaluation.metrics.utility_metrics import UtilityMetrics


def test_vac_evaluator_initialization():
    """Test that VAC evaluator initializes correctly."""
    evaluator = ValueAlignedConfabulationEvaluator()
    assert evaluator is not None
    assert evaluator.alignment_metrics is not None
    assert evaluator.truthfulness_metrics is not None
    assert evaluator.utility_metrics is not None
    print("✓ VAC Evaluator initialization test passed")


def test_medical_scenarios():
    """Test medical scenarios functionality."""
    scenarios = MedicalScenarios()
    assert len(scenarios.scenarios) > 0
    
    # Test getting scenarios by risk level
    high_risk = scenarios.get_scenarios_by_risk_level("high")
    assert len(high_risk) > 0
    
    # Test getting scenarios by VAC tolerance
    low_tolerance = scenarios.get_scenarios_by_vac_tolerance(0.0, 0.2)
    assert len(low_tolerance) > 0
    
    print("✓ Medical scenarios test passed")


def test_evaluation_context():
    """Test evaluation context creation."""
    context = EvaluationContext(
        domain=Domain.MEDICAL,
        user_demographics={"age": "adult"},
        cultural_context="western",
        risk_level="high",
        expert_required=True,
        temporal_sensitivity=False
    )
    assert context.domain == Domain.MEDICAL
    assert context.risk_level == "high"
    print("✓ Evaluation context test passed")


def test_basic_evaluation():
    """Test basic VAC evaluation."""
    evaluator = ValueAlignedConfabulationEvaluator()
    
    context = EvaluationContext(
        domain=Domain.MEDICAL,
        user_demographics={"age": "adult"},
        cultural_context="western",
        risk_level="medium",
        expert_required=False,
        temporal_sensitivity=False
    )
    
    prompt = "What are some ways to stay healthy?"
    response = "Regular exercise, balanced diet, adequate sleep, and stress management can help maintain good health."
    
    score = evaluator.evaluate_response(prompt, response, context)
    
    assert 0.0 <= score.composite_score <= 1.0
    assert 0.0 <= score.alignment_score <= 1.0
    assert 0.0 <= score.truthfulness_score <= 1.0
    assert 0.0 <= score.utility_score <= 1.0
    assert 0.0 <= score.transparency_score <= 1.0
    
    print("✓ Basic evaluation test passed")


def test_alignment_metrics():
    """Test alignment metrics."""
    metrics = AlignmentMetrics()
    
    prompt = "How can I help someone who is sad?"
    response = "Listening with empathy, offering support, and being present can help someone who is feeling sad."
    
    score = metrics.calculate_alignment(prompt, response, "western", "personal_advice")
    
    assert 0.0 <= score <= 1.0
    print("✓ Alignment metrics test passed")


def test_truthfulness_metrics():
    """Test truthfulness metrics."""
    metrics = TruthfulnessMetrics()
    
    prompt = "What is the capital of France?"
    response = "The capital of France is Paris."
    
    score = metrics.calculate_truthfulness(prompt, response, None, "general")
    
    assert 0.0 <= score <= 1.0
    print("✓ Truthfulness metrics test passed")


def test_utility_metrics():
    """Test utility metrics."""
    metrics = UtilityMetrics()
    
    prompt = "How do I bake a cake?"
    response = "To bake a cake, you'll need flour, sugar, eggs, and butter. Mix the ingredients, pour into a pan, and bake at 350°F for 30-40 minutes."
    
    score = metrics.calculate_utility(prompt, response, "general")
    
    assert 0.0 <= score <= 1.0
    print("✓ Utility metrics test passed")


def test_domain_weight_differences():
    """Test that different domains produce different scores."""
    evaluator = ValueAlignedConfabulationEvaluator()
    
    prompt = "What might help with anxiety?"
    speculative_response = "Many people find that deep breathing, meditation, or talking to friends can help with anxiety. Some also find comfort in creative activities."
    
    domains_to_test = [Domain.MEDICAL, Domain.CREATIVE, Domain.EDUCATIONAL]
    scores = {}
    
    for domain in domains_to_test:
        context = EvaluationContext(
            domain=domain,
            user_demographics={"age": "adult"},
            cultural_context="western",
            risk_level="medium",
            expert_required=False,
            temporal_sensitivity=False
        )
        
        score = evaluator.evaluate_response(prompt, speculative_response, context)
        scores[domain] = score.composite_score
    
    # Scores should be different across domains
    unique_scores = set(scores.values())
    assert len(unique_scores) > 1, "Domain-specific scoring should produce different results"
    
    print("✓ Domain weight differences test passed")


def test_batch_evaluation():
    """Test batch evaluation functionality."""
    evaluator = ValueAlignedConfabulationEvaluator()
    
    evaluation_data = [
        {
            "prompt": "What is 2+2?",
            "response": "2+2 equals 4."
        },
        {
            "prompt": "What is the weather like?",
            "response": "I don't have access to current weather data."
        }
    ]
    
    context = EvaluationContext(
        domain=Domain.GENERAL,
        user_demographics={"age": "adult"},
        cultural_context="western",
        risk_level="low",
        expert_required=False,
        temporal_sensitivity=False
    )
    
    results = evaluator.batch_evaluate(evaluation_data, context)
    
    assert len(results) == len(evaluation_data)
    assert all(0.0 <= result.composite_score <= 1.0 for result in results)
    
    print("✓ Batch evaluation test passed")


def run_all_tests():
    """Run all tests."""
    print("Running VAC Framework Tests...")
    print("=" * 40)
    
    tests = [
        test_vac_evaluator_initialization,
        test_medical_scenarios,
        test_evaluation_context,
        test_basic_evaluation,
        test_alignment_metrics,
        test_truthfulness_metrics,
        test_utility_metrics,
        test_domain_weight_differences,
        test_batch_evaluation
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"✗ {test.__name__} failed: {e}")
            failed += 1
    
    print("=" * 40)
    print(f"Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! The VAC framework is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the implementation.")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
