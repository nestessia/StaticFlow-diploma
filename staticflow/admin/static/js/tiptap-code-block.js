import { Node, mergeAttributes } from '@tiptap/core'
import { createDndNodeView } from './tiptap-dnd-nodeview.js'

const SUPPORTED_LANGUAGES = [
    'python',
    'javascript',
    'typescript',
    'html',
    'css',
    'json',
    'bash',
    'cpp',
    'java',
    'csharp',
    'php',
    'ruby',
    'go',
    'rust',
    'swift'
]

export const CodeBlock = Node.create({
    name: 'codeBlock',
    group: 'block',
    content: 'text*',
    code: true,
    atom: true,
    addAttributes() {
        return {
            language: {
                default: '',
                parseHTML: element => element.getAttribute('data-language'),
                renderHTML: attributes => {
                    return {
                        'data-language': attributes.language
                    }
                }
            }
        }
    },
    parseHTML() {
        return [
            {
                tag: 'div.code-block',
                getAttrs: element => ({ language: element.getAttribute('data-language') || '' })
            },
            {
                tag: 'pre',
            },
        ]
    },
    renderHTML({ HTMLAttributes }) {
        return ['pre', mergeAttributes(HTMLAttributes), ['code', {}, 0]]
    },
    addNodeView() {
        return ({ node, getPos, editor }) => {
            const wrapper = document.createElement('div')
            wrapper.className = 'dnd-block dnd-code-block'
            wrapper.style.display = 'flex'
            wrapper.style.alignItems = 'flex-start'

            // Drag handle
            const handle = document.createElement('span')
            handle.className = 'dnd-handle'
            handle.textContent = '⧉'
            handle.style.cursor = 'grab'
            handle.style.userSelect = 'none'
            handle.style.marginRight = '8px'
            handle.draggable = true
            handle.addEventListener('dragstart', (event) => {
                event.dataTransfer.setData('application/x-tiptap-drag', getPos())
                wrapper.classList.add('dragging')
            })
            handle.addEventListener('dragend', () => {
                wrapper.classList.remove('dragging')
            })

            // Delete button
            const deleteButton = document.createElement('button')
            deleteButton.className = 'dnd-delete-btn'
            deleteButton.innerHTML = '×'
            deleteButton.title = 'Delete block'
            deleteButton.onclick = (e) => {
                e.preventDefault()
                e.stopPropagation()
                if (typeof getPos === 'function' && editor) {
                    const pos = getPos()
                    editor.commands.command(({ tr }) => {
                        tr.delete(pos, pos + node.nodeSize)
                        return true
                    })
                }
            }

            // Language selector
            const languageSelect = document.createElement('select')
            languageSelect.className = 'code-language-select'
            languageSelect.style.marginBottom = '8px'
            languageSelect.style.padding = '4px'
            languageSelect.style.borderRadius = '4px'
            languageSelect.style.border = '1px solid #e2e8f0'

            // Add empty option
            const emptyOption = document.createElement('option')
            emptyOption.value = ''
            emptyOption.textContent = 'Выберите язык'
            languageSelect.appendChild(emptyOption)

            // Add language options
            SUPPORTED_LANGUAGES.forEach(lang => {
                const option = document.createElement('option')
                option.value = lang
                option.textContent = lang.charAt(0).toUpperCase() + lang.slice(1)
                languageSelect.appendChild(option)
            })

            // Set current language
            languageSelect.value = node.attrs.language || ''

            // Update language on change
            languageSelect.addEventListener('change', () => {
                setTimeout(() => {
                    if (typeof getPos === 'function' && editor) {
                        const pos = getPos()
                        editor.commands.command(({ tr }) => {
                            tr.setNodeAttribute(pos, 'language', languageSelect.value)
                            return true
                        })
                    }
                }, 150);
            })

            // Content
            const contentDOM = document.createElement('div')
            contentDOM.className = 'dnd-content'
            contentDOM.style.flex = '1'

            // Code input
            const textarea = document.createElement('textarea')
            textarea.value = node.textContent || ''
            textarea.className = 'code-input'
            textarea.placeholder = 'Введите код...'
            textarea.style.width = '100%'
            textarea.style.minHeight = '100px'
            textarea.style.padding = '8px'
            textarea.style.fontFamily = 'monospace'
            textarea.style.border = '1px solid #e2e8f0'
            textarea.style.borderRadius = '4px'
            textarea.style.backgroundColor = '#f8fafc'

            // Update content on input
            textarea.addEventListener('input', () => {
                if (typeof getPos === 'function' && editor) {
                    const pos = getPos()
                    editor.commands.command(({ tr }) => {
                        tr.insertText(textarea.value, pos + 1, pos + node.nodeSize - 1)
                        return true
                    })
                }
            })

            // Add elements to content
            contentDOM.appendChild(languageSelect)
            contentDOM.appendChild(textarea)

            // Drop logic
            wrapper.addEventListener('dragover', (event) => {
                event.preventDefault()
                wrapper.classList.add('drag-over')
            })
            wrapper.addEventListener('dragleave', () => {
                wrapper.classList.remove('drag-over')
            })
            wrapper.addEventListener('drop', (event) => {
                event.preventDefault()
                wrapper.classList.remove('drag-over')
                const from = parseInt(event.dataTransfer.getData('application/x-tiptap-drag'))
                const to = getPos()
                if (from !== to) {
                    editor.commands.command(({ tr }) => {
                        const node = tr.doc.nodeAt(from)
                        if (!node) return false
                        tr.delete(from, from + node.nodeSize)
                        tr.insert(to, node)
                        return true
                    })
                }
            })

            wrapper.appendChild(handle)
            wrapper.appendChild(deleteButton)
            wrapper.appendChild(contentDOM)

            return {
                dom: wrapper,
                contentDOM: null,
                stopEvent: (event) => {
                    if (event && event.type && event.type.startsWith('drag')) return false
                    return undefined
                }
            }
        }
    }
}) 