import { Node, mergeAttributes } from '@tiptap/core'

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
      const dom = document.createElement('div')
      dom.className = 'math-block'
      dom.contentEditable = false
      const textarea = document.createElement('textarea')
      textarea.value = node.textContent
      textarea.className = 'math-input'
      textarea.placeholder = 'Введите формулу LaTeX...'
      dom.appendChild(textarea)
      const preview = document.createElement('div')
      preview.className = 'math-preview'
      dom.appendChild(preview)
      const render = () => {
        try {
          if (window.katex) {
            window.katex.render(textarea.value, preview, {
              throwOnError: false,
              displayMode: true,
            })
          } else {
            preview.textContent = textarea.value
          }
        } catch (e) {
          preview.textContent = 'Ошибка формулы: ' + e.message
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

export const MathInline = Node.create({
  name: 'mathInline',
  group: 'inline',
  inline: true,
  atom: true,
  code: true,
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
    return ({ node, getPos, editor }) => {
      const dom = document.createElement('span')
      dom.className = 'math-inline'
      dom.contentEditable = false
      const input = document.createElement('input')
      input.value = node.textContent
      input.className = 'math-inline-input'
      input.placeholder = 'LaTeX...'
      dom.appendChild(input)
      const preview = document.createElement('span')
      preview.className = 'math-inline-preview'
      dom.appendChild(preview)
      const render = () => {
        try {
          if (window.katex) {
            window.katex.render(input.value, preview, {
              throwOnError: false,
              displayMode: false,
            })
          } else {
            preview.textContent = input.value
          }
        } catch (e) {
          preview.textContent = 'Ошибка формулы'
        }
      }
      render()
      input.addEventListener('input', () => {
        render()
        editor.commands.command(({ tr }) => {
          tr.insertText(input.value, getPos() + 1, getPos() + node.nodeSize - 1)
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