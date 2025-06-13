import { Node, mergeAttributes } from '@tiptap/core'
import { createDndNodeView } from './tiptap-dnd-nodeview.js'

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
      const wrapper = document.createElement('div')
      wrapper.className = 'dnd-block dnd-mermaid-block'
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
      // Content
      const contentDOM = document.createElement('div')
      contentDOM.className = 'dnd-content'
      contentDOM.style.flex = '1'
      // Mermaid input
      const textarea = document.createElement('textarea')
      textarea.value = node.textContent || 'graph TD;\nA-->B;'
      textarea.className = 'mermaid-input'
      textarea.placeholder = 'Введите код диаграммы mermaid...'
      contentDOM.appendChild(textarea)
      // Preview
      const preview = document.createElement('div')
      preview.className = 'mermaid-preview'
      contentDOM.appendChild(preview)
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
          if (event && event.type && event.type.startsWith('drag')) return false;
          return undefined;
        }
      }
    }
  },
}) 