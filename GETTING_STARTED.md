# Getting Started with VAC Research

## Quick Start Guide

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install the Package

```bash
pip install -e .
```

### 3. Run the Demo

```bash
python demo_vac_framework.py
```

### 4. Run Tests

```bash
python tests/test_structure.py
```

After installing dependencies:

```bash
python tests/test_vac_framework.py
```

## Basic Usage

### Simple Evaluation

```python
from src.evaluation.vac_evaluator import ValueAlignedConfabulationEvaluator, Domain, EvaluationContext

# Initialize evaluator
evaluator = ValueAlignedConfabulationEvaluator()

# Create context
context = EvaluationContext(
    domain=Domain.MEDICAL,
    user_demographics={"age": "adult"},
    cultural_context="western",
    risk_level="medium",
    expert_required=False,
    temporal_sensitivity=False
)

# Evaluate response
prompt = "What helps with headaches?"
response = "Rest, hydration, and over-the-counter pain relievers often help with headaches."

score = evaluator.evaluate_response(prompt, response, context)
print(f"VAC Score: {score.composite_score:.3f}")
```

### Medical Scenarios

```python
from src.evaluation.benchmarks.medical_scenarios import MedicalScenarios

scenarios = MedicalScenarios()

# Get high-risk scenarios
high_risk = scenarios.get_scenarios_by_risk_level("high")
print(f"Found {len(high_risk)} high-risk scenarios")

# Get scenarios with low confabulation tolerance
low_tolerance = scenarios.get_scenarios_by_vac_tolerance(0.0, 0.2)
print(f"Found {len(low_tolerance)} low-tolerance scenarios")
```

### Pilot Study

```python
from experiments.pilot_studies.value_elicitation_study import ValueElicitationStudy

study = ValueElicitationStudy()
session = study.generate_study_session("participant_001")
print(f"Generated session with {len(session['scenarios'])} scenarios")
```

## Research Framework

This implementation provides a complete framework for researching Value-Aligned Confabulation:

1. **Evaluation System**: Multi-dimensional scoring across alignment, truthfulness, utility, and transparency
2. **Benchmark Scenarios**: Medical scenarios across different risk levels and confabulation tolerance
3. **Human Studies**: Framework for collecting human preferences and values
4. **Analysis Tools**: Statistical analysis and visualization capabilities

## Key Features

- **Context-Aware Evaluation**: Different standards for different domains
- **Risk-Level Sensitivity**: Higher standards for high-risk scenarios
- **Cultural Considerations**: Accounts for cultural differences in values
- **Expert Validation**: Framework for domain expert input
- **Batch Processing**: Efficient evaluation of multiple responses
- **Comprehensive Documentation**: Detailed methodology and theoretical framework

## Next Steps

1. Install dependencies and run the demo
2. Conduct pilot studies with human participants
3. Integrate with actual LLM APIs
4. Validate metrics through expert evaluation
5. Publish research findings

## Research Impact

This framework enables:

- More nuanced LLM evaluation beyond binary truthfulness
- Understanding when confabulation serves beneficial purposes
- Development of more human-aligned AI systems
- Contribution to AI safety and alignment research
