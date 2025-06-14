from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="staticflow",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Modern Static Site Generator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/staticflow",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Markup",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "staticflow=staticflow.cli:cli",
        ],
    },
    package_data={
        "staticflow": [
            "admin/static/dist/*",
            "admin/static/css/*",
            "admin/templates/*",
            "core/*",
            "utils/*",
            "cli/*",
            "deploy/*",
            "plugins/*",
            "themes/*",
            "tests/*",
        ],
    },
) 