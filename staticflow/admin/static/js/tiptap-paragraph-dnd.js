import { Paragraph } from '@tiptap/extension-paragraph'
import { createDndNodeView } from './tiptap-dnd-nodeview.js'

export const ParagraphDnd = Paragraph.extend({
  draggable: true,
  selectable: true,
  addNodeView() {
    return createDndNodeView('dnd-paragraph-block', '¶')
  }
}) 