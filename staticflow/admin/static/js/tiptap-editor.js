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
import { CodeBlock } from './tiptap-code-block.js'
import {
  HeadingDnd,
  BlockquoteDnd,
  BulletListDnd,
  OrderedListDnd,
  TaskListDnd,
  ImageDnd,
  AudioBlockDnd
} from './tiptap-dnd-blocks.js'
import javascript from 'highlight.js/lib/languages/javascript'
import python from 'highlight.js/lib/languages/python'
import { preprocessMarkdownHtml } from './markdown-preprocessor.js'
import { DropIndicator } from './tiptap-drop-indicator.js'
import { createColorBubbleMenu } from './tiptap-bubblemenu.js'
import { BubbleMenu } from '@tiptap/extension-bubble-menu'
import { ImageBlock } from './tiptap-image.js'
import { VideoBlock } from './tiptap-video.js'

lowlight.registerLanguage('js', javascript)
lowlight.registerLanguage('javascript', javascript)
lowlight.registerLanguage('python', python)

// Функция для замены !AUDIO(...) и !VIDEO(...) на HTML-теги
function preprocessMediaBlocks(html) {
  // AUDIO
  html = html.replace(/!AUDIO\((.*?)\)/g, (match, src) => {
    return `<audio controls src="${src.trim()}"></audio>`;
  });
  // VIDEO
  html = html.replace(/!VIDEO\((.*?)\)/g, (match, src) => {
    return `<video controls src="${src.trim()}"></video>`;
  });
  return html;
}

// === Кастомный contextmenu тулбар для ссылок ===
function createContextLinkToolbar(editor) {
  let toolbar = document.createElement('div');
  toolbar.className = 'context-link-toolbar';
  toolbar.style.position = 'absolute';
  toolbar.style.display = 'none';
  toolbar.style.zIndex = 1000;
  toolbar.style.background = '#fff';
  toolbar.style.border = '1px solid #e5e7eb';
  toolbar.style.borderRadius = '8px';
  toolbar.style.boxShadow = '0 4px 16px rgba(59,130,246,0.10)';
  toolbar.style.padding = '8px 12px';
  toolbar.style.minWidth = '120px';
  toolbar.style.fontSize = '15px';
  toolbar.style.gap = '8px';
  toolbar.style.display = 'flex';
  toolbar.style.alignItems = 'center';

  // Кнопка "Сделать ссылкой"
  const linkBtn = document.createElement('button');
  linkBtn.textContent = 'Сделать ссылкой';
  linkBtn.style.padding = '4px 10px';
  linkBtn.style.background = '#3b82f6';
  linkBtn.style.color = '#fff';
  linkBtn.style.border = 'none';
  linkBtn.style.borderRadius = '5px';
  linkBtn.style.cursor = 'pointer';
  toolbar.appendChild(linkBtn);

  // Инпут для URL (скрыт по умолчанию)
  const urlInput = document.createElement('input');
  urlInput.type = 'text';
  urlInput.placeholder = 'Вставьте ссылку...';
  urlInput.style.display = 'none';
  urlInput.style.marginLeft = '8px';
  urlInput.style.padding = '4px 8px';
  urlInput.style.border = '1px solid #e5e7eb';
  urlInput.style.borderRadius = '5px';
  urlInput.style.width = '180px';
  toolbar.appendChild(urlInput);

  // Кнопка подтверждения (Enter)
  const confirmBtn = document.createElement('button');
  confirmBtn.textContent = 'OK';
  confirmBtn.style.display = 'none';
  confirmBtn.style.marginLeft = '6px';
  confirmBtn.style.padding = '4px 10px';
  confirmBtn.style.background = '#22c55e';
  confirmBtn.style.color = '#fff';
  confirmBtn.style.border = 'none';
  confirmBtn.style.borderRadius = '5px';
  confirmBtn.style.cursor = 'pointer';
  toolbar.appendChild(confirmBtn);

  document.body.appendChild(toolbar);

  // Показать тулбар рядом с выделением
  function showToolbar() {
    const selection = window.getSelection();
    if (!selection || selection.rangeCount === 0) return;
    const range = selection.getRangeAt(0);
    const rect = range.getBoundingClientRect();
    // Позиционируем тулбар относительно окна
    toolbar.style.left = (rect.left + window.scrollX) + 'px';
    toolbar.style.top = (rect.bottom + window.scrollY + 4) + 'px'; // +4px чуть ниже выделения
    toolbar.style.display = 'flex';
    urlInput.style.display = 'none';
    confirmBtn.style.display = 'none';
    linkBtn.style.display = 'inline-block';
  }

  // Скрыть тулбар
  function hideToolbar() {
    toolbar.style.display = 'none';
    urlInput.value = '';
  }

  // Клик вне тулбара — скрыть
  document.addEventListener('mousedown', (e) => {
    if (!toolbar.contains(e.target)) hideToolbar();
  });

  // Клик по "Сделать ссылкой"
  linkBtn.onclick = () => {
    linkBtn.style.display = 'none';
    urlInput.style.display = 'inline-block';
    confirmBtn.style.display = 'inline-block';
    urlInput.focus();
  };

  // Подтверждение ссылки
  function applyLink() {
    const url = urlInput.value.trim();
    if (url) {
      editor.chain().focus().extendMarkRange('link').setLink({ href: url }).run();
    }
    hideToolbar();
  }
  confirmBtn.onclick = applyLink;
  urlInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') applyLink();
    if (e.key === 'Escape') hideToolbar();
  });

  return { showToolbar, hideToolbar };
}

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
            htmlContent = preprocessMediaBlocks(htmlContent);
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
                CodeBlock.configure({ lowlight }),
                BulletListDnd,
                OrderedListDnd,
                TaskListDnd,
                ImageDnd,
                VideoBlock,
                AudioBlockDnd,
                ImageBlock,
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

        // === Кастомный contextmenu тулбар ===
        const contextToolbar = createContextLinkToolbar(this.editor);
        const tiptapContent = document.querySelector('.tiptap-content');
        if (tiptapContent) {
            tiptapContent.addEventListener('contextmenu', (e) => {
                // Проверяем, есть ли выделение и оно не пустое
                const selection = window.getSelection();
                if (!selection || selection.isCollapsed) return;
                // Проверяем, что выделение внутри нужного блока
                const { state } = this.editor;
                const { from, to } = state.selection;
                let allowed = false;
                state.doc.nodesBetween(from, to, (node, pos, parent) => {
                    if ([
                        'heading',
                        'paragraph',
                        'blockquote',
                        'tableCell',
                        'listItem'
                    ].includes(node.type.name)) {
                        allowed = true;
                    }
                });
                if (!allowed) return;
                e.preventDefault();
                contextToolbar.showToolbar(); // Больше не передаём координаты мыши
            });
        }
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
        const doc = this.editor.getJSON();
        let md = '';
        
        // Рекурсивная функция сериализации
        function serializeNode(node) {
            if (!node) return '';
            // Ссылки: если это текст с mark link
            if (node.type === 'text' && node.marks && node.marks.length) {
                const linkMark = node.marks.find(m => m.type === 'link' && m.attrs && m.attrs.href);
                if (linkMark) {
                    return `[${node.text}](${linkMark.attrs.href})`;
                }
            }
            // Обычный текст
            if (node.type === 'text') {
                return node.text || '';
            }
            // Специальные блоки
            if (node.type === 'mermaidBlock') {
                return `\n\n\`\`\`mermaid\n${node.content && node.content.length ? node.content.map(n => n.text || '').join('') : ''}\n\`\`\`\n\n`;
            }
            if (node.type === 'codeBlock') {
                const language = node.attrs?.language || '';
                return `\n\n\`\`\`${language}\n${node.content && node.content.length ? node.content.map(n => n.text || '').join('') : ''}\n\`\`\`\n\n`;
            }
            if (node.type === 'mathBlock') {
                return `\n\n$$\n${node.content && node.content.length ? node.content.map(n => n.text || '').join('') : ''}\n$$\n\n`;
            }
            if (node.type === 'mathInline') {
                return `$${node.content && node.content.length ? node.content.map(n => n.text || '').join('') : ''}$`;
            }
            if (node.type === 'imageBlock') {
                const src = node.attrs?.src || '';
                const alt = node.attrs?.alt || '';
                const title = node.attrs?.title || '';
                return `\n\n![${alt}](${src}${title ? ` \"${title}\"` : ''})\n\n`;
            }
            if (node.type === 'videoBlock') {
                const src = node.attrs?.src || '';
                const title = node.attrs?.title || '';
                return `\n\n!VIDEO(${src})\n\n`;
            }
            if (node.type === 'audioBlock') {
                const src = node.attrs?.src || '';
                return `\n\n!AUDIO(${src})\n\n`;
            }
            
            // Обработка заголовков
            if (node.type === 'heading') {
                const level = node.attrs?.level || 1;
                const content = node.content && node.content.length ? node.content.map(serializeNode).join('') : '';
                return `\n${'#'.repeat(level)} ${content}\n\n`;
            }
            
            // Обработка параграфов
            if (node.type === 'paragraph') {
                const content = node.content && node.content.length ? node.content.map(serializeNode).join('') : '';
                return `\n${content}\n\n`;
            }
            
            // Обработка таблиц
            if (node.type === 'table') {
                let markdown = '\n\n';
                const rows = node.content || [];
                
                // Обработка заголовков
                if (rows.length > 0) {
                    const headerRow = rows[0];
                    const headers = headerRow.content || [];
                    markdown += '| ' + headers.map(header => {
                        const cell = header.content?.[0]?.content?.[0]?.text || '';
                        return cell.trim();
                    }).join(' | ') + ' |\n';
                    
                    // Добавляем разделитель
                    markdown += '| ' + headers.map(() => '---').join(' | ') + ' |\n';
                    
                    // Обработка остальных строк
                    for (let i = 1; i < rows.length; i++) {
                        const cells = rows[i].content || [];
                        markdown += '| ' + cells.map(cell => {
                            const text = cell.content?.[0]?.content?.[0]?.text || '';
                            return text.trim();
                        }).join(' | ') + ' |\n';
                    }
                }
                
                return markdown + '\n';
            }
            
            // Для всех остальных узлов с дочерними элементами
            if (node.content && node.content.length) {
                return node.content.map(serializeNode).join('');
            }
            // Если ничего не подошло — пусто
            return '';
        }

        if (doc.content && Array.isArray(doc.content)) {
            for (const node of doc.content) {
                const customMd = serializeNode(node);
                if (customMd !== null && customMd !== undefined && customMd !== '') {
                    md += customMd;
                } else {
                    // Создаем временный элемент для текущего блока
                    const tempDiv = document.createElement('div');
                    const schema = this.editor.schema;
                    const ProseMirrorNode = schema.nodeFromJSON(node);
                    
                    // Сериализуем только текущий блок
                    const fragment = this.editor.view.someProp('domSerializer')
                        ? this.editor.view.someProp('domSerializer').serializeFragment(ProseMirrorNode.content)
                        : null;
                        
                    if (fragment) {
                        tempDiv.appendChild(fragment);
                        const turndownService = new TurndownService({
                            headingStyle: 'atx',
                            codeBlockStyle: 'fenced',
                            emDelimiter: '*',
                            bulletListMarker: '-',
                            hr: '---',
                            strongDelimiter: '**',
                            linkStyle: 'inlined'
                        });
                        
                        // Добавляем правила для сохранения форматирования
                        turndownService.addRule('preserveNewlines', {
                            filter: ['br'],
                            replacement: () => '\n'
                        });

                        // Добавляем правило для таблиц
                        turndownService.addRule('tables', {
                            filter: ['table'],
                            replacement: function (content, node) {
                                const table = node;
                                const rows = Array.from(table.querySelectorAll('tr'));
                                let markdown = '\n\n';
                                
                                // Обработка заголовков
                                const headers = Array.from(rows[0].querySelectorAll('th, td'));
                                markdown += '| ' + headers.map(header => header.textContent.trim()).join(' | ') + ' |\n';
                                
                                // Добавляем разделитель
                                markdown += '| ' + headers.map(() => '---').join(' | ') + ' |\n';
                                
                                // Обработка остальных строк
                                for (let i = 1; i < rows.length; i++) {
                                    const cells = Array.from(rows[i].querySelectorAll('td'));
                                    markdown += '| ' + cells.map(cell => cell.textContent.trim()).join(' | ') + ' |\n';
                                }
                                
                                return markdown + '\n';
                            }
                        });
                        
                        md += turndownService.turndown(tempDiv.innerHTML);
                    }
                }
            }
        }
        
        return md.trim();
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