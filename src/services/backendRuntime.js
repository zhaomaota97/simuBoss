const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000').replace(/\/$/, '')

function parseEventBlock(block) {
  const lines = block.split('\n')
  let event = 'message'
  const dataLines = []

  for (const line of lines) {
    if (line.startsWith('event:')) {
      event = line.slice(6).trim()
    } else if (line.startsWith('data:')) {
      dataLines.push(line.slice(5).trim())
    }
  }

  if (!dataLines.length) return null
  const raw = dataLines.join('\n')
  return {
    event,
    payload: JSON.parse(raw),
  }
}

function handleParsedEvent(parsed, onEvent) {
  if (!parsed) return { completedResult: null, error: null }
  onEvent?.(parsed)
  if (parsed.event === 'completed') {
    return { completedResult: parsed.payload?.result || null, error: null }
  }
  if (parsed.event === 'error') {
    return { completedResult: null, error: parsed.payload?.message || 'Runtime stream failed' }
  }
  return { completedResult: null, error: null }
}

export async function executeRuntimeTask({
  token,
  task,
  managerId,
  managerName,
  approvedPlan,
  context = {},
  onEvent,
}) {
  const response = await fetch(`${apiBaseUrl}/runtime/tasks/execute`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({
      task,
      managerId,
      managerName,
      approvedPlan,
      context,
    }),
  })

  if (!response.ok || !response.body) {
    const text = await response.text().catch(() => '')
    throw new Error(text || `Runtime request failed with ${response.status}`)
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder('utf-8')
  let buffer = ''
  let completedResult = null

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })
    const segments = buffer.split('\n\n')
    buffer = segments.pop() || ''

    for (const segment of segments) {
      const parsed = parseEventBlock(segment)
      const { completedResult: parsedCompleted, error } = handleParsedEvent(parsed, onEvent)
      if (parsedCompleted) completedResult = parsedCompleted
      if (error) throw new Error(error)
    }
  }

  const finalParsed = parseEventBlock(buffer.trim())
  const { completedResult: parsedCompleted, error } = handleParsedEvent(finalParsed, onEvent)
  if (parsedCompleted) completedResult = parsedCompleted
  if (error) throw new Error(error)

  if (!completedResult) {
    throw new Error('Runtime stream ended without a completed result')
  }

  return completedResult
}
