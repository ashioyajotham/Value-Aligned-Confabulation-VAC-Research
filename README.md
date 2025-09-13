# Value-Aligned Confabulation (VAC) Research

## Overview

This repository contains the implementation of research on **Value-Aligned Confabulation (VAC)** - a novel approach to evaluating LLM outputs that distinguishes between harmful "hallucination" and beneficial "hallucination" that aligns with human values.

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

```text
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

## Running the Value Elicitation Pilot (CLI)

Collect human preferences about when confabulation is acceptable using the interactive CLI:

```powershell
# From the project root
python -m experiments.pilot_studies.value_elicitation_study --participant your_id --outdir experiments\results

# Simulated mode for testing (no manual input)
python -m experiments.pilot_studies.value_elicitation_study --simulate --limit 2 --outdir experiments\results
```

Outputs are saved under a timestamped folder in `experiments/results/` with both `results.json` (full data and analysis) and `responses.csv` (flat table).

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

This is a research project focused on advancing our understanding of beneficial AI confabulation. We welcome contributions from researchers, developers, and AI safety practitioners.

### Ways to Contribute

- **Research**: New evaluation metrics, benchmark scenarios, human study protocols
- **Technical**: Code improvements, integrations, analysis tools
- **Documentation**: Methodology improvements, examples, tutorials
- **Community**: Cross-cultural validation, expert reviews, ethical guidelines

Please see our [Contributing Guide](CONTRIBUTING.md) for detailed information on how to get involved.

### Research Ethics

This project follows ethical guidelines for human subjects research and AI safety. All contributions should consider potential societal impacts and promote beneficial uses of confabulation research.

## Acknowledgements

This research builds upon important insights from the AI research community:

### Terminology

- **Geoffrey Hinton** has advocated for using "confabulation" rather than "hallucination" when describing AI-generated content that isn't grounded in training data, emphasizing that the term better captures the nature of how language models generate responses. See his discussion in the [60 Minutes interview](https://www.youtube.com/watch?v=qrvK_KuIeJk) and the [full interview](https://www.youtube.com/watch?v=qyH3NxFz3Aw).

- **Andrej Karpathy** has discussed the nuanced nature of what we call "hallucinations" in language models, noting that not all factually ungrounded outputs are equally problematic - a key insight that motivates this research. His thoughts on this topic have been shared in various [Twitter/X discussions](https://x.com/karpathy/status/1733299213503787018).

### Foundational Work

- This research was originally conceptualized in "[Hallucinations in Large Language Models](https://ashioyajotham.substack.com/p/hallucinations-in-large-language)" (Ashioya, 2024), which explored the need for more nuanced evaluation of AI-generated content.

### Research Community

We acknowledge the broader AI safety and alignment research community, whose ongoing work on AI evaluation, human preference modeling, and value alignment provides the foundation for this research.

## License

MIT License - See [LICENSE](LICENSE) file for details.

## Citation

If you use this work in your research, please cite:

```bibtex
@misc{vac_research_2025,
  title={Value-Aligned Confabulation: Moving Beyond Binary Truthfulness in LLM Evaluation},
  author={Ashioya Jotham Victor},
  year={2025},
  note={Research in progress}
}
```
