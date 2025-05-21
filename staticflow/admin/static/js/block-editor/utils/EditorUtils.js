(function() {
    function deserializeContent(content, format) {
        if (format === 'rst') {
            return window.deserializeRstContent.call(this, content);
        } else {
            return window.deserializeMdContent.call(this, content);
        }
    }
    window.deserializeContent = deserializeContent;
})(); 