/**
 * EditorUtils - Utility functions for the block editor
 */

// Modified for non-module loading
(function() {
    // Serialize blocks to markdown content
    function serialize(blocks) {
        let markdown = '';
        
        for (const block of blocks) {
            switch (block.type) {
                case 'heading1':
                    markdown += `# ${stripHTML(block.content)}\n\n`;
                    break;
                case 'heading2':
                    markdown += `## ${stripHTML(block.content)}\n\n`;
                    break;
                case 'heading3':
                    markdown += `### ${stripHTML(block.content)}\n\n`;
                    break;
                case 'paragraph':
                    markdown += `${stripHTML(block.content)}\n\n`;
                    break;
                case 'bullet-list':
                    {
                        const items = stripHTML(block.content).split('\n').filter(item => item.trim());
                        for (const item of items) {
                            markdown += `* ${item.trim()}\n`;
                        }
                        markdown += '\n';
                    }
                    break;
                case 'numbered-list':
                    {
                        const items = stripHTML(block.content).split('\n').filter(item => item.trim());
                        for (let i = 0; i < items.length; i++) {
                            markdown += `${i + 1}. ${items[i].trim()}\n`;
                        }
                        markdown += '\n';
                    }
                    break;
                case 'quote':
                    {
                        const lines = stripHTML(block.content).split('\n');
                        for (const line of lines) {
                            markdown += `> ${line}\n`;
                        }
                        markdown += '\n';
                    }
                    break;
                case 'code':
                    {
                        const language = block.meta.language || '';
                        markdown += '```' + language + '\n';
                        markdown += block.content + '\n';
                        markdown += '```\n\n';
                    }
                    break;
                case 'math':
                    if (block.meta && block.meta.inline) {
                        markdown += `$${block.content}$\n\n`;
                    } else {
                        markdown += `$$\n${block.content}\n$$\n\n`;
                    }
                    break;
                case 'diagram':
                    markdown += '```mermaid\n';
                    markdown += block.content + '\n';
                    markdown += '```\n\n';
                    break;
                case 'image':
                    {
                        const alt = block.meta.alt || '';
                        markdown += `![${alt}](${block.content})\n\n`;
                    }
                    break;
                case 'audio':
                    {
                        const caption = block.meta.caption ? ` "${block.meta.caption}"` : '';
                        markdown += `[audio${caption}](${block.content})\n\n`;
                    }
                    break;
                case 'video':
                    {
                        const caption = block.meta.caption ? ` "${block.meta.caption}"` : '';
                        markdown += `[video${caption}](${block.content})\n\n`;
                    }
                    break;
                case 'info':
                    {
                        const title = block.meta.title ? ` "${block.meta.title}"` : '';
                        markdown += `:::info${title}\n${stripHTML(block.content)}\n:::\n\n`;
                    }
                    break;
                case 'warning':
                    {
                        const title = block.meta.title ? ` "${block.meta.title}"` : '';
                        markdown += `:::warning${title}\n${stripHTML(block.content)}\n:::\n\n`;
                    }
                    break;
                case 'danger':
                    {
                        const title = block.meta.title ? ` "${block.meta.title}"` : '';
                        markdown += `:::danger${title}\n${stripHTML(block.content)}\n:::\n\n`;
                    }
                    break;
                default:
                    markdown += `${stripHTML(block.content)}\n\n`;
            }
        }
        
        return markdown.trim();
    }
    
    // Helper function to strip HTML tags
    function stripHTML(html) {
        if (!html) return '';
        
        // Create a temporary div element
        const temp = document.createElement('div');
        temp.innerHTML = html;
        
        // Replace <br> and <p> with newlines
        const elements = temp.querySelectorAll('br, p, div');
        for (const el of elements) {
            if (el.tagName === 'BR') {
                el.replaceWith('\n');
            } else if (el.tagName === 'P' || el.tagName === 'DIV') {
                el.replaceWith('\n' + el.textContent + '\n');
            }
        }
        
        return temp.textContent.trim();
    }
    
    // Deserialize markdown content to blocks
    function deserializeContent(content) {
        
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
    
    // Expose to global scope
    window.serialize = serialize;
    window.stripHTML = stripHTML;
    window.deserializeContent = deserializeContent;
})(); 