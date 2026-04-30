export function createId(prefix = '') {
  const randomUuid = globalThis.crypto?.randomUUID?.bind(globalThis.crypto)
  const id = randomUuid
    ? randomUuid()
    : `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 10)}`

  return prefix ? `${prefix}-${id}` : id
}
