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

export const HeadingDnd = Heading.extend({
  addNodeView() {
    return createDndNodeView('dnd-heading-block', '≡')
  },
})

export const BlockquoteDnd = Blockquote.extend({
  addNodeView() {
    return createDndNodeView('dnd-blockquote-block', '❝')
  },
})

export const CodeBlockDnd = CodeBlockLowlight.extend({
  addNodeView() {
    return createDndNodeView('dnd-code-block', '⧉')
  },
})

export const BulletListDnd = BulletList.extend({
  addNodeView() {
    return createDndNodeView('dnd-bullet-list-block', '•')
  },
})

export const OrderedListDnd = OrderedList.extend({
  addNodeView() {
    return createDndNodeView('dnd-ordered-list-block', '1.')
  },
})

export const TaskListDnd = TaskList.extend({
  addNodeView() {
    return createDndNodeView('dnd-task-list-block', '☑')
  },
})

export const ImageDnd = Image.extend({
  addNodeView() {
    return createDndNodeView('dnd-image-block', '🖼')
  },
})

export const VideoBlockDnd = VideoBlock.extend({
  addNodeView() {
    return createDndNodeView('dnd-video-block', '🎬')
  },
})

export const AudioBlockDnd = AudioBlock.extend({
  addNodeView() {
    return createDndNodeView('dnd-audio-block', '🎵')
  },
}) 