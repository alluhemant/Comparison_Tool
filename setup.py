from setuptools import setup, find_packages

setup(
    name="xml_comparison",
    version="0.1",
    packages=find_packages(where="."),  # explicitly look in the current directory
    package_dir={"": "."},              # Root package directory
    install_requires=[
        'fastapi',
        'uvicorn',
        'streamlit',
        'httpx',
        'deepdiff'
    ],
    python_requires='>=3.8',
)