/**
 * StaticFlow Block Editor v3.0 - Drag and Drop
 * Drag and drop functionality for the block editor
 */

// Modified for non-module loading
(function() {
    // Create drop indicator element
    function createDropIndicator() {
        this.dropIndicator = document.createElement('div');
        this.dropIndicator.className = 'sf-block-drop-indicator';
        this.dropIndicator.innerHTML = '<div class="sf-block-drop-indicator-line"></div>';
        this.dropIndicator.style.display = 'none';
        this.editorContainer.appendChild(this.dropIndicator);
    }
    
    // Set up drag and drop
    function setupDragAndDrop() {
        document.addEventListener('mousemove', (e) => this.handleMouseMove(e));
        document.addEventListener('mouseup', (e) => this.handleMouseUp(e));
    }
    
    // Handle mouse move during drag
    function handleMouseMove(e) {
        // Update the last mouse position
        this.lastMousePosition = { x: e.clientX, y: e.clientY };
        
        if (!this.isDragging || !this.draggedBlockElement) return;
        
        // Position the dragged block element at the mouse position
        this.draggedBlockElement.style.left = (e.clientX - this.dragOffset.x) + 'px';
        this.draggedBlockElement.style.top = (e.clientY - this.dragOffset.y) + 'px';
        
        // Update the drop indicator position
        this.updateDropIndicatorPosition(e);
    }
    
    // Handle mouse up after drag
    function handleMouseUp(e) {
        if (!this.isDragging) return;
        
        this.isDragging = false;
        
        // Remove the drop indicator
        if (this.dropIndicator) {
            this.dropIndicator.style.display = 'none';
        }
        
        // Remove the dragged block element from the DOM
        if (this.draggedBlockElement && this.draggedBlockElement.parentNode) {
            this.draggedBlockElement.parentNode.removeChild(this.draggedBlockElement);
        }
        
        // Determine the drop position based on the drop indicator position
        if (this.dropIndicator && this.dropIndicator.dataset.position) {
            const dropPosition = parseInt(this.dropIndicator.dataset.position);
            const draggedBlockId = this.draggedBlock;
            
            // Move the block to the new position
            this.moveBlock(draggedBlockId, dropPosition);
        }
        
        // Reset the dragged block
        this.draggedBlock = null;
        this.draggedBlockElement = null;
    }
    
    // Start dragging a block
    function startDragging(blockId, e) {
        if (this.isDragging) return;
        
        this.isDragging = true;
        this.draggedBlock = blockId;
        
        // Find the block element
        const blockElement = this.editorContainer.querySelector(`.sf-block[data-block-id="${blockId}"]`);
        if (!blockElement) return;
        
        // Create a clone of the block element
        this.draggedBlockElement = blockElement.cloneNode(true);
        this.draggedBlockElement.classList.add('sf-block-dragging');
        
        // Get the position of the block element
        const rect = blockElement.getBoundingClientRect();
        
        // Calculate the offset from the mouse to the top-left corner of the block
        this.dragOffset = {
            x: e.clientX - rect.left,
            y: e.clientY - rect.top
        };
        
        // Position the dragged block element
        this.draggedBlockElement.style.position = 'fixed';
        this.draggedBlockElement.style.width = rect.width + 'px';
        this.draggedBlockElement.style.left = rect.left + 'px';
        this.draggedBlockElement.style.top = rect.top + 'px';
        this.draggedBlockElement.style.zIndex = '1000';
        this.draggedBlockElement.style.opacity = '0.8';
        this.draggedBlockElement.style.pointerEvents = 'none';
        
        // Add the dragged block element to the DOM
        document.body.appendChild(this.draggedBlockElement);
        
        // Update the drop indicator position
        this.updateDropIndicatorPosition(e);
    }
    
    // Update the position of the drop indicator
    function updateDropIndicatorPosition(e) {
        if (!this.isDragging || !this.dropIndicator) return;
        
        // Show the drop indicator
        this.dropIndicator.style.display = 'block';
        
        // Get all block elements (excluding the dragged block)
        const blockElements = Array.from(this.editorContainer.querySelectorAll('.sf-block:not(.sf-block-dragging)'));
        
        // Calculate the position for the drop indicator
        let insertPosition = 0;
        let closestDistance = Number.MAX_VALUE;
        let found = false;
        
        blockElements.forEach((element, index) => {
            const rect = element.getBoundingClientRect();
            const middle = rect.top + rect.height / 2;
            const distance = Math.abs(e.clientY - middle);
            
            // If the mouse is closer to this element than the previous closest
            if (distance < closestDistance) {
                closestDistance = distance;
                
                // Determine if we're above or below the middle of the element
                if (e.clientY < middle) {
                    // Above - insert before this element
                    insertPosition = index;
                } else {
                    // Below - insert after this element
                    insertPosition = index + 1;
                }
                
                found = true;
            }
        });
        
        // If no blocks found or mouse is above the first block
        if (!found || e.clientY < this.editorContainer.getBoundingClientRect().top) {
            insertPosition = 0;
        }
        
        // If the mouse is below the last block
        if (blockElements.length > 0) {
            const lastBlock = blockElements[blockElements.length - 1];
            const lastBlockRect = lastBlock.getBoundingClientRect();
            
            if (e.clientY > lastBlockRect.bottom) {
                insertPosition = blockElements.length;
            }
        }
        
        // Set the position in the drop indicator
        this.dropIndicator.dataset.position = insertPosition;
        
        // Position the drop indicator
        if (insertPosition === 0) {
            // At the beginning
            this.dropIndicator.style.top = '0';
            this.dropIndicator.style.transform = 'translateY(-50%)';
        } else if (insertPosition === blockElements.length) {
            // At the end
            const lastBlock = blockElements[blockElements.length - 1];
            const lastBlockRect = lastBlock.getBoundingClientRect();
            const editorRect = this.editorContainer.getBoundingClientRect();
            
            this.dropIndicator.style.top = (lastBlockRect.bottom - editorRect.top) + 'px';
            this.dropIndicator.style.transform = 'translateY(-50%)';
        } else {
            // Between blocks
            const element = blockElements[insertPosition];
            const rect = element.getBoundingClientRect();
            const editorRect = this.editorContainer.getBoundingClientRect();
            
            this.dropIndicator.style.top = (rect.top - editorRect.top) + 'px';
            this.dropIndicator.style.transform = 'translateY(-50%)';
        }
    }
    
    // Expose to the global scope
    window.createDropIndicator = createDropIndicator;
    window.setupDragAndDrop = setupDragAndDrop;
    window.handleMouseMove = handleMouseMove;
    window.handleMouseUp = handleMouseUp;
    window.startDragging = startDragging;
    window.updateDropIndicatorPosition = updateDropIndicatorPosition;
})(); 