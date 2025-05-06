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
from rich.prompt import Prompt
from ..templates import (
    load_welcome_content,
    load_default_styles,
    load_default_config,
    load_default_template
)

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
        
        # 4. Язык сайта (с автоопределением и проверкой)
        detected_lang = detect_language()
        language = None
        while language is None:
            lang_input = Prompt.ask(
                "[bold]Site language[/bold] (ISO code)",
                default=detected_lang
            )
            if is_valid_language_code(lang_input):
                language = lang_input.lower()
            else:
                console.print(
                    f"[yellow]'{lang_input}' is not a valid ISO code "
                    "language code[/yellow]"
                )
        
        # Create project structure
        project_path.mkdir(parents=True)
        (project_path / "content").mkdir()
        (project_path / "templates").mkdir()
        (project_path / "static").mkdir()
        (project_path / "static/css").mkdir(parents=True)
        (project_path / "public").mkdir()

        # Update config with project info
        config = load_default_config()
        config["site_name"] = site_name
        config["description"] = description
        config["author"] = author
        config["language"] = language

        # Write files
        with open(project_path / "config.toml", "w", encoding="utf-8") as f:
            toml.dump(config, f)

        with open(project_path / "content/index.md", "w", 
                  encoding="utf-8") as f:
            f.write(load_welcome_content())

        with open(project_path / "templates/base.html", "w", 
                  encoding="utf-8") as f:
            f.write(load_default_template('base.html'))

        # Создаём page.html
        with open(project_path / "templates/page.html", "w", encoding="utf-8") as f:
            f.write(load_default_template('page.html'))

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