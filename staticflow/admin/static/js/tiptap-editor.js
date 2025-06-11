import { Editor } from '@tiptap/core'
import StarterKit from '@tiptap/starter-kit'
import Image from '@tiptap/extension-image'
import Link from '@tiptap/extension-link'
import CodeBlockLowlight from '@tiptap/extension-code-block-lowlight'
import { lowlight } from 'lowlight'
import TaskList from '@tiptap/extension-task-list'
import TaskItem from '@tiptap/extension-task-item'
import { Table } from '@tiptap/extension-table'
import { TableRow } from '@tiptap/extension-table-row'
import { TableCell } from '@tiptap/extension-table-cell'
import { TableHeader } from '@tiptap/extension-table-header'
import { Placeholder } from '@tiptap/extension-placeholder'
import { Highlight } from '@tiptap/extension-highlight'
import { TextAlign } from '@tiptap/extension-text-align'
import { Color } from '@tiptap/extension-color'
import { TextStyle } from '@tiptap/extension-text-style'
import { Underline } from '@tiptap/extension-underline'
import { Subscript } from '@tiptap/extension-subscript'
import { Superscript } from '@tiptap/extension-superscript'
import { HorizontalRule } from '@tiptap/extension-horizontal-rule'
import { Blockquote } from '@tiptap/extension-blockquote'
import { BulletList } from '@tiptap/extension-bullet-list'
import { ListItem } from '@tiptap/extension-list-item'
import { OrderedList } from '@tiptap/extension-ordered-list'
import { Heading } from '@tiptap/extension-heading'
import { Paragraph } from '@tiptap/extension-paragraph'
import { Text } from '@tiptap/extension-text'
import { Document } from '@tiptap/extension-document'
import { Bold } from '@tiptap/extension-bold'
import { Italic } from '@tiptap/extension-italic'
import { Strike } from '@tiptap/extension-strike'
import { Code } from '@tiptap/extension-code'
import { marked } from 'marked'
import TurndownService from 'turndown'

class TipTapEditor {
    constructor(selector, content = '') {
        this.element = document.querySelector(selector)
        this.editor = null
        this.content = content
        this.turndown = new TurndownService({
            headingStyle: 'atx',
            codeBlockStyle: 'fenced',
            emDelimiter: '*'
        })
        this.init()
    }

    init() {
        this.editor = new Editor({
            element: this.element,
            extensions: [
                StarterKit,
                Image,
                Link.configure({
                    openOnClick: false,
                    HTMLAttributes: {
                        class: 'editor-link'
                    }
                }),
                CodeBlockLowlight.configure({
                    lowlight,
                }),
                TaskList,
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
                Highlight,
                TextAlign.configure({
                    types: ['heading', 'paragraph'],
                }),
                Color,
                TextStyle,
                Underline,
                Subscript,
                Superscript,
                HorizontalRule,
                Blockquote,
                BulletList,
                ListItem,
                OrderedList,
                Heading,
                Paragraph,
                Text,
                Document,
                Bold,
                Italic,
                Strike,
                Code,
            ],
            content: this.content ? marked(this.content) : '',
            onUpdate: ({ editor }) => {
                this.onContentUpdate(editor.getHTML())
            },
            editorProps: {
                attributes: {
                    class: 'prose prose-sm sm:prose lg:prose-lg xl:prose-2xl mx-auto focus:outline-none',
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

    setContent(content) {
        this.editor.commands.setContent(marked(content))
    }

    destroy() {
        this.editor.destroy()
    }
}

// Экспортируем класс для использования
window.TipTapEditor = TipTapEditor 