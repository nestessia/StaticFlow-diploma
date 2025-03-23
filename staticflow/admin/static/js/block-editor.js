/**
 * StaticFlow Block Editor
 * A modern block-based editor for static site content
 */

class BlockEditor {
    constructor(container, initialContent = null) {
        console.log("BlockEditor constructor called with container:", container);
        
        this.container = typeof container === 'string' ? document.querySelector(container) : container;
        
        if (!this.container) {
            console.error("Container not found:", container);
            return; // Выходим, чтобы избежать ошибок, если контейнер не найден
        }
        
        console.log("Container found:", this.container);
        
        this.blocks = [];
        this.selectedBlock = null;
        
        // Create editor container
        this.editorContainer = document.createElement('div');
        this.editorContainer.className = 'sf-block-editor';
        this.container.appendChild(this.editorContainer);
        
        // Create toolbar
        this.toolbar = document.createElement('div');
        this.toolbar.className = 'sf-block-toolbar';
        this.container.insertBefore(this.toolbar, this.editorContainer);
        
        // Initialize blocks from content or add empty paragraph
        if (initialContent) {
            console.log("Deserializing initial content...");
            this.deserializeContent(initialContent);
        }
        
        // Если после десериализации блоков нет, создаем параграф
        if (this.blocks.length === 0) {
            console.log("No blocks after deserialization, adding default paragraph");
            this.addBlock('paragraph');
        }
        
        this.setupToolbar();
        this.render();
        
        console.log("BlockEditor initialized with", this.blocks.length, "blocks");
    }
    
    setupToolbar() {
        // Add block buttons
        console.log("Setting up toolbar");
        const blockTypes = [
            { type: 'heading1', icon: 'H1', label: 'Heading 1' },
            { type: 'heading2', icon: 'H2', label: 'Heading 2' },
            { type: 'heading3', icon: 'H3', label: 'Heading 3' },
            { type: 'paragraph', icon: '¶', label: 'Paragraph' },
            { type: 'code', icon: '</>', label: 'Code Block' },
            { type: 'math', icon: '∑', label: 'Math Formula' },
            { type: 'diagram', icon: '◊', label: 'Diagram' }
        ];
        
        blockTypes.forEach(blockType => {
            const button = document.createElement('button');
            button.className = 'sf-block-button';
            button.innerHTML = blockType.icon;
            button.title = blockType.label;
            button.addEventListener('click', (e) => {
                e.preventDefault();
                console.log(`Adding block of type: ${blockType.type}`);
                this.addBlock(blockType.type);
            });
            this.toolbar.appendChild(button);
        });
    }
    
    addBlock(type, content = '', position = this.blocks.length) {
        const newBlock = {
            id: Date.now().toString(),
            type: type,
            content: content
        };
        
        this.blocks.splice(position, 0, newBlock);
        this.selectedBlock = newBlock.id;
        this.render();
        return newBlock;
    }
    
    removeBlock(blockId) {
        const index = this.blocks.findIndex(block => block.id === blockId);
        if (index !== -1) {
            this.blocks.splice(index, 1);
            
            // If we removed the selected block, select another one
            if (this.selectedBlock === blockId) {
                const newIndex = Math.min(index, this.blocks.length - 1);
                this.selectedBlock = newIndex >= 0 ? this.blocks[newIndex].id : null;
            }
            
            this.render();
        }
    }
    
    moveBlock(blockId, direction) {
        const index = this.blocks.findIndex(block => block.id === blockId);
        if (index === -1) return;
        
        const newIndex = direction === 'up' ? Math.max(0, index - 1) : Math.min(this.blocks.length - 1, index + 1);
        if (newIndex === index) return;
        
        const block = this.blocks[index];
        this.blocks.splice(index, 1);
        this.blocks.splice(newIndex, 0, block);
        this.render();
    }
    
    updateBlockContent(blockId, content) {
        const block = this.blocks.find(block => block.id === blockId);
        if (block) {
            block.content = content;
        }
    }
    
    render() {
        console.log("Rendering blocks:", this.blocks.length);
        // Clear the editor container
        this.editorContainer.innerHTML = '';
        
        if (this.blocks.length === 0) {
            console.log("No blocks to render, showing placeholder");
            const placeholder = document.createElement('div');
            placeholder.className = 'sf-empty-editor';
            placeholder.innerHTML = 'Click a button in the toolbar to add content';
            this.editorContainer.appendChild(placeholder);
            return;
        }
        
        // Render each block
        this.blocks.forEach((block, index) => {
            console.log(`Rendering block ${index}:`, block.type);
            const blockElement = this.createBlockElement(block);
            this.editorContainer.appendChild(blockElement);
        });
    }
    
    createBlockElement(block) {
        const blockContainer = document.createElement('div');
        blockContainer.className = 'sf-block';
        blockContainer.dataset.blockId = block.id;
        
        if (this.selectedBlock === block.id) {
            blockContainer.classList.add('sf-block-selected');
        }
        
        // Create block controls
        const blockControls = document.createElement('div');
        blockControls.className = 'sf-block-controls';
        
        const moveUpButton = document.createElement('button');
        moveUpButton.innerHTML = '↑';
        moveUpButton.title = 'Move Up';
        moveUpButton.addEventListener('click', () => this.moveBlock(block.id, 'up'));
        
        const moveDownButton = document.createElement('button');
        moveDownButton.innerHTML = '↓';
        moveDownButton.title = 'Move Down';
        moveDownButton.addEventListener('click', () => this.moveBlock(block.id, 'down'));
        
        const removeButton = document.createElement('button');
        removeButton.innerHTML = '×';
        removeButton.title = 'Remove Block';
        removeButton.addEventListener('click', () => this.removeBlock(block.id));
        
        blockControls.appendChild(moveUpButton);
        blockControls.appendChild(moveDownButton);
        blockControls.appendChild(removeButton);
        
        blockContainer.appendChild(blockControls);
        
        // Create block content
        const blockContent = document.createElement('div');
        blockContent.className = 'sf-block-content';
        blockContainer.appendChild(blockContent);
        
        // Add appropriate editor based on block type
        switch (block.type) {
            case 'heading1':
            case 'heading2':
            case 'heading3':
                this.createHeadingBlock(blockContent, block);
                break;
            case 'paragraph':
                this.createParagraphBlock(blockContent, block);
                break;
            case 'code':
                this.createCodeBlock(blockContent, block);
                break;
            case 'math':
                this.createMathBlock(blockContent, block);
                break;
            case 'diagram':
                this.createDiagramBlock(blockContent, block);
                break;
        }
        
        // Make the block selectable
        blockContainer.addEventListener('click', (e) => {
            if (!e.target.matches('button, input, textarea')) {
                this.selectedBlock = block.id;
                this.render();
            }
        });
        
        return blockContainer;
    }
    
    createHeadingBlock(container, block) {
        const level = block.type.replace('heading', '');
        const input = document.createElement('input');
        input.className = 'sf-heading-input sf-heading' + level;
        input.value = block.content;
        input.placeholder = 'Heading ' + level;
        
        input.addEventListener('input', () => {
            this.updateBlockContent(block.id, input.value);
        });
        
        container.appendChild(input);
    }
    
    createParagraphBlock(container, block) {
        const textarea = document.createElement('textarea');
        textarea.className = 'sf-paragraph-input';
        textarea.value = block.content;
        textarea.placeholder = 'Type paragraph text here...';
        
        textarea.addEventListener('input', () => {
            this.updateBlockContent(block.id, textarea.value);
            // Auto-resize the textarea
            textarea.style.height = 'auto';
            textarea.style.height = textarea.scrollHeight + 'px';
        });
        
        // Trigger a resize on initial render
        setTimeout(() => {
            textarea.style.height = 'auto';
            textarea.style.height = textarea.scrollHeight + 'px';
        }, 0);
        
        container.appendChild(textarea);
    }
    
    createCodeBlock(container, block) {
        // Create a simple container with a textarea for now
        // In a real implementation, this would use a code editor like Monaco/CodeMirror
        const textarea = document.createElement('textarea');
        textarea.className = 'sf-code-input';
        textarea.value = block.content;
        textarea.placeholder = 'Enter code here...';
        
        textarea.addEventListener('input', () => {
            this.updateBlockContent(block.id, textarea.value);
        });
        
        container.appendChild(textarea);
        
        // Language selector
        const langSelect = document.createElement('select');
        langSelect.className = 'sf-code-language';
        ['python', 'javascript', 'html', 'css', 'markdown'].forEach(lang => {
            const option = document.createElement('option');
            option.value = lang;
            option.textContent = lang.charAt(0).toUpperCase() + lang.slice(1);
            langSelect.appendChild(option);
        });
        
        container.appendChild(langSelect);
    }
    
    createMathBlock(container, block) {
        const input = document.createElement('textarea');
        input.className = 'sf-math-input';
        input.value = block.content;
        input.placeholder = 'Enter LaTeX math formula...';
        
        input.addEventListener('input', () => {
            this.updateBlockContent(block.id, input.value);
            // Here you would update the preview with rendered math
        });
        
        const preview = document.createElement('div');
        preview.className = 'sf-math-preview';
        preview.innerHTML = 'Math preview will appear here';
        
        container.appendChild(input);
        container.appendChild(preview);
        
        // In a real implementation, you would render the math using KaTeX or MathJax
    }
    
    createDiagramBlock(container, block) {
        const input = document.createElement('textarea');
        input.className = 'sf-diagram-input';
        input.value = block.content;
        input.placeholder = 'Enter diagram code (e.g., Mermaid syntax)';
        
        input.addEventListener('input', () => {
            this.updateBlockContent(block.id, input.value);
            // Here you would update the preview with rendered diagram
        });
        
        const preview = document.createElement('div');
        preview.className = 'sf-diagram-preview';
        preview.innerHTML = 'Diagram preview will appear here';
        
        container.appendChild(input);
        container.appendChild(preview);
        
        // In a real implementation, you would render the diagram using Mermaid.js or similar
    }
    
    serialize() {
        // This would convert blocks to markdown or HTML with frontmatter
        let output = '';
        
        // Генерируем frontmatter с базовыми полями, если нужно
        // Но в реальном использовании этот frontmatter будет заменен на тот,
        // который пользователь настроил в интерфейсе
        output += '---\n';
        output += 'title: \n';
        output += 'date: ' + new Date().toISOString() + '\n';
        output += '---\n\n';
        
        // Convert blocks to markdown
        this.blocks.forEach(block => {
            try {
                switch (block.type) {
                    case 'heading1':
                        output += `# ${block.content}\n\n`;
                        break;
                    case 'heading2':
                        output += `## ${block.content}\n\n`;
                        break;
                    case 'heading3':
                        output += `### ${block.content}\n\n`;
                        break;
                    case 'paragraph':
                        output += `${block.content}\n\n`;
                        break;
                    case 'code':
                        output += '```\n' + block.content + '\n```\n\n';
                        break;
                    case 'math':
                        output += '$$\n' + block.content + '\n$$\n\n';
                        break;
                    case 'diagram':
                        output += '```mermaid\n' + block.content + '\n```\n\n';
                        break;
                }
            } catch (e) {
                console.error("Error serializing block:", e, block);
            }
        });
        
        return output;
    }
    
    deserializeContent(content) {
        // Simple parsing of markdown to blocks
        // In a real implementation, you would use a proper markdown parser
        if (!content) return;
        
        console.log("Deserializing content:", content);
        
        try {
            // Extract frontmatter
            const frontmatterMatch = content.match(/^---\n([\s\S]*?)\n---\n/);
            const contentWithoutFrontmatter = frontmatterMatch 
                ? content.slice(frontmatterMatch[0].length).trim() 
                : content.trim();
            
            // Split content into lines
            const lines = contentWithoutFrontmatter.split('\n');
            let currentBlock = null;
            let inCodeBlock = false;
            let inMathBlock = false;
            let codeBlockContent = '';
            let paragraphContent = '';
            
            for (let i = 0; i < lines.length; i++) {
                const line = lines[i];
                
                // Check for code block start/end
                if (line.startsWith('```')) {
                    if (inCodeBlock) {
                        // End of code block
                        if (inCodeBlock === 'diagram') {
                            this.addBlock('diagram', codeBlockContent.trim());
                        } else {
                            this.addBlock('code', codeBlockContent.trim());
                        }
                        codeBlockContent = '';
                        inCodeBlock = false;
                    } else {
                        // Start of code block
                        // Flush any paragraph content
                        if (paragraphContent) {
                            this.addBlock('paragraph', paragraphContent.trim());
                            paragraphContent = '';
                        }
                        
                        inCodeBlock = true;
                        // Check if it's a mermaid diagram
                        if (line.includes('mermaid')) {
                            inCodeBlock = 'diagram';
                        }
                    }
                    continue;
                }
                
                // Check for math block start/end
                if (line.startsWith('$$')) {
                    if (inMathBlock) {
                        // End of math block
                        this.addBlock('math', codeBlockContent.trim());
                        codeBlockContent = '';
                        inMathBlock = false;
                    } else {
                        // Start of math block
                        // Flush any paragraph content
                        if (paragraphContent) {
                            this.addBlock('paragraph', paragraphContent.trim());
                            paragraphContent = '';
                        }
                        
                        inMathBlock = true;
                    }
                    continue;
                }
                
                // Collect content if in a special block
                if (inCodeBlock || inMathBlock) {
                    codeBlockContent += line + '\n';
                    continue;
                }
                
                // Parse headings
                if (line.startsWith('# ')) {
                    // Flush any paragraph content
                    if (paragraphContent) {
                        this.addBlock('paragraph', paragraphContent.trim());
                        paragraphContent = '';
                    }
                    
                    this.addBlock('heading1', line.slice(2).trim());
                } else if (line.startsWith('## ')) {
                    // Flush any paragraph content
                    if (paragraphContent) {
                        this.addBlock('paragraph', paragraphContent.trim());
                        paragraphContent = '';
                    }
                    
                    this.addBlock('heading2', line.slice(3).trim());
                } else if (line.startsWith('### ')) {
                    // Flush any paragraph content
                    if (paragraphContent) {
                        this.addBlock('paragraph', paragraphContent.trim());
                        paragraphContent = '';
                    }
                    
                    this.addBlock('heading3', line.slice(4).trim());
                } else if (line.trim() !== '') {
                    // Add to paragraph content
                    paragraphContent += (paragraphContent ? '\n' : '') + line;
                } else if (line.trim() === '' && paragraphContent) {
                    // Empty line after paragraph content - flush paragraph
                    this.addBlock('paragraph', paragraphContent.trim());
                    paragraphContent = '';
                }
            }
            
            // Add any remaining paragraph content
            if (paragraphContent) {
                this.addBlock('paragraph', paragraphContent.trim());
            }
        } catch (error) {
            console.error("Error deserializing content:", error);
            // Fallback - just add content as a single paragraph
            this.addBlock('paragraph', content);
        }
    }
    
    getContent() {
        return this.serialize();
    }
}

// Make the editor available globally
window.BlockEditor = BlockEditor; 