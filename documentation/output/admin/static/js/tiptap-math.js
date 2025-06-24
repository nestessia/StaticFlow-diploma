import { Node, mergeAttributes } from '@tiptap/core'
import { createDndNodeView } from './tiptap-dnd-nodeview.js'

const commonSymbols = [
  { symbol: '±', desc: 'Плюс-минус' },
  { symbol: '×', desc: 'Умножение' },
  { symbol: '÷', desc: 'Деление' },
  { symbol: '≈', desc: 'Приблизительно равно' },
  { symbol: '≠', desc: 'Не равно' },
  { symbol: '≤', desc: 'Меньше или равно' },
  { symbol: '≥', desc: 'Больше или равно' },
  { symbol: '∑', desc: 'Сумма' },
  { symbol: '∏', desc: 'Произведение' },
  { symbol: '∫', desc: 'Интеграл' },
  { symbol: '∞', desc: 'Бесконечность' },
  { symbol: '√', desc: 'Корень' },
]

export const MathBlock = Node.create({
  name: 'mathBlock',
  group: 'block',
  content: 'text*',
  code: true,
  
  addAttributes() {
    return {
      latex: {
        default: '',
        parseHTML: element => element.textContent || '',
        renderHTML: attributes => {
          return {
            'data-latex': attributes.latex,
          }
        },
      },
    }
  },

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
      const wrapper = document.createElement('div')
      wrapper.className = 'math-block-preview-wrapper dnd-block dnd-math-block'
      wrapper.draggable = true
      
      // Drag handle
      const handle = document.createElement('span')
      handle.className = 'dnd-handle'
      handle.textContent = '∑'
      handle.style.cursor = 'grab'
      handle.style.userSelect = 'none'
      handle.style.marginRight = '8px'

      // Content wrapper
      const contentWrapper = document.createElement('div')
      contentWrapper.className = 'math-content-wrapper'
      contentWrapper.style.flex = '1'

      // Help text
      const helpText = document.createElement('div')
      helpText.className = 'math-help-text'
      helpText.textContent = 'Введите формулу в формате LaTeX и нажмите Enter для предпросмотра.'
      helpText.style.marginBottom = '8px'
      helpText.style.color = '#666'
      helpText.style.fontSize = '14px'
      contentWrapper.appendChild(helpText)

      // Input field
      const input = document.createElement('textarea')
      input.className = 'math-block-input'
      input.value = node.attrs.latex || node.textContent || ''
      input.placeholder = 'Введите формулу в формате LaTeX...'
      input.style.width = '100%'
      input.style.minHeight = '60px'
      input.style.padding = '8px'
      input.style.marginBottom = '8px'
      input.style.border = '1px solid #ddd'
      input.style.borderRadius = '4px'
      input.style.fontFamily = 'monospace'

      // Отключаем drag-and-drop только для поля ввода
      input.addEventListener('dragstart', (event) => {
        event.preventDefault()
        event.stopPropagation()
      })

      // Рендеринг только по Enter
      input.addEventListener('keydown', (event) => {
        if (event.key === 'Enter' && !event.shiftKey) {
          event.preventDefault()
          updateNodeContent(input.value)
          updatePreview(input.value)
        }
      })

      // Обновление содержимого блока при любом вводе (чтобы не пропадал)
      input.addEventListener('input', () => {
        updateNodeContent(input.value)
      })

      // Функция для обновления содержимого узла
      function updateNodeContent(content) {
        const pos = getPos()
        if (pos !== undefined) {
          editor.commands.command(({ tr, state }) => {
            const node = tr.doc.nodeAt(pos)
            if (!node || node.type.name !== 'mathBlock') return false
            const from = pos + 1
            const to = pos + node.nodeSize - 1
            tr.insertText(content, from, to)
            // Обновляем атрибут latex
            tr.setNodeAttribute(pos, 'latex', content)
            return true
          })
        }
      }

      contentWrapper.appendChild(input)

      // Preview wrapper
      const previewWrapper = document.createElement('div')
      previewWrapper.className = 'math-preview-wrapper'
      previewWrapper.style.padding = '12px'
      previewWrapper.style.border = '1px dashed #ddd'
      previewWrapper.style.borderRadius = '4px'
      previewWrapper.style.background = '#f9f9f9'

      const previewLabel = document.createElement('div')
      previewLabel.className = 'math-preview-label'
      previewLabel.textContent = 'Предпросмотр:'
      previewLabel.style.marginBottom = '8px'
      previewLabel.style.color = '#666'
      previewWrapper.appendChild(previewLabel)

      const preview = document.createElement('div')
      preview.className = 'math-block-preview'
      previewWrapper.appendChild(preview)
      contentWrapper.appendChild(previewWrapper)

      // Error display
      const errorDisplay = document.createElement('div')
      errorDisplay.className = 'math-error-display'
      errorDisplay.style.color = '#d32f2f'
      errorDisplay.style.fontSize = '14px'
      errorDisplay.style.marginTop = '8px'
      contentWrapper.appendChild(errorDisplay)

      function updatePreview(latex) {
        try {
          if (window.katex) {
            window.katex.render(latex, preview, {
              throwOnError: false,
              displayMode: true,
            })
            errorDisplay.textContent = ''
            preview.style.border = '1px dashed #ddd'
          } else {
            preview.textContent = latex
            errorDisplay.textContent = 'KaTeX не загружен'
          }
        } catch (e) {
          preview.textContent = latex
          errorDisplay.textContent = 'Ошибка формулы: ' + e.message
          preview.style.border = '1px dashed #d32f2f'
        }
      }

      // Initial preview
      updatePreview(node.attrs.latex || node.textContent || '')

      // Drag and drop handlers для всего блока
      wrapper.addEventListener('dragstart', (event) => {
        if (event.target === input) {
          event.preventDefault()
          return
        }
        event.dataTransfer.setData('application/x-tiptap-drag', getPos())
        wrapper.classList.add('dragging')
      })

      wrapper.addEventListener('dragend', () => {
        wrapper.classList.remove('dragging')
      })

      wrapper.appendChild(handle)
      wrapper.appendChild(contentWrapper)

      return {
        dom: wrapper,
        contentDOM: null,
        update: (updatedNode) => {
          if (updatedNode.type.name !== 'mathBlock') return false
          const latexContent = updatedNode.attrs.latex || updatedNode.textContent
          // Синхронизируем значение input с содержимым узла
          if (input.value !== latexContent) {
            input.value = latexContent
          }
          updatePreview(latexContent)
          return true
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