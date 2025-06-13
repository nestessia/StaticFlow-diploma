// Препроцессор для markdown-текста (до markdown)
export function preprocessMarkdownText(md) {
  // Блочные формулы: $\n...\n$
  md = md.replace(/\$\s*\n([\s\S]+?)\n\$/g, (match, formula) => {
    return `<div class=\"math-block\">${formula.trim()}</div>`;
  });
  return md;
}

// Препроцессор для HTML после markdown
export function preprocessMarkdownHtml(html) {
  // Inline math: $...$ (не содержит переводов строки)
  html = html.replace(/\$([^$\n]+)\$/g, (match, formula) => {
    return `<span class=\"math-inline\">${formula}</span>`;
  });

  // Block math: <p> ... $ ... $ ... </p> (гибко к пробелам и переносам строк)
  html = html.replace(/<p>[\s\n]*\$([\s\S]+?)\$[\s\n]*<\/p>/g, (match, formula) => {
    return `<div class=\"math-block\">${formula.trim()}</div>`;
  });

  // Mermaid blocks: ```mermaid ... ```
  html = html.replace(/<pre><code class=\"language-mermaid\">([\s\S]+?)<\/code><\/pre>/g, (match, code) => {
    return `<div class=\"mermaid-block\">${code.trim()}</div>`;
  });

  console.log('HTML после препроцессора:', html);
  return html;
} 