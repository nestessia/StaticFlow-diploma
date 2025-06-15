from typing import Dict, Any
import re
import logging
from pathlib import Path
from bs4 import BeautifulSoup
import csscompressor
import jsmin
from ..core.base import Plugin, PluginMetadata

logger = logging.getLogger(__name__)

class MinifierPlugin(Plugin):
    """Плагин для минификации контента."""
    
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="minifier",
            version="1.0.0",
            description="Минификация HTML, CSS и JavaScript",
            author="StaticFlow",
            requires_config=True
        )
    
    def setup(self, config: Dict[str, Any]) -> None:
        """Настройка плагина с конфигурацией."""
        self.config = {
            "enabled": True,
            "minify_html": True,
            "minify_css": True,
            "minify_js": True,
            "preserve_comments": False,
            **(config or {})
        }
        logger.info(
            "Minifier plugin initialized with config: %s",
            self.config
        )
    
    def on_pre_asset(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Обрабатывает статические файлы перед копированием в output."""
        if not self.config.get("enabled", True):
            return context
            
        file_path = context.get("file_path")
        if not file_path:
            return context
            
        file_path = Path(file_path)
        if not file_path.exists():
            return context
            
        try:
            # Определяем тип файла по расширению
            if (file_path.suffix.lower() == '.css' and 
                    self.config.get("minify_css", True)):
                logger.debug("Minifying CSS file: %s", file_path)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                original_size = len(content)
                content = self._minify_css(content)
                new_size = len(content)
                if new_size != original_size:
                    reduction = (1 - new_size / original_size) * 100
                    logger.info(
                        "CSS file minified: %s (%d -> %d bytes, %.1f%% reduction)",
                        file_path,
                        original_size,
                        new_size,
                        reduction
                    )
                context["content"] = content
                    
            elif (file_path.suffix.lower() in ('.js', '.mjs') and 
                    self.config.get("minify_js", True)):
                logger.debug("Minifying JavaScript file: %s", file_path)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                original_size = len(content)
                content = self._minify_js(content)
                new_size = len(content)
                if new_size != original_size:
                    reduction = (1 - new_size / original_size) * 100
                    logger.info(
                        "JavaScript file minified: %s (%d -> %d bytes, %.1f%% "
                        "reduction)",
                        file_path,
                        original_size,
                        new_size,
                        reduction
                    )
                context["content"] = content
                    
        except Exception as e:
            logger.error("Error minifying file %s: %s", file_path, e)
            
        return context
    
    def process_content(self, content: str) -> str:
        """Обрабатывает и минифицирует HTML-контент."""
        if not content or not self.config.get("enabled", True):
            return content
            
        logger.debug("Processing content for minification")
        original_size = len(content)
            
        # Минифицируем HTML
        if self.config.get("minify_html", True):
            logger.debug("Minifying HTML")
            content = self._minify_html(content)
        
        # Минифицируем встроенные стили и скрипты
        minify_assets = (
            self.config.get("minify_css", True) or
            self.config.get("minify_js", True)
        )
        if minify_assets:
            logger.debug("Minifying inline assets")
            content = self._minify_inline_assets(content)
        
        new_size = len(content)
        if new_size != original_size:
            reduction = (1 - new_size / original_size) * 100
            logger.info(
                "Content minified: %d -> %d bytes (%.1f%% reduction)",
                original_size,
                new_size,
                reduction
            )
        
        return content
    
    def on_post_page(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Минифицирует HTML контент страницы."""
        if not self.config.get("enabled", True):
            return context
            
        content = context.get('content', '')
        if not content:
            return context
            
        url = context.get('url', 'unknown')
        logger.debug("Processing page for minification: %s", url)
        original_size = len(content)
            
        # Минифицируем HTML
        if self.config.get("minify_html", True):
            logger.debug("Minifying HTML")
            content = self._minify_html(content)
        
        # Минифицируем встроенные стили и скрипты
        minify_assets = (
            self.config.get("minify_css", True) or
            self.config.get("minify_js", True)
        )
        if minify_assets:
            logger.debug("Minifying inline assets")
            content = self._minify_inline_assets(content)
        
        new_size = len(content)
        if new_size != original_size:
            reduction = (1 - new_size / original_size) * 100
            logger.info(
                "Page minified: %s (%d -> %d bytes, %.1f%% reduction)",
                url,
                original_size,
                new_size,
                reduction
            )
        
        context['content'] = content
        return context
    
    def _minify_html(self, content: str) -> str:
        """Минифицирует HTML."""
        try:
            # Используем BeautifulSoup для парсинга
            soup = BeautifulSoup(content, 'html.parser')
            
            # Удаляем комментарии если не нужно их сохранять
            if not self.config.get("preserve_comments", False):
                comments = soup.find_all(string=lambda text: isinstance(text, str) and text.strip().startswith('<!--'))
                if comments:
                    logger.debug("Removing %d HTML comments", len(comments))
                for comment in comments:
                    comment.extract()
            
            # Удаляем пробелы между тегами
            content = str(soup)
            content = re.sub(r'>\s+<', '><', content)
            content = re.sub(r'\s{2,}', ' ', content)
            
            return content.strip()
        except Exception as e:
            logger.error("Error minifying HTML: %s", e)
            return content
    
    def _minify_inline_assets(self, content: str) -> str:
        """Минифицирует встроенные стили и скрипты."""
        try:
            soup = BeautifulSoup(content, 'html.parser')
            
            # Минифицируем CSS
            if self.config.get("minify_css", True):
                styles = soup.find_all('style')
                if styles:
                    logger.debug("Minifying %d style blocks", len(styles))
                for style in styles:
                    if style.string:
                        style.string = self._minify_css(style.string)
            
            # Минифицируем JavaScript
            minify_js = self.config.get("minify_js", True)
            if minify_js:
                scripts = soup.find_all('script')
                inline_scripts = [s for s in scripts if s.string and not s.get('src')]
                if inline_scripts:
                    logger.debug("Minifying %d inline script blocks", len(inline_scripts))
                for script in inline_scripts:
                    script.string = self._minify_js(script.string)
            
            return str(soup)
        except Exception as e:
            logger.error("Error minifying inline assets: %s", e)
            return content
    
    def _minify_css(self, css: str) -> str:
        """Минифицирует CSS."""
        try:
            return csscompressor.compress(css)
        except Exception as e:
            logger.error("Error minifying CSS: %s", e)
            return css
    
    def _minify_js(self, js: str) -> str:
        """Минифицирует JavaScript."""
        try:
            return jsmin.jsmin(js)
        except Exception as e:
            logger.error("Error minifying JavaScript: %s", e)
            return js 