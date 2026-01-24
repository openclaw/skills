from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pdf-form-filler",
    version="0.1.0",
    author="Raul C. Sîmpetru",
    author_email="raul.simpetru@fau.de",
    description="Fill PDF forms programmatically with text and checkboxes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/RaulSimpetru/pdf-form-filler",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Office/Business",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=[
        "pdfrw>=0.4",
    ],
)
