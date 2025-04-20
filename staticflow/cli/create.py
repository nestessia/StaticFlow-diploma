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
    load_base_template,
    load_default_styles,
    load_default_config
)
import json

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
                "[bold]Default site language[/bold] (ISO code)",
                default=detected_lang
            )
            if is_valid_language_code(lang_input):
                language = lang_input.lower()
            else:
                console.print(
                    f"[yellow]'{lang_input}' is not a valid ISO code "
                    "language code[/yellow]"
                )
        
        # 5. Многоязычность
        add_languages = Prompt.ask(
            "[bold]Add additional languages?[/bold] (comma-separated ISO codes, e.g., en,es,fr)",
            default=""
        )
        
        languages = [language]
        is_multilingual = False
        
        if add_languages:
            additional_langs = [lang.strip().lower() for lang in add_languages.split(",")]
            for lang in additional_langs:
                if is_valid_language_code(lang) and lang != language:
                    languages.append(lang)
                elif lang != language:
                    console.print(
                        f"[yellow]'{lang}' is not a valid ISO code "
                        "language code, skipping[/yellow]"
                    )
            
            # Проверяем, получилось ли добавить дополнительные языки
            is_multilingual = len(languages) > 1
        
        # Create project structure
        project_path.mkdir(parents=True)
        (project_path / "content").mkdir()
        (project_path / "templates").mkdir()
        (project_path / "static").mkdir()
        (project_path / "static/css").mkdir(parents=True)
        
        # Создаем структуру для многоязычности только если она нужна
        if is_multilingual:
            (project_path / "static/i18n").mkdir(parents=True)
            for lang in languages:
                # Создаем директории для контента на разных языках
                if lang != language:  # Для основного языка уже создали директорию
                    (project_path / "content" / lang).mkdir(parents=True, exist_ok=True)
                # Создаем директории для переводов
                (project_path / "static" / "i18n" / lang).mkdir(parents=True, exist_ok=True)
        
        (project_path / "public").mkdir()

        # Update config with project info
        config = load_default_config()
        config["site_name"] = site_name
        config["description"] = description
        config["author"] = author
        config["language"] = language
        
        # При обновлении удаляем все связанные с языками ключи
        # для предотвращения ошибок при сохранении в TOML
        for key in list(config.keys()):
            if key == "languages" or (isinstance(key, str) and key.startswith("languages.")):
                del config[key]
        
        # Добавляем список языков только для многоязычных сайтов
        if is_multilingual:
            # Список языков для TOML (массив строк)
            config["languages"] = languages.copy()
            
            # Создаем секции для каждого языка
            for lang in languages:
                # Создаем вложенные словари только для TOML
                config[f"languages.{lang}"] = {
                    "site_name": site_name,
                    "description": get_description_for_language(lang, description)
                }

        # Отладочный вывод конечной конфигурации для понимания структуры
        print(f"FINAL CONFIG STRUCTURE: {config}")
        
        # Write files
        with open(project_path / "config.toml", "w", encoding="utf-8") as f:
            toml.dump(config, f)

        # Создаем index.md для каждого языка в многоязычном режиме или только для основного языка
        if is_multilingual:
            for lang in languages:
                content_dir = project_path / "content"
                if lang != language:
                    content_dir = content_dir / lang
                
                with open(content_dir / "index.md", "w", encoding="utf-8") as f:
                    f.write(load_welcome_content(lang))
        else:
            # Для моноязычного сайта создаем только основной файл
            with open(project_path / "content/index.md", "w", encoding="utf-8") as f:
                f.write(load_welcome_content(language))

        with open(project_path / "templates/base.html", "w", 
                  encoding="utf-8") as f:
            f.write(load_base_template(language))

        with open(project_path / "static/css/style.css", "w", 
                  encoding="utf-8") as f:
            f.write(load_default_styles(language))
            
        # Создаем файлы переводов для каждого языка только в многоязычном режиме
        if is_multilingual:
            for lang in languages:
                i18n_dir = project_path / "static" / "i18n" / lang
                
                # Базовый словарь переводов
                translations = {}
                if lang == "ru":
                    translations = {
                        "powered_by": "Сайт создан с помощью StaticFlow",
                        "home": "Главная",
                        "about": "О нас",
                        "contact": "Контакты"
                    }
                elif lang == "en":
                    translations = {
                        "powered_by": "Powered by StaticFlow",
                        "home": "Home",
                        "about": "About",
                        "contact": "Contact"
                    }
                elif lang == "es":
                    translations = {
                        "powered_by": "Desarrollado con StaticFlow",
                        "home": "Inicio",
                        "about": "Acerca de",
                        "contact": "Contacto"
                    }
                else:
                    translations = {
                        "powered_by": "Powered by StaticFlow",
                        "home": "Home",
                        "about": "About",
                        "contact": "Contact"
                    }
                    
                # Записываем файл переводов
                with open(i18n_dir / "common.json", "w", encoding="utf-8") as f:
                    json.dump(translations, f, indent=2, ensure_ascii=False)

        # Выводим разное сообщение в зависимости от того, многоязычный сайт или нет
        success_message = f"[green]Project '{site_name}' created successfully![/green]\n\n"
        if is_multilingual:
            success_message += f"Your site supports the following languages: {', '.join(languages)}\n\n"
        
        success_message += f"cd {path}\nstaticflow serve"
        
        console.print(Panel.fit(
            success_message,
            title="Next steps"
        ))

    except Exception as e:
        console.print(f"[red]Error creating project:[/red] {str(e)}")


def get_description_for_language(lang, default_description):
    """Возвращает описание на указанном языке."""
    if lang == "ru":
        return "Новый сайт на StaticFlow"
    elif lang == "en":
        return "A new StaticFlow site"
    elif lang == "es":
        return "Un nuevo sitio con StaticFlow"
    else:
        return default_description 