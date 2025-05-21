// EditorUtils.rst.js — десериализация rst для блочного редактора
(function() {
    function deserializeRstContent(content) {
        if (!content) {
            console.log("RST content is empty, adding default paragraph");
            this.addBlock('paragraph');
            return;
        }
        this.blocks = [];
        const lines = content.split('\n');
        let i = 0;
        let currentBlock = null;
        while (i < lines.length) {
            let line = lines[i];
            // Headings (underline style)
            if (i + 1 < lines.length && (lines[i + 1].match(/^=+$/) || lines[i + 1].match(/^-+$/) || lines[i + 1].match(/^~+$/))) {
                const level = lines[i + 1][0];
                let type = 'heading2';
                if (level === '=') type = 'heading1';
                else if (level === '-') type = 'heading2';
                else if (level === '~') type = 'heading3';
                this.blocks.push({
                    id: `block_${Date.now()}_${Math.floor(Math.random() * 1000)}`,
                    type,
                    content: line,
                    meta: { level: type.replace('heading', 'h') }
                });
                i += 2;
                currentBlock = null;
            }
            // Code block: .. code-block:: lang
            else if (line.trim().startsWith('.. code-block::')) {
                const lang = line.trim().split('::')[1].trim() || '';
                let codeContent = '';
                i++;
                // Пропускаем пустые строки после объявления блока
                while (i < lines.length && lines[i].trim() === '') i++;
                // Собираем строки с отступом
                while (i < lines.length && (lines[i].startsWith('    ') || lines[i].trim() === '')) {
                    codeContent += (codeContent ? '\n' : '') + lines[i].replace(/^    /, '');
                    i++;
                }
                this.blocks.push({
                    id: `block_${Date.now()}_${Math.floor(Math.random() * 1000)}`,
                    type: 'code',
                    content: codeContent,
                    meta: { language: lang }
                });
                currentBlock = null;
            }
            // Note/Warning blocks: .. note::, .. warning::
            else if (line.trim().startsWith('.. note::') || line.trim().startsWith('.. warning::')) {
                const type = line.includes('note') ? 'info' : 'warning';
                let blockContent = '';
                i++;
                // Пропускаем пустые строки после объявления блока
                while (i < lines.length && lines[i].trim() === '') i++;
                // Собираем строки с отступом
                while (i < lines.length && (lines[i].startsWith('    ') || lines[i].trim() === '')) {
                    blockContent += (blockContent ? '\n' : '') + lines[i].replace(/^    /, '');
                    i++;
                }
                this.blocks.push({
                    id: `block_${Date.now()}_${Math.floor(Math.random() * 1000)}`,
                    type,
                    content: blockContent,
                    meta: { title: type === 'info' ? 'Информация' : 'Предупреждение' }
                });
                currentBlock = null;
            }
            // Empty line - reset current block
            else if (line.trim() === '') {
                currentBlock = null;
                i++;
            }
            // Paragraph (default)
            else {
                if (currentBlock && currentBlock.type === 'paragraph') {
                    currentBlock.content += '\n' + line;
                } else {
                    currentBlock = {
                        id: `block_${Date.now()}_${Math.floor(Math.random() * 1000)}`,
                        type: 'paragraph',
                        content: line,
                        meta: {}
                    };
                    this.blocks.push(currentBlock);
                }
                i++;
            }
        }
        console.log("Deserialized RST content into blocks:", this.blocks);
    }
    window.deserializeRstContent = deserializeRstContent;
})(); 