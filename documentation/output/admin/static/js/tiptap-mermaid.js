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
      // --- Стилизация textarea ---
      textarea.style.width = '100%';
      textarea.style.minHeight = '100px';
      textarea.style.fontFamily = 'monospace';
      textarea.style.border = '1.5px solid #bdbdbd';
      textarea.style.borderRadius = '8px';
      textarea.style.padding = '10px';
      textarea.style.background = '#f9f9f9';
      textarea.style.boxShadow = '0 2px 8px rgba(0,0,0,0.04)';
      textarea.style.transition = 'border 0.2s, box-shadow 0.2s';
      textarea.style.resize = 'vertical';
      textarea.addEventListener('focus', () => {
        textarea.style.border = '2px solid #1976d2';
        textarea.style.boxShadow = '0 2px 12px rgba(25,118,210,0.08)';
      });
      textarea.addEventListener('blur', () => {
        textarea.style.border = '1.5px solid #bdbdbd';
        textarea.style.boxShadow = '0 2px 8px rgba(0,0,0,0.04)';
      });
      // --- Автоувеличение высоты ---
      function autoResize() {
        textarea.style.height = 'auto';
        textarea.style.height = textarea.scrollHeight + 'px';
      }
      textarea.addEventListener('input', autoResize);
      setTimeout(autoResize, 0);
      // --- Debounce для обновления ---
      let debounceTimer = null;
      function updateEditorValue() {
        editor.commands.command(({ tr }) => {
          tr.insertText(textarea.value, getPos() + 1, getPos() + node.nodeSize - 1)
          return true
        })
        render();
      }
      // --- Обновление только по Enter ---
      textarea.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
          e.preventDefault();
          updateEditorValue();
        }
      });
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
          if (event.target && event.target.classList && event.target.classList.contains('mermaid-input')) {
            return true; // разрешить все события на textarea
          }
          if (event && event.type && event.type.startsWith('drag')) return false;
          return undefined;
        }
      }
    }
  },
}) 