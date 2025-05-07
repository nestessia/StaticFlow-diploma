/**
 * Audio Block Implementation
 */

// Modified for non-module loading
(function() {
    // Создать блок аудио
    function createAudioBlock(container, block) {
        const audioWrapper = document.createElement('div');
        audioWrapper.className = 'sf-audio-block-wrapper';
        
        if (block.isPreview) {
            // Create a styled preview of the audio
            if (block.content) {
                const audioContainer = document.createElement('div');
                audioContainer.className = 'sf-audio-container';
                
                const audio = document.createElement('audio');
                audio.controls = true;
                audio.src = block.content;
                audio.className = 'sf-audio-player';
                
                audioContainer.appendChild(audio);
                
                if (block.meta.caption) {
                    const caption = document.createElement('div');
                    caption.className = 'sf-audio-caption';
                    caption.textContent = block.meta.caption;
                    audioContainer.appendChild(caption);
                }
                
                audioWrapper.appendChild(audioContainer);
            } else {
                const placeholder = document.createElement('div');
                placeholder.className = 'sf-audio-placeholder';
                placeholder.textContent = 'Audio: No URL provided';
                audioWrapper.appendChild(placeholder);
            }
        } else {
            // Create audio input form
            const audioForm = document.createElement('div');
            audioForm.className = 'sf-audio-form';
            
            // Audio URL input
            const urlLabel = document.createElement('label');
            urlLabel.textContent = 'Audio URL:';
            urlLabel.htmlFor = `audio-url-${block.id}`;
            
            const urlInput = document.createElement('input');
            urlInput.type = 'text';
            urlInput.id = `audio-url-${block.id}`;
            urlInput.className = 'sf-audio-url-input';
            urlInput.value = block.content || '';
            urlInput.placeholder = 'https://example.com/audio.mp3';
            
            // Caption input
            const captionLabel = document.createElement('label');
            captionLabel.textContent = 'Caption:';
            captionLabel.htmlFor = `audio-caption-${block.id}`;
            
            const captionInput = document.createElement('input');
            captionInput.type = 'text';
            captionInput.id = `audio-caption-${block.id}`;
            captionInput.className = 'sf-audio-caption-input';
            captionInput.value = block.meta.caption || '';
            captionInput.placeholder = 'Audio caption (optional)';
            
            // Preview container
            const previewContainer = document.createElement('div');
            previewContainer.className = 'sf-audio-preview-container';
            
            const updatePreview = () => {
                previewContainer.innerHTML = '';
                
                if (urlInput.value) {
                    const audio = document.createElement('audio');
                    audio.controls = true;
                    audio.src = urlInput.value;
                    audio.className = 'sf-audio-player';
                    previewContainer.appendChild(audio);
                } else {
                    previewContainer.textContent = 'Audio preview will appear here';
                    previewContainer.classList.add('sf-audio-placeholder');
                }
            };
            
            // Update preview on input
            urlInput.addEventListener('blur', updatePreview);
            
            // Update block content and metadata
            urlInput.addEventListener('input', () => {
                this.updateBlockContent(block.id, urlInput.value);
            });
            
            captionInput.addEventListener('input', () => {
                if (!block.meta) block.meta = {};
                block.meta.caption = captionInput.value;
            });
            
            // Add form elements
            audioForm.appendChild(urlLabel);
            audioForm.appendChild(urlInput);
            audioForm.appendChild(captionLabel);
            audioForm.appendChild(captionInput);
            
            // Initial preview
            updatePreview();
            
            audioWrapper.appendChild(audioForm);
            audioWrapper.appendChild(previewContainer);
        }
        
        container.appendChild(audioWrapper);
    }
    
    // Expose to global scope
    window.createAudioBlock = createAudioBlock;
})(); 