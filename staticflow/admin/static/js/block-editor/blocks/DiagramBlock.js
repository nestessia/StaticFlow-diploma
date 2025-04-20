/**
 * Diagram Block Implementation
 */

// Modified for non-module loading
(function() {
    // Создать блок диаграммы
    function createDiagramBlock(container, block) {
        const diagramWrapper = document.createElement('div');
        diagramWrapper.className = 'sf-diagram-block-wrapper';
        
        if (block.isPreview) {
            // Create a styled preview of the diagram
            const diagramHeader = document.createElement('div');
            diagramHeader.className = 'sf-diagram-header';
            diagramHeader.textContent = 'Diagram';
            
            const diagramPreview = document.createElement('div');
            diagramPreview.className = 'sf-diagram-preview';
            
            // Render diagram if Mermaid is available
            if (window.mermaid) {
                try {
                    const diagram = document.createElement('div');
                    diagram.className = 'mermaid';
                    diagram.textContent = block.content || 'graph TD;\nA-->B;';
                    diagramPreview.appendChild(diagram);
                    
                    // Initialize mermaid diagrams
                    window.mermaid.init(undefined, diagram);
                } catch (e) {
                    diagramPreview.textContent = block.content || 'graph TD;\nA-->B;';
                    console.warn('Error rendering diagram:', e);
                }
            } else {
                diagramPreview.textContent = block.content || 'graph TD;\nA-->B;';
                console.warn('mermaid.js is not available for rendering diagrams');
            }
            
            diagramWrapper.appendChild(diagramHeader);
            diagramWrapper.appendChild(diagramPreview);
        } else {
            // Create diagram input area
            const diagramInput = document.createElement('textarea');
            diagramInput.className = 'sf-diagram-input';
            diagramInput.value = block.content || 'graph TD;\nA-->B;';
            diagramInput.placeholder = 'Enter Mermaid diagram code...';
            diagramInput.spellcheck = false;
            
            // Create preview area
            const diagramPreview = document.createElement('div');
            diagramPreview.className = 'sf-diagram-preview';
            
            // Live preview function (with debounce)
            let previewTimeout = null;
            const updateDiagramPreview = () => {
                clearTimeout(previewTimeout);
                previewTimeout = setTimeout(() => {
                    diagramPreview.innerHTML = '';
                    const diagram = document.createElement('div');
                    diagram.className = 'mermaid';
                    diagram.textContent = diagramInput.value || 'graph TD;\nA-->B;';
                    diagramPreview.appendChild(diagram);
                    
                    // Initialize mermaid diagrams if available
                    if (window.mermaid) {
                        try {
                            window.mermaid.init(undefined, diagram);
                        } catch (e) {
                            console.warn('Error rendering diagram:', e);
                        }
                    }
                }, 500);
            };
            
            // Initial preview
            updateDiagramPreview();
            
            // Update preview on input
            diagramInput.addEventListener('input', () => {
                this.updateBlockContent(block.id, diagramInput.value);
                updateDiagramPreview();
            });
            
            diagramWrapper.appendChild(diagramInput);
            diagramWrapper.appendChild(diagramPreview);
        }
        
        container.appendChild(diagramWrapper);
    }
    
    // Expose to global scope
    window.createDiagramBlock = createDiagramBlock;
})(); 