from setuptools import setup, find_packages
import os
from pathlib import Path

# Read the contents of your README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="value-aligned-confabulation",
    version="0.1.0",
    author="Ashioya Jotham Victor",
    author_email="victorashioya960@gmail.com",
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
    install_requires=[
        "certifi==2025.7.14",
        "charset-normalizer==3.4.2",
        "cmudict==1.1.1",
        "idna==3.10",
        "importlib_metadata==8.7.0",
        "importlib_resources==6.5.2",
        "joblib==1.5.1",
        "numpy==2.3.2",
        "pyphen==0.17.2",
        "requests==2.32.4",
        "scikit-learn==1.7.1",
        "scipy==1.16.1",
        "textstat==0.7.8",
        "threadpoolctl==3.6.0",
        "urllib3==2.5.0",
        "zipp==3.23.0"
    ],
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