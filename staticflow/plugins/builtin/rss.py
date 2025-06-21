from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
import xml.etree.ElementTree as ET
from ..core.base import Plugin, PluginMetadata
from ...core.page import Page


class RSSPlugin(Plugin):
    """Плагин для генерации RSS-ленты."""
    
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="rss",
            version="1.0.0",
            description="Генератор RSS-ленты",
            author="StaticFlow",
            requires_config=True
        )
    
    def process_content(self, content: str) -> str:
        """Пустая реализация для совместимости с интерфейсом плагина.
        RSS плагин не изменяет контент на этом этапе."""
        return content
    
    def validate_config(self) -> bool:
        """Проверяет конфигурацию плагина."""
        required = {
            'site_name',
            'site_description',
            'base_url',
            'output_path',
            'language'
        }
        return all(key in self.config for key in required)
    
    def post_build(self, site) -> None:
        """Генерирует RSS-ленту после сборки сайта."""
        print("RSS Plugin: post_build called")
        pages = site.get_all_pages()
        print(f"RSS Plugin: found {len(pages)} pages")
        if not pages:
            print("RSS Plugin: no pages found")
            return
            
        # Фильтруем только страницы с валидной датой публикации
        pages = [
            p for p in pages 
            if 'date' in p.metadata and p.metadata['date'] is not None
        ]
        print(f"RSS Plugin: {len(pages)} pages with valid date")
        
        # Сортируем по дате (новые первыми)
        pages.sort(
            key=lambda x: (
                x.metadata['date'] if x.metadata['date'] else datetime.min
            ),
            reverse=True
        )
        
        # Берем только 10 последних записей
        rss = self._create_rss(pages[:10], site)
        print("RSS Plugin: created RSS structure")
        self._save_rss(rss)
        print("RSS Plugin: saved RSS feed")
    
    def _create_rss(self, pages: List[Page], site) -> ET.Element:
        """Создает XML структуру RSS."""
        # Создаем корневой элемент
        rss = ET.Element('rss', {'version': '2.0'})
        channel = ET.SubElement(rss, 'channel')
        
        # Добавляем информацию о канале
        title = ET.SubElement(channel, 'title')
        title.text = self.config['site_name']
        
        description = ET.SubElement(channel, 'description')
        description.text = self.config['site_description']
        
        link = ET.SubElement(channel, 'link')
        base_url = self.config['base_url']
        if isinstance(base_url, Path):
            base_url = str(base_url)
        link.text = base_url
        
        language = ET.SubElement(channel, 'language')
        language.text = self.config['language']
        
        generator = ET.SubElement(channel, 'generator')
        generator.text = 'StaticFlow RSS Generator'
        
        last_build = ET.SubElement(channel, 'lastBuildDate')
        last_build.text = datetime.now().strftime('%a, %d %b %Y %H:%M:%S %z')
        
        # Добавляем элементы
        for page in pages:
            item = ET.SubElement(channel, 'item')
            
            # Заголовок
            item_title = ET.SubElement(item, 'title')
            item_title.text = page.metadata.get('title', '')
            
            # Ссылка
            item_link = ET.SubElement(item, 'link')
            base_url = self.config['base_url']
            if isinstance(base_url, Path):
                base_url = str(base_url)
            else:
                base_url = str(base_url)
                
            # Получаем URL страницы
            if page.output_path and site.output_dir:
                page_url = str(
                    page.output_path.relative_to(site.output_dir)
                )
            else:
                page_url = str(page.source_path)
                
            # Теперь оба значения точно строки
            base_url_str = base_url.rstrip('/')
            page_url_str = page_url.lstrip('/')
            item_link.text = (
                f"{base_url_str}/"
                f"{page_url_str}"
            )
            
            # Описание
            item_desc = ET.SubElement(item, 'description')
            item_desc.text = page.metadata.get('description', '')
            
            # Дата публикации
            if 'date' in page.metadata:
                pub_date = ET.SubElement(item, 'pubDate')
                pub_date.text = page.metadata['date'].strftime('%a, %d %b %Y %H:%M:%S %z')
            
            # Уникальный идентификатор для RSS-агрегаторов
            guid = ET.SubElement(item, 'guid')
            guid.set('isPermaLink', 'true')
            guid.text = item_link.text
            
            # Автор
            if 'author' in page.metadata and page.metadata['author'] is not None:
                author = ET.SubElement(item, 'author')
                author.text = page.metadata['author']
                
            # Категории
            if 'tags' in page.metadata and page.metadata['tags'] is not None:
                for tag in page.metadata['tags']:
                    if tag is not None:  # Пропускаем None теги
                        category = ET.SubElement(item, 'category')
                        category.text = str(tag)  # Преобразуем в строку на всякий случай
                    
        return rss
    
    def _save_rss(self, rss: ET.Element) -> None:
        """Сохраняет RSS-ленту."""
        output_path_str = self.config['output_path']
        
        # Преобразуем к Path только если это строка
        if not isinstance(output_path_str, Path):
            output_dir = Path(output_path_str)
        else:
            output_dir = output_path_str
            
        output_path = output_dir / 'feed.xml'
        
        # Создаем директорию если её нет
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Записываем файл
        tree = ET.ElementTree(rss)
        tree.write(
            output_path,
            encoding='utf-8',
            xml_declaration=True,
            method='xml'
        ) 