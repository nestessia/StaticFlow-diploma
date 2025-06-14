import { Node, mergeAttributes } from '@tiptap/core'
import { createDndNodeView } from './tiptap-dnd-nodeview.js'

export const MathBlock = Node.create({
  name: 'mathBlock',
  group: 'block',
  content: 'text*',
  code: true,
  atom: true,
  parseHTML() {
    return [
      {
        tag: 'div.math-block',
      },
    ]
  },
  renderHTML({ HTMLAttributes }) {
    return ['div', mergeAttributes(HTMLAttributes, { class: 'math-block' }), 0]
  },
  addNodeView() {
    return ({ node, getPos, editor }) => {
      console.log('MathBlock NodeView!', node.textContent, node);
      const wrapper = document.createElement('div')
      wrapper.className = 'math-block-preview-wrapper dnd-block dnd-math-block'
      wrapper.style.display = 'flex'
      wrapper.style.alignItems = 'flex-start'
      // Drag handle
      const handle = document.createElement('span')
      handle.className = 'dnd-handle'
      handle.textContent = '∑'
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
      // Content
      const contentDOM = document.createElement('div')
      contentDOM.className = 'dnd-content'
      contentDOM.style.flex = '1'
      // Исходный LaTeX
      const source = document.createElement('pre')
      source.className = 'math-block-source'
      source.textContent = node.textContent
      contentDOM.appendChild(source)
      // Preview
      const preview = document.createElement('div')
      preview.className = 'math-block-preview'
      try {
        if (window.katex) {
          window.katex.render(node.textContent, preview, {
            throwOnError: false,
            displayMode: true,
          })
        } else {
          preview.textContent = node.textContent
        }
      } catch (e) {
        preview.textContent = 'Ошибка формулы: ' + e.message
      }
      contentDOM.appendChild(preview)
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

export const MathInline = Node.create({
  name: 'mathInline',
  group: 'inline',
  inline: true,
  atom: true,
  code: true,
  content: 'text*',
  parseHTML() {
    return [
      {
        tag: 'span.math-inline',
      },
    ]
  },
  renderHTML({ HTMLAttributes }) {
    return ['span', mergeAttributes(HTMLAttributes, { class: 'math-inline' }), 0]
  },
  addNodeView() {
    return ({ node }) => {
      console.log('MathInline NodeView!', node.textContent, node);
      const wrapper = document.createElement('span');
      wrapper.className = 'math-inline-preview-wrapper';

      // Исходный текст
      const text = document.createElement('span');
      text.className = 'math-inline-source';
      text.textContent = `$${node.textContent}$`;
      wrapper.appendChild(text);

      // Превью
      const preview = document.createElement('span');
      preview.className = 'math-inline-preview';
      preview.style.marginLeft = '8px';
      try {
        if (window.katex) {
          window.katex.render(node.textContent, preview, {
            throwOnError: false,
            displayMode: false,
          });
        } else {
          preview.textContent = node.textContent;
        }
      } catch (e) {
        preview.textContent = 'Ошибка формулы';
      }
      wrapper.appendChild(preview);

      return {
        dom: wrapper,
        contentDOM: null,
      };
    }
  },
}) 