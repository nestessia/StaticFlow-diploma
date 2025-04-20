/**
 * StaticFlow Block Editor v3.0
 * Notion-style block-based editor for static site content
 */

class BlockEditor {
    constructor(container, initialContent = null) {
        console.log("BlockEditor constructor called with container:", container);
        
        this.container = typeof container === 'string' ? document.querySelector(container) : container;
        
        if (!this.container) {
            console.error("Container not found:", container);
            return;
        }
        
        console.log("Container found:", this.container);
        
        this.blocks = [];
        this.selectedBlock = null;
        this.draggedBlock = null;
        this.draggedBlockElement = null;
        this.dropIndicator = null;
        this.isDragging = false;
        this.lastMousePosition = { x: 0, y: 0 };
        this.dragOffset = null;
        
        // Create editor container
        this.editorContainer = document.createElement('div');
        this.editorContainer.className = 'sf-block-editor';
        this.container.appendChild(this.editorContainer);
        
        // Create drop indicator element
        this.createDropIndicator();
        
        // Initialize blocks from content or add empty paragraph
        if (initialContent) {
            console.log("Deserializing initial content...");
            this.deserializeContent(initialContent);
        }
        
        // If no blocks after deserialization, create a paragraph
        if (this.blocks.length === 0) {
            console.log("No blocks after deserialization, adding default paragraph");
            this.addBlock('paragraph');
        }
        
        // Set up drag and drop globals
        this.setupDragAndDrop();
        
        this.render();
        this.setupEventListeners();
        
        console.log("BlockEditor initialized with", this.blocks.length, "blocks");
    }
    
    // Create a drop indicator element
    createDropIndicator() {
        this.dropIndicator = document.createElement('div');
        this.dropIndicator.className = 'sf-block-drop-indicator';
        this.editorContainer.appendChild(this.dropIndicator);
    }
    
    // Set up drag and drop functionality
    setupDragAndDrop() {
        document.addEventListener('mousemove', this.handleMouseMove.bind(this));
        document.addEventListener('mouseup', this.handleMouseUp.bind(this));
    }
    
    // Handle mouse move for drag and drop
    handleMouseMove(e) {
        if (this.isDragging && this.draggedBlockElement) {
            // Store last mouse position
            this.lastMousePosition = { x: e.clientX, y: e.clientY };
            
            // Move the dragged element with the cursor, accounting for the initial offset
            const left = e.clientX - this.dragOffset.x;
            const top = e.clientY - this.dragOffset.y;
            
            this.draggedBlockElement.style.left = `${left}px`;
            this.draggedBlockElement.style.top = `${top}px`;
            
            // Apply subtle rotation based on horizontal movement
            const movementX = e.movementX || 0;
            const rotationAmount = Math.min(Math.max(movementX * 0.1, -3), 3);
            this.draggedBlockElement.style.transform = `rotate(${rotationAmount}deg)`;
            
            // Determine the position to insert the block
            this.updateDropIndicatorPosition(e.clientY);
        }
    }
    
    // Handle mouse up to end dragging
    handleMouseUp(e) {
        if (this.isDragging && this.draggedBlock) {
            // Remove the clone element if it exists
            if (this.draggedBlockElement && this.draggedBlockElement.classList.contains('sf-block-dragging')) {
                this.draggedBlockElement.remove();
            }
            
            // Reset the original block element's opacity
            const originalElement = document.querySelector(`.sf-block[data-block-id="${this.draggedBlock.id}"]`);
            if (originalElement) {
                originalElement.style.opacity = '';
            }
            
            // Move the block to its new position
            if (this.dropPosition !== undefined) {
                const currentPosition = this.blocks.indexOf(this.draggedBlock);
                
                // Only move if the position has changed
                if (currentPosition !== this.dropPosition && 
                    currentPosition !== this.dropPosition - 1) {
                    
                    // Adjust drop position if moving down
                    const adjustedPosition = currentPosition < this.dropPosition ? 
                        this.dropPosition - 1 : this.dropPosition;
                    
                    // Remove block from current position
                    this.blocks.splice(currentPosition, 1);
                    
                    // Insert at new position
                    this.blocks.splice(adjustedPosition, 0, this.draggedBlock);
                    
                    // Re-render the editor
                    this.render();
                    
                    // Select the moved block
                    this.selectBlock(this.draggedBlock.id);
                }
            }
            
            // Hide drop indicator
            this.dropIndicator.style.display = 'none';
            
            // Reset drag state
            this.isDragging = false;
            this.draggedBlock = null;
            this.draggedBlockElement = null;
            this.dropPosition = undefined;
            this.dragOffset = null;
        }
    }
    
    // Start dragging a block
    startDragging(blockId, e) {
        const block = this.blocks.find(b => b.id === blockId);
        const blockElement = document.querySelector(`.sf-block[data-block-id="${blockId}"]`);
        
        if (block && blockElement) {
            e.preventDefault();
            
            this.isDragging = true;
            this.draggedBlock = block;
            this.draggedBlockElement = blockElement;
            
            // Calculate block offset to maintain cursor position relative to the block
            const blockRect = blockElement.getBoundingClientRect();
            this.dragOffset = {
                x: e.clientX - blockRect.left,
                y: e.clientY - blockRect.top
            };
            
            // Create a clone for dragging with same dimensions as original
            const clone = blockElement.cloneNode(true);
            clone.classList.add('sf-block-dragging');
            clone.style.width = `${blockRect.width}px`;
            clone.style.position = 'absolute';
            clone.style.left = `${blockRect.left}px`;
            clone.style.top = `${blockRect.top}px`;
            clone.style.zIndex = '1000';
            
            // Add ghost element to the document body
            document.body.appendChild(clone);
            this.draggedBlockElement = clone;
            
            // Mark original as being dragged position placeholder
            blockElement.style.opacity = '0.2';
            
            // Store initial mouse position
            this.lastMousePosition = { x: e.clientX, y: e.clientY };
            
            // Show the drop indicator
            this.dropIndicator.style.display = 'block';
            
            // Update the drop indicator
            this.updateDropIndicatorPosition(e.clientY);
        }
    }
    
    // Настраиваем обработчики событий
    setupEventListeners() {
        // Клик на кнопке добавления нового блока
        this.container.addEventListener('click', (e) => {
            if (e.target.closest('.add-block-button')) {
                const button = e.target.closest('.add-block-button');
                const blockId = button.dataset.blockId;
                this.showBlockTypeMenu(button, blockId);
                e.stopPropagation(); // Prevent event bubbling
            }
            
            // Обработка клика по меню выбора типа блока (выделяем в отдельный обработчик на уровне документа)
            document.addEventListener('click', (e) => {
                if (e.target.closest('.block-type-option')) {
                    const option = e.target.closest('.block-type-option');
                    const blockType = option.dataset.type;
                    const menu = option.closest('.block-type-menu');
                    
                    if (!menu || !menu.dataset.position) {
                        console.error("Menu element or position attribute missing", menu);
                        return;
                    }
                    
                    const position = parseInt(menu.dataset.position);
                    
                    console.log("Block type option clicked:", 
                        "option:", option, 
                        "blockType:", blockType, 
                        "menu:", menu, 
                        "position:", position);
                    
                    console.log("Adding block:", blockType, "at position:", position);
                    this.addBlock(blockType, '', position);
                    this.hideBlockTypeMenu();
                    e.stopPropagation(); // Prevent event bubbling
                }
            });
            
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
                this.hideBlockTypeMenu();
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
    
    // Toggle preview mode for a block
    toggleBlockPreview(blockId, showPreview) {
        const blockIndex = this.blocks.findIndex(b => b.id === blockId);
        if (blockIndex === -1) return;
        
        const block = this.blocks[blockIndex];
        block.isPreview = showPreview;
        
        // Re-render just this block
        const blockElement = document.querySelector(`.sf-block[data-block-id="${blockId}"]`);
        if (blockElement) {
            const newBlockElement = this.createBlockElement(block, blockIndex);
            blockElement.parentNode.replaceChild(newBlockElement, blockElement);
            
            // If not in preview mode, focus the element
            if (!showPreview) {
                const editableElement = newBlockElement.querySelector('[contenteditable]');
                if (editableElement) {
                    editableElement.focus();
                    
                    // Place cursor at the end
                    const range = document.createRange();
                    const selection = window.getSelection();
                    range.selectNodeContents(editableElement);
                    range.collapse(false);
                    selection.removeAllRanges();
                    selection.addRange(range);
                }
            }
        }
    }
    
    // Показать меню выбора типа блока
    showBlockTypeMenu(button, blockId) {
        console.log("Showing block type menu for blockId:", blockId);
        
        // Удаляем предыдущее меню, если оно существует
        this.hideBlockTypeMenu();
        
        // Создаем меню
        const menu = document.createElement('div');
        menu.className = 'block-type-menu';
        
        // Если передан ID блока, сохраняем его как data-атрибут
        // для определения позиции добавления нового блока
        if (blockId) {
            const blockIndex = this.blocks.findIndex(block => block.id === blockId);
            console.log("Block index for position:", blockIndex);
            if (blockIndex !== -1) {
                menu.dataset.position = blockIndex + 1; // Добавляем после текущего блока
            } else {
                menu.dataset.position = this.blocks.length; // Fallback: Добавляем в конец
            }
        } else {
            menu.dataset.position = this.blocks.length; // Добавляем в конец
        }
        
        // Добавляем явный атрибут для отладки
        menu.setAttribute('data-debug', `position: ${menu.dataset.position}, blockId: ${blockId || 'none'}`);
        
        // Определяем группы блоков с улучшенными иконками
        const blockGroups = [
            {
                title: 'Основные',
                types: [
                    { type: 'paragraph', icon: '¶', label: 'Параграф', color: '#4dabf7' },
                    { type: 'heading1', icon: 'H1', label: 'Заголовок 1', color: '#4c6ef5' },
                    { type: 'heading2', icon: 'H2', label: 'Заголовок 2', color: '#4c6ef5' },
                    { type: 'heading3', icon: 'H3', label: 'Заголовок 3', color: '#4c6ef5' }
                ]
            },
            {
                title: 'Списки',
                types: [
                    { type: 'bullet-list', icon: '•', label: 'Маркированный список', color: '#37b24d' },
                    { type: 'numbered-list', icon: '1.', label: 'Нумерованный список', color: '#37b24d' }
                ]
            },
            {
                title: 'Специальные',
                types: [
                    { type: 'quote', icon: '"', label: 'Цитата', color: '#f76707' },
                    { type: 'code', icon: '</>', label: 'Блок кода', color: '#ae3ec9' },
                    { type: 'math', icon: '∑', label: 'Математическая формула', color: '#ae3ec9' },
                    { type: 'diagram', icon: '◊', label: 'Диаграмма', color: '#ae3ec9' }
                ]
            },
            {
                title: 'Медиа',
                types: [
                    { type: 'image', icon: '🖼️', label: 'Изображение', color: '#1098ad' },
                    { type: 'audio', icon: '🔊', label: 'Аудио', color: '#1098ad' },
                    { type: 'video', icon: '🎥', label: 'Видео', color: '#1098ad' }
                ]
            },
            {
                title: 'Информационные блоки',
                types: [
                    { type: 'info', icon: 'ℹ️', label: 'Информация', color: '#1c7ed6' },
                    { type: 'warning', icon: '⚠️', label: 'Предупреждение', color: '#f59f00' },
                    { type: 'danger', icon: '⛔', label: 'Опасность', color: '#e03131' }
                ]
            }
        ];
        
        // Поисковое поле
        const searchContainer = document.createElement('div');
        searchContainer.className = 'block-type-search';
        
        const searchInput = document.createElement('input');
        searchInput.type = 'text';
        searchInput.placeholder = 'Поиск блоков...';
        searchInput.className = 'block-type-search-input';
        
        searchContainer.appendChild(searchInput);
        menu.appendChild(searchContainer);
        
        // Создаем контейнер для групп блоков
        const groupsContainer = document.createElement('div');
        groupsContainer.className = 'block-type-groups-container';
        
        // Создаем разделы меню
        blockGroups.forEach(group => {
            const groupElement = document.createElement('div');
            groupElement.className = 'block-type-group';
            
            const groupTitle = document.createElement('div');
            groupTitle.className = 'block-type-group-title';
            groupTitle.textContent = group.title;
            groupElement.appendChild(groupTitle);
            
            // Добавляем варианты блоков
            group.types.forEach(blockType => {
                const option = document.createElement('div');
                option.className = 'block-type-option';
                option.dataset.type = blockType.type;
                option.setAttribute('role', 'button');
                option.setAttribute('tabindex', '0');
                option.title = `Добавить блок ${blockType.label}`;
                
                const icon = document.createElement('span');
                icon.className = 'block-type-icon';
                icon.textContent = blockType.icon;
                icon.style.backgroundColor = blockType.color ? `${blockType.color}15` : '#f5f5f5'; // 15% opacity
                icon.style.color = blockType.color || '#444';
                
                const label = document.createElement('span');
                label.className = 'block-type-label';
                label.textContent = blockType.label;
                
                option.appendChild(icon);
                option.appendChild(label);
                
                // Добавляем явный обработчик клика
                option.addEventListener('click', (e) => {
                    const blockType = option.dataset.type;
                    const menu = option.closest('.block-type-menu');
                    if (!menu || !menu.dataset.position) {
                        console.error("Menu element or position attribute missing during click", menu);
                        return;
                    }
                    
                    const position = parseInt(menu.dataset.position);
                    console.log("Block type option clicked directly:", blockType, "at position:", position);
                    this.addBlock(blockType, '', position);
                    this.hideBlockTypeMenu();
                    e.stopPropagation();
                });
                
                // Функция фильтрации
                option.dataset.searchTerms = blockType.label.toLowerCase();
                
                groupElement.appendChild(option);
            });
            
            groupsContainer.appendChild(groupElement);
        });
        
        menu.appendChild(groupsContainer);
        
        // Добавляем меню в DOM перед позиционированием
        this.editorContainer.appendChild(menu);
        
        // Функция поиска
        searchInput.addEventListener('input', () => {
            const searchTerm = searchInput.value.toLowerCase().trim();
            const options = menu.querySelectorAll('.block-type-option');
            const groups = menu.querySelectorAll('.block-type-group');
            
            groups.forEach(group => {
                group.style.display = 'block';
                let hasVisibleOptions = false;
                
                const groupOptions = group.querySelectorAll('.block-type-option');
                groupOptions.forEach(option => {
                    const searchTerms = option.dataset.searchTerms;
                    if (searchTerm === '' || searchTerms.includes(searchTerm)) {
                        option.style.display = 'flex';
                        hasVisibleOptions = true;
                    } else {
                        option.style.display = 'none';
                    }
                });
                
                // Скрываем группу, если в ней нет видимых опций
                if (!hasVisibleOptions) {
                    group.style.display = 'none';
                }
            });
        });
        
        // Размещаем меню рядом с кнопкой
        const buttonRect = button.getBoundingClientRect();
        const editorRect = this.editorContainer.getBoundingClientRect();
        const blockElement = button.closest('.sf-block');
        
        menu.style.position = 'absolute';
        
        // Вычисляем середину блока для позиционирования
        if (blockElement) {
            const blockRect = blockElement.getBoundingClientRect();
            // Позиционируем по центру блока, чуть ниже его
            menu.style.top = `${blockRect.bottom - editorRect.top + 10}px`;
            const menuWidth = Math.min(320, window.innerWidth * 0.95);
            menu.style.left = `${(blockRect.left + blockRect.right) / 2 - menuWidth/2}px`; // Центрируем меню
        } else {
            // Запасной вариант, если блок не найден
            menu.style.top = `${buttonRect.bottom - editorRect.top + 5}px`;
            const menuWidth = Math.min(320, window.innerWidth * 0.95);
            menu.style.left = `${buttonRect.left - menuWidth/2}px`;
        }
        
        menu.style.zIndex = '1000';
        
        // Проверяем, не выходит ли меню за пределы контейнера
        setTimeout(() => {
            const menuRect = menu.getBoundingClientRect();
            
            // Если меню выходит за правый край
            if (menuRect.right > editorRect.right) {
                menu.style.left = `${Math.max(10, editorRect.right - menuRect.width - 20)}px`;
            }
            
            // Если меню выходит за левый край
            if (menuRect.left < editorRect.left) {
                menu.style.left = `${editorRect.left + 10}px`;
            }
            
            // Если меню выходит за нижний край видимой области
            if (menuRect.bottom > window.innerHeight) {
                // Если не хватает места снизу, размещаем над кнопкой
                if (blockElement) {
                    const blockRect = blockElement.getBoundingClientRect();
                    menu.style.top = `${blockRect.top - editorRect.top - menuRect.height - 10}px`;
                } else {
                    menu.style.top = `${buttonRect.top - editorRect.top - menuRect.height - 10}px`;
                }
            }
            
            // Добавляем CSS-класс для анимации после позиционирования
            menu.classList.add('block-type-menu-positioned');
            
            // Фокус на поисковом поле
            searchInput.focus();
        }, 0);
    }
    
    // Скрыть меню выбора типа блока
    hideBlockTypeMenu() {
        const menu = this.editorContainer.querySelector('.block-type-menu');
        if (menu) {
            console.log("Removing block type menu");
            menu.remove();
        }
    }
    
    // Выбрать блок (установить фокус)
    selectBlock(blockId) {
        // Если уже выбран этот блок, не делаем ничего
        if (this.selectedBlock === blockId) return;
        
        // Убираем выделение с предыдущего блока
        if (this.selectedBlock) {
            const prevBlock = document.querySelector(`.sf-block[data-block-id="${this.selectedBlock}"]`);
            if (prevBlock) {
                prevBlock.classList.remove('sf-block-selected');
            }
        }
        
        // Устанавливаем новый выбранный блок
        this.selectedBlock = blockId;
        
        // Выделяем новый блок
        const block = document.querySelector(`.sf-block[data-block-id="${blockId}"]`);
        if (block) {
            block.classList.add('sf-block-selected');
            
            // Устанавливаем фокус на редактируемый элемент внутри блока
            const editableElement = block.querySelector('[contenteditable]');
            if (editableElement) {
                editableElement.focus();
                
                // Устанавливаем курсор в конец текста
                const range = document.createRange();
                const selection = window.getSelection();
                
                // Проверяем, есть ли у элемента текстовые узлы
                if (editableElement.childNodes.length > 0) {
                    const lastNode = editableElement.childNodes[editableElement.childNodes.length - 1];
                    
                    if (lastNode.nodeType === Node.TEXT_NODE) {
                        range.setStart(lastNode, lastNode.length);
                    } else {
                        range.selectNodeContents(lastNode);
                        range.collapse(false);
                    }
                } else {
                    range.selectNodeContents(editableElement);
                    range.collapse(false);
                }
                
                selection.removeAllRanges();
                selection.addRange(range);
            }
        }
    }
    
    // Добавить новый блок
    addBlock(type, content = '', position = this.blocks.length) {
        console.log(`Adding block of type ${type} at position ${position}`);
        
        const newBlock = {
            id: `block_${Date.now()}_${Math.floor(Math.random() * 1000)}`,
            type,
            content: content,
            isPreview: false,
            meta: {}
        };
        
        // Добавляем блок в указанную позицию
        this.blocks.splice(position, 0, newBlock);
        console.log(`Added block with ID ${newBlock.id}, now have ${this.blocks.length} blocks`);
        
        // Перерисовываем редактор
        this.render();
        
        // Выбираем новый блок
        this.selectBlock(newBlock.id);
        
        // Возвращаем ID нового блока
        return newBlock.id;
    }
    
    // Удалить блок
    removeBlock(blockId) {
        const blockIndex = this.blocks.findIndex(block => block.id === blockId);
        
        if (blockIndex > -1) {
            // Сохраняем индекс для выбора следующего блока
            const newSelectedIndex = Math.min(blockIndex, this.blocks.length - 2);
            
            // Удаляем блок
            this.blocks.splice(blockIndex, 1);
            
            // Если не осталось блоков, добавляем пустой параграф
            if (this.blocks.length === 0) {
                this.addBlock('paragraph');
                this.render();
                return;
            }
            
            // Перерисовываем редактор
            this.render();
            
            // Выбираем блок с тем же индексом или предыдущий
            if (newSelectedIndex >= 0) {
                this.selectBlock(this.blocks[newSelectedIndex].id);
            }
        }
    }
    
    // Переместить блок вверх или вниз
    moveBlock(blockId, direction) {
        const blockIndex = this.blocks.findIndex(block => block.id === blockId);
        
        if (blockIndex > -1) {
            let newIndex;
            
            if (direction === 'up' && blockIndex > 0) {
                newIndex = blockIndex - 1;
            } else if (direction === 'down' && blockIndex < this.blocks.length - 1) {
                newIndex = blockIndex + 1;
            } else {
                return; // Нельзя переместить дальше
            }
            
            // Перемещаем блок
            const [block] = this.blocks.splice(blockIndex, 1);
            this.blocks.splice(newIndex, 0, block);
            
            // Перерисовываем редактор
            this.render();
            
            // Оставляем выбранным текущий блок
            this.selectBlock(blockId);
        }
    }
    
    // Обновить содержимое блока
    updateBlockContent(blockId, content) {
        const block = this.blocks.find(block => block.id === blockId);
        if (block) {
            block.content = content;
        }
    }
    
    // Отрисовать весь редактор
    render() {
        console.log("Rendering editor with", this.blocks.length, "blocks");
        
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
    
    // Apply syntax highlighting to all code blocks
    applyCodeSyntaxHighlighting() {
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
    
    // Создать DOM-элемент блока
    createBlockElement(block, index) {
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
    
    // Создать блок заголовка
    createHeadingBlock(container, block) {
        const level = block.type.charAt(block.type.length - 1);
        
        // Determine if we should show content or editing interface
        if (block.isPreview) {
            const headingElement = document.createElement(`h${level}`);
            headingElement.innerHTML = block.content || `Заголовок ${level}`;
            container.appendChild(headingElement);
        } else {
            const input = document.createElement('div');
            input.className = `sf-heading-input sf-heading${level}`;
            input.contentEditable = 'true';
            input.innerHTML = block.content;
            input.dataset.placeholder = `Заголовок ${level}`;
            container.appendChild(input);
        }
    }
    
    // Создать блок параграфа
    createParagraphBlock(container, block) {
        // Determine if we should show content or editing interface
        if (block.isPreview) {
            const paragraphElement = document.createElement('p');
            paragraphElement.innerHTML = block.content || 'Параграф';
            container.appendChild(paragraphElement);
        } else {
            const input = document.createElement('div');
            input.className = 'sf-paragraph-input';
            input.contentEditable = 'true';
            input.innerHTML = block.content;
            input.dataset.placeholder = 'Начните печатать текст...';
            container.appendChild(input);
        }
    }
    
    // Создать блок маркированного списка
    createBulletListBlock(container, block) {
        // Determine if we should show content or editing interface
        if (block.isPreview) {
            const listElement = document.createElement('ul');
            
            // Split the content by lines to create list items
            const items = block.content ? block.content.split('\n') : ['Пункт списка'];
            items.forEach(item => {
                if (item.trim()) {
                    const li = document.createElement('li');
                    li.innerHTML = item;
                    listElement.appendChild(li);
                }
            });
            
            container.appendChild(listElement);
        } else {
            const wrapper = document.createElement('div');
            wrapper.className = 'sf-bullet-list';
            
            const input = document.createElement('div');
            input.className = 'sf-list-input';
            input.contentEditable = 'true';
            input.innerHTML = block.content;
            input.dataset.placeholder = 'Маркированный список...';
            
            wrapper.appendChild(input);
            container.appendChild(wrapper);
        }
    }
    
    // Создать блок нумерованного списка
    createNumberedListBlock(container, block) {
        // Determine if we should show content or editing interface
        if (block.isPreview) {
            const listElement = document.createElement('ol');
            
            // Split the content by lines to create list items
            const items = block.content ? block.content.split('\n') : ['Пункт списка'];
            items.forEach(item => {
                if (item.trim()) {
                    const li = document.createElement('li');
                    li.innerHTML = item;
                    listElement.appendChild(li);
                }
            });
            
            container.appendChild(listElement);
        } else {
            const wrapper = document.createElement('div');
            wrapper.className = 'sf-numbered-list';
            
            const input = document.createElement('div');
            input.className = 'sf-list-input';
            input.contentEditable = 'true';
            input.innerHTML = block.content;
            input.dataset.placeholder = 'Нумерованный список...';
            
            wrapper.appendChild(input);
            container.appendChild(wrapper);
        }
    }
    
    // Создать блок цитаты
    createQuoteBlock(container, block) {
        // Determine if we should show content or editing interface
        if (block.isPreview) {
            const quoteElement = document.createElement('blockquote');
            quoteElement.innerHTML = block.content || 'Цитата';
            container.appendChild(quoteElement);
        } else {
            const quoteWrapper = document.createElement('div');
            quoteWrapper.className = 'sf-quote';
            
            const input = document.createElement('div');
            input.className = 'sf-paragraph-input';
            input.contentEditable = 'true';
            input.innerHTML = block.content;
            input.dataset.placeholder = 'Введите цитату...';
            
            quoteWrapper.appendChild(input);
            container.appendChild(quoteWrapper);
        }
    }
    
    // Создать блок кода
    createCodeBlock(container, block) {
        // Setup block meta if not exists
        if (!block.meta.language) {
            block.meta.language = 'text';
        }
        
        const blockWrapper = document.createElement('div');
        blockWrapper.className = 'sf-code-block-wrapper';
        
        if (block.isPreview) {
            // Create a styled preview of the code (Notion-like)
            const codeHeader = document.createElement('div');
            codeHeader.className = 'sf-code-header';
            
            const languageLabel = document.createElement('div');
            languageLabel.className = 'sf-code-language-label';
            
            // Format language name to be more user-friendly
            const langName = block.meta.language || 'text';
            const formattedLang = langName.charAt(0).toUpperCase() + langName.slice(1);
            languageLabel.textContent = formattedLang;
            
            codeHeader.appendChild(languageLabel);
            
            const preElement = document.createElement('pre');
            const codeElement = document.createElement('code');
            
            // Add language class for highlighting if available
            if (block.meta.language) {
                codeElement.className = `language-${block.meta.language}`;
            }
            
            codeElement.textContent = block.content || '// Your code here';
            
            preElement.appendChild(codeElement);
            blockWrapper.appendChild(codeHeader);
            blockWrapper.appendChild(preElement);
            
            // Attempt to highlight code if hljs is available
            if (window.hljs) {
                try {
                    window.hljs.highlightElement(codeElement);
                    console.log('Syntax highlighting applied to code block');
                } catch (e) {
                    console.warn('Error highlighting code:', e);
                }
            } else {
                console.warn('highlight.js is not available for syntax highlighting');
            }
        } else {
            // Create language selector
            const languageSelect = document.createElement('select');
            languageSelect.className = 'sf-code-language';
            
            const languages = [
                { value: 'text', label: 'Plain text' },
                { value: 'html', label: 'HTML' },
                { value: 'css', label: 'CSS' },
                { value: 'javascript', label: 'JavaScript' },
                { value: 'typescript', label: 'TypeScript' },
                { value: 'python', label: 'Python' },
                { value: 'java', label: 'Java' },
                { value: 'c', label: 'C' },
                { value: 'cpp', label: 'C++' },
                { value: 'csharp', label: 'C#' },
                { value: 'php', label: 'PHP' },
                { value: 'ruby', label: 'Ruby' },
                { value: 'go', label: 'Go' },
                { value: 'rust', label: 'Rust' },
                { value: 'swift', label: 'Swift' },
                { value: 'bash', label: 'Bash' },
                { value: 'sql', label: 'SQL' },
                { value: 'json', label: 'JSON' },
                { value: 'yaml', label: 'YAML' },
                { value: 'markdown', label: 'Markdown' }
            ];
            
            languages.forEach(lang => {
                const option = document.createElement('option');
                option.value = lang.value;
                option.textContent = lang.label;
                if (lang.value === block.meta.language) {
                    option.selected = true;
                }
                languageSelect.appendChild(option);
            });
            
            // Create code input area
            const codeInput = document.createElement('textarea');
            codeInput.className = 'sf-code-input';
            codeInput.value = block.content || '';
            codeInput.placeholder = '// Your code here';
            codeInput.spellcheck = false;
            
            // Add language selector and code input to wrapper
            blockWrapper.appendChild(languageSelect);
            blockWrapper.appendChild(codeInput);
            
            // Handle language change
            languageSelect.addEventListener('change', () => {
                block.meta.language = languageSelect.value;
                
                // If the block is toggled to preview mode after language change, 
                // ensure highlighting will be applied with the new language
                if (block.isPreview) {
                    this.applyCodeSyntaxHighlighting();
                }
            });
            
            // Handle code input
            codeInput.addEventListener('input', () => {
                this.updateBlockContent(block.id, codeInput.value);
            });
            
            // Tab key handling for code indentation
            codeInput.addEventListener('keydown', (e) => {
                if (e.key === 'Tab') {
                    e.preventDefault();
                    
                    // Insert tab at cursor position
                    const start = codeInput.selectionStart;
                    const end = codeInput.selectionEnd;
                    
                    // Insert 2 spaces for tab
                    const newValue = codeInput.value.substring(0, start) + '  ' + codeInput.value.substring(end);
                    codeInput.value = newValue;
                    
                    // Move cursor after the tab
                    codeInput.selectionStart = codeInput.selectionEnd = start + 2;
                    
                    // Update block content
                    this.updateBlockContent(block.id, codeInput.value);
                }
            });
        }
        
        container.appendChild(blockWrapper);
    }
    
    // Создать блок математической формулы
    createMathBlock(container, block) {
        const mathWrapper = document.createElement('div');
        mathWrapper.className = 'sf-math-block-wrapper';
        
        if (block.isPreview) {
            // Create a styled preview of the math formula
            const previewLabel = document.createElement('div');
            previewLabel.className = 'sf-preview-label';
            previewLabel.textContent = 'Math formula';
            
            const mathPreview = document.createElement('div');
            mathPreview.className = 'sf-math-preview';
            
            // Render the formula if KaTeX is available
            if (window.katex) {
                try {
                    window.katex.render(block.content || 'e = mc^2', mathPreview, {
                        throwOnError: false,
                        displayMode: true
                    });
                } catch (e) {
                    mathPreview.textContent = block.content || 'e = mc^2';
                    console.warn('Error rendering math:', e);
                }
            } else {
                mathPreview.textContent = block.content || 'e = mc^2';
            }
            
            mathWrapper.appendChild(previewLabel);
            mathWrapper.appendChild(mathPreview);
        } else {
            // Create math input area
            const mathInput = document.createElement('textarea');
            mathInput.className = 'sf-math-input';
            mathInput.value = block.content || '';
            mathInput.placeholder = 'Enter LaTeX math formula (e.g., e = mc^2)';
            mathInput.spellcheck = false;
            
            // Create preview area
            const mathPreview = document.createElement('div');
            mathPreview.className = 'sf-math-preview';
            
            // Live preview function
            const updateMathPreview = () => {
                const formula = mathInput.value;
                
                if (window.katex && formula) {
                    try {
                        window.katex.render(formula, mathPreview, {
                            throwOnError: false,
                            displayMode: true
                        });
                    } catch (e) {
                        mathPreview.textContent = 'Error: ' + e.message;
                    }
                } else {
                    mathPreview.textContent = formula || 'Preview will appear here';
                }
            };
            
            // Initial preview
            updateMathPreview();
            
            // Update preview on input
            mathInput.addEventListener('input', () => {
                this.updateBlockContent(block.id, mathInput.value);
                updateMathPreview();
            });
            
            mathWrapper.appendChild(mathInput);
            mathWrapper.appendChild(mathPreview);
        }
        
        container.appendChild(mathWrapper);
    }
    
    // Создать блок диаграммы
    createDiagramBlock(container, block) {
        const diagramWrapper = document.createElement('div');
        diagramWrapper.className = 'sf-diagram-block-wrapper';
        
        if (block.isPreview) {
            // Create a styled preview of the diagram
            const previewLabel = document.createElement('div');
            previewLabel.className = 'sf-preview-label';
            previewLabel.textContent = 'Diagram';
            
            const diagramPreview = document.createElement('div');
            diagramPreview.className = 'sf-diagram-preview mermaid';
            diagramPreview.textContent = block.content || 'graph TD;\nA-->B;';
            
            // Render diagram if Mermaid is available
            if (window.mermaid) {
                try {
                    window.mermaid.init(undefined, diagramPreview);
                } catch (e) {
                    console.warn('Error rendering diagram:', e);
                }
            }
            
            diagramWrapper.appendChild(previewLabel);
            diagramWrapper.appendChild(diagramPreview);
        } else {
            // Create diagram input area
            const diagramInput = document.createElement('textarea');
            diagramInput.className = 'sf-diagram-input';
            diagramInput.value = block.content || 'graph TD;\nA-->B;';
            diagramInput.placeholder = 'Enter Mermaid diagram code';
            diagramInput.spellcheck = false;
            
            // Create preview area
            const diagramPreview = document.createElement('div');
            diagramPreview.className = 'sf-diagram-preview mermaid';
            
            // Preview button
            const previewButton = document.createElement('button');
            previewButton.className = 'sf-diagram-preview-button';
            previewButton.textContent = 'Update Preview';
            
            // Update preview function
            const updateDiagramPreview = () => {
                const code = diagramInput.value;
                
                // Clear previous diagram
                diagramPreview.innerHTML = '';
                diagramPreview.textContent = code;
                
                // Render new diagram if Mermaid is available
                if (window.mermaid) {
                    try {
                        window.mermaid.init(undefined, diagramPreview);
                    } catch (e) {
                        diagramPreview.innerHTML = `<div class="sf-diagram-error">Error: ${e.message}</div>`;
                        console.warn('Error rendering diagram:', e);
                    }
                }
            };
            
            // Initial preview
            updateDiagramPreview();
            
            // Update preview on button click
            previewButton.addEventListener('click', updateDiagramPreview);
            
            // Update block content on input
            diagramInput.addEventListener('input', () => {
                this.updateBlockContent(block.id, diagramInput.value);
            });
            
            diagramWrapper.appendChild(diagramInput);
            diagramWrapper.appendChild(previewButton);
            diagramWrapper.appendChild(diagramPreview);
        }
        
        container.appendChild(diagramWrapper);
    }
    
    // Создать блок изображения
    createImageBlock(container, block) {
        const imageWrapper = document.createElement('div');
        imageWrapper.className = 'sf-image-block-wrapper';
        
        if (block.isPreview) {
            // Display the image
            if (block.content) {
                const img = document.createElement('img');
                img.className = 'sf-image-preview';
                img.src = block.content;
                img.alt = block.meta.alt || 'Image';
                img.onload = () => img.classList.add('sf-image-loaded');
                img.onerror = () => img.classList.add('sf-image-error');
                
                imageWrapper.appendChild(img);
            } else {
                const placeholder = document.createElement('div');
                placeholder.className = 'sf-empty-preview';
                placeholder.textContent = 'No image URL provided';
                imageWrapper.appendChild(placeholder);
            }
        } else {
            const inputsContainer = document.createElement('div');
            inputsContainer.className = 'sf-image-inputs';
            
            // Image URL input
            const urlInput = document.createElement('input');
            urlInput.type = 'text';
            urlInput.className = 'sf-image-url-input';
            urlInput.placeholder = 'Enter image URL';
            urlInput.value = block.content || '';
            
            // Alt text input
            const altInput = document.createElement('input');
            altInput.type = 'text';
            altInput.className = 'sf-image-alt-input';
            altInput.placeholder = 'Alt text (for accessibility)';
            altInput.value = block.meta.alt || '';
            
            // Upload button (placeholder functionality)
            const uploadButton = document.createElement('button');
            uploadButton.className = 'sf-upload-button';
            uploadButton.textContent = 'Upload';
            uploadButton.title = 'Upload image (not implemented)';
            
            // Preview area
            const imagePreview = document.createElement('div');
            imagePreview.className = 'sf-image-preview-container';
            
            const updateImagePreview = () => {
                const url = urlInput.value.trim();
                imagePreview.innerHTML = '';
                
                if (url) {
                    const img = document.createElement('img');
                    img.className = 'sf-image-preview';
                    img.src = url;
                    img.alt = altInput.value || 'Preview';
                    img.onload = () => img.classList.add('sf-image-loaded');
                    img.onerror = () => img.classList.add('sf-image-error');
                    
                    imagePreview.appendChild(img);
                } else {
                    const placeholder = document.createElement('div');
                    placeholder.className = 'sf-empty-preview';
                    placeholder.textContent = 'Enter a URL to preview the image';
                    imagePreview.appendChild(placeholder);
                }
            };
            
            // Update preview and block content on input
            urlInput.addEventListener('input', () => {
                this.updateBlockContent(block.id, urlInput.value);
                updateImagePreview();
            });
            
            altInput.addEventListener('input', () => {
                if (!block.meta) block.meta = {};
                block.meta.alt = altInput.value;
            });
            
            // Add elements to the container
            inputsContainer.appendChild(urlInput);
            inputsContainer.appendChild(altInput);
            inputsContainer.appendChild(uploadButton);
            
            imageWrapper.appendChild(inputsContainer);
            imageWrapper.appendChild(imagePreview);
            
            // Initial preview
            updateImagePreview();
        }
        
        container.appendChild(imageWrapper);
    }
    
    // Создать блок аудио
    createAudioBlock(container, block) {
        const audioWrapper = document.createElement('div');
        audioWrapper.className = 'sf-audio-block-wrapper';
        
        if (block.isPreview) {
            // Display the audio player
            if (block.content) {
                const audio = document.createElement('audio');
                audio.className = 'sf-audio-preview';
                audio.controls = true;
                audio.src = block.content;
                
                const caption = document.createElement('div');
                caption.className = 'sf-audio-caption';
                caption.textContent = block.meta.caption || '';
                
                audioWrapper.appendChild(audio);
                if (block.meta.caption) {
                    audioWrapper.appendChild(caption);
                }
            } else {
                const placeholder = document.createElement('div');
                placeholder.className = 'sf-empty-preview';
                placeholder.textContent = 'No audio URL provided';
                audioWrapper.appendChild(placeholder);
            }
        } else {
            const inputsContainer = document.createElement('div');
            inputsContainer.className = 'sf-audio-inputs';
            
            // Audio URL input
            const urlInput = document.createElement('input');
            urlInput.type = 'text';
            urlInput.className = 'sf-audio-url-input';
            urlInput.placeholder = 'Enter audio URL';
            urlInput.value = block.content || '';
            
            // Caption input
            const captionInput = document.createElement('input');
            captionInput.type = 'text';
            captionInput.className = 'sf-audio-caption-input';
            captionInput.placeholder = 'Caption (optional)';
            captionInput.value = block.meta.caption || '';
            
            // Upload button (placeholder functionality)
            const uploadButton = document.createElement('button');
            uploadButton.className = 'sf-upload-button';
            uploadButton.textContent = 'Upload';
            uploadButton.title = 'Upload audio (not implemented)';
            
            // Preview area
            const audioPreview = document.createElement('div');
            audioPreview.className = 'sf-audio-preview-container';
            
            const updateAudioPreview = () => {
                const url = urlInput.value.trim();
                audioPreview.innerHTML = '';
                
                if (url) {
                    const audio = document.createElement('audio');
                    audio.className = 'sf-audio-preview';
                    audio.controls = true;
                    audio.src = url;
                    
                    audioPreview.appendChild(audio);
                } else {
                    const placeholder = document.createElement('div');
                    placeholder.className = 'sf-empty-preview';
                    placeholder.textContent = 'Enter a URL to preview the audio';
                    audioPreview.appendChild(placeholder);
                }
            };
            
            // Update preview and block content on input
            urlInput.addEventListener('input', () => {
                this.updateBlockContent(block.id, urlInput.value);
                updateAudioPreview();
            });
            
            captionInput.addEventListener('input', () => {
                if (!block.meta) block.meta = {};
                block.meta.caption = captionInput.value;
            });
            
            // Add elements to the container
            inputsContainer.appendChild(urlInput);
            inputsContainer.appendChild(captionInput);
            inputsContainer.appendChild(uploadButton);
            
            audioWrapper.appendChild(inputsContainer);
            audioWrapper.appendChild(audioPreview);
            
            // Initial preview
            updateAudioPreview();
        }
        
        container.appendChild(audioWrapper);
    }
    
    // Создать блок видео
    createVideoBlock(container, block) {
        const videoWrapper = document.createElement('div');
        videoWrapper.className = 'sf-video-block-wrapper';
        
        if (block.isPreview) {
            // Display the video player
            if (block.content) {
                const videoContainer = document.createElement('div');
                videoContainer.className = 'sf-video-container';
                
                // Check if it's a YouTube URL
                const youtubeMatch = block.content.match(/(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})/);
                
                if (youtubeMatch) {
                    const iframe = document.createElement('iframe');
                    iframe.className = 'sf-youtube-embed';
                    iframe.src = `https://www.youtube.com/embed/${youtubeMatch[1]}`;
                    iframe.allowFullscreen = true;
                    iframe.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture';
                    
                    videoContainer.appendChild(iframe);
                } else {
                    // Standard video player for direct video URLs
                    const video = document.createElement('video');
                    video.className = 'sf-video-preview';
                    video.controls = true;
                    video.src = block.content;
                    
                    videoContainer.appendChild(video);
                }
                
                const caption = document.createElement('div');
                caption.className = 'sf-video-caption';
                caption.textContent = block.meta.caption || '';
                
                videoWrapper.appendChild(videoContainer);
                if (block.meta.caption) {
                    videoWrapper.appendChild(caption);
                }
            } else {
                const placeholder = document.createElement('div');
                placeholder.className = 'sf-empty-preview';
                placeholder.textContent = 'No video URL provided';
                videoWrapper.appendChild(placeholder);
            }
        } else {
            const inputsContainer = document.createElement('div');
            inputsContainer.className = 'sf-video-inputs';
            
            // Video URL input
            const urlInput = document.createElement('input');
            urlInput.type = 'text';
            urlInput.className = 'sf-video-url-input';
            urlInput.placeholder = 'Enter video URL (direct or YouTube)';
            urlInput.value = block.content || '';
            
            // Caption input
            const captionInput = document.createElement('input');
            captionInput.type = 'text';
            captionInput.className = 'sf-video-caption-input';
            captionInput.placeholder = 'Caption (optional)';
            captionInput.value = block.meta.caption || '';
            
            // Upload button (placeholder functionality)
            const uploadButton = document.createElement('button');
            uploadButton.className = 'sf-upload-button';
            uploadButton.textContent = 'Upload';
            uploadButton.title = 'Upload video (not implemented)';
            
            // Preview area
            const videoPreview = document.createElement('div');
            videoPreview.className = 'sf-video-preview-container';
            
            const updateVideoPreview = () => {
                const url = urlInput.value.trim();
                videoPreview.innerHTML = '';
                
                if (url) {
                    const videoContainer = document.createElement('div');
                    videoContainer.className = 'sf-video-container';
                    
                    // Check if it's a YouTube URL
                    const youtubeMatch = url.match(/(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})/);
                    
                    if (youtubeMatch) {
                        const iframe = document.createElement('iframe');
                        iframe.className = 'sf-youtube-embed';
                        iframe.src = `https://www.youtube.com/embed/${youtubeMatch[1]}`;
                        iframe.allowFullscreen = true;
                        iframe.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture';
                        
                        videoContainer.appendChild(iframe);
                    } else {
                        // Standard video player for direct video URLs
                        const video = document.createElement('video');
                        video.className = 'sf-video-preview';
                        video.controls = true;
                        video.src = url;
                        
                        videoContainer.appendChild(video);
                    }
                    
                    videoPreview.appendChild(videoContainer);
                } else {
                    const placeholder = document.createElement('div');
                    placeholder.className = 'sf-empty-preview';
                    placeholder.textContent = 'Enter a URL to preview the video';
                    videoPreview.appendChild(placeholder);
                }
            };
            
            // Update preview and block content on input
            urlInput.addEventListener('input', () => {
                this.updateBlockContent(block.id, urlInput.value);
                updateVideoPreview();
            });
            
            captionInput.addEventListener('input', () => {
                if (!block.meta) block.meta = {};
                block.meta.caption = captionInput.value;
            });
            
            // Add elements to the container
            inputsContainer.appendChild(urlInput);
            inputsContainer.appendChild(captionInput);
            inputsContainer.appendChild(uploadButton);
            
            videoWrapper.appendChild(inputsContainer);
            videoWrapper.appendChild(videoPreview);
            
            // Initial preview
            updateVideoPreview();
        }
        
        container.appendChild(videoWrapper);
    }
    
    // Создать информационный/предупреждающий блок
    createInfoBlock(container, block) {
        const infoType = block.type; // 'info', 'warning', or 'danger'
        
        const infoWrapper = document.createElement('div');
        infoWrapper.className = `sf-${infoType}-block-wrapper`;
        
        if (block.isPreview) {
            // Create a styled preview of the info block
            const infoPreview = document.createElement('div');
            infoPreview.className = `sf-preview-${infoType}`;
            
            // Add title if it exists
            if (block.meta.title) {
                const titleElement = document.createElement('div');
                titleElement.className = 'sf-preview-title';
                titleElement.innerHTML = block.meta.title;
                infoPreview.appendChild(titleElement);
            }
            
            // Add content
            const contentElement = document.createElement('div');
            contentElement.className = 'sf-preview-content';
            contentElement.innerHTML = block.content || `${infoType.charAt(0).toUpperCase() + infoType.slice(1)} content`;
            infoPreview.appendChild(contentElement);
            
            infoWrapper.appendChild(infoPreview);
        } else {
            // Create title input
            const titleInput = document.createElement('input');
            titleInput.type = 'text';
            titleInput.className = `sf-${infoType}-title-input`;
            titleInput.placeholder = `${infoType.charAt(0).toUpperCase() + infoType.slice(1)} title (optional)`;
            titleInput.value = block.meta.title || '';
            
            // Create content input
            const contentInput = document.createElement('div');
            contentInput.className = `sf-${infoType}-input`;
            contentInput.contentEditable = 'true';
            contentInput.innerHTML = block.content || '';
            contentInput.dataset.placeholder = `${infoType.charAt(0).toUpperCase() + infoType.slice(1)} content...`;
            
            // Update block data on input
            titleInput.addEventListener('input', () => {
                if (!block.meta) block.meta = {};
                block.meta.title = titleInput.value;
            });
            
            contentInput.addEventListener('input', () => {
                this.updateBlockContent(block.id, contentInput.innerHTML);
            });
            
            infoWrapper.appendChild(titleInput);
            infoWrapper.appendChild(contentInput);
        }
        
        container.appendChild(infoWrapper);
    }
    
    // Сериализовать содержимое
    serialize() {
        let markdown = '';
        
        for (const block of this.blocks) {
            switch (block.type) {
                case 'heading1':
                    markdown += `# ${this.stripHTML(block.content)}\n\n`;
                    break;
                case 'heading2':
                    markdown += `## ${this.stripHTML(block.content)}\n\n`;
                    break;
                case 'heading3':
                    markdown += `### ${this.stripHTML(block.content)}\n\n`;
                    break;
                case 'paragraph':
                    markdown += `${this.stripHTML(block.content)}\n\n`;
                    break;
                case 'bullet-list':
                    {
                        const items = this.stripHTML(block.content).split('\n').filter(item => item.trim());
                        for (const item of items) {
                            markdown += `* ${item.trim()}\n`;
                        }
                        markdown += '\n';
                    }
                    break;
                case 'numbered-list':
                    {
                        const items = this.stripHTML(block.content).split('\n').filter(item => item.trim());
                        for (let i = 0; i < items.length; i++) {
                            markdown += `${i + 1}. ${items[i].trim()}\n`;
                        }
                        markdown += '\n';
                    }
                    break;
                case 'quote':
                    {
                        const lines = this.stripHTML(block.content).split('\n');
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
                        markdown += `:::info${title}\n${this.stripHTML(block.content)}\n:::\n\n`;
                    }
                    break;
                case 'warning':
                    {
                        const title = block.meta.title ? ` "${block.meta.title}"` : '';
                        markdown += `:::warning${title}\n${this.stripHTML(block.content)}\n:::\n\n`;
                    }
                    break;
                case 'danger':
                    {
                        const title = block.meta.title ? ` "${block.meta.title}"` : '';
                        markdown += `:::danger${title}\n${this.stripHTML(block.content)}\n:::\n\n`;
                    }
                    break;
                default:
                    markdown += `${this.stripHTML(block.content)}\n\n`;
            }
        }
        
        return markdown.trim();
    }
    
    // Helper method to strip HTML tags
    stripHTML(html) {
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
    
    // Десериализовать содержимое
    deserializeContent(content) {
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
                    content: match[1]
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
                    content: line.substring(2)
                });
                currentBlock = null;
            } else if (line.startsWith('## ')) {
                this.blocks.push({
                    id: `block_${Date.now()}_${Math.floor(Math.random() * 1000)}`,
                    type: 'heading2',
                    content: line.substring(3)
                });
                currentBlock = null;
            } else if (line.startsWith('### ')) {
                this.blocks.push({
                    id: `block_${Date.now()}_${Math.floor(Math.random() * 1000)}`,
                    type: 'heading3',
                    content: line.substring(4)
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
                        content: listContent
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
                        content: listContent
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
                        content: quoteContent
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
                        content: line
                    };
                    this.blocks.push(currentBlock);
                }
            }
        }
        
        console.log("Deserialized content into blocks:", this.blocks);
    }
    
    // Получить содержимое редактора
    getContent() {
        return this.serialize();
    }
    
    // Проверяет, находится ли курсор в конце редактируемого элемента
    isCaretAtEnd(editableElement) {
        const selection = window.getSelection();
        if (!selection.rangeCount) return false;
        
        const range = selection.getRangeAt(0);
        const clonedRange = range.cloneRange();
        clonedRange.selectNodeContents(editableElement);
        clonedRange.setStart(range.endContainer, range.endOffset);
        
        return clonedRange.collapsed;
    }
    
    // Update drop indicator position
    updateDropIndicatorPosition(mouseY) {
        const blocks = Array.from(this.editorContainer.querySelectorAll('.sf-block'));
        
        // Find the block that is closest to the mouse cursor
        let closestBlock = null;
        let closestDistance = Infinity;
        let insertBefore = true;
        
        blocks.forEach(block => {
            // Skip processing if the block is the one being dragged
            if (this.draggedBlock && block.dataset.blockId === this.draggedBlock.id) {
                return;
            }
            
            const rect = block.getBoundingClientRect();
            const blockTop = rect.top;
            const blockBottom = rect.bottom;
            
            // Check if mouse is above the block
            if (mouseY < blockTop) {
                const distance = blockTop - mouseY;
                if (distance < closestDistance) {
                    closestDistance = distance;
                    closestBlock = block;
                    insertBefore = true;
                }
            }
            // Check if mouse is below the block
            else if (mouseY > blockBottom) {
                const distance = mouseY - blockBottom;
                if (distance < closestDistance) {
                    closestDistance = distance;
                    closestBlock = block;
                    insertBefore = false;
                }
            }
            // Mouse is inside the block
            else {
                const middleY = (blockTop + blockBottom) / 2;
                insertBefore = mouseY < middleY;
                closestDistance = 0;
                closestBlock = block;
            }
        });
        
        if (closestBlock) {
            // Position the drop indicator
            const rect = closestBlock.getBoundingClientRect();
            const editorRect = this.editorContainer.getBoundingClientRect();
            
            this.dropIndicator.style.display = 'block';
            
            // Find the index of the block in the DOM (accounting for other elements)
            const allBlocks = Array.from(this.editorContainer.querySelectorAll('.sf-block'));
            const indexOfBlock = allBlocks.indexOf(closestBlock);
            
            if (insertBefore) {
                // If inserting before, position the indicator at the top of the closest block
                const top = closestBlock.offsetTop - 2;
                this.dropIndicator.style.transform = `translateY(${top}px)`;
                this.dropPosition = indexOfBlock;
            } else {
                // If inserting after, position the indicator at the bottom of the closest block
                const top = closestBlock.offsetTop + closestBlock.offsetHeight;
                this.dropIndicator.style.transform = `translateY(${top}px)`;
                this.dropPosition = indexOfBlock + 1;
            }
        }
    }
}

// Make the editor available globally
window.BlockEditor = BlockEditor; 