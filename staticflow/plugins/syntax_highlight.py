import re
import logging
import html
from typing import Dict, Any, Optional
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, TextLexer, guess_lexer
from .base import Plugin

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SyntaxHighlight")


class SyntaxHighlightPlugin(Plugin):
    """Plugin for syntax highlighting code blocks in content."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        linenums = self.config.get('linenums', False)
        
        logger.info("Initializing SyntaxHighlightPlugin")
        
        # Create formatter with explicit settings for tabulation
        self.formatter = HtmlFormatter(
            style=self.config.get('style', 'monokai'),
            cssclass=self.config.get('css_class', 'highlight'),
            linenos=linenums,
            wrapcode=True,
            noclasses=False,
            tabsize=4,
            # Critical settings for preserving tabs and newlines
            prestyles="white-space: pre !important; tab-size: 4 !important;",
            nobackground=True,
            tabreplace='',  # Preserve tabs instead of converting to spaces
        )
        
    def _detect_language_from_code(self, code):
        """Detect language from code content."""
        # Detect Python by keywords
        if (re.search(r'\bdef\s+\w+\s*\(', code) or 
                re.search(r'\bclass\s+\w+\s*\(', code) or 
                re.search(r'\bimport\s+\w+', code) or
                re.search(r'\bprint\s*\(', code)):
            logger.info("Detected Python from code content")
            return "python"
        
        # Try to guess language automatically with Pygments
        try:
            lexer = guess_lexer(code)
            lang = lexer.aliases[0]
            logger.info(f"Pygments detected language: {lang}")
            return lang
        except Exception:
            logger.info("Failed to detect language, using text")
            return "text"
    
    def _decode_entities(self, content):
        """Decode HTML entities to normal characters."""
        return html.unescape(content)
    
    def _process_code_with_linebreaks(self, code, lexer):
        """Process code with explicit line breaks to preserve formatting."""
        lines = code.splitlines()
        html_parts = []
        
        for line in lines:
            # Process each line individually to preserve whitespace
            if line.strip() == "":
                # For empty lines, add a non-breaking space to force line height
                html_parts.append('<span class="line">&nbsp;</span><br>')
            else:
                # Highlight the line and add an explicit line break
                highlighted = highlight(line, lexer, self.formatter)
                
                # Extract just the code part without the container divs
                code_part = re.search(r'<div class="highlight"><pre>(.*?)</pre></div>', 
                                     highlighted, re.DOTALL)
                
                if code_part:
                    content = code_part.group(1)
                    html_parts.append(f'<span class="line">{content}</span><br>')
                else:
                    html_parts.append(f'<span class="line">{highlighted}</span><br>')
        
        # Combine all lines into a single HTML output
        return f'<div class="highlight"><pre>{"".join(html_parts)}</pre></div>'
    
    def process_content(self, content: str) -> str:
        """Process content and highlight code blocks."""
        if not content or len(content) < 10:
            return content
        
        logger.info("Starting syntax highlighting processing")
        
        # Function for highlighting code with tab/newline preservation
        def highlight_block(code, lang):
            try:
                # Decode HTML entities properly
                code = self._decode_entities(code)
                
                # Check if code has tabs
                has_tabs = '\t' in code
                
                try:
                    # Try to get lexer by language
                    lexer = get_lexer_by_name(lang)
                except ValueError:
                    # Try to detect language automatically
                    detected_lang = self._detect_language_from_code(code)
                    lang = detected_lang
                    try:
                        lexer = get_lexer_by_name(lang)
                    except ValueError:
                        lexer = TextLexer()
                
                # Process code with explicit line breaks
                html_code = self._process_code_with_linebreaks(code, lexer)
                
                # Add has-tabs class if needed
                if has_tabs:
                    html_code = html_code.replace(
                        'class="highlight"',
                        'class="highlight has-tabs"'
                    )
                
                # Create code block with language tag
                return f'''
                <div class="code-block language-{lang}">
                    <div class="language-tag">{lang}</div>
                    {html_code}
                </div>
                '''
            except Exception as e:
                logger.error(f"Error highlighting code: {e}")
                # Fallback to simple HTML with line breaks
                escaped = html.escape(code)
                lines = escaped.split('\n')
                html_lines = [f'{line}<br>' for line in lines]
                return f'<pre><code>{"".join(html_lines)}</code></pre>'
        
        # Process markdown code blocks: ```lang ...code... ```
        def process_md_block(match):
            lang = match.group(1).strip() if match.group(1) else 'text'
            code = match.group(2)
            logger.info(f"Processing markdown code block: {lang}")
            return highlight_block(code, lang)
        
        # Find all markdown code blocks
        md_pattern = re.compile(
            r'```\s*([a-zA-Z0-9_+-]+)?\s*\n((?:(?!```).|\n)+?)\s*```',
            re.MULTILINE
        )
        content = md_pattern.sub(process_md_block, content)
        
        # Process HTML code blocks: <pre><code>...</code></pre>
        def process_html_block(match):
            full_match = match.group(0)
            code = match.group(1)
            
            # Look for language in class attribute
            lang_match = re.search(
                r'class=["\'](.*?language-(\w+))["\']', full_match
            )
            
            if lang_match:
                lang = lang_match.group(2)
            else:
                # Detect language by content
                lang = self._detect_language_from_code(code)
            
            logger.info(f"Processing HTML code block: {lang}")
            return highlight_block(code, lang)
        
        # Find HTML code blocks
        html_pattern = re.compile(
            r'<pre>\s*<code.*?>(.*?)</code>\s*</pre>',
            re.DOTALL
        )
        content = html_pattern.sub(process_html_block, content)
        
        # Process inline code: `code`
        content = re.sub(
            r'`([^`\n]+)`',
            lambda m: f'<code class="inline-code">'
                      f'{html.escape(m.group(1))}</code>',
            content
        )
        
        return content
    
    def get_head_content(self) -> str:
        """Get content to be inserted in the head section."""
        # Basic Pygments styles
        base_styles = self.formatter.get_style_defs()
        
        # Add custom styles with proper tab and whitespace handling
        additional_styles = """
        /* Custom monospace font */
        @font-face {
            font-family: 'CodeFont';
            src: local('Consolas'), local('Liberation Mono'), 
                 local('Menlo'), local('Monaco'), local('Courier New'), 
                 monospace;
            font-display: swap;
        }

        /* Code block styling */
        .code-block {
            margin: 1.5rem 0;
            position: relative;
            border-radius: 0.5rem;
            overflow: hidden;
            background: #272822;
            color: #f8f8f2;
        }
        
        /* Language tag */
        .language-tag {
            position: absolute;
            top: 0;
            right: 0;
            padding: 3px 10px;
            font-size: 0.75rem;
            font-family: sans-serif;
            color: white;
            background: #444;
            border-radius: 0 0.3rem 0 0.3rem;
            z-index: 5;
        }
        
        /* Language-specific colors */
        .language-python .language-tag { background: #306998; }
        .language-js .language-tag, 
        .language-javascript .language-tag { 
            background: #f0db4f; 
            color: black; 
        }
        .language-html .language-tag { background: #e34c26; }
        .language-css .language-tag { background: #264de4; }
        
        /* Highlight block styles - CRITICAL for proper code display */
        .highlight {
            background: transparent !important;
            color: #f8f8f2;
            padding: 1.25rem;
            margin: 0;
            overflow-x: auto;
            tab-size: 4 !important;
            -moz-tab-size: 4 !important;
            -o-tab-size: 4 !important;
            -webkit-tab-size: 4 !important;
        }
        
        /* ESSENTIAL: Proper whitespace and tab preservation */
        .highlight pre, 
        .highlight code,
        .has-tabs pre, 
        .has-tabs code,
        .code-block pre,
        .code-block code {
            font-family: 'CodeFont', monospace !important;
            white-space: pre !important;
            tab-size: 4 !important;
            -moz-tab-size: 4 !important;
            -o-tab-size: 4 !important;
            -webkit-tab-size: 4 !important;
            background: transparent !important;
            word-wrap: normal !important;
            overflow-wrap: normal !important;
            overflow-x: auto !important;
            display: block !important;
            line-height: 1.5 !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        
        /* Fix spacing in highlight spans */
        .highlight .lineno,
        .highlight .line,
        .highlight span {
            white-space: pre !important;
            display: inline !important;
            line-height: inherit !important;
        }
        
        /* Ensure line breaks appear properly */
        .highlight br {
            display: block !important;
            content: "" !important;
            margin-top: 0 !important;
            line-height: inherit !important;
        }
        
        /* Fix for extra space bug */
        .highlight div {
            margin: 0 !important;
            padding: 0 !important;
            line-height: inherit !important;
        }
        
        /* Make all code block backgrounds transparent */
        .code-block *,
        .highlight * {
            background-color: transparent !important;
        }
        
        /* Inline code */
        code.inline-code {
            background-color: #f5f5f5;
            padding: 0.2em 0.4em;
            border-radius: 3px;
            font-family: 'CodeFont', monospace;
            font-size: 90%;
            display: inline;
            white-space: normal;
        }
        
        /* Python syntax highlighting */
        .highlight .k { color: #66d9ef; } /* Keyword */
        .highlight .kc { color: #66d9ef; } /* Keyword.Constant */
        .highlight .kd { color: #66d9ef; } /* Keyword.Declaration */
        .highlight .kn { color: #f92672; } /* Keyword.Namespace */
        .highlight .kp { color: #66d9ef; } /* Keyword.Pseudo */
        .highlight .kr { color: #66d9ef; } /* Keyword.Reserved */
        .highlight .kt { color: #66d9ef; } /* Keyword.Type */
        
        .highlight .n { color: #f8f8f2; } /* Name */
        .highlight .na { color: #a6e22e; } /* Name.Attribute */
        .highlight .nb { color: #a6e22e; } /* Name.Builtin */
        .highlight .nc { color: #a6e22e; } /* Name.Class */
        .highlight .no { color: #66d9ef; } /* Name.Constant */
        .highlight .nd { color: #a6e22e; } /* Name.Decorator */
        .highlight .ni { color: #f8f8f2; } /* Name.Entity */
        .highlight .ne { color: #a6e22e; } /* Name.Exception */
        .highlight .nf { color: #a6e22e; } /* Name.Function */
        .highlight .nl { color: #f8f8f2; } /* Name.Label */
        .highlight .nn { color: #f8f8f2; } /* Name.Namespace */
        .highlight .nx { color: #a6e22e; } /* Name.Other */
        .highlight .py { color: #f8f8f2; } /* Name.Property */
        .highlight .nt { color: #f92672; } /* Name.Tag */
        .highlight .nv { color: #f8f8f2; } /* Name.Variable */
        
        .highlight .o { color: #f92672; } /* Operator */
        .highlight .ow { color: #f92672; } /* Operator.Word */
        
        .highlight .p { color: #f8f8f2; } /* Punctuation */
        
        .highlight .c { color: #75715e; } /* Comment */
        .highlight .cm { color: #75715e; } /* Comment.Multiline */
        .highlight .cp { color: #75715e; } /* Comment.Preproc */
        .highlight .c1 { color: #75715e; } /* Comment.Single */
        .highlight .cs { color: #75715e; } /* Comment.Special */
        
        .highlight .s { color: #e6db74; } /* String */
        .highlight .sb { color: #e6db74; } /* String.Backtick */
        .highlight .sc { color: #e6db74; } /* String.Char */
        .highlight .sd { color: #e6db74; } /* String.Doc */
        .highlight .s2 { color: #e6db74; } /* String.Double */
        .highlight .se { color: #ae81ff; } /* String.Escape */
        .highlight .sh { color: #e6db74; } /* String.Heredoc */
        .highlight .si { color: #e6db74; } /* String.Interpol */
        .highlight .sx { color: #e6db74; } /* String.Other */
        .highlight .sr { color: #e6db74; } /* String.Regex */
        .highlight .s1 { color: #e6db74; } /* String.Single */
        .highlight .ss { color: #e6db74; } /* String.Symbol */
        
        .highlight .m { color: #ae81ff; } /* Number */
        .highlight .mb { color: #ae81ff; } /* Number.Bin */
        .highlight .mf { color: #ae81ff; } /* Number.Float */
        .highlight .mh { color: #ae81ff; } /* Number.Hex */
        .highlight .mi { color: #ae81ff; } /* Number.Integer */
        .highlight .mo { color: #ae81ff; } /* Number.Oct */
        """
        
        return f'<style>{base_styles}{additional_styles}</style>'