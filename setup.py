from setuptools import setup

setup(
    name="ASE_Project",
    version="1.0.0",
    packages=["src", "test", "src.study"],
    license="LICENSE.md",
    description="ASE project for Multi-objective Semi-Supervised System",
    long_description=open("README.md", encoding="utf8").read(),
)
