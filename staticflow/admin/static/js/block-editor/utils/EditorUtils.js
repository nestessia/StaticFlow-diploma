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
                    markdown += `$$\n${block.content}\n$$\n\n`;
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
        console.log("Deserializing content:", content);
        
        if (!content) {
            console.log("Content is empty, adding default paragraph");
            this.addBlock('paragraph');
            return;
        }
        
        this.blocks = [];
        
        // Special blocks (fenced)
        const specialBlocks = [
            // Code blocks
            { regex: /```(\w*)\n([\s\S]*?)\n```/g, type: 'code', position: 1 },
            // Math blocks
            { regex: /\$\$([\s\S]*?)\$\$/g, type: 'math', position: 1 },
            // Info blocks
            { regex: /:::info(?:\s+"(.*)")?\n([\s\S]*?)\n:::/g, type: 'info', position: 2 },
            // Warning blocks
            { regex: /:::warning(?:\s+"(.*)")?\n([\s\S]*?)\n:::/g, type: 'warning', position: 2 },
            // Danger blocks
            { regex: /:::danger(?:\s+"(.*)")?\n([\s\S]*?)\n:::/g, type: 'danger', position: 2 }
        ];
        
        // Process special blocks first
        let remainingContent = content;
        
        // Helper function to process special blocks
        const processBlock = (match, type, position) => {
            if (type === 'code') {
                const language = match[1] || 'text';
                const codeContent = match[2];
                
                this.blocks.push({
                    id: `block_${Date.now()}_${Math.floor(Math.random() * 1000)}`,
                    type: 'code',
                    content: codeContent,
                    meta: { language }
                });
            } else if (type === 'math') {
                this.blocks.push({
                    id: `block_${Date.now()}_${Math.floor(Math.random() * 1000)}`,
                    type: 'math',
                    content: match[1],
                    meta: {}
                });
            } else if (type === 'info' || type === 'warning' || type === 'danger') {
                const title = match[1] || '';
                const content = match[2];
                
                this.blocks.push({
                    id: `block_${Date.now()}_${Math.floor(Math.random() * 1000)}`,
                    type,
                    content,
                    meta: { title }
                });
            }
            
            // Remove the processed block from remaining content
            return '';
        };
        
        // Process each special block type
        for (const blockDef of specialBlocks) {
            remainingContent = remainingContent.replace(blockDef.regex, (...args) => {
                processBlock(args, blockDef.type, blockDef.position);
                return '';
            });
        }
        
        // Process remaining content line by line
        const lines = remainingContent.split('\n');
        let currentBlock = null;
        
        for (let i = 0; i < lines.length; i++) {
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
            } else if (line.startsWith('## ')) {
                this.blocks.push({
                    id: `block_${Date.now()}_${Math.floor(Math.random() * 1000)}`,
                    type: 'heading2',
                    content: line.substring(3),
                    meta: { level: 'h2' }
                });
                currentBlock = null;
            } else if (line.startsWith('### ')) {
                this.blocks.push({
                    id: `block_${Date.now()}_${Math.floor(Math.random() * 1000)}`,
                    type: 'heading3',
                    content: line.substring(4),
                    meta: { level: 'h3' }
                });
                currentBlock = null;
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
            } else if (line.match(/^\s*\d+\.\s+/)) {
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
            }
            // Empty line - reset current block
            else if (line.trim() === '') {
                currentBlock = null;
            } 
            // Regular text (paragraph)
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
            }
        }
        
        console.log("Deserialized content into blocks:", this.blocks);
    }
    
    // Expose to global scope
    window.serialize = serialize;
    window.stripHTML = stripHTML;
    window.deserializeContent = deserializeContent;
})(); 