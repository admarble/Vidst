from setuptools import find_packages, setup

setup(
    name="video-understanding-ai",
    version="0.1.0",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "pytest>=7.0.0",
        "pytest-cov>=4.0.0",
        "black>=22.0.0",
        "isort>=5.0.0",
        "coverage-badge>=1.1.0",
    ],
)
