import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import { createId } from '../utils/id'

export const useMessageStore = defineStore('messages', () => {
  const messages = ref([])

  const visibleMessages = computed(() => messages.value)

  function remove(id) {
    messages.value = messages.value.filter((item) => item.id !== id)
  }

  function push({ title, message = '', type = 'info', duration = 3200, persistent = false }) {
    const id = createId('msg')
    messages.value.push({ id, title, message, type, persistent })
    if (!persistent) {
      window.setTimeout(() => remove(id), duration)
    }
    return id
  }

  function update(id, patch = {}) {
    messages.value = messages.value.map((item) =>
      item.id === id ? { ...item, ...patch } : item,
    )
  }

  function success(title, message = '', options = {}) {
    return push({ title, message, type: 'success', ...options })
  }

  function error(title, message = '', options = {}) {
    return push({ title, message, type: 'error', duration: 5200, ...options })
  }

  function info(title, message = '', options = {}) {
    return push({ title, message, type: 'info', ...options })
  }

  return {
    visibleMessages,
    push,
    update,
    remove,
    success,
    error,
    info,
  }
})
