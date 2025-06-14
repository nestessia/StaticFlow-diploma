from markdown.extensions import Extension
from markdown.blockprocessors import BlockProcessor
import xml.etree.ElementTree as etree
import re


class AudioBlockProcessor(BlockProcessor):
    RE = re.compile(r'^!AUDIO\((.*?)\)$')

    def test(self, parent, block):
        return bool(self.RE.match(block.strip()))

    def run(self, parent, blocks):
        block = blocks.pop(0).strip()
        m = self.RE.match(block)
        
        if not m:
            return False
            
        src = m.group(1)
        
        # Создаем аудио элемент
        audio = etree.SubElement(parent, 'audio')
        audio.set('controls', 'controls')
        
        # Добавляем source элемент
        etree.SubElement(
            audio,
            'source',
            {
                'src': src,
                'type': 'audio/mpeg'
            }
        )
        
        audio.text = 'Your browser does not support the audio tag.'
        return True


class AudioExtension(Extension):
    def extendMarkdown(self, md):
        md.parser.blockprocessors.register(
            AudioBlockProcessor(md.parser),
            'audio',
            15  # Более высокий приоритет, чем у параграфов
        )


def makeExtension(**kwargs):
    return AudioExtension(**kwargs) 