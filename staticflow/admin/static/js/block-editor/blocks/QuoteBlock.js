/**
 * Quote Block Implementation
 */

// Modified for non-module loading
(function() {
    // Создать блок цитаты
    function createQuoteBlock(container, block, editor) {
        console.log('createQuoteBlock', {container, block, editor});
        // Determine if we should show content or editing interface
        if (block.isPreview) {
            const blockquote = document.createElement('blockquote');
            blockquote.innerHTML = block.content || 'Цитата';
            container.appendChild(blockquote);
        } else {
            const wrapper = document.createElement('div');
            wrapper.className = 'sf-quote-wrapper';
            
            const input = document.createElement('div');
            input.className = 'sf-quote-input';
            input.contentEditable = 'true';
            input.innerHTML = block.content;
            input.dataset.placeholder = 'Введите цитату...';
            input.addEventListener('input', () => {
                editor.updateBlockContent(block.id, input.innerHTML);
            });
            
            wrapper.appendChild(input);
            container.appendChild(wrapper);
        }
    }
    
    // Expose to global scope
    window.createQuoteBlock = createQuoteBlock;
})(); 