/**
 * StaticFlow Block Editor v3.0 - Main Class
 * Notion-style block-based editor for static site content
 */

// Modified for non-module loading

(function() {
    // Constructor definition for BlockEditor
    class BlockEditor {
        constructor(container, initialContent = null) {
            
            this.container = typeof container === 'string' ? document.querySelector(container) : container;
            
            if (!this.container) {
                console.error("Container not found:", container);
                return;
            }
            
            
            this.blocks = [];
            this.selectedBlock = null;
            this.draggedBlock = null;
            this.draggedBlockElement = null;
            this.dropIndicator = null;
            this.isDragging = false;
            this.lastMousePosition = { x: 0, y: 0 };
            this.dragOffset = null;
            
            // Привязываем методы-экшены к экземпляру
            this.addBlock = window.addBlock.bind(this);
            this.removeBlock = window.removeBlock.bind(this);
            this.selectBlock = window.selectBlock.bind(this);
            this.moveBlock = window.moveBlock.bind(this);
            this.toggleBlockPreview = window.toggleBlockPreview.bind(this);
            this.updateBlockContent = window.updateBlockContent.bind(this);
            
            // Create editor container
            this.editorContainer = document.createElement('div');
            this.editorContainer.className = 'sf-block-editor';
            this.container.appendChild(this.editorContainer);
            
            // Create drop indicator element
            this.createDropIndicator = window.createDropIndicator.bind(this);
            this.createDropIndicator();
            
            // Initialize blocks from content or add empty paragraph
            if (initialContent) {
                console.log("Deserializing initial content...");
                this.deserializeContent = window.deserializeContent.bind(this);
                this.deserializeContent(initialContent);
            }
            
            // Если нет блоков после десериализации, создаём параграф
            if (this.blocks.length === 0) {
                console.log("No blocks after deserialization, adding default paragraph");
                this.addBlock('paragraph');
            }
            
            // Set up drag and drop globals
            this.setupDragAndDrop = window.setupDragAndDrop.bind(this);
            this.handleMouseMove = window.handleMouseMove.bind(this);
            this.handleMouseUp = window.handleMouseUp.bind(this);
            this.startDragging = window.startDragging.bind(this);
            this.updateDropIndicatorPosition = window.updateDropIndicatorPosition.bind(this);
            this.setupDragAndDrop();
            
            this.render();
            this.setupEventListeners();
            
            console.log("BlockEditor initialized with", this.blocks.length, "blocks");
        }
        
        // Bind action methods
        setupEventListeners() {
            // Binding UI action methods
            this.hideBlockTypeMenu = window.hideBlockTypeMenu.bind(this);
            this.toggleBlockPreview = window.toggleBlockPreview.bind(this);
            this.selectBlock = window.selectBlock.bind(this);
            this.removeBlock = window.removeBlock.bind(this); 
            this.moveBlock = window.moveBlock.bind(this);
            this.updateBlockContent = window.updateBlockContent.bind(this);
            this.isCaretAtEnd = window.isCaretAtEnd;
            
            // Клик на кнопке добавления нового блока
            this.container.addEventListener('click', (e) => {
                if (e.target.closest('.add-block-button')) {
                    const button = e.target.closest('.add-block-button');
                    const blockId = button.dataset.blockId;
                    console.log('this в обработчике клика:', this);
                    this.showBlockTypeMenu(button, blockId);
                    e.stopPropagation(); // Prevent event bubbling
                }
                
                // Handle drag handle click
                if (e.target.closest('.sf-block-drag-handle')) {
                    const dragHandle = e.target.closest('.sf-block-drag-handle');
                    const blockId = dragHandle.closest('.sf-block').dataset.blockId;
                    this.startDragging(blockId, e);
                    e.stopPropagation(); // Prevent event bubbling
                }
                
                // Обработка клика по блоку для его выбора
                const blockElement = e.target.closest('.sf-block');
                if (blockElement && !e.target.closest('.sf-block-controls button') && 
                    !e.target.closest('.add-block-button') && 
                    !e.target.closest('.block-type-menu')) {
                    const blockId = blockElement.dataset.blockId;
                    this.selectBlock(blockId);
                }
                
                // Клик по кнопке удаления блока
                if (e.target.closest('.delete-block-button')) {
                    const button = e.target.closest('.delete-block-button');
                    const blockId = button.closest('.sf-block').dataset.blockId;
                    this.removeBlock(blockId);
                    e.stopPropagation(); // Prevent event bubbling
                }
            });
            
            // Двойной клик по блоку для перехода в режим редактирования
            this.editorContainer.addEventListener('dblclick', (e) => {
                const blockElement = e.target.closest('.sf-block');
                if (blockElement && blockElement.classList.contains('sf-block-preview-mode')) {
                    const blockId = blockElement.dataset.blockId;
                    // Переключаем блок в режим редактирования
                    this.toggleBlockPreview(blockId, false);
                    e.stopPropagation(); // Prevent event bubbling
                }
            });
            
            // Закрываем меню выбора типа блока при клике в другом месте
            document.addEventListener('click', (e) => {
                if (!e.target.closest('.block-type-menu') && !e.target.closest('.add-block-button')) {
                    window.hideBlockTypeMenu(this);
                }
            });
            
            // Обработка Enter и Shift+Enter в редактируемых блоках
            this.editorContainer.addEventListener('keydown', (e) => {
                // Проверяем, что мы в редактируемом блоке
                const editableElement = e.target.closest('[contenteditable]');
                if (!editableElement) return;
                
                // Получаем блок и его ID
                const block = editableElement.closest('.sf-block');
                if (!block) return;
                
                const blockId = block.dataset.blockId;
                const currentBlock = this.blocks.find(b => b.id === blockId);
                if (!currentBlock) return;
                
                // Обработка нажатия Enter
                if (e.key === 'Enter') {
                    // Shift+Enter - просто перенос строки в текущем блоке
                    if (e.shiftKey) {
                        // Позволяем браузеру обработать событие обычным образом (добавить <br>)
                        return;
                    }
                    
                    // Enter без Shift - создаем новый блок и переключаем текущий в режим просмотра
                    e.preventDefault(); // Предотвращаем стандартное поведение (перенос строки)
                    
                    // Определяем позицию курсора и разделяем текст
                    const selection = window.getSelection();
                    const range = selection.getRangeAt(0);
                    
                    // Получаем текст текущего блока
                    const containerContent = editableElement.innerHTML;
                    
                    // Сохраняем текущее содержимое
                    this.updateBlockContent(blockId, containerContent);
                    
                    // Если курсор в конце блока, просто добавляем новый блок
                    if (this.isCaretAtEnd(editableElement)) {
                        // Создаем новый пустой блок после текущего
                        const blockIndex = this.blocks.findIndex(b => b.id === blockId);
                        const newBlockId = this.addBlock('paragraph', '', blockIndex + 1);
                        
                        // Переключаем текущий блок в режим просмотра
                        this.toggleBlockPreview(blockId, true);
                        return;
                    }
                    
                    // Если курсор в середине текста
                    const currentSelection = selection.toString();
                    const currentNodeContent = range.startContainer.textContent || '';
                    const contentBefore = currentNodeContent.substring(0, range.startOffset);
                    const contentAfter = currentNodeContent.substring(range.startOffset);
                    
                    // Если выделение пустое, разделяем текущий блок
                    if (currentSelection === '') {
                        // Обновляем текущий блок (текст до курсора)
                        if (range.startContainer.nodeType === Node.TEXT_NODE) {
                            range.startContainer.textContent = contentBefore;
                        }
                        this.updateBlockContent(blockId, editableElement.innerHTML);
                        
                        // Переключаем текущий блок в режим просмотра
                        this.toggleBlockPreview(blockId, true);
                        
                        // Создаем новый блок с текстом после курсора
                        const blockIndex = this.blocks.findIndex(b => b.id === blockId);
                        const newBlockType = currentBlock.type;
                        this.addBlock(newBlockType, contentAfter, blockIndex + 1);
                    } else {
                        // Если есть выделение, удаляем его и создаем новый блок
                        range.deleteContents();
                        selection.collapseToEnd();
                        this.updateBlockContent(blockId, editableElement.innerHTML);
                        
                        // Переключаем текущий блок в режим просмотра
                        this.toggleBlockPreview(blockId, true);
                        
                        // Создаем новый пустой блок после текущего
                        const blockIndex = this.blocks.findIndex(b => b.id === blockId);
                        this.addBlock('paragraph', '', blockIndex + 1);
                    }
                }
            });
            
            // Handle content editable input events for updating block content
            this.editorContainer.addEventListener('input', (e) => {
                const editableElement = e.target.closest('[contenteditable]');
                if (editableElement) {
                    const block = editableElement.closest('.sf-block');
                    if (block) {
                        const blockId = block.dataset.blockId;
                        const content = editableElement.innerHTML;
                        this.updateBlockContent(blockId, content);
                    }
                }
            });
        }
        
        // Отрисовать весь редактор
        render() {
            console.log("Rendering editor with", this.blocks.length, "blocks");
            
            // Bind the method for creating block elements
            this.createBlockElement = window.createBlockElement.bind(this);
            this.applyCodeSyntaxHighlighting = window.applyCodeSyntaxHighlighting.bind(this);
            
            // Очищаем контейнер, сохраняя dropIndicator
            const dropIndicator = this.editorContainer.querySelector('.sf-block-drop-indicator');
            this.editorContainer.innerHTML = '';
            if (dropIndicator) {
                this.editorContainer.appendChild(dropIndicator);
            }
            
            // Если нет блоков, показываем заглушку
            if (this.blocks.length === 0) {
                console.log("No blocks to render, showing empty message");
                const emptyMsg = document.createElement('div');
                emptyMsg.className = 'sf-empty-editor';
                emptyMsg.textContent = 'Добавьте блок контента, нажав "+"';
                this.editorContainer.appendChild(emptyMsg);
                return;
            }
            
            // Отрисовываем каждый блок
            this.blocks.forEach((block, index) => {
                console.log(`Rendering block ${index}: type=${block.type}, id=${block.id}`);
                const blockElement = this.createBlockElement(block, index);
                this.editorContainer.appendChild(blockElement);
            });
            
            // Apply syntax highlighting to all code blocks
            this.applyCodeSyntaxHighlighting();
        }
        
        // Сериализовать содержимое
        serialize() {
            return window.serialize(this.blocks);
        }
        
        // Получить содержимое редактора
        getContent() {
            return this.serialize();
        }
        
        showBlockTypeMenu(button, blockId) {
            const editor = this;
            window.showBlockTypeMenu(editor, button, blockId, (blockType, position) => {
                console.log('CALLBACK: addBlock', blockType, position, editor);
                editor.addBlock(blockType, '', position);
                window.hideBlockTypeMenu(editor);
                setTimeout(() => {
                    const blocks = editor.editorContainer.querySelectorAll('.sf-block');
                    if (blocks[position]) {
                        blocks[position].focus();
                    }
                }, 0);
            });
        }
    }
    
    // Expose BlockEditor to the global scope
    window.BlockEditor = BlockEditor;
})(); 