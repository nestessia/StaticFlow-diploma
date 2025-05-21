/**
 * StaticFlow Block Editor v3.0
 * Notion-style block-based editor for static site content
 * 
 * This file loads the block editor implementation without using ES modules
 */

// Define a global variable to store the editor implementation
window.BlockEditor = null;

// Wait for DOM to be ready
document.addEventListener('DOMContentLoaded', function() {
    // Список скриптов для загрузки: всегда EditorUtils.js, EditorUtils.md.js, EditorUtils.rst.js
    const scripts = [
        '/admin/static/js/block-editor/utils/EditorUtils.js',
        '/admin/static/js/block-editor/utils/EditorUtils.md.js',
        '/admin/static/js/block-editor/utils/EditorUtils.rst.js',
        // Core components
        '/admin/static/js/block-editor/DragAndDrop.js',
        '/admin/static/js/block-editor/BlockActions.js',
        '/admin/static/js/block-editor/BlockTypeMenu.js',
        // Block implementations
        '/admin/static/js/block-editor/blocks/HeadingBlock.js',
        '/admin/static/js/block-editor/blocks/ParagraphBlock.js',
        '/admin/static/js/block-editor/blocks/BulletListBlock.js',
        '/admin/static/js/block-editor/blocks/NumberedListBlock.js',
        '/admin/static/js/block-editor/blocks/QuoteBlock.js',
        '/admin/static/js/block-editor/blocks/CodeBlock.js',
        '/admin/static/js/block-editor/blocks/MathBlock.js',
        '/admin/static/js/block-editor/blocks/DiagramBlock.js',
        '/admin/static/js/block-editor/blocks/ImageBlock.js',
        '/admin/static/js/block-editor/blocks/AudioBlock.js',
        '/admin/static/js/block-editor/blocks/VideoBlock.js',
        '/admin/static/js/block-editor/blocks/InfoBlock.js',
        // Factory implementation
        '/admin/static/js/block-editor/blocks/BlockFactory.js',
        // Main editor implementation
        '/admin/static/js/block-editor/BlockEditor.js'
    ];
    
    // Function to load scripts sequentially
    function loadScriptSequentially(scripts, index) {
        if (index >= scripts.length) {
            console.log("All BlockEditor scripts loaded");
            // Dispatch an event when all scripts are loaded
            document.dispatchEvent(new CustomEvent('blockEditorLoaded'));
            return;
        }
        
        const script = document.createElement('script');
        script.src = scripts[index];
        script.onload = function() {
            loadScriptSequentially(scripts, index + 1);
        };
        script.onerror = function() {
            console.error("Failed to load script:", scripts[index]);
            loadScriptSequentially(scripts, index + 1);
        };
        document.head.appendChild(script);
    }
    
    // Start loading scripts
    loadScriptSequentially(scripts, 0);

    // После загрузки всех скриптов:
    document.addEventListener('blockEditorLoaded', function() {
        // Получаем формат страницы
        var format = (window.pageData && window.pageData.metadata && window.pageData.metadata.format) ? window.pageData.metadata.format : 'markdown';
        // Выбираем нужную функцию десериализации
        var deserializer = (format === 'rst') ? window.deserializeRstContent : window.deserializeContent;
        // Переопределяем метод в BlockEditor
        if (window.BlockEditor) {
            window.BlockEditor.prototype.deserializeContent = deserializer;
        }
    });
}); 