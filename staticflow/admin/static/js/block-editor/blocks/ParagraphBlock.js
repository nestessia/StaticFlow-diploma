/**
 * Paragraph Block Implementation
 */

// Modified for non-module loading
(function() {
    // Создать блок параграфа
    function createParagraphBlock(container, block, editor) {
        console.log('createParagraphBlock', {container, block, editor});
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
            input.addEventListener('input', () => {
                editor.updateBlockContent(block.id, input.innerHTML);
            });
            container.appendChild(input);
        }
    }
    
    // Expose to global scope
    window.createParagraphBlock = createParagraphBlock;
})(); 