const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL || '/api').replace(/\/$/, '')

export function getApiBaseUrl() {
  return apiBaseUrl
}

export function getStoredToken() {
  try {
    const session = JSON.parse(localStorage.getItem('sb_auth_session') || '{}')
    return session?.token || ''
  } catch {
    return ''
  }
}

export async function apiRequest(path, options = {}) {
  const token = options.token === undefined ? getStoredToken() : options.token
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(options.headers || {}),
  }

  const response = await fetch(`${apiBaseUrl}${path}`, {
    ...options,
    headers,
  })

  const data = await response.json().catch(() => ({}))
  if (!response.ok) {
    throw new Error(data.detail || data.message || `Request failed with ${response.status}`)
  }
  return data
}

export function createDebouncedWorkspaceSaver(kind, getData, delay = 700) {
  let timer = null
  let pending = Promise.resolve()

  return function scheduleSave() {
    window.clearTimeout(timer)
    timer = window.setTimeout(() => {
      const data = getData()
      pending = pending
        .catch(() => null)
        .then(() =>
          apiRequest(`/workspace/${kind}`, {
            method: 'PUT',
            body: JSON.stringify({ data }),
          }),
        )
        .catch((error) => {
          console.error(`Failed to save workspace document "${kind}"`, error)
        })
    }, delay)
  }
}
