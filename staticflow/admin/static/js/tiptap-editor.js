import { Editor } from '@tiptap/core'
import StarterKit from '@tiptap/starter-kit'
import Link from '@tiptap/extension-link'
import { lowlight } from 'lowlight'
import TaskItem from '@tiptap/extension-task-item'
import { Table } from '@tiptap/extension-table'
import { TableRow } from '@tiptap/extension-table-row'
import { TableCell } from '@tiptap/extension-table-cell'
import { TableHeader } from '@tiptap/extension-table-header'
import { Placeholder } from '@tiptap/extension-placeholder'
import { TextAlign } from '@tiptap/extension-text-align'
import { Color } from '@tiptap/extension-color'
import { TextStyle } from '@tiptap/extension-text-style'
import { Underline } from '@tiptap/extension-underline'
import { Subscript } from '@tiptap/extension-subscript'
import { Superscript } from '@tiptap/extension-superscript'
import { marked } from 'marked'
import TurndownService from 'turndown'
import { MathBlock, MathInline } from './tiptap-math.js'
import { MermaidBlock } from './tiptap-mermaid.js'
import { ParagraphDnd } from './tiptap-paragraph-dnd.js'
import {
  HeadingDnd,
  BlockquoteDnd,
  CodeBlockDnd,
  BulletListDnd,
  OrderedListDnd,
  TaskListDnd,
  ImageDnd,
  VideoBlockDnd,
  AudioBlockDnd
} from './tiptap-dnd-blocks.js'
import javascript from 'highlight.js/lib/languages/javascript'
import python from 'highlight.js/lib/languages/python'
import { preprocessMarkdownHtml } from './markdown-preprocessor.js'
import { DropIndicator } from './tiptap-drop-indicator.js'
import { createColorBubbleMenu } from './tiptap-bubblemenu.js'
import { BubbleMenu } from '@tiptap/extension-bubble-menu'

lowlight.registerLanguage('js', javascript)
lowlight.registerLanguage('javascript', javascript)
lowlight.registerLanguage('python', python)

class TipTapEditor {
    constructor(selector, content = '', type = 'markdown') {
        this.element = document.querySelector(selector)
        this.editor = null
        this.content = content
        this.type = type
        this.turndown = new TurndownService({
            headingStyle: 'atx',
            codeBlockStyle: 'fenced',
            emDelimiter: '*'
        })
        this.init()
    }

    init() {
        let htmlContent = ''
        if (this.type === 'markdown') {
            htmlContent = this.content ? marked(this.content) : ''
            htmlContent = preprocessMarkdownHtml(htmlContent)
        } else {
            htmlContent = this.content || ''
        }
        // Создаём bubble menu DOM-элемент
        const colorBubbleMenu = createColorBubbleMenu(this.editor)
        this.editor = new Editor({
            element: this.element,
            extensions: [
                StarterKit.configure({
                    paragraph: false,
                    heading: false,
                    blockquote: false,
                    codeBlock: false,
                    bulletList: false,
                    orderedList: false,
                    taskList: false,
                    image: false,
                }),
                ParagraphDnd,
                HeadingDnd,
                BlockquoteDnd,
                CodeBlockDnd.configure({ lowlight }),
                BulletListDnd,
                OrderedListDnd,
                TaskListDnd,
                ImageDnd,
                VideoBlockDnd,
                AudioBlockDnd,
                Link.configure({
                    openOnClick: false,
                    HTMLAttributes: {
                        class: 'editor-link'
                    }
                }),
                TaskItem.configure({
                    nested: true,
                }),
                Table.configure({
                    resizable: true,
                }),
                TableRow,
                TableCell,
                TableHeader,
                Placeholder.configure({
                    placeholder: 'Начните писать...',
                }),
                TextAlign.configure({
                    types: ['heading', 'paragraph'],
                }),
                Color,
                TextStyle,
                Underline,
                Subscript,
                Superscript,
                MathBlock,
                MathInline,
                MermaidBlock,
                DropIndicator,
                BubbleMenu.configure({
                    element: colorBubbleMenu,
                    tippyOptions: { duration: 150 },
                    shouldShow: ({ editor }) => editor.isActive('textStyle') || editor.isActive('highlight') || editor.isActive('text'),
                }),
            ],
            content: htmlContent,
            onUpdate: ({ editor }) => {
                this.onContentUpdate(editor.getHTML())
            },
            editorProps: {
                attributes: {
                    class: 'prose prose-sm sm:prose lg:prose-lg xl:prose-2xl mx-auto focus:outline-none',
                    spellcheck: 'false',
                    autocorrect: 'off',
                    autocomplete: 'off',
                    autocapitalize: 'off',
                },
            },
        })
    }

    onContentUpdate(html) {
        // Вызываем событие обновления контента
        const event = new CustomEvent('editor:update', {
            detail: {
                html,
                markdown: this.getMarkdown()
            }
        })
        document.dispatchEvent(event)
    }

    getHTML() {
        return this.editor.getHTML()
    }

    getMarkdown() {
        return this.turndown.turndown(this.editor.getHTML())
    }

    getContentForSave() {
        if (this.type === 'markdown') {
            return this.getMarkdown()
        } else {
            return this.getHTML()
        }
    }

    setContent(content) {
        if (this.type === 'markdown') {
            this.editor.commands.setContent(marked(content))
        } else {
            this.editor.commands.setContent(content)
        }
    }

    destroy() {
        this.editor.destroy()
    }
}

// Экспортируем класс для использования
window.TipTapEditor = TipTapEditor 