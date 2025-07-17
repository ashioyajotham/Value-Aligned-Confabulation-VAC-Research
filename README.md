# Value-Aligned Confabulation (VAC) Research

## Overview

This repository contains the implementation of research on **Value-Aligned Confabulation (VAC)** - a novel approach to evaluating LLM outputs that distinguishes between harmful hallucination and beneficial confabulation that aligns with human values.

## Core Concept

Traditional LLM evaluation treats all factually ungrounded outputs as equally problematic "hallucinations." VAC research proposes that:

- **Harmful Hallucination**: Factually incorrect outputs that mislead or cause harm
- **Value-Aligned Confabulation**: LLM outputs that are factually ungrounded but align with human values and serve beneficial purposes
- **Truthfulness-Utility Trade-off**: The balance between factual accuracy and beneficial outcomes

## Key Research Questions

1. Can LLMs learn to confabulate in ways that align with human values?
2. How do we measure the alignment between beneficial confabulation and truthfulness?
3. What contextual factors determine when confabulation becomes harmful vs. helpful?

## Repository Structure

```
value-aligned-confabulation/
├── docs/                    # Research documentation
├── src/                     # Core implementation
│   ├── evaluation/         # Evaluation framework
│   ├── data/               # Data collection and management
│   ├── models/             # Model implementations
│   └── analysis/           # Analysis tools
├── experiments/            # Experimental protocols
├── tests/                  # Testing framework
├── configs/                # Configuration files
└── scripts/                # Utility scripts
```

## Installation

```bash
pip install -r requirements.txt
python setup.py install
```

## Quick Start

```python
from src.evaluation.vac_evaluator import ValueAlignedConfabulationEvaluator

evaluator = ValueAlignedConfabulationEvaluator()
score = evaluator.evaluate_response(prompt, response, context)
```

## Research Phases

### Phase 1: Foundation (Weeks 1-2)
- Core evaluation framework
- Initial benchmark scenarios
- Basic metrics implementation

### Phase 2: Human Studies (Weeks 3-4)
- Value elicitation study
- Expert judgment collection
- Baseline human preferences

### Phase 3: Model Evaluation (Weeks 5-6)
- Baseline model evaluation
- Cross-domain testing
- Alignment-truthfulness trade-off analysis

### Phase 4: Analysis & Iteration (Weeks 7-8)
- Statistical analysis
- Metric refinement
- Research publication preparation

## Contributing

This is a research project focused on advancing our understanding of beneficial AI confabulation. Contributions are welcome in the form of:

- New evaluation metrics
- Additional benchmark scenarios
- Human study protocols
- Analysis tools

## License

MIT License - See LICENSE file for details.

## Citation

If you use this work in your research, please cite:

```bibtex
@misc{vac_research_2025,
  title={Value-Aligned Confabulation: Moving Beyond Binary Truthfulness in LLM Evaluation},
  author={VAC Research Team},
  year={2025},
  note={Research in progress}
}
```
