/**
 * Code Block Implementation
 */

// Modified for non-module loading
(function() {
    // Создать блок кода
    function createCodeBlock(container, block, editor) {
        console.log('createCodeBlock', {container, block, editor});
        // Setup block meta if not exists
        if (!block.meta.language) {
            block.meta.language = 'text';
        }
        
        const blockWrapper = document.createElement('div');
        blockWrapper.className = 'sf-code-block-wrapper';
        
        if (block.isPreview) {
            // Create a styled preview of the code (Notion-like)
            const codeHeader = document.createElement('div');
            codeHeader.className = 'sf-code-header';
            
            const languageLabel = document.createElement('div');
            languageLabel.className = 'sf-code-language-label';
            
            // Format language name to be more user-friendly
            const langName = block.meta.language || 'text';
            const formattedLang = langName.charAt(0).toUpperCase() + langName.slice(1);
            languageLabel.textContent = formattedLang;
            
            codeHeader.appendChild(languageLabel);
            
            const preElement = document.createElement('pre');
            const codeElement = document.createElement('code');
            
            // Add language class for highlighting if available
            if (block.meta.language) {
                codeElement.className = `language-${block.meta.language}`;
            }
            
            codeElement.textContent = block.content || '// Your code here';
            
            preElement.appendChild(codeElement);
            blockWrapper.appendChild(codeHeader);
            blockWrapper.appendChild(preElement);
            
            // Attempt to highlight code if hljs is available
            if (window.hljs) {
                try {
                    window.hljs.highlightElement(codeElement);
                    console.log('Syntax highlighting applied to code block');
                } catch (e) {
                    console.warn('Error highlighting code:', e);
                }
            } else {
                console.warn('highlight.js is not available for syntax highlighting');
            }
        } else {
            // Create language selector
            const languageSelect = document.createElement('select');
            languageSelect.className = 'sf-code-language';
            
            const languages = [
                { value: 'text', label: 'Plain text' },
                { value: 'html', label: 'HTML' },
                { value: 'css', label: 'CSS' },
                { value: 'javascript', label: 'JavaScript' },
                { value: 'typescript', label: 'TypeScript' },
                { value: 'python', label: 'Python' },
                { value: 'java', label: 'Java' },
                { value: 'c', label: 'C' },
                { value: 'cpp', label: 'C++' },
                { value: 'csharp', label: 'C#' },
                { value: 'php', label: 'PHP' },
                { value: 'ruby', label: 'Ruby' },
                { value: 'go', label: 'Go' },
                { value: 'rust', label: 'Rust' },
                { value: 'swift', label: 'Swift' },
                { value: 'bash', label: 'Bash' },
                { value: 'sql', label: 'SQL' },
                { value: 'json', label: 'JSON' },
                { value: 'yaml', label: 'YAML' },
                { value: 'markdown', label: 'Markdown' }
            ];
            
            languages.forEach(lang => {
                const option = document.createElement('option');
                option.value = lang.value;
                option.textContent = lang.label;
                if (lang.value === block.meta.language) {
                    option.selected = true;
                }
                languageSelect.appendChild(option);
            });
            
            // Create code input area
            const codeInput = document.createElement('textarea');
            codeInput.className = 'sf-code-input';
            codeInput.value = block.content || '';
            codeInput.placeholder = '// Your code here';
            codeInput.spellcheck = false;
            
            // Add language selector and code input to wrapper
            blockWrapper.appendChild(languageSelect);
            blockWrapper.appendChild(codeInput);
            
            // Handle language change
            languageSelect.addEventListener('change', () => {
                block.meta.language = languageSelect.value;
                if (block.isPreview) {
                    editor.applyCodeSyntaxHighlighting();
                }
            });
            
            // Handle code input
            codeInput.addEventListener('input', () => {
                editor.updateBlockContent(block.id, codeInput.value);
            });
            
            // Tab key handling for code indentation
            codeInput.addEventListener('keydown', (e) => {
                if (e.key === 'Tab') {
                    e.preventDefault();
                    
                    // Insert tab at cursor position
                    const start = codeInput.selectionStart;
                    const end = codeInput.selectionEnd;
                    
                    // Insert 2 spaces for tab
                    const newValue = codeInput.value.substring(0, start) + '  ' + codeInput.value.substring(end);
                    codeInput.value = newValue;
                    
                    // Move cursor after the tab
                    codeInput.selectionStart = codeInput.selectionEnd = start + 2;
                    
                    // Update block content
                    editor.updateBlockContent(block.id, codeInput.value);
                }
            });
        }
        
        container.appendChild(blockWrapper);
    }
    
    // Expose to global scope
    window.createCodeBlock = createCodeBlock;
})(); 