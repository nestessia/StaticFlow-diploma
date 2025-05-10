/**
 * Heading Block Implementation
 */

// Modified for non-module loading
(function() {
    // Create heading block
    function createHeadingBlock(container, block, editor) {
        console.log('createHeadingBlock', {container, block, editor});
        // Initialize meta if it doesn't exist
        if (!block.meta) block.meta = {};
        
        // Map heading types to HTML heading levels if not already set
        if (!block.meta.level) {
            switch (block.type) {
                case 'heading1':
                    block.meta.level = 'h1';
                    break;
                case 'heading2':
                    block.meta.level = 'h2';
                    break;
                case 'heading3':
                    block.meta.level = 'h3';
                    break;
                default:
                    block.meta.level = 'h2'; // Default to h2
            }
        }
        
        const headingElement = document.createElement(block.meta.level);
        headingElement.className = 'sf-heading-block';
        
        if (block.isPreview) {
            // Display preview mode
            headingElement.textContent = block.content || 'Heading';
            headingElement.className = 'sf-heading-block sf-heading-preview';
        } else {
            // Create contenteditable heading
            headingElement.contentEditable = true;
            headingElement.textContent = block.content || '';
            headingElement.dataset.placeholder = 'Heading';
            
            // Event listener для обновления содержимого
            headingElement.addEventListener('input', () => {
                editor.updateBlockContent(block.id, headingElement.textContent);
            });
            
            // Добавляем элемент заголовка непосредственно в контейнер, без выпадающего списка
            container.appendChild(headingElement);
            return;
        }
        
        container.appendChild(headingElement);
    }

    // Expose to global scope
    window.createHeadingBlock = createHeadingBlock;
})(); 