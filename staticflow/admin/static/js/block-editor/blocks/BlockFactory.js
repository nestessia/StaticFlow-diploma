/**
 * BlockFactory - Functions for creating different block types
 */

// Modified for non-module loading
(function() {
    // Создать DOM-элемент блока
    function createBlockElement(block, index) {
        // Ensure block has meta property
        if (!block.meta) block.meta = {};
        
        const blockElement = document.createElement('div');
        blockElement.className = `sf-block sf-block-${block.type}`;
        blockElement.dataset.blockId = block.id;
        
        // Если блок выбран, добавляем соответствующий класс
        if (this.selectedBlock === block.id) {
            blockElement.classList.add('sf-block-selected');
        }
        
        // Если блок находится в режиме предпросмотра
        if (block.isPreview) {
            blockElement.classList.add('sf-block-preview-mode');
        }
        
        // Создаем контейнер для левых контролов (перетаскивание и добавление)
        const leftControls = document.createElement('div');
        leftControls.className = 'sf-block-left-controls';
        
        // Добавляем drag handle в контейнер левых контролов
        const dragHandle = document.createElement('div');
        dragHandle.className = 'sf-block-drag-handle';
        dragHandle.innerHTML = '<svg width="10" height="10" viewBox="0 0 10 10" fill="currentColor"><rect x="0" y="1" width="2" height="2"/><rect x="4" y="1" width="2" height="2"/><rect x="8" y="1" width="2" height="2"/><rect x="0" y="5" width="2" height="2"/><rect x="4" y="5" width="2" height="2"/><rect x="8" y="5" width="2" height="2"/><rect x="0" y="9" width="2" height="2"/><rect x="4" y="9" width="2" height="2"/><rect x="8" y="9" width="2" height="2"/></svg>';
        dragHandle.title = 'Перетащить блок';
        dragHandle.setAttribute('aria-label', 'Перетащить блок');
        leftControls.appendChild(dragHandle);
        
        // Добавляем кнопку "+" для добавления нового блока в контейнер левых контролов
        const addButton = document.createElement('button');
        addButton.className = 'add-block-button';
        addButton.textContent = '+';
        addButton.dataset.blockId = block.id;
        addButton.title = 'Добавить блок';
        addButton.setAttribute('type', 'button');
        addButton.setAttribute('aria-label', 'Добавить новый блок');
        leftControls.appendChild(addButton);
        
        // Добавляем контейнер левых контролов к блоку
        blockElement.appendChild(leftControls);
        
        // Контейнер для контента блока
        const contentContainer = document.createElement('div');
        contentContainer.className = 'sf-block-content';
        
        // Load block type creation methods from global scope
        this.createHeadingBlock = window.createHeadingBlock;
        this.createParagraphBlock = window.createParagraphBlock;
        this.createBulletListBlock = window.createBulletListBlock;
        this.createNumberedListBlock = window.createNumberedListBlock;
        this.createQuoteBlock = window.createQuoteBlock;
        this.createCodeBlock = window.createCodeBlock;
        this.createMathBlock = window.createMathBlock;
        this.createDiagramBlock = window.createDiagramBlock;
        this.createImageBlock = window.createImageBlock;
        this.createAudioBlock = window.createAudioBlock;
        this.createVideoBlock = window.createVideoBlock;
        this.createInfoBlock = window.createInfoBlock;
        
        // Создаем различные типы блоков в зависимости от их типа
        switch (block.type) {
            case 'heading1':
            case 'heading2':
            case 'heading3':
                this.createHeadingBlock(contentContainer, block);
                break;
            case 'paragraph':
                this.createParagraphBlock(contentContainer, block);
                break;
            case 'bullet-list':
                this.createBulletListBlock(contentContainer, block);
                break;
            case 'numbered-list':
                this.createNumberedListBlock(contentContainer, block);
                break;
            case 'quote':
                this.createQuoteBlock(contentContainer, block);
                break;
            case 'code':
                this.createCodeBlock(contentContainer, block);
                break;
            case 'math':
                this.createMathBlock(contentContainer, block);
                break;
            case 'diagram':
                this.createDiagramBlock(contentContainer, block);
                break;
            case 'image':
                this.createImageBlock(contentContainer, block);
                break;
            case 'audio':
                this.createAudioBlock(contentContainer, block);
                break;
            case 'video':
                this.createVideoBlock(contentContainer, block);
                break;
            case 'info':
            case 'warning':
            case 'danger':
                this.createInfoBlock(contentContainer, block);
                break;
            default:
                this.createParagraphBlock(contentContainer, block);
        }
        
        blockElement.appendChild(contentContainer);
        
        // Добавляем контролы для блока (кнопки удаления и перемещения)
        if (!block.isPreview) {
            const controls = document.createElement('div');
            controls.className = 'sf-block-controls';
            
            const deleteButton = document.createElement('button');
            deleteButton.className = 'delete-block-button';
            deleteButton.title = 'Удалить блок';
            deleteButton.innerHTML = '&times;';
            deleteButton.setAttribute('type', 'button');
            deleteButton.setAttribute('aria-label', 'Удалить блок');
            
            controls.appendChild(deleteButton);
            blockElement.appendChild(controls);
        }
        
        return blockElement;
    }
    
    // Apply syntax highlighting to all code blocks
    function applyCodeSyntaxHighlighting() {
        if (!window.hljs) {
            console.warn('highlight.js is not available for syntax highlighting');
            return;
        }
        
        // Find all code elements in preview mode
        const codeElements = this.editorContainer.querySelectorAll('code[class*="language-"]');
        
        codeElements.forEach(codeElement => {
            try {
                window.hljs.highlightElement(codeElement);
                console.log('Syntax highlighting applied to code block');
            } catch (e) {
                console.warn('Error highlighting code:', e);
            }
        });
    }
    
    // Expose functions to global scope
    window.createBlockElement = createBlockElement;
    window.applyCodeSyntaxHighlighting = applyCodeSyntaxHighlighting;
})(); 