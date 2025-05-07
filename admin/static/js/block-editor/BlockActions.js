/**
 * Block Actions - Functions for manipulating blocks
 */

// Modified for non-module loading
(function() {
    // Toggle preview mode for a block
    function toggleBlockPreview(blockId, showPreview) {
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
    
    // Выбрать блок (установить фокус)
    function selectBlock(blockId) {
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
    function addBlock(type, content = '', position = this.blocks.length) {
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
    function removeBlock(blockId) {
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
    function moveBlock(blockId, direction) {
        const blockIndex = this.blocks.findIndex(block => block.id === blockId);
        
        if (blockIndex > -1) {
            let newIndex;
            
            if (typeof direction === 'number') {
                // If direction is a number, treat it as a target position
                newIndex = direction;
                
                // Make sure the index is within bounds
                if (newIndex < 0) newIndex = 0;
                if (newIndex > this.blocks.length) newIndex = this.blocks.length;
                
                // If target is the same as current, do nothing
                if (newIndex === blockIndex) return;
                
                // Adjust the target index if moving down to account for the removal of the block first
                if (newIndex > blockIndex) newIndex--;
            } else if (direction === 'up' && blockIndex > 0) {
                newIndex = blockIndex - 1;
            } else if (direction === 'down' && blockIndex < this.blocks.length - 1) {
                newIndex = blockIndex + 1;
            } else {
                return; // No valid direction specified
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
    function updateBlockContent(blockId, content) {
        const block = this.blocks.find(block => block.id === blockId);
        if (block) {
            block.content = content;
        }
    }
    
    // Check if caret is at the end of an editable element
    function isCaretAtEnd(editableElement) {
        const selection = window.getSelection();
        if (!selection.rangeCount) return false;
        
        const range = selection.getRangeAt(0);
        const clonedRange = range.cloneRange();
        clonedRange.selectNodeContents(editableElement);
        clonedRange.setStart(range.endContainer, range.endOffset);
        
        return clonedRange.collapsed;
    }
    
    // Expose to global scope
    window.toggleBlockPreview = toggleBlockPreview;
    window.selectBlock = selectBlock;
    window.addBlock = addBlock;
    window.removeBlock = removeBlock;
    window.moveBlock = moveBlock;
    window.updateBlockContent = updateBlockContent;
    window.isCaretAtEnd = isCaretAtEnd;
})(); 