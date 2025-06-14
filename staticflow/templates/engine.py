from pathlib import Path
from typing import Any, Dict
from jinja2 import Environment, FileSystemLoader, select_autoescape


class TemplateEngine:
    """Движок шаблонизации на основе Jinja2."""

    def __init__(self, templates_dir: Path):
        self.templates_dir = templates_dir
        self.env = Environment(
            loader=FileSystemLoader(str(templates_dir)),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True
        )
        self._setup_filters()
        self._setup_globals()

    def _setup_filters(self) -> None:
        """Настраивает пользовательские фильтры."""
        self.env.filters.update({
            'datetime': lambda dt: dt.strftime('%Y-%m-%d %H:%M'),
            'date': lambda dt: dt.strftime('%Y-%m-%d'),
            'time': lambda dt: dt.strftime('%H:%M'),
        })

    def _setup_globals(self) -> None:
        """Настраивает глобальные переменные."""
        self.env.globals.update({
            'site_name': 'StaticFlow Site',
            'site_description': 'A site built with StaticFlow',
            'static_url': '/static',
        })

    def render(self, template_name: str, context: Dict[str, Any]) -> str:
        """Рендерит шаблон с заданным контекстом."""
        template = self.env.get_template(template_name)
        return template.render(**context)

    def render_string(self, template_string: str, context: Dict[str, Any]) -> str:
        """Рендерит строку шаблона с заданным контекстом."""
        template = self.env.from_string(template_string)
        return template.render(**context)

    def add_filter(self, name: str, filter_func: Any) -> None:
        """Добавляет пользовательский фильтр."""
        self.env.filters[name] = filter_func

    def add_global(self, name: str, value: Any) -> None:
        """Добавляет глобальную переменную."""
        self.env.globals[name] = value

    def get_template(self, template_name: str) -> Any:
        """Получает объект шаблона по имени."""
        return self.env.get_template(template_name)
