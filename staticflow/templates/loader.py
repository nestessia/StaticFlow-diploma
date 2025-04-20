"""Template loader for StaticFlow."""
import toml
from pathlib import Path
from typing import Dict, Any
import re


def load_template_file(file_path: str) -> str:
    """Load a template file content."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def load_default_template(template_name: str, language: str = 'ru') -> str:
    """
    Load a default template file from the default templates directory.
    
    Args:
        template_name: Name of the template file
        language: Language code (ISO 639-1)
        
    Returns:
        Template content as string
    """
    template_dir = Path(__file__).parent / 'default'
    
    # Сначала проверяем наличие языковой версии шаблона
    lang_template_dir = template_dir / language
    lang_file_path = lang_template_dir / template_name
    
    # Если есть языковая версия, используем её
    if lang_file_path.exists():
        return load_template_file(str(lang_file_path))
    
    # Если нет языковой версии, используем стандартную версию
    file_path = template_dir / template_name
    
    if not file_path.exists():
        raise FileNotFoundError(f"Default template not found: {template_name}")
    
    return load_template_file(str(file_path))


def load_welcome_content(language: str = 'ru') -> str:
    """
    Load the default welcome content for new projects.
    
    Args:
        language: Language code (ISO 639-1)
        
    Returns:
        Welcome content as string
    """
    return load_default_template('welcome.md', language)


def load_base_template(language: str = 'ru') -> str:
    """
    Load the default base HTML template for new projects.
    
    Args:
        language: Language code (ISO 639-1)
        
    Returns:
        Base template content as string
    """
    return load_default_template('base.html', language)


def load_default_styles(language: str = 'ru') -> str:
    """
    Load the default CSS styles for new projects.
    
    Args:
        language: Language code (ISO 639-1)
        
    Returns:
        Default styles content as string
    """
    return load_default_template('style.css', language)


def load_default_config() -> Dict[str, Any]:
    """Load the default configuration for new projects."""
    config_path = Path(__file__).parent / 'default' / 'config.toml'
    with open(config_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Удаляем секции [languages.xx] из TOML перед загрузкой
    # Это более надежный способ, чем удаление после загрузки
    content = re.sub(r'\n\[languages\..*?\].*?(?=\n\[|\Z)', '', content, flags=re.DOTALL)
    
    # Удаляем строку с languages = ["ru", "en", "es"]
    content = re.sub(r'\nlanguages\s*=\s*\[.*?\]', '', content)
    
    # Загружаем очищенную конфигурацию
    config = toml.loads(content)
    
    print(f"DEFAULT CONFIG LOADED: {config}")
    return config 