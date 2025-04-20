"""Template loader for StaticFlow."""
import toml
from pathlib import Path
from typing import Dict, Any


def load_template_file(file_path: str) -> str:
    """Load a template file content."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def load_default_template(template_name: str) -> str:
    """Load a default template file from the default templates directory."""
    template_dir = Path(__file__).parent / 'default'
    file_path = template_dir / template_name
    
    if not file_path.exists():
        raise FileNotFoundError(f"Default template not found: {template_name}")
    
    return load_template_file(str(file_path))


def load_welcome_content() -> str:
    """Load the default welcome content for new projects."""
    return load_default_template('welcome.md')


def load_base_template() -> str:
    """Load the default base HTML template for new projects."""
    return load_default_template('base.html')


def load_default_styles() -> str:
    """Load the default CSS styles for new projects."""
    return load_default_template('style.css')


def load_default_config() -> Dict[str, Any]:
    """Load the default configuration for new projects."""
    config_path = Path(__file__).parent / 'default' / 'config.toml'
    with open(config_path, 'r', encoding='utf-8') as f:
        return toml.load(f) 