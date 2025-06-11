import { Node, mergeAttributes } from '@tiptap/core'

export const MermaidBlock = Node.create({
  name: 'mermaidBlock',
  group: 'block',
  content: 'text*',
  code: true,
  atom: true,
  parseHTML() {
    return [
      {
        tag: 'div.mermaid-block',
      },
    ]
  },
  renderHTML({ HTMLAttributes }) {
    return ['div', mergeAttributes(HTMLAttributes, { class: 'mermaid-block' }), 0]
  },
  addNodeView() {
    return ({ node, getPos, editor }) => {
      const dom = document.createElement('div')
      dom.className = 'mermaid-block'
      dom.contentEditable = false
      const textarea = document.createElement('textarea')
      textarea.value = node.textContent || 'graph TD;\nA-->B;'
      textarea.className = 'mermaid-input'
      textarea.placeholder = 'Введите код диаграммы mermaid...'
      dom.appendChild(textarea)
      const preview = document.createElement('div')
      preview.className = 'mermaid-preview'
      dom.appendChild(preview)
      const render = () => {
        preview.innerHTML = ''
        const diagram = document.createElement('div')
        diagram.className = 'mermaid'
        diagram.textContent = textarea.value || 'graph TD;\nA-->B;'
        preview.appendChild(diagram)
        if (window.mermaid) {
          try {
            window.mermaid.init(undefined, diagram)
          } catch (e) {
            diagram.textContent = 'Ошибка рендера диаграммы: ' + e.message
          }
        }
      }
      render()
      textarea.addEventListener('input', () => {
        render()
        editor.commands.command(({ tr }) => {
          tr.insertText(textarea.value, getPos() + 1, getPos() + node.nodeSize - 1)
          return true
        })
      })
      return {
        dom,
        contentDOM: null,
      }
    }
  },
}) 