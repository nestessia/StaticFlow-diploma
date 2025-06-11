import { Node, mergeAttributes } from '@tiptap/core'

export const AudioBlock = Node.create({
  name: 'audioBlock',
  group: 'block',
  atom: true,
  draggable: true,
  selectable: true,
  addAttributes() {
    return {
      src: { default: '' },
      controls: { default: true },
    }
  },
  parseHTML() {
    return [
      {
        tag: 'audio',
      },
    ]
  },
  renderHTML({ HTMLAttributes }) {
    return ['audio', mergeAttributes(HTMLAttributes, { controls: true }), 0]
  },
  addNodeView() {
    return ({ node, getPos, editor }) => {
      const dom = document.createElement('div')
      dom.className = 'audio-block'
      dom.contentEditable = false
      // Аудио превью
      const audio = document.createElement('audio')
      audio.controls = true
      audio.style.width = '100%'
      audio.src = node.attrs.src || ''
      dom.appendChild(audio)
      // Форма для вставки/загрузки
      const form = document.createElement('div')
      form.className = 'audio-form'
      const urlInput = document.createElement('input')
      urlInput.type = 'text'
      urlInput.placeholder = 'URL аудио...'
      urlInput.value = node.attrs.src || ''
      form.appendChild(urlInput)
      const fileInput = document.createElement('input')
      fileInput.type = 'file'
      fileInput.accept = 'audio/*'
      form.appendChild(fileInput)
      const setBtn = document.createElement('button')
      setBtn.type = 'button'
      setBtn.textContent = 'Вставить'
      form.appendChild(setBtn)
      dom.appendChild(form)
      // Обработка вставки по URL
      setBtn.onclick = () => {
        const src = urlInput.value.trim()
        if (src) {
          editor.commands.command(({ tr }) => {
            tr.setNodeMarkup(getPos(), undefined, { ...node.attrs, src })
            return true
          })
          audio.src = src
        }
      }
      // Обработка загрузки файла
      fileInput.onchange = async (e) => {
        const file = e.target.files[0]
        if (!file) return
        const formData = new FormData()
        formData.append('file', file)
        // Загрузка на сервер (API должен принимать /admin/api/upload)
        const resp = await fetch('/admin/api/upload', {
          method: 'POST',
          body: formData,
        })
        if (resp.ok) {
          const data = await resp.json()
          if (data.url) {
            urlInput.value = data.url
            audio.src = data.url
            editor.commands.command(({ tr }) => {
              tr.setNodeMarkup(getPos(), undefined, { ...node.attrs, src: data.url })
              return true
            })
          }
        } else {
          alert('Ошибка загрузки файла')
        }
      }
      return {
        dom,
        contentDOM: null,
      }
    }
  },
}) 