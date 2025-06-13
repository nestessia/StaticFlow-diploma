import { Node, mergeAttributes } from '@tiptap/core'

export const ImageBlock = Node.create({
  name: 'imageBlock',
  group: 'block',
  atom: true,
  draggable: true,
  selectable: true,
  addAttributes() {
    return {
      src: { default: '' },
      alt: { default: '' },
      title: { default: '' },
    }
  },
  parseHTML() {
    return [
      {
        tag: 'img',
      },
    ]
  },
  renderHTML({ HTMLAttributes }) {
    return ['img', mergeAttributes(HTMLAttributes)]
  },
  addNodeView() {
    return ({ node, getPos, editor }) => {
      const dom = document.createElement('div')
      dom.className = 'image-block'
      dom.contentEditable = false

      // Изображение превью
      const img = document.createElement('img')
      img.style.maxWidth = '100%'
      img.style.borderRadius = '8px'
      img.src = node.attrs.src || ''
      img.alt = node.attrs.alt || ''
      img.title = node.attrs.title || ''
      dom.appendChild(img)

      // Форма для вставки/загрузки
      const form = document.createElement('div')
      form.className = 'image-form'
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
      urlInput.placeholder = 'URL изображения...'
      urlInput.value = node.attrs.src || ''
      urlInput.style.width = '100%'
      urlInput.style.marginBottom = '8px'
      urlInput.style.display = 'block'
      form.appendChild(urlInput)

      // File input
      const fileInput = document.createElement('input')
      fileInput.type = 'file'
      fileInput.accept = 'image/*'
      fileInput.style.marginBottom = '8px'
      fileInput.style.display = 'none'
      form.appendChild(fileInput)

      // Alt text input
      const altInput = document.createElement('input')
      altInput.type = 'text'
      altInput.placeholder = 'Альтернативный текст...'
      altInput.value = node.attrs.alt || ''
      altInput.style.width = '100%'
      altInput.style.marginBottom = '8px'
      form.appendChild(altInput)

      // Title input
      const titleInput = document.createElement('input')
      titleInput.type = 'text'
      titleInput.placeholder = 'Заголовок изображения...'
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

      dom.appendChild(form)

      // Функция обновления изображения
      const updateImage = (src, alt, title) => {
        editor.commands.command(({ tr }) => {
          tr.setNodeMarkup(getPos(), undefined, { 
            ...node.attrs, 
            src,
            alt,
            title
          })
          return true
        })
        img.src = src
        img.alt = alt
        img.title = title
      }

      // Обработка вставки по URL
      setBtn.onclick = () => {
        const src = urlInput.value.trim()
        const alt = altInput.value.trim()
        const title = titleInput.value.trim()
        
        if (src) {
          updateImage(src, alt, title)
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
              updateImage(data.url, altInput.value.trim(), titleInput.value.trim())
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