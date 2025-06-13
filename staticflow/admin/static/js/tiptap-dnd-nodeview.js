// --- глобальная карта для связи DOM-элемента блока и getPos ---
const dndBlockPosMap = new Map();

export function createDndNodeView(blockClass = '', dragIcon = '⋮⋮') {
  return function DndNodeView({ node, getPos, editor }) {
    const wrapper = document.createElement('div')
    wrapper.className = 'dnd-block ' + blockClass
    wrapper.draggable = true

    // Добавляем кнопку удаления
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

    const contentDOM = document.createElement('div')
    contentDOM.className = 'dnd-content'

    wrapper.appendChild(deleteButton)
    wrapper.appendChild(contentDOM)

    return {
      dom: wrapper,
      contentDOM,
      ignoreMutation: () => false,
      stopEvent: () => false
    }
  }
} 