from setuptools import find_packages, setup

setup(
    name="video_understanding",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "numpy",
        "opencv-python",
        "pillow",
        "torch",
        "tensorflow",
        "scikit-learn",
        "pytest",
        "pytest-cov",
        "pytest-asyncio",
        "aiohttp",
    ],
    python_requires=">=3.10",
)
