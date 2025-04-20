"""
Интернационализация и локализация для StaticFlow.

Этот модуль обеспечивает поддержку многоязычности в StaticFlow,
включая перевод строк, форматирование дат и другие аспекты локализации.
"""

import json
import yaml
import toml
from pathlib import Path
from typing import Dict, Any, Optional, Union
import logging

# Получаем логгер
logger = logging.getLogger("staticflow.i18n")

# Язык по умолчанию
DEFAULT_LANGUAGE = "ru"


class I18N:
    """Класс для работы с локализацией."""
    
    def __init__(self):
        self.default_language = DEFAULT_LANGUAGE
        self.languages = [DEFAULT_LANGUAGE]
        self.translations: Dict[str, Dict[str, str]] = {}
        self.config: Dict[str, Any] = {}
        self.is_multilingual = False
        
    def configure(self, config: Dict[str, Any]) -> None:
        """
        Настройка локализации из конфигурации сайта.
        
        Args:
            config: Конфигурация сайта
        """
        self.config = config
        
        # Установка языка по умолчанию из конфигурации
        self.default_language = config.get("language", DEFAULT_LANGUAGE)
        logger.debug(f"Default language set to: {self.default_language}")
        
        # Получаем конфигурацию языков
        languages_config = config.get("languages", None)
        logger.debug(f"Languages config: {languages_config}")
        
        # Языки могут быть заданы как список или как словарь (в TOML)
        language_codes = []
        
        if languages_config:
            # Если это список, используем его напрямую
            if isinstance(languages_config, list):
                language_codes = languages_config
            # Если это словарь, используем ключи как коды языков
            elif isinstance(languages_config, dict):
                language_codes = list(languages_config.keys())
        
        # Если список языков не пуст, используем его
        if language_codes:
            self.languages = language_codes.copy()  # Создаем копию списка
            logger.debug(f"Languages from config: {self.languages}")
            
            # Убедимся, что язык по умолчанию в списке языков
            if self.default_language not in self.languages:
                self.languages.append(self.default_language)
                logger.debug(f"Added default language to list: {self.languages}")
            
            # Проверяем, является ли сайт многоязычным (больше одного языка)
            self.is_multilingual = len(self.languages) > 1
        else:
            # Если languages не указан, используем только язык по умолчанию
            self.languages = [self.default_language]
            self.is_multilingual = False
            logger.debug(f"Using only default language: {self.languages}")
        
        logger.info(
            f"I18N configured: multilingual={self.is_multilingual}, "
            f"languages={self.languages}"
        )
    
    def load_translations(self, i18n_dir: Union[str, Path]) -> None:
        """
        Загрузка переводов из директории с языковыми файлами.
        
        Args:
            i18n_dir: Путь к директории с языковыми файлами
        """
        # Если сайт не многоязычный, не загружаем переводы
        if not self.is_multilingual:
            return
            
        i18n_path = Path(i18n_dir)
        
        if not i18n_path.exists():
            return
        
        # Загружаем переводы для каждого языка
        for lang in self.languages:
            lang_dir = i18n_path / lang
            
            if not lang_dir.exists():
                continue
                
            self.translations[lang] = {}
            
            # Загружаем все файлы переводов в директории
            for file_path in lang_dir.glob("*.*"):
                suffix = file_path.suffix.lower()
                
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        if suffix == ".json":
                            translations = json.load(f)
                        elif suffix in (".yaml", ".yml"):
                            translations = yaml.safe_load(f)
                        elif suffix == ".toml":
                            translations = toml.load(f)
                        else:
                            continue
                            
                        # Добавляем переводы из файла
                        if isinstance(translations, dict):
                            self.translations[lang].update(translations)
                except Exception as e:
                    print(f"Error loading translation file {file_path}: {e}")
    
    def translate(self, key: str, language: Optional[str] = None) -> str:
        """
        Перевод строки на указанный язык.
        
        Args:
            key: Ключ строки для перевода
            language: Язык перевода (если None, используется язык по умолчанию)
            
        Returns:
            Переведенная строка или ключ, если перевод не найден
        """
        # Если сайт не многоязычный, возвращаем ключ
        if not self.is_multilingual:
            return key
            
        if language is None:
            language = self.default_language
            
        # Проверка наличия переводов для языка
        if language not in self.translations:
            return key
            
        # Возвращаем перевод или исходный ключ
        return self.translations[language].get(key, key)
    
    def get_content_path(self, base_path: Union[str, Path], language: str) -> Path:
        """
        Получение пути к контенту для указанного языка.
        
        Args:
            base_path: Базовый путь к директории с контентом
            language: Язык
            
        Returns:
            Путь к директории с контентом для указанного языка
        """
        base = Path(base_path)
        
        # Если сайт не многоязычный или язык по умолчанию, используем базовый путь
        if not self.is_multilingual or language == self.default_language:
            return base
            
        # Для других языков используем поддиректорию
        return base / language
    
    def get_url_prefix(self, language: str) -> str:
        """
        Получение префикса URL для указанного языка.
        
        Args:
            language: Язык
            
        Returns:
            Префикс URL для указанного языка
        """
        # Если сайт не многоязычный или для языка по умолчанию префикс пустой
        if not self.is_multilingual or language == self.default_language:
            return ""
            
        # Для других языков используем код языка
        return f"/{language}"


# Глобальный экземпляр для использования в приложении
i18n = I18N()


def get_i18n() -> I18N:
    """
    Получение глобального экземпляра I18N.
    
    Returns:
        Глобальный экземпляр I18N
    """
    return i18n 