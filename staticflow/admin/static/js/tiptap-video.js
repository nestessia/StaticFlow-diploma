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
      title: { default: '' },
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
    return ['video', mergeAttributes(HTMLAttributes, { controls: true })]
  },
  addNodeView() {
    return ({ node, getPos, editor }) => {
      const dom = document.createElement('div')
      dom.className = 'video-block'
      dom.contentEditable = false

      // Форма для вставки/загрузки
      const form = document.createElement('div')
      form.className = 'video-form'
      form.style.marginTop = '8px'

      // Переключатель режима
      const modeSwitch = document.createElement('div')
      modeSwitch.style.marginBottom = '8px'
      modeSwitch.style.display = 'flex'
      modeSwitch.style.gap = '8px'

      const urlModeBtn = document.createElement('button')
      urlModeBtn.textContent = 'Insert by URL'
      urlModeBtn.style.padding = '4px 8px'
      urlModeBtn.style.flex = '1'
      urlModeBtn.style.backgroundColor = '#f0f0f0'
      urlModeBtn.style.border = '1px solid #ddd'
      urlModeBtn.style.borderRadius = '4px'
      urlModeBtn.style.cursor = 'pointer'

      const uploadModeBtn = document.createElement('button')
      uploadModeBtn.textContent = 'Загрузить файл'
      uploadModeBtn.style.padding = '4px 8px'
      uploadModeBtn.style.flex = '1'
      uploadModeBtn.style.backgroundColor = '#f0f0f0'
      uploadModeBtn.style.border = '1px solid #ddd'
      uploadModeBtn.style.borderRadius = '4px'
      uploadModeBtn.style.cursor = 'pointer'

      modeSwitch.appendChild(urlModeBtn)
      modeSwitch.appendChild(uploadModeBtn)
      form.appendChild(modeSwitch)

      // URL input
      const urlInput = document.createElement('input')
      urlInput.type = 'text'
      urlInput.placeholder = 'URL видео...'
      urlInput.value = node.attrs.src || ''
      urlInput.style.width = '100%'
      urlInput.style.marginBottom = '8px'
      urlInput.style.display = 'block'
      form.appendChild(urlInput)

      // File input
      const fileInput = document.createElement('input')
      fileInput.type = 'file'
      fileInput.accept = 'video/*'
      fileInput.style.marginBottom = '8px'
      fileInput.style.display = 'none'
      form.appendChild(fileInput)

      // Title input
      const titleInput = document.createElement('input')
      titleInput.type = 'text'
      titleInput.placeholder = 'Заголовок видео...'
      titleInput.value = node.attrs.title || ''
      titleInput.style.width = '100%'
      titleInput.style.marginBottom = '8px'
      form.appendChild(titleInput)

      // Показываем видео только если src есть
      if (node.attrs.src) {
        const video = document.createElement('video')
        video.controls = true
        video.style.maxWidth = '100%'
        video.style.borderRadius = '8px'
        video.src = node.attrs.src
        if (node.attrs.poster) video.poster = node.attrs.poster
        dom.appendChild(video)
      }

      dom.appendChild(form)

      // Функция обновления видео
      const updateVideo = (src, title) => {
        editor.commands.command(({ tr }) => {
          tr.setNodeMarkup(getPos(), undefined, { 
            ...node.attrs, 
            src,
            title
          })
          return true
        })
        // Если видео уже есть, обновим src
        const videoEl = dom.querySelector('video')
        if (videoEl) {
          videoEl.src = src
          videoEl.title = title
        } else if (src) {
          // Если видео не было, но теперь src есть — добавить превью
          const video = document.createElement('video')
          video.controls = true
          video.style.maxWidth = '100%'
          video.style.borderRadius = '8px'
          video.src = src
          video.title = title
          dom.insertBefore(video, form)
        }
      }

      // Обработка вставки по URL (автоматически при изменении поля)
      urlInput.onblur = () => {
        const src = urlInput.value.trim()
        const title = titleInput.value.trim()
        if (src) {
          updateVideo(src, title)
        }
      }

      // Обработка загрузки файла
      fileInput.onchange = async (e) => {
        const file = e.target.files[0]
        if (!file) return

        const formData = new FormData()
        formData.append('file', file)

        try {
          const resp = await fetch('/admin/api/upload', {
            method: 'POST',
            body: formData,
          })

          if (resp.ok) {
            const data = await resp.json()
            if (data.url) {
              urlInput.value = data.url
              // Сразу обновляем node в редакторе
              updateVideo(data.url, titleInput.value.trim())
            }
          } else {
            alert('Ошибка загрузки файла')
          }
        } catch (error) {
          console.error('Ошибка при загрузке файла:', error)
          alert('Ошибка при загрузке файла')
        }
      }

      // Обновление title по потере фокуса
      titleInput.onblur = () => {
        const src = urlInput.value.trim()
        updateVideo(src, titleInput.value.trim())
      }

      // Обработка переключения режимов
      urlModeBtn.onclick = () => {
        urlInput.style.display = 'block'
        fileInput.style.display = 'none'
        urlModeBtn.style.backgroundColor = '#e0e0e0'
        uploadModeBtn.style.backgroundColor = '#f0f0f0'
      }

      uploadModeBtn.onclick = () => {
        urlInput.style.display = 'none'
        fileInput.style.display = 'block'
        uploadModeBtn.style.backgroundColor = '#e0e0e0'
        urlModeBtn.style.backgroundColor = '#f0f0f0'
      }

      // Устанавливаем начальный режим
      urlModeBtn.click()

      return {
        dom,
        contentDOM: null,
      }
    }
  }
}) 