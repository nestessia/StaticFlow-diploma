/**
 * InfoBlock Implementation (also used for warning and danger blocks)
 */

// Modified for non-module loading
(function() {
    // Создать информационный/предупреждающий блок
    function createInfoBlock(container, block, editor) {
        console.log('createInfoBlock', {container, block, editor});
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
                editor.updateBlockContent(block.id, contentInput.innerHTML);
            });
            
            infoWrapper.appendChild(titleInput);
            infoWrapper.appendChild(contentInput);
        }
        
        container.appendChild(infoWrapper);
    }
    
    // Expose to global scope
    window.createInfoBlock = createInfoBlock;
})(); 