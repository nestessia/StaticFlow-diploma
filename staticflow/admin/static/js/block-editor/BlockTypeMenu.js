/**
 * BlockTypeMenu - Functions for block type selection menu
 */

// Modified for non-module loading
(function() {
    // Показать меню выбора типа блока
    function showBlockTypeMenu(button, blockId) {
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
    function hideBlockTypeMenu() {
        const menu = this.editorContainer.querySelector('.block-type-menu');
        if (menu) {
            console.log("Removing block type menu");
            menu.remove();
        }
    }
    
    // Expose to global scope
    window.showBlockTypeMenu = showBlockTypeMenu;
    window.hideBlockTypeMenu = hideBlockTypeMenu;
})(); 