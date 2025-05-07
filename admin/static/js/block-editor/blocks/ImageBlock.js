/**
 * Image Block Implementation
 */

// Modified for non-module loading
(function() {
    // Создать блок изображения
    function createImageBlock(container, block) {
        const imageWrapper = document.createElement('div');
        imageWrapper.className = 'sf-image-block-wrapper';
        
        if (block.isPreview) {
            // Create a styled preview of the image
            const figure = document.createElement('figure');
            
            if (block.content) {
                const img = document.createElement('img');
                img.src = block.content;
                img.alt = block.meta.alt || '';
                img.className = 'sf-image-preview';
                figure.appendChild(img);
                
                if (block.meta.caption) {
                    const figcaption = document.createElement('figcaption');
                    figcaption.textContent = block.meta.caption;
                    figure.appendChild(figcaption);
                }
            } else {
                figure.textContent = 'Image placeholder';
                figure.className = 'sf-image-placeholder';
            }
            
            imageWrapper.appendChild(figure);
        } else {
            // Create image input form
            const imageForm = document.createElement('div');
            imageForm.className = 'sf-image-form';
            
            // Image URL input
            const urlLabel = document.createElement('label');
            urlLabel.textContent = 'Image URL:';
            urlLabel.htmlFor = `image-url-${block.id}`;
            
            const urlInput = document.createElement('input');
            urlInput.type = 'text';
            urlInput.id = `image-url-${block.id}`;
            urlInput.className = 'sf-image-url-input';
            urlInput.value = block.content || '';
            urlInput.placeholder = 'https://example.com/image.jpg';
            
            // Alt text input
            const altLabel = document.createElement('label');
            altLabel.textContent = 'Alt text:';
            altLabel.htmlFor = `image-alt-${block.id}`;
            
            const altInput = document.createElement('input');
            altInput.type = 'text';
            altInput.id = `image-alt-${block.id}`;
            altInput.className = 'sf-image-alt-input';
            altInput.value = block.meta.alt || '';
            altInput.placeholder = 'Description of image';
            
            // Caption input
            const captionLabel = document.createElement('label');
            captionLabel.textContent = 'Caption:';
            captionLabel.htmlFor = `image-caption-${block.id}`;
            
            const captionInput = document.createElement('input');
            captionInput.type = 'text';
            captionInput.id = `image-caption-${block.id}`;
            captionInput.className = 'sf-image-caption-input';
            captionInput.value = block.meta.caption || '';
            captionInput.placeholder = 'Image caption (optional)';
            
            // Preview container
            const previewContainer = document.createElement('div');
            previewContainer.className = 'sf-image-preview-container';
            
            const updatePreview = () => {
                previewContainer.innerHTML = '';
                
                if (urlInput.value) {
                    const img = document.createElement('img');
                    img.src = urlInput.value;
                    img.alt = altInput.value;
                    img.className = 'sf-image-preview';
                    previewContainer.appendChild(img);
                } else {
                    previewContainer.textContent = 'Image preview will appear here';
                    previewContainer.classList.add('sf-image-placeholder');
                }
            };
            
            // Update preview on input
            urlInput.addEventListener('blur', updatePreview);
            
            // Update block content and metadata
            urlInput.addEventListener('input', () => {
                this.updateBlockContent(block.id, urlInput.value);
            });
            
            altInput.addEventListener('input', () => {
                if (!block.meta) block.meta = {};
                block.meta.alt = altInput.value;
            });
            
            captionInput.addEventListener('input', () => {
                if (!block.meta) block.meta = {};
                block.meta.caption = captionInput.value;
            });
            
            // Add form elements
            imageForm.appendChild(urlLabel);
            imageForm.appendChild(urlInput);
            imageForm.appendChild(altLabel);
            imageForm.appendChild(altInput);
            imageForm.appendChild(captionLabel);
            imageForm.appendChild(captionInput);
            
            // Initial preview
            updatePreview();
            
            imageWrapper.appendChild(imageForm);
            imageWrapper.appendChild(previewContainer);
        }
        
        container.appendChild(imageWrapper);
    }
    
    // Expose to global scope
    window.createImageBlock = createImageBlock;
})(); 