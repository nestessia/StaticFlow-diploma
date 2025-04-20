/**
 * Math Block Implementation
 */

// Modified for non-module loading
(function() {
    // Создать блок математической формулы
    function createMathBlock(container, block) {
        const mathWrapper = document.createElement('div');
        mathWrapper.className = 'sf-math-block-wrapper';
        
        if (block.isPreview) {
            // Create a styled preview of the math formula
            const previewLabel = document.createElement('div');
            previewLabel.className = 'sf-preview-label';
            previewLabel.textContent = 'Math formula';
            
            const mathPreview = document.createElement('div');
            mathPreview.className = 'sf-math-preview';
            
            // Render the formula if KaTeX is available
            if (window.katex) {
                try {
                    window.katex.render(block.content || 'e = mc^2', mathPreview, {
                        throwOnError: false,
                        displayMode: true
                    });
                } catch (e) {
                    mathPreview.textContent = block.content || 'e = mc^2';
                    console.warn('Error rendering math:', e);
                }
            } else {
                mathPreview.textContent = block.content || 'e = mc^2';
            }
            
            mathWrapper.appendChild(previewLabel);
            mathWrapper.appendChild(mathPreview);
        } else {
            // Create math input area
            const mathInput = document.createElement('textarea');
            mathInput.className = 'sf-math-input';
            mathInput.value = block.content || '';
            mathInput.placeholder = 'Enter LaTeX math formula (e.g., e = mc^2)';
            mathInput.spellcheck = false;
            
            // Create preview area
            const mathPreview = document.createElement('div');
            mathPreview.className = 'sf-math-preview';
            
            // Live preview function
            const updateMathPreview = () => {
                const formula = mathInput.value;
                
                if (window.katex && formula) {
                    try {
                        window.katex.render(formula, mathPreview, {
                            throwOnError: false,
                            displayMode: true
                        });
                    } catch (e) {
                        mathPreview.textContent = 'Error: ' + e.message;
                    }
                } else {
                    mathPreview.textContent = formula || 'Preview will appear here';
                }
            };
            
            // Initial preview
            updateMathPreview();
            
            // Update preview on input
            mathInput.addEventListener('input', () => {
                this.updateBlockContent(block.id, mathInput.value);
                updateMathPreview();
            });
            
            mathWrapper.appendChild(mathInput);
            mathWrapper.appendChild(mathPreview);
        }
        
        container.appendChild(mathWrapper);
    }
    
    // Expose to global scope
    window.createMathBlock = createMathBlock;
})(); 