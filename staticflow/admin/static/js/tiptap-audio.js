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
      title: { default: '' },
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
    return ['audio', mergeAttributes(HTMLAttributes, { controls: true })]
  },

  addNodeView() {
    return ({ node, getPos, editor }) => {
      const dom = document.createElement('div')
      dom.className = 'audio-block'
      dom.contentEditable = false

      // Форма для вставки/загрузки
      const form = document.createElement('div')
      form.className = 'audio-form'
      form.style.marginTop = '8px'

      // Переключатель режима
      const modeSwitch = document.createElement('div')
      modeSwitch.style.marginBottom = '8px'
      modeSwitch.style.display = 'flex'
      modeSwitch.style.gap = '8px'

      const urlModeBtn = document.createElement('button')
      urlModeBtn.textContent = 'Вставить по URL'
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
      urlInput.placeholder = 'URL аудио...'
      urlInput.value = node.attrs.src || ''
      urlInput.style.width = '100%'
      urlInput.style.marginBottom = '8px'
      urlInput.style.display = 'block'
      form.appendChild(urlInput)

      // File input
      const fileInput = document.createElement('input')
      fileInput.type = 'file'
      fileInput.accept = 'audio/*'
      fileInput.style.marginBottom = '8px'
      fileInput.style.display = 'none'
      form.appendChild(fileInput)

      // Title input
      const titleInput = document.createElement('input')
      titleInput.type = 'text'
      titleInput.placeholder = 'Заголовок аудио...'
      titleInput.value = node.attrs.title || ''
      titleInput.style.width = '100%'
      titleInput.style.marginBottom = '8px'
      form.appendChild(titleInput)

      // Кнопка вставки
      const setBtn = document.createElement('button')
      setBtn.type = 'button'
      setBtn.textContent = 'Вставить'
      setBtn.style.padding = '4px 8px'
      form.appendChild(setBtn)

      // Показываем аудио только если src есть
      if (node.attrs.src) {
        const audio = document.createElement('audio')
        audio.controls = true
        audio.style.width = '100%'
        audio.style.borderRadius = '8px'
        audio.src = node.attrs.src
        audio.title = node.attrs.title || ''
        dom.appendChild(audio)
      }

      dom.appendChild(form)

      // Функция обновления аудио
      const updateAudio = (src, title) => {
        editor.commands.command(({ tr }) => {
          tr.setNodeMarkup(getPos(), undefined, { 
            ...node.attrs, 
            src,
            title
          })
          return true
        })
        // Если аудио уже есть, обновим src
        const audioEl = dom.querySelector('audio')
        if (audioEl) {
          audioEl.src = src
          audioEl.title = title
        } else if (src) {
          // Если аудио не было, но теперь src есть — добавить превью
          const audio = document.createElement('audio')
          audio.controls = true
          audio.style.width = '100%'
          audio.style.borderRadius = '8px'
          audio.src = src
          audio.title = title
          dom.insertBefore(audio, form)
        }
      }

      // Обработка вставки по URL
      setBtn.onclick = () => {
        const src = urlInput.value.trim()
        const title = titleInput.value.trim()
        
        if (src) {
          updateAudio(src, title)
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
              updateAudio(data.url, titleInput.value.trim())
            }
          } else {
            alert('Ошибка загрузки файла')
          }
        } catch (error) {
          console.error('Ошибка при загрузке файла:', error)
          alert('Ошибка при загрузке файла')
        }
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