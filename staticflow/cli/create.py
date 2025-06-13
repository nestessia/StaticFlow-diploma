import click
import toml
import locale
import geocoder
import pycountry
import getpass
import os
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from ..templates import (
    load_welcome_content,
    load_default_styles,
    load_default_config,
    load_default_template
)
from staticflow.core.config import Config

console = Console()


def detect_language():
    """Определить язык пользователя по его IP."""
    try:
        # Получаем страну по IP
        g = geocoder.ip('me')
        if g.country:
            # Находим язык страны
            country = pycountry.countries.get(alpha_2=g.country)
            if country:
                # Находим основной язык страны
                languages = pycountry.languages.get(
                    alpha_2=country.alpha_2.lower()
                )
                if languages:
                    return languages.alpha_2
        
        # Если не получилось определить по IP, используем локаль системы
        loc = locale.getlocale()[0]
        if loc:
            lang_code = loc.split('_')[0]
            return lang_code
    except Exception:
        pass
    
    # Если всё остальное не сработало, возвращаем английский
    return "en"


def get_system_username():
    """Получить имя пользователя из системы."""
    try:
        # Пробуем получить полное имя пользователя
        # На Unix-подобных системах
        if hasattr(os, 'getlogin'):
            return os.getlogin()
        # Или более надежный метод через getpass
        return getpass.getuser()
    except Exception:
        return ""


def is_valid_language_code(code):
    """Проверяет, является ли код допустимым кодом языка ISO-639-1."""
    if len(code) != 2:
        return False
    try:
        language = pycountry.languages.get(alpha_2=code.lower())
        return language is not None
    except (KeyError, AttributeError):
        return False


def get_language_name(code):
    """Получить название языка по его коду."""
    try:
        language = pycountry.languages.get(alpha_2=code.lower())
        if language and hasattr(language, 'name'):
            return language.name
        return code
    except (KeyError, AttributeError):
        return code


@click.command()
@click.argument('path')
def create(path: str):
    """Create new StaticFlow project"""
    project_path = Path(path)
    if project_path.exists():
        console.print(f"[red]Error:[/red] Directory {path} already exists")
        return

    try:
        # Интерактивный опрос для настройки проекта
        console.print(Panel.fit(
            "[bold]Let's configure your new StaticFlow site[/bold]",
            title="New Project Setup"
        ))
        
        # 1. Имя сайта (обязательно)
        site_name = ""
        while not site_name:
            site_name = Prompt.ask(
                "[bold]Site name[/bold]", 
                default=project_path.name
            )
            if not site_name:
                console.print("[yellow]Site name cannot be empty[/yellow]")
        
        # 2. Описание сайта (опционально)
        description = Prompt.ask(
            "[bold]Site description[/bold] (enter to skip)",
            default="A new StaticFlow site"
        )
        
        # 3. Автор сайта (обязательно, по умолчанию - системное имя пользователя)
        default_author = get_system_username()
        author = ""
        while not author:
            author = Prompt.ask(
                "[bold]Author name[/bold]", 
                default=default_author
            )
            if not author:
                console.print("[yellow]Author name cannot be empty[/yellow]")
        
        # 4. Основной язык сайта (с автоопределением и проверкой)
        detected_lang = detect_language()
        default_language = None
        while default_language is None:
            lang_input = Prompt.ask(
                "[bold]Default site language[/bold] (ISO code)",
                default=detected_lang
            )
            if is_valid_language_code(lang_input):
                default_language = lang_input.lower()
            else:
                console.print(
                    f"[yellow]'{lang_input}' is not a valid ISO code "
                    "language code[/yellow]"
                )
        
        # 5. Спрашиваем о дополнительных языках
        additional_languages = []
        multilingual = Confirm.ask(
            "\n[bold]Do you want to add additional languages?[/bold]",
            default=False
        )
        
        if multilingual:
            console.print("\n[bold]Adding additional languages:[/bold]")
            console.print(
                "Enter language ISO codes (e.g., en, fr, es). "
                "Type 'done' when finished."
            )
            
            while True:
                lang_input = Prompt.ask(
                    "[bold]Additional language[/bold] (or 'done' to finish)"
                )
                
                if lang_input.lower() == 'done':
                    break
                    
                if lang_input.lower() == default_language:
                    console.print(
                        f"[yellow]'{lang_input}' is already set as the "
                        "default language[/yellow]"
                    )
                    continue
                    
                if lang_input.lower() in additional_languages:
                    console.print(
                        f"[yellow]'{lang_input}' is already added[/yellow]"
                    )
                    continue
                    
                if is_valid_language_code(lang_input):
                    additional_languages.append(lang_input.lower())
                    language_name = get_language_name(lang_input)
                    console.print(
                        f"  Added [green]{language_name}[/green] "
                        f"({lang_input.lower()})"
                    )
                else:
                    console.print(
                        f"[yellow]'{lang_input}' is not a valid ISO code "
                        "language code[/yellow]"
                    )
        
        # Create project structure
        project_path.mkdir(parents=True)
        
        # Adjust directory structure based on multilingual settings
        if multilingual:
            # Create language-specific directories
            content_dir = project_path / "content"
            content_dir.mkdir()
            
            # Create default language directory
            (content_dir / default_language).mkdir()
            
            # Create additional language directories
            for lang in additional_languages:
                (content_dir / lang).mkdir()
                
            # Print information about created directories
            console.print("\n[bold]Created language directories:[/bold]")
            default_name = get_language_name(default_language)
            console.print(
                f"  Default language: [green]{default_name}[/green] "
                f"({default_language})"
            )
            console.print("  Additional languages:")
            for lang in additional_languages:
                lang_name = get_language_name(lang)
                console.print(
                    f"    - [green]{lang_name}[/green] ({lang})"
                )
        else:
            # Standard content directory for monolingual site
            (project_path / "content").mkdir()
            
        (project_path / "templates").mkdir()
        (project_path / "static").mkdir()
        (project_path / "static/css").mkdir(parents=True)
        from staticflow.core.config import Config
        config_path = project_path / "config.toml"
        config = Config(config_path)
        output_dir = config.get('output_dir')
        (project_path / output_dir).mkdir(exist_ok=True)

        # Update config with project info
        config = load_default_config()
        config["site_name"] = site_name
        config["description"] = description
        config["author"] = author
        config["language"] = default_language

        if multilingual:
            console.print("\n[bold]Created language directories:[/bold]")
            default_name = get_language_name(default_language)
            console.print(
                f"  Default language: [green]{default_name}[/green] "
                f"({default_language})"
            )
            console.print("  Additional languages:")
            for lang in additional_languages:
                lang_name = get_language_name(lang)
                console.print(
                    f"    - [green]{lang_name}[/green] ({lang})"
                )

        # Write config file
        with open(project_path / "config.toml", "w", encoding="utf-8") as f:
            toml.dump(config, f)

        # Write content files based on language settings
        if multilingual:
            # Only create standard content file in main content directory
            # No files in language directories
            with open(project_path / "content/index.md", "w", 
                      encoding="utf-8") as f:
                f.write(load_welcome_content())
        else:
            # Standard monolingual content
            with open(project_path / "content/index.md", "w", 
                      encoding="utf-8") as f:
                f.write(load_welcome_content())

        # Write template files
        with open(project_path / "templates/base.html", "w", 
                  encoding="utf-8") as f:
            f.write(load_default_template('base.html'))

        # Создаём page.html
        with open(project_path / "templates/page.html", "w", encoding="utf-8") as f:
            f.write(load_default_template('page.html'))

        # Write CSS files
        with open(project_path / "static/css/style.css", "w", 
                  encoding="utf-8") as f:
            f.write(load_default_styles())

        console.print(Panel.fit(
            f"[green]Project '{site_name}' created successfully![/green]\n\n"
            f"cd {path}\n"
            "staticflow serve",
            title="Next steps"
        ))

    except Exception as e:
        console.print(f"[red]Error creating project:[/red] {str(e)}") 