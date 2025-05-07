from pathlib import Path
from typing import Any, Dict, Optional
import re
from datetime import datetime
import os


class Router:
    """URL router for StaticFlow."""
    
    # Стандартные шаблоны URL для различных типов контента
    # Аналогично Pelican URL формируются через шаблоны и подстановку переменных
    DEFAULT_URL_PATTERNS = {
        # Страницы имеют простые URL без вложенности по умолчанию
        "page": "{slug}.html",                           
        # Посты по категориям
        "post": "{category}/{slug}.html",                
        # Страницы тегов
        "tag": "tag/{name}.html",                        
        # Страницы категорий
        "category": "category/{name}.html",              
        # Страницы авторов 
        "author": "author/{name}.html",                  
        # Главная страница
        "index": "index.html",                           
        # Архив
        "archive": "archives.html"                       
    }
    
    # Шаблоны для сохранения файлов (могут отличаться от URL)
    DEFAULT_SAVE_AS_PATTERNS = {
        "page": "{slug}.html",  
        "post": "{category}/{slug}.html",
        "tag": "tag/{name}.html",
        "category": "category/{name}.html",
        "author": "author/{name}.html",
        "index": "index.html",
        "archive": "archives.html"
    }
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize router with optional routes from config."""
        # Копируем стандартные настройки
        self.url_patterns = self.DEFAULT_URL_PATTERNS.copy()
        self.save_as_patterns = self.DEFAULT_SAVE_AS_PATTERNS.copy()
        
        # Флаг использования чистых URL (без .html)
        self.use_clean_urls = False
        
        # Настройки языковых префиксов
        self.use_language_prefixes = False
        
        # Опция для исключения префикса для языка по умолчанию
        self.exclude_default_lang_prefix = True
        
        # Язык по умолчанию (будет переопределен из конфига)
        self.default_language = 'ru'
        
        # Обновляем конфигурацию если она предоставлена
        if config:
            self.update_config(config)
    
    def update_config(self, config: Dict[str, Any]) -> None:
        """Update router configuration from site config."""
        # Обновляем URL паттерны из конфига
        url_patterns = config.get('URL_PATTERNS', {})
        if url_patterns:
            self.url_patterns.update(url_patterns)
            
        # Обновляем SAVE_AS паттерны из конфига
        save_as_patterns = config.get('SAVE_AS_PATTERNS', {})
        if save_as_patterns:
            self.save_as_patterns.update(save_as_patterns)
            
        # Опция для чистых URL (без .html на конце)
        self.use_clean_urls = config.get('CLEAN_URLS', False)
        
        # Опция для использования языковых префиксов
        self.use_language_prefixes = config.get('USE_LANGUAGE_PREFIXES', True)
        
        # Опция для исключения префикса для языка по умолчанию
        self.exclude_default_lang_prefix = config.get('EXCLUDE_DEFAULT_LANG_PREFIX', True)
        
        # Язык по умолчанию (будет переопределен из конфига)
        self.default_language = config.get('default_language', 'ru')
    
    def get_url(self, content_type: str, metadata: Dict[str, Any]) -> str:
        """Получить URL для контента на основе типа и метаданных."""
        # Если в метаданных есть явное указание url - используем его
        if 'url' in metadata:
            return metadata['url']
        
        # Выбираем подходящий шаблон URL для типа контента
        pattern = self.url_patterns.get(content_type)
        if not pattern:
            # Если нет подходящего шаблона, используем slug или путь
            if 'slug' in metadata:
                return f"{metadata['slug']}.html"
            return ""
        
        # Заменяем переменные в шаблоне URL значениями из метаданных
        url = self._format_pattern(pattern, metadata)
        
        # Обрабатываем "чистые URL" если они включены
        if self.use_clean_urls and url.endswith('.html'):
            url = url[:-5]
        
        # Добавляем языковой префикс если включено
        if self.use_language_prefixes and 'language' in metadata:
            language = metadata['language']
            # Если язык не является языком по умолчанию или если мы не исключаем префикс для языка по умолчанию
            if language != self.default_language or not self.exclude_default_lang_prefix:
                if url == "index.html" or (self.use_clean_urls and url == "index"):
                    # Для индексной страницы создаем url вида /en/ или /en/index.html
                    if self.use_clean_urls:
                        url = f"{language}/"
                    else:
                        url = f"{language}/index.html"
                else:
                    # Для остальных страниц добавляем языковой префикс
                    url = f"{language}/{url}"
            
        return url
    
    def get_save_as(self, content_type: str, metadata: Dict[str, Any]) -> str:
        """Получить путь сохранения для контента."""
        # Если в метаданных есть явное указание save_as - используем его
        if 'save_as' in metadata:
            return metadata['save_as']
        
        # Выбираем подходящий шаблон для пути сохранения
        pattern = self.save_as_patterns.get(content_type)
        if not pattern:
            # Используем URL если нет шаблона save_as
            return self.get_url(content_type, metadata)
        
        # Заменяем переменные в шаблоне значениями из метаданных
        save_as = self._format_pattern(pattern, metadata)
        
        # Добавляем языковой префикс если включено
        if self.use_language_prefixes and 'language' in metadata:
            language = metadata['language']
            # Если язык не является языком по умолчанию или если мы не исключаем префикс для языка по умолчанию
            if language != self.default_language or not self.exclude_default_lang_prefix:
                if save_as == "index.html":
                    # Для индексной страницы создаем путь вида /en/index.html
                    save_as = f"{language}/index.html"
                else:
                    # Для остальных страниц добавляем языковой префикс
                    save_as = f"{language}/{save_as}"
        
        return save_as
    
    def get_output_path(
        self, base_dir: Path, content_type: str, metadata: Dict[str, Any]
    ) -> Path:
        """Получить полный путь для выходного файла."""
        save_as = self.get_save_as(content_type, metadata)
        
        # Проверяем, является ли save_as абсолютным путем
        if os.path.isabs(save_as):
            return Path(save_as)
        
        # Иначе объединяем с базовым каталогом
        return base_dir / save_as
    
    def _format_pattern(self, pattern: str, metadata: Dict[str, Any]) -> str:
        """Заменить все переменные в шаблоне значениями из метаданных."""
        result = pattern
        
        # Заменяем переменные в формате {name}
        for match in re.finditer(r'\{([^}]+)\}', pattern):
            key = match.group(1)
            
            # Обработка специальных переменных
            if key == 'category' and 'category' in metadata:
                # Может быть строкой или списком
                category = metadata['category']
                # Берем первую категорию если список
                if isinstance(category, list) and category:
                    replacement = category[0]
                else:
                    replacement = str(category)
            elif key in ('year', 'month', 'day') and 'date' in metadata:
                # Форматирование даты
                if key == 'year':
                    replacement = self._format_date(metadata['date'], '%Y')
                elif key == 'month':
                    replacement = self._format_date(metadata['date'], '%m')
                elif key == 'day':
                    replacement = self._format_date(metadata['date'], '%d')
                else:
                    replacement = ''
            else:
                # Обычная подстановка из метаданных
                replacement = str(metadata.get(key, ''))
            
            # Заменяем переменную в шаблоне
            pattern_to_replace = '{' + key + '}'
            result = result.replace(pattern_to_replace, replacement)
        
        # Обработка путей: замена двойных слэшей и т.д.
        return self._normalize_path(result)
    
    def _normalize_path(self, path: str) -> str:
        """Нормализовать путь (убрать двойные слэши и т.д.)."""
        # Заменяем двойные слэши на одинарные (не в URL)
        normalized = re.sub(r'(?<!:)//+', '/', path)
        # Удаляем слэш в конце если он есть (кроме корневого пути)
        if normalized.endswith('/') and len(normalized) > 1:
            normalized = normalized[:-1]
        return normalized
    
    def _format_date(self, date_value: Any, format_str: str) -> str:
        """Форматировать значение даты по шаблону."""
        if isinstance(date_value, datetime):
            return date_value.strftime(format_str)
        elif isinstance(date_value, str):
            try:
                date_obj = datetime.fromisoformat(date_value)
                return date_obj.strftime(format_str)
            except (ValueError, TypeError):
                return ""
        return "" 