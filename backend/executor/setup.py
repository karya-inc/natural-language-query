from setuptools import setup, find_packages

setup(
    name="executor",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "openai",
    ],
    python_requires=">=3.6",
)
