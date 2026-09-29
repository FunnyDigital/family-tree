export function escapeHtml(value) {
  return String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
}

function safeUrl(url) {
  const trimmed = url.trim()
  if (/^(https?:|mailto:|\/)/i.test(trimmed)) return trimmed
  return '#'
}

function inline(text) {
  let out = escapeHtml(text)
  out = out.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
  out = out.replace(/(^|[^*])\*([^*\n]+)\*/g, '$1<em>$2</em>')
  out = out.replace(/_([^_\n]+)_/g, '<em>$1</em>')
  out = out.replace(
    /\[([^\]]+)\]\(([^)\s]+)\)/g,
    (_m, label, url) => `<a href="${safeUrl(url)}" target="_blank" rel="noopener noreferrer">${label}</a>`,
  )
  return out
}

export function formatStory(text) {
  if (!text) return ''
  const paragraphs = String(text).replace(/\r\n/g, '\n').split(/\n{2,}/)
  return paragraphs
    .map((block) => {
      const trimmed = block.trim()
      if (!trimmed) return ''
      return `<p>${inline(trimmed).replace(/\n/g, '<br />')}</p>`
    })
    .filter(Boolean)
    .join('')
}

export function initials(name) {
  if (!name) return '?'
  const parts = String(name).trim().split(/\s+/).filter(Boolean)
  if (!parts.length) return '?'
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase()
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase()
}

export function yearOf(value) {
  if (!value) return null
  const match = String(value).match(/\d{4}/)
  return match ? match[0] : null
}
