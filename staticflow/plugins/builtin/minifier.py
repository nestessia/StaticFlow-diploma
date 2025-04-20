from typing import Dict, Any
import re
from bs4 import BeautifulSoup
import csscompressor
import jsmin
from ..core.base import Plugin, PluginMetadata


class MinifierPlugin(Plugin):
    """Плагин для минификации контента."""
    
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="minifier",
            version="1.0.0",
            description="Минификация HTML, CSS и JavaScript",
            author="StaticFlow",
            requires_config=False
        )
    
    def process_content(self, content: str) -> str:
        """Обрабатывает и минифицирует HTML-контент."""
        if not content:
            return content
            
        # Минифицируем HTML
        content = self._minify_html(content)
        
        # Минифицируем встроенные стили и скрипты
        content = self._minify_inline_assets(content)
        
        return content
    
    def on_post_page(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Минифицирует HTML контент страницы."""
        content = context.get('content', '')
        if not content:
            return context
            
        # Минифицируем HTML
        content = self._minify_html(content)
        
        # Минифицируем встроенные стили и скрипты
        content = self._minify_inline_assets(content)
        
        context['content'] = content
        return context
    
    def _minify_html(self, content: str) -> str:
        """Минифицирует HTML."""
        # Используем BeautifulSoup для парсинга
        soup = BeautifulSoup(content, 'html.parser')
        
        # Удаляем комментарии
        for comment in soup.find_all(string=lambda text: isinstance(text, str) and text.strip().startswith('<!--')):
            comment.extract()
        
        # Удаляем пробелы между тегами
        content = str(soup)
        content = re.sub(r'>\s+<', '><', content)
        content = re.sub(r'\s{2,}', ' ', content)
        
        return content.strip()
    
    def _minify_inline_assets(self, content: str) -> str:
        """Минифицирует встроенные стили и скрипты."""
        soup = BeautifulSoup(content, 'html.parser')
        
        # Минифицируем CSS
        for style in soup.find_all('style'):
            if style.string:
                style.string = self._minify_css(style.string)
        
        # Минифицируем JavaScript
        for script in soup.find_all('script'):
            if script.string and not script.get('src'):
                script.string = self._minify_js(script.string)
        
        return str(soup)
    
    def _minify_css(self, css: str) -> str:
        """Минифицирует CSS."""
        try:
            return csscompressor.compress(css)
        except Exception as e:
            print(f"Ошибка при минификации CSS: {e}")
            return css
    
    def _minify_js(self, js: str) -> str:
        """Минифицирует JavaScript."""
        try:
            return jsmin.jsmin(js)
        except Exception as e:
            print(f"Ошибка при минификации JavaScript: {e}")
            return js 