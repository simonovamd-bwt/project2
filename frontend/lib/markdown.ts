/**
 * Minimal markdown -> HTML for the live document preview (issue #2).
 *
 * Deliberately tiny: the backend emits a fixed, trusted document template
 * (headings, bold, italics, paragraphs) — not arbitrary user markdown — so a
 * full parser would be overkill. Input is escaped first, so the only HTML that
 * reaches the DOM is the handful of tags produced here.
 */
function escapeHtml(text: string): string {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function inline(text: string): string {
  return escapeHtml(text)
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/_(.+?)_/g, "<em>$1</em>");
}

export function renderMarkdown(markdown: string): string {
  const lines = markdown.split("\n");
  const html: string[] = [];
  let paragraph: string[] = [];

  const flush = () => {
    if (paragraph.length) {
      html.push(`<p>${inline(paragraph.join(" "))}</p>`);
      paragraph = [];
    }
  };

  for (const line of lines) {
    const trimmed = line.trim();
    if (trimmed === "") {
      flush();
    } else if (trimmed.startsWith("## ")) {
      flush();
      html.push(`<h2>${inline(trimmed.slice(3))}</h2>`);
    } else if (trimmed.startsWith("# ")) {
      flush();
      html.push(`<h1>${inline(trimmed.slice(2))}</h1>`);
    } else {
      paragraph.push(trimmed);
    }
  }
  flush();
  return html.join("\n");
}
