const path = require('path');

module.exports = {
    entry: {
        'tiptap-editor': './static/js/tiptap-editor.js',
        'tiptap-toolbar': './static/js/tiptap-toolbar.js',
        'tiptap-dnd-blocks': './static/js/tiptap-dnd-blocks.js',
        'tiptap-dnd-nodeview': './static/js/tiptap-dnd-nodeview.js',
        'tiptap-paragraph-dnd': './static/js/tiptap-paragraph-dnd.js',
        'tiptap-drop-indicator': './static/js/tiptap-drop-indicator.js',
        'tiptap-code-block': './static/js/tiptap-code-block.js',
        'tiptap-video': './static/js/tiptap-video.js',
        'tiptap-audio': './static/js/tiptap-audio.js',
        'tiptap-image': './static/js/tiptap-image.js',
        'tiptap-mermaid': './static/js/tiptap-mermaid.js',
        'tiptap-math': './static/js/tiptap-math.js',
        'markdown-preprocessor': './static/js/markdown-preprocessor.js',
        'admin': './static/js/admin.js',
        'deploy': './static/js/deploy.js',
        'tiptap-bubblemenu': './static/js/tiptap-bubblemenu.js',

    },
    output: {
        path: path.resolve(__dirname, 'static/dist'),
        filename: '[name].js',
        library: {
            type: 'umd',
            name: '[name]'
        }
    },
    module: {
        rules: [
            {
                test: /\.js$/,
                exclude: /node_modules/,
                use: {
                    loader: 'babel-loader',
                    options: {
                        presets: ['@babel/preset-env']
                    }
                }
            }
        ]
    },
    resolve: {
        extensions: ['.js']
    }
}; 