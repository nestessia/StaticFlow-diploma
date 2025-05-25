// Инициализация Mermaid
document.addEventListener('DOMContentLoaded', function() {
    if (window.mermaid) {
        mermaid.initialize({startOnLoad: true});
    }

    // Инициализация подсветки кода
    if (window.hljs) {
        document.querySelectorAll('pre code').forEach((block) => {
            hljs.highlightBlock(block);
        });
    }

    // Инициализация KaTeX
    if (window.katex) {
        document.querySelectorAll('.math').forEach(function(element) {
            try {
                katex.render(element.textContent, element, {
                    throwOnError: false,
                    displayMode: element.classList.contains('math-display')
                });
            } catch (e) {
                console.error('KaTeX error:', e);
            }
        });
    }
}); 