import { computed } from 'vue'
import { defineStore } from 'pinia'
import { useStorage } from '@vueuse/core'

const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000').replace(/\/$/, '')

async function request(path, options = {}) {
  const response = await fetch(`${apiBaseUrl}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
  })

  const data = await response.json().catch(() => ({}))
  if (!response.ok) {
    throw new Error(data.detail || `Request failed with ${response.status}`)
  }
  return data
}

export const useAuthStore = defineStore('auth', () => {
  const session = useStorage('sb_auth_session', {
    loggedIn: false,
    username: '',
    token: '',
  })

  const isLoggedIn = computed(() => Boolean(session.value?.loggedIn && session.value?.token))
  const username = computed(() => session.value?.username || '')
  const authToken = computed(() => session.value?.token || '')

  async function login(usernameInput, passwordInput) {
    try {
      const data = await request('/auth/login', {
        method: 'POST',
        body: JSON.stringify({
          username: String(usernameInput || '').trim(),
          password: String(passwordInput || ''),
        }),
      })

      session.value = {
        loggedIn: true,
        username: data.username,
        token: data.token,
      }

      return { ok: true }
    } catch (error) {
      return {
        ok: false,
        message: error instanceof Error ? error.message : '登录失败',
      }
    }
  }

  async function restoreSession() {
    if (!session.value?.token) return false
    try {
      const data = await request('/auth/me', {
        headers: {
          Authorization: `Bearer ${session.value.token}`,
        },
      })
      session.value = {
        loggedIn: Boolean(data.logged_in),
        username: data.username || '',
        token: session.value.token,
      }
      return true
    } catch {
      session.value = {
        loggedIn: false,
        username: '',
        token: '',
      }
      return false
    }
  }

  async function logout() {
    const token = session.value?.token
    try {
      if (token) {
        await request('/auth/logout', {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${token}`,
          },
        })
      }
    } finally {
      session.value = {
        loggedIn: false,
        username: '',
        token: '',
      }
    }
  }

  return {
    session,
    isLoggedIn,
    username,
    authToken,
    login,
    logout,
    restoreSession,
  }
})
