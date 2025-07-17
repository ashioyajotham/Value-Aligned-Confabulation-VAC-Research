from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="value-aligned-confabulation",
    version="0.1.0",
    author="VAC Research Team",
    author_email="research@vac-project.org",
    description="A framework for evaluating Value-Aligned Confabulation in Large Language Models",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/vac-research/value-aligned-confabulation",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Text Processing :: Linguistic",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=0.991",
            "pre-commit>=2.20.0",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
        "analysis": [
            "jupyter>=1.0.0",
            "ipywidgets>=7.7.0",
            "plotly>=5.8.0",
            "wandb>=0.13.0",
        ],
        "web": [
            "flask>=2.2.0",
            "flask-cors>=3.0.0",
            "flask-sqlalchemy>=3.0.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "vac-evaluate=src.scripts.run_evaluation:main",
            "vac-collect-data=src.scripts.collect_human_data:main",
            "vac-generate-report=src.scripts.generate_report:main",
            "vac-run-experiment=src.scripts.run_experiment:main",
        ],
    },
    package_data={
        "": ["*.yaml", "*.json", "*.txt"],
    },
    include_package_data=True,
    zip_safe=False,
)
