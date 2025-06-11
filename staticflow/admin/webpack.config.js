const path = require('path');

module.exports = {
    entry: {
        'tiptap-editor': './static/js/tiptap-editor.js',
        'tiptap-toolbar': './static/js/tiptap-toolbar.js'
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