
from setuptools import setup, find_packages

setup(
    name="adaptive-executor",
    version="0.1.0",
    description="Adaptive thread pool executor with dynamic scaling policies",
    author="",
    packages=find_packages(),
    install_requires=[
        "pytz",
        "psutil",
    ],
    python_requires=">=3.7",
)
