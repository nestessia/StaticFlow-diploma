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
                icon: 'bold',
                title: 'Жирный',
                action: () => this.editor.chain().focus().toggleBold().run(),
                isActive: () => this.editor.isActive('bold'),
            },
            {
                icon: 'italic',
                title: 'Курсив',
                action: () => this.editor.chain().focus().toggleItalic().run(),
                isActive: () => this.editor.isActive('italic'),
            },
            {
                icon: 'strikethrough',
                title: 'Зачеркнутый',
                action: () => this.editor.chain().focus().toggleStrike().run(),
                isActive: () => this.editor.isActive('strike'),
            },
            {
                icon: 'code',
                title: 'Код',
                action: () => this.editor.chain().focus().toggleCode().run(),
                isActive: () => this.editor.isActive('code'),
            },
            {
                type: 'divider',
            },
            {
                icon: 'heading-1',
                title: 'Заголовок 1',
                action: () => this.editor.chain().focus().toggleHeading({ level: 1 }).run(),
                isActive: () => this.editor.isActive('heading', { level: 1 }),
            },
            {
                icon: 'heading-2',
                title: 'Заголовок 2',
                action: () => this.editor.chain().focus().toggleHeading({ level: 2 }).run(),
                isActive: () => this.editor.isActive('heading', { level: 2 }),
            },
            {
                icon: 'heading-3',
                title: 'Заголовок 3',
                action: () => this.editor.chain().focus().toggleHeading({ level: 3 }).run(),
                isActive: () => this.editor.isActive('heading', { level: 3 }),
            },
            {
                type: 'divider',
            },
            {
                icon: 'list-ul',
                title: 'Маркированный список',
                action: () => this.editor.chain().focus().toggleBulletList().run(),
                isActive: () => this.editor.isActive('bulletList'),
            },
            {
                icon: 'list-ol',
                title: 'Нумерованный список',
                action: () => this.editor.chain().focus().toggleOrderedList().run(),
                isActive: () => this.editor.isActive('orderedList'),
            },
            {
                icon: 'tasks',
                title: 'Список задач',
                action: () => this.editor.chain().focus().toggleTaskList().run(),
                isActive: () => this.editor.isActive('taskList'),
            },
            {
                type: 'divider',
            },
            {
                icon: 'quote',
                title: 'Цитата',
                action: () => this.editor.chain().focus().toggleBlockquote().run(),
                isActive: () => this.editor.isActive('blockquote'),
            },
            {
                icon: 'code-block',
                title: 'Блок кода',
                action: () => this.editor.chain().focus().toggleCodeBlock().run(),
                isActive: () => this.editor.isActive('codeBlock'),
            },
            {
                type: 'divider',
            },
            {
                icon: 'table',
                title: 'Таблица',
                action: () => this.editor.chain().focus().insertTable({ rows: 3, cols: 3, withHeaderRow: true }).run(),
            },
            {
                icon: 'image',
                title: 'Изображение',
                action: () => {
                    const url = window.prompt('URL изображения:')
                    if (url) {
                        this.editor.chain().focus().setImage({ src: url }).run()
                    }
                },
            },
            {
                icon: 'link',
                title: 'Ссылка',
                action: () => {
                    const url = window.prompt('URL:')
                    if (url) {
                        this.editor.chain().focus().setLink({ href: url }).run()
                    }
                },
                isActive: () => this.editor.isActive('link'),
            },
            {
                type: 'divider',
            },
            {
                icon: 'align-left',
                title: 'По левому краю',
                action: () => this.editor.chain().focus().setTextAlign('left').run(),
                isActive: () => this.editor.isActive({ textAlign: 'left' }),
            },
            {
                icon: 'align-center',
                title: 'По центру',
                action: () => this.editor.chain().focus().setTextAlign('center').run(),
                isActive: () => this.editor.isActive({ textAlign: 'center' }),
            },
            {
                icon: 'align-right',
                title: 'По правому краю',
                action: () => this.editor.chain().focus().setTextAlign('right').run(),
                isActive: () => this.editor.isActive({ textAlign: 'right' }),
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
                buttonElement.innerHTML = `<i class="fas fa-${button.icon}"></i>`
                buttonElement.title = button.title
                buttonElement.addEventListener('click', (e) => {
                    e.preventDefault()
                    button.action()
                })

                // Обновляем состояние кнопки при изменении редактора
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

// Экспортируем класс для использования
window.TipTapToolbar = TipTapToolbar 