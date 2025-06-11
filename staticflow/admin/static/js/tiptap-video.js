import { Node, mergeAttributes } from '@tiptap/core'

export const VideoBlock = Node.create({
  name: 'videoBlock',
  group: 'block',
  atom: true,
  draggable: true,
  selectable: true,
  addAttributes() {
    return {
      src: { default: '' },
      poster: { default: '' },
      controls: { default: true },
    }
  },
  parseHTML() {
    return [
      {
        tag: 'video',
      },
    ]
  },
  renderHTML({ HTMLAttributes }) {
    return ['video', mergeAttributes(HTMLAttributes, { controls: true }), 0]
  },
  addNodeView() {
    return ({ node, getPos, editor }) => {
      const dom = document.createElement('div')
      dom.className = 'video-block'
      dom.contentEditable = false
      // Видео превью
      const video = document.createElement('video')
      video.controls = true
      video.style.maxWidth = '100%'
      video.src = node.attrs.src || ''
      if (node.attrs.poster) video.poster = node.attrs.poster
      dom.appendChild(video)
      // Форма для вставки/загрузки
      const form = document.createElement('div')
      form.className = 'video-form'
      const urlInput = document.createElement('input')
      urlInput.type = 'text'
      urlInput.placeholder = 'URL видео...'
      urlInput.value = node.attrs.src || ''
      form.appendChild(urlInput)
      const fileInput = document.createElement('input')
      fileInput.type = 'file'
      fileInput.accept = 'video/*'
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
          video.src = src
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
            video.src = data.url
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