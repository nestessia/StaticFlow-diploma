from typing import Dict, Any
from bs4 import BeautifulSoup
from ..core.base import Plugin, PluginMetadata


class SEOPlugin(Plugin):
    """Плагин для SEO оптимизации."""
    
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="seo",
            version="1.0.0",
            description="SEO оптимизация страниц",
            author="StaticFlow",
            requires_config=True
        )
    
    def process_content(self, content: str) -> str:
        """Пустая реализация для совместимости с интерфейсом плагина.
        SEO плагин не изменяет контент на этом этапе."""
        return content
    
    def validate_config(self) -> bool:
        """Проверяет конфигурацию плагина."""
        required = {'site_name', 'site_description', 'default_image'}
        return all(key in self.config for key in required)
    
    def on_post_page(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Обрабатывает страницу после рендеринга."""
        content = context.get('content', '')
        if not content:
            return context
            
        soup = BeautifulSoup(content, 'html.parser')
        
        # Добавляем Open Graph теги
        self._add_open_graph_tags(soup, context)
        
        # Добавляем Twitter Card теги
        self._add_twitter_card_tags(soup, context)
        
        # Добавляем Schema.org разметку
        self._add_schema_markup(soup, context)
        
        # Оптимизируем заголовки
        self._optimize_headings(soup)
        
        # Добавляем alt к изображениям
        self._optimize_images(soup)
        
        context['content'] = str(soup)
        return context
    
    def _add_open_graph_tags(self, soup: BeautifulSoup, context: Dict[str, Any]) -> None:
        """Добавляет Open Graph теги."""
        head = soup.find('head')
        if not head:
            return
            
        # Основные OG теги
        og_tags = {
            'og:title': context.get('title', self.config['site_name']),
            'og:description': context.get('description', self.config['site_description']),
            'og:type': 'website',
            'og:image': context.get('image', self.config['default_image']),
            'og:url': context.get('url', ''),
            'og:site_name': self.config['site_name']
        }
        
        for prop, content in og_tags.items():
            if content:
                meta = soup.new_tag('meta', property=prop, content=content)
                head.append(meta)
    
    def _add_twitter_card_tags(self, soup: BeautifulSoup, context: Dict[str, Any]) -> None:
        """Добавляет Twitter Card теги."""
        head = soup.find('head')
        if not head:
            return
            
        twitter_tags = {
            'twitter:card': 'summary_large_image',
            'twitter:title': context.get('title', self.config['site_name']),
            'twitter:description': context.get('description', self.config['site_description']),
            'twitter:image': context.get('image', self.config['default_image'])
        }
        
        for name, content in twitter_tags.items():
            if content:
                meta = soup.new_tag('meta', name=name, content=content)
                head.append(meta)
    
    def _add_schema_markup(self, soup: BeautifulSoup, context: Dict[str, Any]) -> None:
        """Добавляет Schema.org разметку."""
        schema = {
            "@context": "https://schema.org",
            "@type": "WebPage",
            "name": context.get('title', self.config['site_name']),
            "description": context.get('description', self.config['site_description']),
            "url": context.get('url', ''),
            "image": context.get('image', self.config['default_image'])
        }
        
        script = soup.new_tag('script', type='application/ld+json')
        script.string = str(schema)
        soup.find('head').append(script)
    
    def _optimize_headings(self, soup: BeautifulSoup) -> None:
        """Оптимизирует заголовки на странице."""
        # Проверяем наличие H1
        h1_tags = soup.find_all('h1')
        if not h1_tags:
            # Если нет H1, создаем его из title
            title = soup.find('title')
            if title:
                h1 = soup.new_tag('h1')
                h1.string = title.string
                soup.body.insert(0, h1)
    
    def _optimize_images(self, soup: BeautifulSoup) -> None:
        """Оптимизирует изображения на странице."""
        for img in soup.find_all('img'):
            # Добавляем alt если его нет
            if not img.get('alt'):
                img['alt'] = img.get('src', '').split('/')[-1].split('.')[0]
            
            # Добавляем loading="lazy" для отложенной загрузки
            if not img.get('loading'):
                img['loading'] = 'lazy' 