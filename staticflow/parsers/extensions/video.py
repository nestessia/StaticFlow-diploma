from markdown.extensions import Extension
from markdown.blockprocessors import BlockProcessor
import xml.etree.ElementTree as etree
import re


class VideoBlockProcessor(BlockProcessor):
    RE = re.compile(r'^!VIDEO\((.*?)\)$')

    def test(self, parent, block):
        return bool(self.RE.match(block.strip()))

    def run(self, parent, blocks):
        block = blocks.pop(0).strip()
        m = self.RE.match(block)
        
        if not m:
            return False
            
        src = m.group(1)
        
        # Создаем видео элемент
        video = etree.SubElement(parent, 'video')
        video.set('controls', 'controls')
        
        # Добавляем source элемент
        etree.SubElement(
            video,
            'source',
            {
                'src': src,
                'type': 'video/mp4'
            }
        )
        
        video.text = 'Your browser does not support the video tag.'
        return True


class VideoExtension(Extension):
    def extendMarkdown(self, md):
        md.parser.blockprocessors.register(
            VideoBlockProcessor(md.parser),
            'video',
            15  # Более высокий приоритет, чем у параграфов
        )


def makeExtension(**kwargs):
    return VideoExtension(**kwargs)
