/**
 * Bullet List Block Implementation
 */

// Modified for non-module loading
(function() {
    // Создать блок маркированного списка
    function createBulletListBlock(container, block) {
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
    
    // Expose to global scope
    window.createBulletListBlock = createBulletListBlock;
})(); 