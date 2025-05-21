// EditorUtils.md.js — десериализация markdown для блочного редактора
(function() {
    function deserializeMdContent(content) {
        if (!content) {
            console.log("Content is empty, adding default paragraph");
            this.addBlock('paragraph');
            return;
        }
        this.blocks = [];
        // Process content using a line-by-line approach that preserves the original order
        const lines = content.split('\n');
        let i = 0;
        let currentBlock = null;
        while (i < lines.length) {
            const line = lines[i];
            // Headings
            if (line.startsWith('# ')) {
                this.blocks.push({
                    id: `block_${Date.now()}_${Math.floor(Math.random() * 1000)}`,
                    type: 'heading1',
                    content: line.substring(2),
                    meta: { level: 'h1' }
                });
                currentBlock = null;
                i++;
            } else if (line.startsWith('## ')) {
                this.blocks.push({
                    id: `block_${Date.now()}_${Math.floor(Math.random() * 1000)}`,
                    type: 'heading2',
                    content: line.substring(3),
                    meta: { level: 'h2' }
                });
                currentBlock = null;
                i++;
            } else if (line.startsWith('### ')) {
                this.blocks.push({
                    id: `block_${Date.now()}_${Math.floor(Math.random() * 1000)}`,
                    type: 'heading3',
                    content: line.substring(4),
                    meta: { level: 'h3' }
                });
                currentBlock = null;
                i++;
            } 
            // Code blocks
            else if (line.startsWith('```')) {
                const language = line.substring(3);
                let codeContent = '';
                let j = i + 1;
                // Collect all lines until the closing ```
                while (j < lines.length && !lines[j].startsWith('```')) {
                    codeContent += (j > i + 1 ? '\n' : '') + lines[j];
                    j++;
                }
                // Skip the closing ``` if found
                if (j < lines.length) {
                    j++;
                }
                // Determine if this is a Mermaid diagram
                if (language.trim() === 'mermaid') {
                    this.blocks.push({
                        id: `block_${Date.now()}_${Math.floor(Math.random() * 1000)}`,
                        type: 'diagram',
                        content: codeContent,
                        meta: {}
                    });
                } else {
                    this.blocks.push({
                        id: `block_${Date.now()}_${Math.floor(Math.random() * 1000)}`,
                        type: 'code',
                        content: codeContent,
                        meta: { language: language.trim() }
                    });
                }
                currentBlock = null;
                i = j; // Skip to after the closing ```
            }
            // Math blocks
            else if (line.includes('$$')) {
                // Check if it's a single-line math block
                if (line.match(/\$\$(.*?)\$\$/)) {
                    const mathContent = line.match(/\$\$(.*?)\$\$/)[1];
                    this.blocks.push({
                        id: `block_${Date.now()}_${Math.floor(Math.random() * 1000)}`,
                        type: 'math',
                        content: mathContent,
                        meta: {}
                    });
                    i++;
                } else {
                    // Multi-line math block
                    let mathContent = '';
                    let j = i;
                    // Skip opening $$
                    if (line === '$$') {
                        j = i + 1;
                    } else {
                        // Get content after $$ on the same line
                        mathContent = line.substring(line.indexOf('$$') + 2);
                        j = i + 1;
                    }
                    // Collect content until closing $$
                    while (j < lines.length && !lines[j].includes('$$')) {
                        mathContent += '\n' + lines[j];
                        j++;
                    }
                    // Add content before closing $$ if there is any
                    if (j < lines.length) {
                        const closingLine = lines[j];
                        if (closingLine.includes('$$')) {
                            mathContent += '\n' + closingLine.substring(0, closingLine.indexOf('$$'));
                        }
                        j++;
                    }
                    this.blocks.push({
                        id: `block_${Date.now()}_${Math.floor(Math.random() * 1000)}`,
                        type: 'math',
                        content: mathContent,
                        meta: {}
                    });
                    i = j;
                }
                currentBlock = null;
            }
            // Проверяем случай однострочного $ на отдельной строке (начало блочной формулы)
            else if (line.trim() === '$') {
                let mathContent = '';
                let j = i + 1;
                // Собираем контент до закрывающего $
                while (j < lines.length && lines[j].trim() !== '$') {
                    mathContent += (j > i + 1 ? '\n' : '') + lines[j];
                    j++;
                }
                // Пропускаем закрывающий $
                if (j < lines.length) {
                    j++;
                }
                this.blocks.push({
                    id: `block_${Date.now()}_${Math.floor(Math.random() * 1000)}`,
                    type: 'math',
                    content: mathContent,
                    meta: {}
                });
                currentBlock = null;
                i = j;
            }
            // Info, Warning, Danger blocks
            else if (line.startsWith(':::')) {
                const blockMatch = line.match(/^:::(\w+)(?:\s+"(.*?)")?/);
                if (blockMatch) {
                    const blockType = blockMatch[1]; // info, warning, or danger
                    const title = blockMatch[2] || '';
                    let blockContent = '';
                    let j = i + 1;
                    // Collect content until closing :::
                    while (j < lines.length && !lines[j].startsWith(':::')) {
                        blockContent += (j > i + 1 ? '\n' : '') + lines[j];
                        j++;
                    }
                    // Skip the closing ::: if found
                    if (j < lines.length) {
                        j++;
                    }
                    this.blocks.push({
                        id: `block_${Date.now()}_${Math.floor(Math.random() * 1000)}`,
                        type: blockType,
                        content: blockContent,
                        meta: { title }
                    });
                    currentBlock = null;
                    i = j;
                } else {
                    // Not a valid block start, treat as paragraph
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
            // List items
            else if (line.match(/^\s*[\*\-]\s+/)) {
                const listContent = line.replace(/^\s*[\*\-]\s+/, '');
                if (currentBlock && currentBlock.type === 'bullet-list') {
                    currentBlock.content += '\n' + listContent;
                } else {
                    currentBlock = {
                        id: `block_${Date.now()}_${Math.floor(Math.random() * 1000)}`,
                        type: 'bullet-list',
                        content: listContent,
                        meta: {}
                    };
                    this.blocks.push(currentBlock);
                }
                i++;
            }
            else if (line.match(/^\s*\d+\.\s+/)) {
                const listContent = line.replace(/^\s*\d+\.\s+/, '');
                if (currentBlock && currentBlock.type === 'numbered-list') {
                    currentBlock.content += '\n' + listContent;
                } else {
                    currentBlock = {
                        id: `block_${Date.now()}_${Math.floor(Math.random() * 1000)}`,
                        type: 'numbered-list',
                        content: listContent,
                        meta: {}
                    };
                    this.blocks.push(currentBlock);
                }
                i++;
            }
            // Quote
            else if (line.startsWith('> ')) {
                const quoteContent = line.substring(2);
                if (currentBlock && currentBlock.type === 'quote') {
                    currentBlock.content += '\n' + quoteContent;
                } else {
                    currentBlock = {
                        id: `block_${Date.now()}_${Math.floor(Math.random() * 1000)}`,
                        type: 'quote',
                        content: quoteContent,
                        meta: {}
                    };
                    this.blocks.push(currentBlock);
                }
                i++;
            }
            // Image
            else if (line.match(/!\[(.*?)\]\((.*?)\)/)) {
                const match = line.match(/!\[(.*?)\]\((.*?)\)/);
                this.blocks.push({
                    id: `block_${Date.now()}_${Math.floor(Math.random() * 1000)}`,
                    type: 'image',
                    content: match[2],
                    meta: { alt: match[1] }
                });
                currentBlock = null;
                i++;
            }
            // Empty line - reset current block
            else if (line.trim() === '') {
                currentBlock = null;
                i++;
            } 
            // Regular text (paragraph)
            else {
                // Проверяем, содержит ли строка inline формулу в виде $...$
                if (line.match(/\$(.*?)\$/)) {
                    // Если формула встроена в текст, создаем блок math
                    const mathContent = line.match(/\$(.*?)\$/)[1];
                    this.blocks.push({
                        id: `block_${Date.now()}_${Math.floor(Math.random() * 1000)}`,
                        type: 'math',
                        content: mathContent,
                        meta: { inline: true }
                    });
                } else if (currentBlock && currentBlock.type === 'paragraph') {
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
        console.log("Deserialized content into blocks in original order:", this.blocks);
    }
    window.deserializeMdContent = deserializeMdContent;
})(); 