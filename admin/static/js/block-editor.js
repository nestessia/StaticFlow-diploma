/**
 * StaticFlow Block Editor v2.0
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
        
        // Create editor container
        this.editorContainer = document.createElement('div');
        this.editorContainer.className = 'sf-block-editor';
        this.container.appendChild(this.editorContainer);
        
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
        
        this.render();
        this.setupEventListeners();
        
        console.log("BlockEditor initialized with", this.blocks.length, "blocks");
    }
    
    // Настраиваем обработчики событий
    setupEventListeners() {
        // Делегирование событий для добавления новых блоков и взаимодействия с ними
        this.editorContainer.addEventListener('click', (e) => {
            // Обработка клика по плюсику для добавления блока
            if (e.target.closest('.add-block-button')) {
                const button = e.target.closest('.add-block-button');
                const blockId = button.dataset.blockId;
                this.showBlockTypeMenu(button, blockId);
            }
            
            // Обработка клика по меню выбора типа блока
            if (e.target.closest('.block-type-option')) {
                const option = e.target.closest('.block-type-option');
                const blockType = option.dataset.type;
                const position = parseInt(option.closest('.block-type-menu').dataset.position);
                
                this.addBlock(blockType, '', position);
                this.hideBlockTypeMenu();
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
            }
            
            // Клик по кнопке перемещения блока вверх
            if (e.target.closest('.move-up-button')) {
                const button = e.target.closest('.move-up-button');
                const blockId = button.closest('.sf-block').dataset.blockId;
                this.moveBlock(blockId, 'up');
            }
            
            // Клик по кнопке перемещения блока вниз
            if (e.target.closest('.move-down-button')) {
                const button = e.target.closest('.move-down-button');
                const blockId = button.closest('.sf-block').dataset.blockId;
                this.moveBlock(blockId, 'down');
            }
        });
        
        // Закрываем меню выбора типа блока при клике в другом месте
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.block-type-menu') && !e.target.closest('.add-block-button')) {
                this.hideBlockTypeMenu();
            }
        });
        
        // Обработка клавиатурных событий для всего редактора
        this.editorContainer.addEventListener('keydown', (e) => {
            // Обработка Enter для создания нового блока
            if (e.key === 'Enter' && !e.shiftKey) {
                const activeElement = document.activeElement;
                // Игнорируем Enter в многострочных элементах (textarea)
                if (activeElement.tagName === 'TEXTAREA' && 
                    !activeElement.classList.contains('sf-single-line')) {
                    return;
                }
                
                if (activeElement.closest('.sf-block')) {
                    e.preventDefault(); // Предотвращаем стандартное поведение
                    const block = activeElement.closest('.sf-block');
                    const blockId = block.dataset.blockId;
                    const blockIndex = this.blocks.findIndex(b => b.id === blockId);
                    
                    // Добавляем новый блок после текущего
                    this.addBlock('paragraph', '', blockIndex + 1);
                }
            }
            
            // Обработка Backspace для объединения или удаления блоков
            if (e.key === 'Backspace') {
                const activeElement = document.activeElement;
                if (activeElement.closest('.sf-block')) {
                    const block = activeElement.closest('.sf-block');
                    const blockId = block.dataset.blockId;
                    const currentBlock = this.blocks.find(b => b.id === blockId);
                    
                    // Если текст пуст и это не первый блок, удаляем его
                    if (currentBlock && currentBlock.content === '' && 
                        this.blocks.indexOf(currentBlock) > 0) {
                        e.preventDefault();
                        this.removeBlock(blockId);
                        
                        // Выбираем предыдущий блок
                        const prevBlockIndex = Math.max(0, this.blocks.indexOf(currentBlock) - 1);
                        if (prevBlockIndex >= 0 && this.blocks[prevBlockIndex]) {
                            this.selectBlock(this.blocks[prevBlockIndex].id);
                        }
                    }
                }
            }
        });
    }
    
    // Показать меню выбора типа блока
    showBlockTypeMenu(button, blockId) {
        // Закрываем предыдущее меню, если оно открыто
        this.hideBlockTypeMenu();
        
        const blockIndex = this.blocks.findIndex(block => block.id === blockId);
        const position = blockIndex + 1; // Позиция для вставки нового блока
        
        const menu = document.createElement('div');
        menu.className = 'block-type-menu';
        menu.dataset.position = position;
        
        // Группы блоков с соответствующими иконками и описаниями
        const blockGroups = [
            {
                title: 'Базовые',
                types: [
                    { type: 'paragraph', icon: '¶', label: 'Обычный текст' },
                    { type: 'heading1', icon: 'H1', label: 'Заголовок 1' },
                    { type: 'heading2', icon: 'H2', label: 'Заголовок 2' },
                    { type: 'heading3', icon: 'H3', label: 'Заголовок 3' }
                ]
            },
            {
                title: 'Списки',
                types: [
                    { type: 'bullet-list', icon: '•', label: 'Маркированный список' },
                    { type: 'numbered-list', icon: '1.', label: 'Нумерованный список' }
                ]
            },
            {
                title: 'Специальные',
                types: [
                    { type: 'quote', icon: '"', label: 'Цитата' },
                    { type: 'code', icon: '</>', label: 'Блок кода' },
                    { type: 'math', icon: '∑', label: 'Математическая формула' },
                    { type: 'diagram', icon: '◊', label: 'Диаграмма' }
                ]
            },
            {
                title: 'Медиа',
                types: [
                    { type: 'image', icon: '🖼️', label: 'Изображение' },
                    { type: 'audio', icon: '🔊', label: 'Аудио' },
                    { type: 'video', icon: '🎥', label: 'Видео' }
                ]
            },
            {
                title: 'Информационные блоки',
                types: [
                    { type: 'info', icon: 'ℹ️', label: 'Информация' },
                    { type: 'warning', icon: '⚠️', label: 'Предупреждение' },
                    { type: 'danger', icon: '⛔', label: 'Опасность' }
                ]
            }
        ];
        
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
                
                const icon = document.createElement('span');
                icon.className = 'block-type-icon';
                icon.textContent = blockType.icon;
                
                const label = document.createElement('span');
                label.className = 'block-type-label';
                label.textContent = blockType.label;
                
                option.appendChild(icon);
                option.appendChild(label);
                
                groupElement.appendChild(option);
            });
            
            menu.appendChild(groupElement);
        });
        
        // Размещаем меню рядом с кнопкой
        const rect = button.getBoundingClientRect();
        menu.style.position = 'absolute';
        menu.style.top = `${rect.bottom + window.scrollY}px`;
        menu.style.left = `${rect.left + window.scrollX}px`;
        
        document.body.appendChild(menu);
    }
    
    // Скрыть меню выбора типа блока
    hideBlockTypeMenu() {
        const menu = document.querySelector('.block-type-menu');
        if (menu) {
            menu.remove();
        }
    }
    
    // Выбрать блок (установить фокус)
    selectBlock(blockId) {
        this.selectedBlock = blockId;
        
        // Обновляем классы выбранных блоков
        document.querySelectorAll('.sf-block').forEach(block => {
            if (block.dataset.blockId === blockId) {
                block.classList.add('sf-block-selected');
                
                // Устанавливаем фокус на элемент ввода внутри блока
                const input = block.querySelector('input, textarea');
                if (input) {
                    input.focus();
                }
            } else {
                block.classList.remove('sf-block-selected');
            }
        });
    }
    
    // Добавить новый блок
    addBlock(type, content = '', position = this.blocks.length) {
        const newBlock = {
            id: Date.now().toString(),
            type: type,
            content: content
        };
        
        this.blocks.splice(position, 0, newBlock);
        this.selectedBlock = newBlock.id;
        this.render();
        
        // Устанавливаем фокус на новый блок
        setTimeout(() => {
            const blockElement = document.querySelector(`.sf-block[data-block-id="${newBlock.id}"]`);
            if (blockElement) {
                const input = blockElement.querySelector('input, textarea');
                if (input) {
                    input.focus();
                }
            }
        }, 0);
        
        return newBlock;
    }
    
    // Удалить блок
    removeBlock(blockId) {
        const index = this.blocks.findIndex(block => block.id === blockId);
        if (index !== -1) {
            this.blocks.splice(index, 1);
            
            // Если удалили последний блок, добавляем пустой параграф
            if (this.blocks.length === 0) {
                this.addBlock('paragraph');
                return;
            }
            
            // Выбираем следующий или предыдущий блок
            if (this.selectedBlock === blockId) {
                const newIndex = Math.min(index, this.blocks.length - 1);
                this.selectedBlock = newIndex >= 0 ? this.blocks[newIndex].id : null;
            }
            
            this.render();
            
            // Фокусируемся на выбранном блоке
            if (this.selectedBlock) {
                this.selectBlock(this.selectedBlock);
            }
        }
    }
    
    // Переместить блок вверх или вниз
    moveBlock(blockId, direction) {
        const index = this.blocks.findIndex(block => block.id === blockId);
        if (index === -1) return;
        
        const newIndex = direction === 'up' ? 
                        Math.max(0, index - 1) : 
                        Math.min(this.blocks.length - 1, index + 1);
                        
        if (newIndex === index) return;
        
        const block = this.blocks[index];
        this.blocks.splice(index, 1);
        this.blocks.splice(newIndex, 0, block);
        
        this.render();
        this.selectBlock(blockId);
    }
    
    // Обновить содержимое блока
    updateBlockContent(blockId, content) {
        const block = this.blocks.find(block => block.id === blockId);
        if (block) {
            block.content = content;
        }
    }
    
    // Отрисовать блоки
    render() {
        console.log("Rendering blocks:", this.blocks.length);
        // Очищаем содержимое редактора
        this.editorContainer.innerHTML = '';
        
        if (this.blocks.length === 0) {
            console.log("No blocks to render, showing placeholder");
            const placeholder = document.createElement('div');
            placeholder.className = 'sf-empty-editor';
            placeholder.innerHTML = 'Добавьте свой первый блок, нажав кнопку +';
            this.editorContainer.appendChild(placeholder);
            return;
        }
        
        // Отрисовываем каждый блок
        this.blocks.forEach((block, index) => {
            console.log(`Rendering block ${index}:`, block.type);
            const blockElement = this.createBlockElement(block, index);
            this.editorContainer.appendChild(blockElement);
        });
    }
    
    // Создать элемент блока
    createBlockElement(block, index) {
        const blockContainer = document.createElement('div');
        blockContainer.className = 'sf-block';
        blockContainer.dataset.blockId = block.id;
        blockContainer.dataset.blockType = block.type;
        
        if (this.selectedBlock === block.id) {
            blockContainer.classList.add('sf-block-selected');
        }
        
        // Добавляем кнопки управления блоком
        const blockControls = document.createElement('div');
        blockControls.className = 'sf-block-controls';
        
        const moveUpButton = document.createElement('button');
        moveUpButton.className = 'move-up-button';
        moveUpButton.innerHTML = '↑';
        moveUpButton.title = 'Переместить вверх';
        blockControls.appendChild(moveUpButton);
        
        const moveDownButton = document.createElement('button');
        moveDownButton.className = 'move-down-button';
        moveDownButton.innerHTML = '↓';
        moveDownButton.title = 'Переместить вниз';
        blockControls.appendChild(moveDownButton);
        
        const deleteButton = document.createElement('button');
        deleteButton.className = 'delete-block-button';
        deleteButton.innerHTML = '×';
        deleteButton.title = 'Удалить блок';
        blockControls.appendChild(deleteButton);
        
        blockContainer.appendChild(blockControls);
        
        // Создаем содержимое блока
        const blockContent = document.createElement('div');
        blockContent.className = 'sf-block-content';
        blockContainer.appendChild(blockContent);
        
        // Создаем специфичное для типа блока содержимое
        switch (block.type) {
            case 'heading1':
            case 'heading2':
            case 'heading3':
                this.createHeadingBlock(blockContent, block);
                break;
            case 'paragraph':
                this.createParagraphBlock(blockContent, block);
                break;
            case 'bullet-list':
                this.createBulletListBlock(blockContent, block);
                break;
            case 'numbered-list':
                this.createNumberedListBlock(blockContent, block);
                break;
            case 'quote':
                this.createQuoteBlock(blockContent, block);
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
            case 'image':
                this.createImageBlock(blockContent, block);
                break;
            case 'audio':
                this.createAudioBlock(blockContent, block);
                break;
            case 'video':
                this.createVideoBlock(blockContent, block);
                break;
            case 'info':
            case 'warning': 
            case 'danger':
                this.createInfoBlock(blockContent, block);
                break;
            default:
                // Для неизвестных типов создаем параграф
                this.createParagraphBlock(blockContent, block);
        }
        
        // Добавляем кнопку "+" для добавления нового блока после текущего
        const addBlockButton = document.createElement('button');
        addBlockButton.className = 'add-block-button';
        addBlockButton.dataset.blockId = block.id;
        addBlockButton.innerHTML = '+';
        addBlockButton.title = 'Добавить новый блок';
        blockContainer.appendChild(addBlockButton);
        
        return blockContainer;
    }
    
    // Создать блок заголовка
    createHeadingBlock(container, block) {
        const level = block.type.replace('heading', '');
        const input = document.createElement('input');
        input.className = `sf-heading-input sf-heading${level} sf-single-line`;
        input.value = block.content;
        input.placeholder = `Заголовок ${level}`;
        
        input.addEventListener('input', () => {
            this.updateBlockContent(block.id, input.value);
        });
        
        container.appendChild(input);
    }
    
    // Создать блок параграфа
    createParagraphBlock(container, block) {
        const textarea = document.createElement('textarea');
        textarea.className = 'sf-paragraph-input';
        textarea.value = block.content;
        textarea.placeholder = 'Введите текст...';
        
        textarea.addEventListener('input', () => {
            this.updateBlockContent(block.id, textarea.value);
            // Автоматически изменяем размер textarea
            textarea.style.height = 'auto';
            textarea.style.height = textarea.scrollHeight + 'px';
        });
        
        // Устанавливаем начальный размер
        setTimeout(() => {
            textarea.style.height = 'auto';
            textarea.style.height = textarea.scrollHeight + 'px';
        }, 0);
        
        container.appendChild(textarea);
    }
    
    // Создать блок маркированного списка
    createBulletListBlock(container, block) {
        const textarea = document.createElement('textarea');
        textarea.className = 'sf-list-input sf-bullet-list';
        textarea.value = block.content;
        textarea.placeholder = '• Пункт списка (каждая строка - отдельный пункт)';
        
        textarea.addEventListener('input', () => {
            this.updateBlockContent(block.id, textarea.value);
            // Автоматически изменяем размер textarea
            textarea.style.height = 'auto';
            textarea.style.height = textarea.scrollHeight + 'px';
        });
        
        // Устанавливаем начальный размер
        setTimeout(() => {
            textarea.style.height = 'auto';
            textarea.style.height = textarea.scrollHeight + 'px';
        }, 0);
        
        container.appendChild(textarea);
    }
    
    // Создать блок нумерованного списка
    createNumberedListBlock(container, block) {
        const textarea = document.createElement('textarea');
        textarea.className = 'sf-list-input sf-numbered-list';
        textarea.value = block.content;
        textarea.placeholder = '1. Пункт списка (каждая строка - отдельный пункт)';
        
        textarea.addEventListener('input', () => {
            this.updateBlockContent(block.id, textarea.value);
            // Автоматически изменяем размер textarea
            textarea.style.height = 'auto';
            textarea.style.height = textarea.scrollHeight + 'px';
        });
        
        // Устанавливаем начальный размер
        setTimeout(() => {
            textarea.style.height = 'auto';
            textarea.style.height = textarea.scrollHeight + 'px';
        }, 0);
        
        container.appendChild(textarea);
    }
    
    // Создать блок цитаты
    createQuoteBlock(container, block) {
        const textarea = document.createElement('textarea');
        textarea.className = 'sf-quote-input';
        textarea.value = block.content;
        textarea.placeholder = 'Введите цитату...';
        
        textarea.addEventListener('input', () => {
            this.updateBlockContent(block.id, textarea.value);
            // Автоматически изменяем размер textarea
            textarea.style.height = 'auto';
            textarea.style.height = textarea.scrollHeight + 'px';
        });
        
        // Устанавливаем начальный размер
        setTimeout(() => {
            textarea.style.height = 'auto';
            textarea.style.height = textarea.scrollHeight + 'px';
        }, 0);
        
        container.appendChild(textarea);
    }
    
    // Создать блок кода
    createCodeBlock(container, block) {
        const wrapper = document.createElement('div');
        wrapper.className = 'sf-code-block-wrapper';
        
        // Поле выбора языка программирования
        const languageSelect = document.createElement('select');
        languageSelect.className = 'sf-code-language';
        
        const languages = [
            { value: '', label: 'Обычный текст' },
            { value: 'python', label: 'Python' },
            { value: 'javascript', label: 'JavaScript' },
            { value: 'html', label: 'HTML' },
            { value: 'css', label: 'CSS' },
            { value: 'markdown', label: 'Markdown' },
            { value: 'bash', label: 'Bash' },
            { value: 'sql', label: 'SQL' },
            { value: 'json', label: 'JSON' },
            { value: 'yaml', label: 'YAML' }
        ];
        
        // Парсим содержимое - первая строка может содержать информацию о языке
        let codeContent = block.content;
        let language = '';
        
        if (block.content.startsWith('```')) {
            const firstLineEnd = block.content.indexOf('\n');
            if (firstLineEnd > 3) {
                language = block.content.substring(3, firstLineEnd).trim();
                codeContent = block.content.substring(firstLineEnd + 1);
                
                // Удаляем закрывающие ``` если они есть
                if (codeContent.endsWith('```')) {
                    codeContent = codeContent.substring(0, codeContent.length - 3).trim();
                }
            }
        }
        
        // Заполняем select языками
        languages.forEach(lang => {
            const option = document.createElement('option');
            option.value = lang.value;
            option.textContent = lang.label;
            if (lang.value === language) {
                option.selected = true;
            }
            languageSelect.appendChild(option);
        });
        
        const textarea = document.createElement('textarea');
        textarea.className = 'sf-code-input';
        textarea.value = codeContent;
        textarea.placeholder = 'Введите код...';
        
        // Обновляем содержимое при изменении
        const updateCodeBlock = () => {
            const lang = languageSelect.value;
            let content = textarea.value;
            
            // Форматируем содержимое с маркерами markdown
            if (lang) {
                this.updateBlockContent(block.id, '```' + lang + '\n' + content + '\n```');
            } else {
                this.updateBlockContent(block.id, '```\n' + content + '\n```');
            }
            
            // Автоматически изменяем размер textarea
            textarea.style.height = 'auto';
            textarea.style.height = textarea.scrollHeight + 'px';
        };
        
        textarea.addEventListener('input', updateCodeBlock);
        languageSelect.addEventListener('change', updateCodeBlock);
        
        // Устанавливаем начальный размер
        setTimeout(() => {
            textarea.style.height = 'auto';
            textarea.style.height = textarea.scrollHeight + 'px';
        }, 0);
        
        wrapper.appendChild(languageSelect);
        wrapper.appendChild(textarea);
        container.appendChild(wrapper);
    }
    
    // Создать блок математической формулы
    createMathBlock(container, block) {
        const wrapper = document.createElement('div');
        wrapper.className = 'sf-math-block-wrapper';
        
        const textarea = document.createElement('textarea');
        textarea.className = 'sf-math-input';
        textarea.value = block.content.replace(/^\$\$|\$\$$/g, ''); // Удаляем $$ в начале и конце если есть
        textarea.placeholder = 'Введите математическую формулу в формате LaTeX...';
        
        const preview = document.createElement('div');
        preview.className = 'sf-math-preview';
        preview.innerHTML = '<div class="sf-preview-label">Предпросмотр:</div>';
        
        const formulaDisplay = document.createElement('div');
        formulaDisplay.className = 'sf-math-formula';
        preview.appendChild(formulaDisplay);
        
        textarea.addEventListener('input', () => {
            const formula = textarea.value;
            this.updateBlockContent(block.id, '$$' + formula + '$$');
            
            // Обновляем предпросмотр если доступен KaTeX
            if (window.katex) {
                try {
                    katex.render(formula, formulaDisplay, {
                        throwOnError: false,
                        displayMode: true
                    });
                } catch (e) {
                    formulaDisplay.innerHTML = '<span style="color: red;">Ошибка рендеринга: ' + e.message + '</span>';
                }
            } else {
                formulaDisplay.textContent = formula;
            }
            
            // Автоматически изменяем размер textarea
            textarea.style.height = 'auto';
            textarea.style.height = textarea.scrollHeight + 'px';
        });
        
        // Устанавливаем начальный размер и вызываем обработчик для инициализации предпросмотра
        setTimeout(() => {
            textarea.style.height = 'auto';
            textarea.style.height = textarea.scrollHeight + 'px';
            textarea.dispatchEvent(new Event('input'));
        }, 0);
        
        wrapper.appendChild(textarea);
        wrapper.appendChild(preview);
        container.appendChild(wrapper);
    }
    
    // Создать блок диаграммы
    createDiagramBlock(container, block) {
        const wrapper = document.createElement('div');
        wrapper.className = 'sf-diagram-block-wrapper';
        
        const textarea = document.createElement('textarea');
        textarea.className = 'sf-diagram-input';
        
        // Извлекаем содержимое диаграммы без тегов ```mermaid
        let diagramContent = block.content;
        if (block.content.startsWith('```mermaid')) {
            diagramContent = block.content.replace(/^```mermaid\n|```$/g, '');
        }
        
        textarea.value = diagramContent;
        textarea.placeholder = 'Введите код диаграммы Mermaid...';
        
        const preview = document.createElement('div');
        preview.className = 'sf-diagram-preview';
        preview.innerHTML = '<div class="sf-preview-label">Предпросмотр:</div>';
        
        const diagramDisplay = document.createElement('div');
        diagramDisplay.className = 'mermaid';
        preview.appendChild(diagramDisplay);
        
        textarea.addEventListener('input', () => {
            const diagram = textarea.value;
            this.updateBlockContent(block.id, '```mermaid\n' + diagram + '\n```');
            
            // Обновляем предпросмотр диаграммы, если доступен Mermaid
            diagramDisplay.textContent = diagram; // Сначала устанавливаем текст
            
            if (window.mermaid) {
                try {
                    // Уникальный ID для диаграммы
                    const id = 'mermaid-' + block.id;
                    diagramDisplay.id = id;
                    
                    // Очищаем предыдущую диаграмму
                    diagramDisplay.innerHTML = diagram;
                    
                    // Рендерим новую диаграмму
                    window.mermaid.init(undefined, diagramDisplay);
                } catch (e) {
                    diagramDisplay.innerHTML = '<span style="color: red;">Ошибка рендеринга: ' + e.message + '</span>';
                }
            }
            
            // Автоматически изменяем размер textarea
            textarea.style.height = 'auto';
            textarea.style.height = textarea.scrollHeight + 'px';
        });
        
        // Устанавливаем начальный размер и вызываем обработчик для инициализации предпросмотра
        setTimeout(() => {
            textarea.style.height = 'auto';
            textarea.style.height = textarea.scrollHeight + 'px';
            textarea.dispatchEvent(new Event('input'));
        }, 0);
        
        wrapper.appendChild(textarea);
        wrapper.appendChild(preview);
        container.appendChild(wrapper);
    }
    
    // Создать блок изображения
    createImageBlock(container, block) {
        const wrapper = document.createElement('div');
        wrapper.className = 'sf-image-block-wrapper';
        
        // Извлекаем URL и alt текст из markdown
        let imageUrl = '';
        let altText = '';
        
        const mdMatch = block.content.match(/!\[(.*?)\]\((.*?)\)/);
        if (mdMatch) {
            altText = mdMatch[1] || '';
            imageUrl = mdMatch[2] || '';
        }
        
        // Поле для URL
        const urlInput = document.createElement('input');
        urlInput.className = 'sf-image-url-input';
        urlInput.placeholder = 'URL изображения';
        urlInput.value = imageUrl;
        
        // Поле для альтернативного текста
        const altInput = document.createElement('input');
        altInput.className = 'sf-image-alt-input';
        altInput.placeholder = 'Альтернативный текст';
        altInput.value = altText;
        
        // Предпросмотр изображения
        const preview = document.createElement('div');
        preview.className = 'sf-image-preview';
        
        // Обновляем блок и предпросмотр
        const updateImageBlock = () => {
            const url = urlInput.value.trim();
            const alt = altInput.value.trim();
            
            this.updateBlockContent(block.id, `![${alt}](${url})`);
            
            // Обновляем предпросмотр
            if (url) {
                preview.innerHTML = `<img src="${url}" alt="${alt}" style="max-width: 100%;">`;
            } else {
                preview.innerHTML = '<div class="sf-empty-preview">Предпросмотр изображения</div>';
            }
        };
        
        urlInput.addEventListener('input', updateImageBlock);
        altInput.addEventListener('input', updateImageBlock);
        
        // Кнопка для загрузки изображения (просто заглушка)
        const uploadButton = document.createElement('button');
        uploadButton.className = 'sf-upload-button';
        uploadButton.textContent = 'Загрузить';
        uploadButton.addEventListener('click', () => {
            alert('Функция загрузки изображений будет доступна в следующем обновлении.');
        });
        
        // Инициализируем предпросмотр
        updateImageBlock();
        
        // Поля ввода группируем в контейнер
        const inputsContainer = document.createElement('div');
        inputsContainer.className = 'sf-image-inputs';
        inputsContainer.appendChild(urlInput);
        inputsContainer.appendChild(altInput);
        inputsContainer.appendChild(uploadButton);
        
        wrapper.appendChild(inputsContainer);
        wrapper.appendChild(preview);
        container.appendChild(wrapper);
    }
    
    // Создать блок аудио
    createAudioBlock(container, block) {
        const wrapper = document.createElement('div');
        wrapper.className = 'sf-audio-block-wrapper';
        
        // Извлекаем URL и описание
        let audioUrl = '';
        let description = '';
        
        // Проверяем формат: [description](url)
        const mdMatch = block.content.match(/\[(.*?)\]\((.*?)\)/);
        if (mdMatch) {
            description = mdMatch[1] || '';
            audioUrl = mdMatch[2] || '';
        }
        
        // Поле для URL
        const urlInput = document.createElement('input');
        urlInput.className = 'sf-audio-url-input';
        urlInput.placeholder = 'URL аудио файла';
        urlInput.value = audioUrl;
        
        // Поле для описания
        const descInput = document.createElement('input');
        descInput.className = 'sf-audio-desc-input';
        descInput.placeholder = 'Описание';
        descInput.value = description;
        
        // Предпросмотр аудио
        const preview = document.createElement('div');
        preview.className = 'sf-audio-preview';
        
        // Обновляем блок и предпросмотр
        const updateAudioBlock = () => {
            const url = urlInput.value.trim();
            const desc = descInput.value.trim();
            
            this.updateBlockContent(block.id, `[${desc}](${url}) {.audio}`);
            
            // Обновляем предпросмотр
            if (url) {
                preview.innerHTML = `
                    <audio controls style="width: 100%;">
                        <source src="${url}" type="audio/mpeg">
                        Ваш браузер не поддерживает аудио элемент.
                    </audio>
                    <div class="sf-audio-desc">${desc}</div>
                `;
            } else {
                preview.innerHTML = '<div class="sf-empty-preview">Предпросмотр аудио</div>';
            }
        };
        
        urlInput.addEventListener('input', updateAudioBlock);
        descInput.addEventListener('input', updateAudioBlock);
        
        // Инициализируем предпросмотр
        updateAudioBlock();
        
        // Поля ввода группируем в контейнер
        const inputsContainer = document.createElement('div');
        inputsContainer.className = 'sf-audio-inputs';
        inputsContainer.appendChild(urlInput);
        inputsContainer.appendChild(descInput);
        
        wrapper.appendChild(inputsContainer);
        wrapper.appendChild(preview);
        container.appendChild(wrapper);
    }
    
    // Создать блок видео
    createVideoBlock(container, block) {
        const wrapper = document.createElement('div');
        wrapper.className = 'sf-video-block-wrapper';
        
        // Извлекаем URL и описание
        let videoUrl = '';
        let description = '';
        
        // Проверяем формат: [description](url)
        const mdMatch = block.content.match(/\[(.*?)\]\((.*?)\)/);
        if (mdMatch) {
            description = mdMatch[1] || '';
            videoUrl = mdMatch[2] || '';
        }
        
        // Поле для URL
        const urlInput = document.createElement('input');
        urlInput.className = 'sf-video-url-input';
        urlInput.placeholder = 'URL видео или YouTube/Vimeo ID';
        urlInput.value = videoUrl;
        
        // Поле для описания
        const descInput = document.createElement('input');
        descInput.className = 'sf-video-desc-input';
        descInput.placeholder = 'Описание';
        descInput.value = description;
        
        // Предпросмотр видео
        const preview = document.createElement('div');
        preview.className = 'sf-video-preview';
        
        // Обновляем блок и предпросмотр
        const updateVideoBlock = () => {
            const url = urlInput.value.trim();
            const desc = descInput.value.trim();
            
            this.updateBlockContent(block.id, `[${desc}](${url}) {.video}`);
            
            // Обновляем предпросмотр
            if (url) {
                // Проверяем тип URL (YouTube, Vimeo или обычное видео)
                if (url.includes('youtube.com') || url.includes('youtu.be')) {
                    // Извлекаем ID видео из YouTube URL
                    let videoId = url;
                    if (url.includes('youtube.com/watch?v=')) {
                        videoId = url.split('v=')[1].split('&')[0];
                    } else if (url.includes('youtu.be/')) {
                        videoId = url.split('youtu.be/')[1];
                    }
                    
                    preview.innerHTML = `
                        <iframe width="100%" height="315" 
                                src="https://www.youtube.com/embed/${videoId}" 
                                frameborder="0" 
                                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                                allowfullscreen></iframe>
                        <div class="sf-video-desc">${desc}</div>
                    `;
                } else if (url.includes('vimeo.com')) {
                    // Извлекаем ID видео из Vimeo URL
                    let videoId = url;
                    if (url.includes('vimeo.com/')) {
                        videoId = url.split('vimeo.com/')[1];
                    }
                    
                    preview.innerHTML = `
                        <iframe src="https://player.vimeo.com/video/${videoId}" 
                                width="100%" height="315" 
                                frameborder="0" 
                                allow="autoplay; fullscreen; picture-in-picture" 
                                allowfullscreen></iframe>
                        <div class="sf-video-desc">${desc}</div>
                    `;
                } else {
                    // Обычное видео
                    preview.innerHTML = `
                        <video controls style="width: 100%;">
                            <source src="${url}" type="video/mp4">
                            Ваш браузер не поддерживает видео элемент.
                        </video>
                        <div class="sf-video-desc">${desc}</div>
                    `;
                }
            } else {
                preview.innerHTML = '<div class="sf-empty-preview">Предпросмотр видео</div>';
            }
        };
        
        urlInput.addEventListener('input', updateVideoBlock);
        descInput.addEventListener('input', updateVideoBlock);
        
        // Инициализируем предпросмотр
        updateVideoBlock();
        
        // Поля ввода группируем в контейнер
        const inputsContainer = document.createElement('div');
        inputsContainer.className = 'sf-video-inputs';
        inputsContainer.appendChild(urlInput);
        inputsContainer.appendChild(descInput);
        
        wrapper.appendChild(inputsContainer);
        wrapper.appendChild(preview);
        container.appendChild(wrapper);
    }
    
    // Создать информационный/предупреждающий блок
    createInfoBlock(container, block) {
        const wrapper = document.createElement('div');
        wrapper.className = `sf-${block.type}-block-wrapper`;
        
        // Получаем содержимое блока без обертки :::
        let content = block.content;
        const typeLabel = {
            'info': 'Информация',
            'warning': 'Предупреждение',
            'danger': 'Опасность'
        };
        
        // Проверяем формат: :::type title\ncontent:::
        const regex = new RegExp(`:::${block.type}(.*?):::`);
        const match = content.match(regex);
        if (match) {
            content = match[1];
        }
        
        // Создаем поле для заголовка
        const titleInput = document.createElement('input');
        titleInput.className = `sf-${block.type}-title-input`;
        titleInput.placeholder = `Заголовок (${typeLabel[block.type]})`;
        
        // Создаем текстовое поле для содержимого
        const textarea = document.createElement('textarea');
        textarea.className = `sf-${block.type}-input`;
        textarea.placeholder = 'Содержимое блока...';
        
        // Разделяем заголовок и содержимое
        const firstLineBreak = content.indexOf('\n');
        if (firstLineBreak > 0) {
            titleInput.value = content.substring(0, firstLineBreak).trim();
            textarea.value = content.substring(firstLineBreak + 1).trim();
        } else {
            textarea.value = content.trim();
        }
        
        // Обновляем блок
        const updateInfoBlock = () => {
            const title = titleInput.value.trim();
            const text = textarea.value.trim();
            
            let updatedContent;
            if (title) {
                updatedContent = `:::${block.type} ${title}\n${text}:::`;
            } else {
                updatedContent = `:::${block.type}\n${text}:::`;
            }
            
            this.updateBlockContent(block.id, updatedContent);
            
            // Автоматически изменяем размер textarea
            textarea.style.height = 'auto';
            textarea.style.height = textarea.scrollHeight + 'px';
        };
        
        titleInput.addEventListener('input', updateInfoBlock);
        textarea.addEventListener('input', updateInfoBlock);
        
        // Устанавливаем начальный размер
        setTimeout(() => {
            textarea.style.height = 'auto';
            textarea.style.height = textarea.scrollHeight + 'px';
        }, 0);
        
        // Предпросмотр блока
        const preview = document.createElement('div');
        preview.className = 'sf-info-preview';
        preview.innerHTML = `<div class="sf-preview-${block.type}">
            <div class="sf-preview-title">${typeLabel[block.type]}</div>
            <div class="sf-preview-content">${textarea.value}</div>
        </div>`;
        
        wrapper.appendChild(titleInput);
        wrapper.appendChild(textarea);
        wrapper.appendChild(preview);
        container.appendChild(wrapper);
    }
    
    // Сериализовать содержимое
    serialize() {
        let markdown = '';
        
        this.blocks.forEach(block => {
            switch (block.type) {
                case 'heading1':
                    markdown += `# ${block.content}\n\n`;
                    break;
                case 'heading2':
                    markdown += `## ${block.content}\n\n`;
                    break;
                case 'heading3':
                    markdown += `### ${block.content}\n\n`;
                    break;
                case 'paragraph':
                    markdown += `${block.content}\n\n`;
                    break;
                case 'bullet-list':
                    // Обрабатываем каждую строку как отдельный пункт списка
                    {
                        const lines = block.content.split('\n');
                        lines.forEach(line => {
                            if (line.trim()) {
                                markdown += `* ${line.trim()}\n`;
                            }
                        });
                        markdown += '\n';
                    }
                    break;
                case 'numbered-list':
                    // Обрабатываем каждую строку как отдельный пункт списка
                    {
                        const lines = block.content.split('\n');
                        lines.forEach((line, index) => {
                            if (line.trim()) {
                                markdown += `${index + 1}. ${line.trim()}\n`;
                            }
                        });
                        markdown += '\n';
                    }
                    break;
                case 'quote':
                    // Добавляем символ > к каждой строке цитаты
                    {
                        const lines = block.content.split('\n');
                        lines.forEach(line => {
                            markdown += `> ${line}\n`;
                        });
                        markdown += '\n';
                    }
                    break;
                case 'code':
                case 'math':
                case 'diagram':
                    // Для блоков кода, мат. формул и диаграмм сохраняем как есть
                    markdown += `${block.content}\n\n`;
                    break;
                case 'image':
                case 'audio':
                case 'video':
                    // Для медиа блоков сохраняем markdown разметку
                    markdown += `${block.content}\n\n`;
                    break;
                case 'info':
                case 'warning':
                case 'danger':
                    // Для инфо-блоков сохраняем с обертками :::
                    markdown += `${block.content}\n\n`;
                    break;
                default:
                    // Для неизвестных типов сохраняем как текст
                    markdown += `${block.content}\n\n`;
            }
        });
        
        return markdown.trim();
    }
    
    // Десериализовать содержимое
    deserializeContent(content) {
        console.log("Deserializing content...");
        if (!content) {
            console.log("Content is empty, nothing to deserialize");
            return;
        }
        
        // Регулярные выражения для поиска блоков в markdown
        const patterns = [
            { type: 'heading1', pattern: /^# (.+)$/gm },
            { type: 'heading2', pattern: /^## (.+)$/gm },
            { type: 'heading3', pattern: /^### (.+)$/gm },
            { type: 'quote', pattern: /^>(.+)(?:\n>(.+))*$/gm },
            { type: 'bullet-list', pattern: /^[*+-](.+)(?:\n[*+-](.+))*$/gm },
            { type: 'numbered-list', pattern: /^(\d+\.|\d+\))(.+)(?:\n(\d+\.|\d+\))(.+))*$/gm },
            { type: 'code', pattern: /^```[\s\S]*?^```$/gm },
            { type: 'math', pattern: /^\$\$([\s\S]*?)\$\$$/gm },
            { type: 'diagram', pattern: /^```mermaid[\s\S]*?^```$/gm },
            { type: 'image', pattern: /^!\[.*?\]\(.*?\)$/gm },
            { type: 'info', pattern: /^:::info[\s\S]*?^:::$/gm },
            { type: 'warning', pattern: /^:::warning[\s\S]*?^:::$/gm },
            { type: 'danger', pattern: /^:::danger[\s\S]*?^:::$/gm },
            { type: 'audio', pattern: /^\[.*?\]\(.*?\) \{\.audio\}$/gm },
            { type: 'video', pattern: /^\[.*?\]\(.*?\) \{\.video\}$/gm }
        ];
        
        // Заменяем переносы строк на единый формат
        content = content.replace(/\r\n/g, '\n');
        
        // Сначала проходим по контенту и помечаем блоки
        const blocks = [];
        let remainingContent = content;
        
        // Функция для обработки блока
        const processBlock = (match, type, position) => {
            blocks.push({
                type: type,
                content: match[0],
                position: position
            });
            
            // Заменяем найденный блок на плейсхолдер
            const placeholder = `___BLOCK_${blocks.length - 1}___`;
            remainingContent = remainingContent.replace(match[0], placeholder);
        };
        
        // Проходим по всем паттернам и ищем блоки
        let anyMatchFound = true;
        while (anyMatchFound) {
            anyMatchFound = false;
            
            for (const { type, pattern } of patterns) {
                pattern.lastIndex = 0; // Сбрасываем индекс поиска
                
                const match = pattern.exec(remainingContent);
                if (match) {
                    const position = match.index;
                    processBlock(match, type, position);
                    anyMatchFound = true;
                    break; // После нахождения одного блока начинаем поиск заново
                }
            }
        }
        
        // Разбиваем оставшийся контент на параграфы
        const paragraphs = remainingContent
            .split(/___BLOCK_\d+___/)
            .filter(p => p.trim())
            .map(p => p.trim())
            .reduce((acc, p) => {
                // Разбиваем на параграфы по двойным переносам строк
                const paragraphSplit = p.split(/\n\s*\n/);
                return acc.concat(paragraphSplit);
            }, [])
            .filter(p => p.trim());
        
        // Добавляем параграфы в список блоков
        paragraphs.forEach(p => {
            blocks.push({
                type: 'paragraph',
                content: p,
                position: content.indexOf(p)
            });
        });
        
        // Сортируем блоки по их позиции в исходном тексте
        blocks.sort((a, b) => a.position - b.position);
        
        // Создаем блоки редактора
        this.blocks = [];
        
        blocks.forEach(block => {
            // Создаем блок соответствующего типа
            const newBlock = {
                id: Date.now().toString() + Math.floor(Math.random() * 1000),
                type: block.type,
                content: block.content
            };
            
            // Обрабатываем содержимое блока
            switch (block.type) {
                case 'heading1':
                case 'heading2':
                case 'heading3':
                    newBlock.content = block.content.replace(/^#+\s*/, '');
                    break;
                case 'bullet-list':
                    newBlock.content = block.content
                        .split('\n')
                        .map(line => line.replace(/^[*+-]\s*/, ''))
                        .join('\n');
                    break;
                case 'numbered-list':
                    newBlock.content = block.content
                        .split('\n')
                        .map(line => line.replace(/^\d+\.|\d+\)\s*/, ''))
                        .join('\n');
                    break;
                case 'quote':
                    newBlock.content = block.content
                        .split('\n')
                        .map(line => line.replace(/^>\s*/, ''))
                        .join('\n');
                    break;
                // Для остальных типов оставляем как есть
            }
            
            this.blocks.push(newBlock);
        });
        
        console.log(`Deserialized ${this.blocks.length} blocks`);
    }
    
    // Получить содержимое редактора
    getContent() {
        return this.serialize();
    }
}

// Make the editor available globally
window.BlockEditor = BlockEditor; 