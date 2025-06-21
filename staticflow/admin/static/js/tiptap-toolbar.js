class TipTapToolbar {
    constructor(editor) {
        this.editor = editor
        this.toolbar = null
        this.init()
    }

    init() {
        this.toolbar = document.createElement('div')
        this.toolbar.className = 'tiptap-toolbar'
        this.createToolbar()
    }

    createToolbar() {
        const buttons = [
            {
                icon: 'align-left',
                title: 'Text',
                action: () => {
                    this.editor.chain().focus().insertContentAt(0, {
                        type: 'paragraph',
                        content: [{ type: 'text', text: ' ' }]
                    }).run();
                },
            },
            {
                type: 'divider',
            },
            {
                icon: 'heading',
                title: 'Header 1',
                label: '1',
                action: () => {
                    this.editor.chain().focus().insertContentAt(0, {
                        type: 'heading',
                        attrs: { level: 1 },
                        content: [{ type: 'text', text: ' ' }]
                    }).run();
                },
                isActive: () => this.editor.isActive('heading', { level: 1 }),
            },
            {
                icon: 'heading',
                title: 'Header 2',
                label: '2',
                action: () => {
                    this.editor.chain().focus().insertContentAt(0, {
                        type: 'heading',
                        attrs: { level: 2 },
                        content: [{ type: 'text', text: ' ' }]
                    }).run();
                },
                isActive: () => this.editor.isActive('heading', { level: 2 }),
            },
            {
                icon: 'heading',
                title: 'Header 3',
                label: '3',
                action: () => {
                    this.editor.chain().focus().insertContentAt(0, {
                        type: 'heading',
                        attrs: { level: 3 },
                        content: [{ type: 'text', text: ' ' }]
                    }).run();
                },
                isActive: () => this.editor.isActive('heading', { level: 3 }),
            },
            {
                type: 'divider',
            },
            {
                icon: 'list-ul',
                title: 'Unordered List',
                action: () => {
                    this.editor.chain().focus().insertContentAt(0, {
                        type: 'bulletList',
                        content: [
                            { type: 'listItem', content: [{ type: 'paragraph', content: [{ type: 'text', text: ' ' }] }] }
                        ]
                    }).run();
                },
                isActive: () => this.editor.isActive('bulletList'),
            },
            {
                icon: 'list-ol',
                title: 'Ordered List',
                action: () => {
                    this.editor.chain().focus().insertContentAt(0, {
                        type: 'orderedList',
                        content: [
                            { type: 'listItem', content: [{ type: 'paragraph', content: [{ type: 'text', text: ' ' }] }] }
                        ]
                    }).run();
                },
                isActive: () => this.editor.isActive('orderedList'),
            },
            {
                icon: 'tasks',
                title: 'Task List',
                action: () => {
                    this.editor.chain().focus().insertContentAt(0, {
                        type: 'taskList',
                        content: [
                            { type: 'taskItem', attrs: { checked: false }, content: [{ type: 'paragraph', content: [{ type: 'text', text: ' ' }] }] }
                        ]
                    }).run();
                },
                isActive: () => this.editor.isActive('taskList'),
            },
            {
                type: 'divider',
            },
            {
                icon: 'quote-right',
                title: 'Quote',
                action: () => {
                    this.editor.chain().focus().insertContentAt(0, {
                        type: 'blockquote',
                        content: [{ type: 'paragraph', content: [{ type: 'text', text: ' ' }] }]
                    }).run();
                },
                isActive: () => this.editor.isActive('blockquote'),
            },
            {
                icon: 'code',
                title: 'Code Block',
                action: () => {
                    this.editor.chain().focus().insertContentAt(0, {
                        type: 'codeBlock',
                        attrs: { language: '' },
                        content: [{ type: 'text', text: ' ' }]
                    }).run();
                },
                isActive: () => this.editor.isActive('codeBlock'),
            },
            {
                type: 'divider',
            },
            {
                icon: 'table',
                title: 'Table',
                action: () => {
                    this.editor.chain().focus().insertContentAt(0, {
                        type: 'table',
                        content: [
                            {
                                type: 'tableRow',
                                content: [
                                    { type: 'tableHeader', content: [{ type: 'paragraph', content: [{ type: 'text', text: ' ' }] }] },
                                    { type: 'tableHeader', content: [{ type: 'paragraph', content: [{ type: 'text', text: ' ' }] }] },
                                    { type: 'tableHeader', content: [{ type: 'paragraph', content: [{ type: 'text', text: ' ' }] }] }
                                ]
                            },
                            {
                                type: 'tableRow',
                                content: [
                                    { type: 'tableCell', content: [{ type: 'paragraph', content: [{ type: 'text', text: ' ' }] }] },
                                    { type: 'tableCell', content: [{ type: 'paragraph', content: [{ type: 'text', text: ' ' }] }] },
                                    { type: 'tableCell', content: [{ type: 'paragraph', content: [{ type: 'text', text: ' ' }] }] }
                                ]
                            },
                            {
                                type: 'tableRow',
                                content: [
                                    { type: 'tableCell', content: [{ type: 'paragraph', content: [{ type: 'text', text: ' ' }] }] },
                                    { type: 'tableCell', content: [{ type: 'paragraph', content: [{ type: 'text', text: ' ' }] }] },
                                    { type: 'tableCell', content: [{ type: 'paragraph', content: [{ type: 'text', text: ' ' }] }] }
                                ]
                            }
                        ]
                    }).run();
                },
            },
            {
                icon: 'image',
                title: 'Image',
                action: () => {
                    this.editor.chain().focus().insertContentAt(0, {
                        type: 'imageBlock',
                        attrs: { src: '', alt: '', title: '' }
                    }).run();
                },
            },
            {
                icon: 'video',
                title: 'Video',
                action: () => {
                    this.editor.chain().focus().insertContentAt(0, {
                        type: 'videoBlock',
                        attrs: { src: '', title: '', controls: true }
                    }).run();
                },
            },
            {
                icon: 'music',
                title: 'Audio',
                action: () => {
                    this.editor.chain().focus().insertContentAt(0, {
                        type: 'audioBlock',
                        attrs: { src: '', controls: true }
                    }).run();
                },
            },
            {
                icon: 'link',
                title: 'Link',
                action: () => {
                    const url = window.prompt('URL:');
                    if (url) {
                        this.editor.chain().focus().insertContentAt(0, {
                            type: 'paragraph',
                            content: [
                                {
                                    type: 'text',
                                    text: url,
                                    marks: [{ type: 'link', attrs: { href: url } }]
                                }
                            ]
                        }).run();
                    }
                },
                isActive: () => this.editor.isActive('link'),
            },
            {
                type: 'divider',
            },
            {
                icon: 'square-root-alt',
                title: 'Formula (KaTeX)',
                action: () => {
                    this.editor.chain().focus().insertContentAt(0, {
                        type: 'mathBlock',
                        content: [{ type: 'text', text: ' ' }]
                    }).run();
                },
            },
            {
                icon: 'project-diagram',
                title: 'Diagram (Mermaid)',
                action: () => {
                    this.editor.chain().focus().insertContentAt(0, {
                        type: 'mermaidBlock',
                        content: [{ type: 'text', text: 'graph TD;\nA-->B;' }]
                    }).run();
                },
            },
        ]

        buttons.forEach(button => {
            if (button.type === 'divider') {
                const divider = document.createElement('div')
                divider.className = 'toolbar-divider'
                this.toolbar.appendChild(divider)
            } else {
                const buttonElement = document.createElement('button')
                buttonElement.type = 'button'
                buttonElement.className = 'toolbar-button'
                buttonElement.innerHTML = `<i class="fas fa-${button.icon}"></i>${button.label ? `<span class="toolbar-label">${button.label}</span>` : ''}`
                buttonElement.title = button.title
                buttonElement.addEventListener('click', (e) => {
                    e.preventDefault()
                    button.action()
                })

                this.editor.on('update', () => {
                    if (button.isActive) {
                        buttonElement.classList.toggle('is-active', button.isActive())
                    }
                })

                this.toolbar.appendChild(buttonElement)
            }
        })
    }

    getElement() {
        return this.toolbar
    }
}

window.TipTapToolbar = TipTapToolbar 