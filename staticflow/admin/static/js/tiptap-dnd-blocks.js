import { Heading } from '@tiptap/extension-heading'
import { Blockquote } from '@tiptap/extension-blockquote'
import { CodeBlockLowlight } from '@tiptap/extension-code-block-lowlight'
import { BulletList } from '@tiptap/extension-bullet-list'
import { OrderedList } from '@tiptap/extension-ordered-list'
import { TaskList } from '@tiptap/extension-task-list'
import { Image } from '@tiptap/extension-image'
import { VideoBlock } from './tiptap-video.js'
import { AudioBlock } from './tiptap-audio'
import { createDndNodeView } from './tiptap-dnd-nodeview.js'

const createDraggableExtension = (Extension, className, icon, extraAttrs) => {
  return Extension.extend({
    draggable: true,
    selectable: true,
    addAttributes() {
      return {
        ...this.parent?.(),
        id: {
          default: null,
          parseHTML: element => element.getAttribute('data-node-id'),
          renderHTML: attributes => {
            return {
              'data-node-id': attributes.id || Math.random().toString(36).substr(2, 9)
            }
          }
        },
        ...(extraAttrs || {})
      }
    },
    addNodeView() {
      return function (props) {
        const nodeView = createDndNodeView(className, icon)(props)
        if (className === 'dnd-heading-block' && props.node?.attrs?.level) {
          nodeView.dom.setAttribute('data-level', props.node.attrs.level)
        }
        return nodeView
      }
    }
  })
}

export const HeadingDnd = createDraggableExtension(Heading, 'dnd-heading-block', 'H', { level: { default: 1 } })
export const BlockquoteDnd = createDraggableExtension(Blockquote, 'dnd-blockquote-block', '❝')
export const CodeBlockDnd = createDraggableExtension(CodeBlockLowlight, 'dnd-code-block', '⧉')
export const BulletListDnd = createDraggableExtension(BulletList, 'dnd-bullet-list-block', '•')
export const OrderedListDnd = createDraggableExtension(OrderedList, 'dnd-ordered-list-block', '1.')
export const TaskListDnd = createDraggableExtension(TaskList, 'dnd-task-list-block', '☐')
export const ImageDnd = createDraggableExtension(Image, 'dnd-image-block', '🖼')
export const VideoBlockDnd = createDraggableExtension(VideoBlock, 'dnd-video-block', '🎬')
export const AudioBlockDnd = AudioBlock.extend({
  draggable: true,
  selectable: true,
}); 