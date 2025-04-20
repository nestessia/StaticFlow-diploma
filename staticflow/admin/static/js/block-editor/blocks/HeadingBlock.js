/**
 * Heading Block Implementation
 */

// Modified for non-module loading
(function() {
    // Create heading block
    function createHeadingBlock(container, block) {
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
            
            // Create heading level selector
            const levelSelector = document.createElement('select');
            levelSelector.className = 'sf-heading-level-selector';
            
            // Add heading level options
            for (let i = 1; i <= 6; i++) {
                const option = document.createElement('option');
                option.value = `h${i}`;
                option.textContent = `H${i}`;
                if (block.meta.level === `h${i}`) {
                    option.selected = true;
                }
                levelSelector.appendChild(option);
            }
            
            // Event listeners
            headingElement.addEventListener('input', () => {
                this.updateBlockContent(block.id, headingElement.textContent);
            });
            
            levelSelector.addEventListener('change', () => {
                // Update heading level in the meta property
                block.meta.level = levelSelector.value;
                
                // Replace the current heading with a new one of the selected level
                const newHeading = document.createElement(levelSelector.value);
                newHeading.contentEditable = true;
                newHeading.className = 'sf-heading-block';
                newHeading.textContent = headingElement.textContent;
                newHeading.dataset.placeholder = 'Heading';
                
                // Add the same event listener to the new heading
                newHeading.addEventListener('input', () => {
                    this.updateBlockContent(block.id, newHeading.textContent);
                });
                
                // Replace the old heading with the new one
                container.insertBefore(newHeading, headingElement);
                container.removeChild(headingElement);
                
                // Update the reference to the heading element
                headingElement = newHeading;
            });
            
            // Create a wrapper to contain both the heading and the level selector
            const headingWrapper = document.createElement('div');
            headingWrapper.className = 'sf-heading-wrapper';
            
            headingWrapper.appendChild(headingElement);
            headingWrapper.appendChild(levelSelector);
            
            container.appendChild(headingWrapper);
            return;  // Return early since we're using the wrapper
        }
        
        container.appendChild(headingElement);
    }

    // Expose to global scope
    window.createHeadingBlock = createHeadingBlock;
})(); 