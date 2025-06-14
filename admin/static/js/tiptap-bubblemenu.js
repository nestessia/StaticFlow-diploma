import { BubbleMenu } from '@tiptap/extension-bubble-menu'

export function createColorBubbleMenu(editor) {
    // Создаём контейнер для bubble menu
    const menu = document.createElement('div')
    menu.className = 'tiptap-bubble-menu'

    // Кнопка палитры
    const paletteBtn = document.createElement('button')
    paletteBtn.className = 'bubblemenu-palette-btn'
    paletteBtn.title = 'Цвет текста/фона/обводки'
    paletteBtn.innerHTML = '<i class="fas fa-palette"></i>'
    menu.appendChild(paletteBtn)

    // Модальное окно выбора цветов
    const modal = document.createElement('div')
    modal.className = 'bubblemenu-color-modal'
    modal.style.display = 'none'
    modal.innerHTML = `
      <label>Цвет текста: <input type="color" id="color-text" value="#111111"></label><br>
      <label>Фон: <input type="color" id="color-bg" value="#ffffff"></label><br>
      <label>Обводка: <input type="color" id="color-outline" value="#000000"></label><br>
      <button id="apply-colors">Применить</button>
      <button id="close-colors">Отмена</button>
    `
    document.body.appendChild(modal)

    paletteBtn.addEventListener('click', (e) => {
        e.preventDefault()
        // Позиционируем модалку рядом с bubble menu
        const rect = menu.getBoundingClientRect()
        modal.style.position = 'absolute'
        modal.style.left = rect.left + 'px'
        modal.style.top = (rect.bottom + 8) + 'px'
        modal.style.display = 'block'
    })

    modal.querySelector('#close-colors').onclick = () => {
        modal.style.display = 'none'
    }
    modal.querySelector('#apply-colors').onclick = () => {
        const color = modal.querySelector('#color-text').value
        const bg = modal.querySelector('#color-bg').value
        const outline = modal.querySelector('#color-outline').value
        // Применяем цвет текста
        editor.chain().focus().setColor(color).run()
        // Применяем фон (highlight)
        editor.chain().focus().setHighlight({ color: bg }).run()
        // Применяем outline через textStyle
        editor.chain().focus().setTextStyle({ 'text-shadow': `0 0 0 2px ${outline}` }).run()
        modal.style.display = 'none'
    }

    return menu
} 