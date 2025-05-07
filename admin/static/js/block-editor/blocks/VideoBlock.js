/**
 * Video Block Implementation
 */

// Modified for non-module loading
(function() {
    // Создать блок видео
    function createVideoBlock(container, block) {
        const videoWrapper = document.createElement('div');
        videoWrapper.className = 'sf-video-block-wrapper';
        
        if (block.isPreview) {
            // Create a styled preview of the video
            if (block.content) {
                const videoContainer = document.createElement('div');
                videoContainer.className = 'sf-video-container';
                
                const video = document.createElement('video');
                video.controls = true;
                video.src = block.content;
                video.className = 'sf-video-player';
                
                videoContainer.appendChild(video);
                
                if (block.meta.caption) {
                    const caption = document.createElement('div');
                    caption.className = 'sf-video-caption';
                    caption.textContent = block.meta.caption;
                    videoContainer.appendChild(caption);
                }
                
                videoWrapper.appendChild(videoContainer);
            } else {
                const placeholder = document.createElement('div');
                placeholder.className = 'sf-video-placeholder';
                placeholder.textContent = 'Video: No URL provided';
                videoWrapper.appendChild(placeholder);
            }
        } else {
            // Create video input form
            const videoForm = document.createElement('div');
            videoForm.className = 'sf-video-form';
            
            // Video URL input
            const urlLabel = document.createElement('label');
            urlLabel.textContent = 'Video URL:';
            urlLabel.htmlFor = `video-url-${block.id}`;
            
            const urlInput = document.createElement('input');
            urlInput.type = 'text';
            urlInput.id = `video-url-${block.id}`;
            urlInput.className = 'sf-video-url-input';
            urlInput.value = block.content || '';
            urlInput.placeholder = 'https://example.com/video.mp4';
            
            // Caption input
            const captionLabel = document.createElement('label');
            captionLabel.textContent = 'Caption:';
            captionLabel.htmlFor = `video-caption-${block.id}`;
            
            const captionInput = document.createElement('input');
            captionInput.type = 'text';
            captionInput.id = `video-caption-${block.id}`;
            captionInput.className = 'sf-video-caption-input';
            captionInput.value = block.meta.caption || '';
            captionInput.placeholder = 'Video caption (optional)';
            
            // Preview container
            const previewContainer = document.createElement('div');
            previewContainer.className = 'sf-video-preview-container';
            
            const updatePreview = () => {
                previewContainer.innerHTML = '';
                
                if (urlInput.value) {
                    const video = document.createElement('video');
                    video.controls = true;
                    video.src = urlInput.value;
                    video.className = 'sf-video-player';
                    previewContainer.appendChild(video);
                } else {
                    previewContainer.textContent = 'Video preview will appear here';
                    previewContainer.classList.add('sf-video-placeholder');
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
            videoForm.appendChild(urlLabel);
            videoForm.appendChild(urlInput);
            videoForm.appendChild(captionLabel);
            videoForm.appendChild(captionInput);
            
            // Initial preview
            updatePreview();
            
            videoWrapper.appendChild(videoForm);
            videoWrapper.appendChild(previewContainer);
        }
        
        container.appendChild(videoWrapper);
    }
    
    // Expose to global scope
    window.createVideoBlock = createVideoBlock;
})(); 