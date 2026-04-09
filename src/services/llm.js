const deepSeekApiKey = import.meta.env.VITE_DEEPSEEK_API_KEY || ''
const deepSeekModel = import.meta.env.VITE_DEEPSEEK_MODEL || 'deepseek-chat'
const deepSeekBaseUrl =
  (import.meta.env.VITE_DEEPSEEK_BASE_URL || 'https://api.deepseek.com').replace(/\/$/, '')

function parseDeepSeekStreamChunk(rawChunk) {
  const payload = rawChunk
    .split('\n')
    .find((line) => line.startsWith('data: '))
    ?.slice(6)

  if (!payload || payload === '[DONE]') {
    return ''
  }

  const parsed = JSON.parse(payload)
  return parsed.choices?.[0]?.delta?.content || ''
}

export async function streamChatCompletion({ systemPrompt, userPrompt, onChunk }) {
  if (!deepSeekApiKey) {
    throw new Error('VITE_DEEPSEEK_API_KEY 未配置，前端无法直接请求 DeepSeek。')
  }

  const response = await fetch(`${deepSeekBaseUrl}/chat/completions`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${deepSeekApiKey}`,
    },
    body: JSON.stringify({
      model: deepSeekModel,
      stream: true,
      messages: [
        { role: 'system', content: systemPrompt || 'You are a helpful assistant.' },
        { role: 'user', content: userPrompt || '' },
      ],
    }),
  })

  if (!response.ok || !response.body) {
    const text = await response.text()
    throw new Error(text || `LLM request failed with ${response.status}`)
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder('utf-8')
  let fullText = ''
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })
    const segments = buffer.split('\n\n')
    buffer = segments.pop() || ''

    for (const segment of segments) {
      const delta = parseDeepSeekStreamChunk(segment)
      if (!delta) continue
      fullText += delta
      onChunk?.(delta, fullText)
    }
  }

  return fullText
}
