import { Heading } from '@tiptap/extension-heading'
import { Blockquote } from '@tiptap/extension-blockquote'
import { CodeBlockLowlight } from '@tiptap/extension-code-block-lowlight'
import { BulletList } from '@tiptap/extension-bullet-list'
import { OrderedList } from '@tiptap/extension-ordered-list'
import { TaskList } from '@tiptap/extension-task-list'
import { Image } from '@tiptap/extension-image'
import { VideoBlock } from './tiptap-video.js'
import { AudioBlock } from './tiptap-audio.js'
import { createDndNodeView } from './tiptap-dnd-nodeview.js'

const createDraggableExtension = (Extension, className, icon) => {
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
        }
      }
    },
    addNodeView() {
      return createDndNodeView(className, icon)
    }
  })
}

export const HeadingDnd = createDraggableExtension(Heading, 'dnd-heading-block', 'H')
export const BlockquoteDnd = createDraggableExtension(Blockquote, 'dnd-blockquote-block', '❝')
export const CodeBlockDnd = createDraggableExtension(CodeBlockLowlight, 'dnd-code-block', '⧉')
export const BulletListDnd = createDraggableExtension(BulletList, 'dnd-bullet-list-block', '•')
export const OrderedListDnd = createDraggableExtension(OrderedList, 'dnd-ordered-list-block', '1.')
export const TaskListDnd = createDraggableExtension(TaskList, 'dnd-task-list-block', '☐')
export const ImageDnd = createDraggableExtension(Image, 'dnd-image-block', '🖼')
export const VideoBlockDnd = createDraggableExtension(VideoBlock, 'dnd-video-block', '🎬')
export const AudioBlockDnd = createDraggableExtension(AudioBlock, 'dnd-audio-block', '🎵') 