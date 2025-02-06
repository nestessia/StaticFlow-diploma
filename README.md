# StaticFlow

A modern static site generator framework built with Python.

## Features

- Asynchronous content processing
- Incremental builds
- Smart caching
- Multiple template engine support
- Advanced metadata system
- Plugin architecture
- SEO optimization
- Multi-language support

## Installation

```bash
pip install staticflow
```

## Quick Start

```python
from staticflow import Engine
from pathlib import Path

# Initialize the engine
engine = Engine()

# Set up directories
engine.initialize(
    source_dir=Path("content"),
    output_dir=Path("public"),
    templates_dir=Path("templates")
)

# Build the site
engine.build()
```

## Development

1. Clone the repository:
```bash
git clone https://github.com/yourusername/staticflow.git
cd staticflow
```

2. Install dependencies:
```bash
poetry install
```

3. Run tests:
```bash
poetry run pytest
```

## License

MIT License 