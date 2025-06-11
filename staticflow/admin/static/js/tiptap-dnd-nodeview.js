export function createDndNodeView(blockClass = '', dragIcon = '⋮⋮') {
  return function DndNodeView({ node, getPos, editor }) {
    const wrapper = document.createElement('div')
    wrapper.className = 'dnd-block ' + blockClass
    wrapper.style.display = 'flex'
    wrapper.style.alignItems = 'flex-start'
    // Drag handle
    const handle = document.createElement('span')
    handle.className = 'dnd-handle'
    handle.textContent = dragIcon
    handle.style.cursor = 'grab'
    handle.style.userSelect = 'none'
    handle.style.marginRight = '8px'
    handle.draggable = true
    // Drag events
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
    wrapper.appendChild(handle)
    wrapper.appendChild(contentDOM)
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
    return {
      dom: wrapper,
      contentDOM,
    }
  }
} 