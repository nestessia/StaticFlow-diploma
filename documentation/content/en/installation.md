---
title: Installation
date: 2025-05-20
author: nestessia
tags: [installation, setup, requirements]
format: markdown
template: en_page.html
language: en
---

# Installing StaticFlow

This section covers the StaticFlow installation process and requirements.

## Requirements

StaticFlow requires:

- Python 3.8 or higher
- pip (Python package manager)
- Git (optional, for repository work)

## Installation via pip

The easiest way to install StaticFlow is using pip:

```bash
pip install staticflow-framework
```

## Verifying installation

After installation, check that StaticFlow is available:

```bash
staticflow --version
```

## Updating

To update to the latest version:

```bash
pip install --upgrade staticflow-framework
```

## Installation on Windows

1. Download and install Python from the official website: https://www.python.org/downloads/
   - During installation, be sure to select "Add Python to PATH".
2. Open Command Prompt (Win+R → cmd).
3. Check Python and pip versions:
   ```bash
   python --version
   pip --version
   ```
4. Install StaticFlow:
   ```bash
   pip install staticflow-framework
   ```
5. Run StaticFlow:
   ```bash
   staticflow-framework --version
   ```

## Installation on Ubuntu

1. Update packages:
   ```bash
   sudo apt update && sudo apt upgrade
   ```
2. Install Python and pip:
   ```bash
   sudo apt install python3 python3-pip
   ```
3. Check Python version:
   ```bash
   python3 --version
   pip3 --version
   ```
4. Install StaticFlow:
   ```bash
   pip3 install staticflow-framework
   ```
5. Run StaticFlow:
   ```bash
   staticflow-framework --version
   ```

## Installation on macOS

1. Make sure Homebrew is installed (if not — install from https://brew.sh/):
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
2. Install Python and pip:
   ```bash
   brew install python
   ```
3. Check Python version:
   ```bash
   python3 --version
   pip3 --version
   ```
4. Install StaticFlow:
   ```bash
   pip3 install staticflow-framework
   ```
5. Run StaticFlow:
   ```bash
   staticflow-framework --version
   ```

## Troubleshooting

### Common issues

1. **"command not found" error**
   - Make sure Python and pip are installed
   - Check that the Python executable directory is in PATH

2. **Dependency issues**
   - Try creating a new virtual environment
   - Update pip: `pip install --upgrade pip`

3. **Build errors**
   - Check Python version
   - Make sure all dependencies are installed

### Getting help

If you encounter problems:

- Check [GitHub Issues](https://github.com/nestessia/StaticFlow-diploma/issues)

- Create a new issue with detailed problem description 