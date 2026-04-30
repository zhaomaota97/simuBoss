import { computed } from 'vue'
import { defineStore } from 'pinia'
import { useStorage } from '@vueuse/core'
import { apiRequest } from '../services/api'
import { clearWorkspaceLoadState, isWorkspaceLoaded, loadUserWorkspace } from '../services/workspace'

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
      const data = await apiRequest('/auth/login', {
        method: 'POST',
        token: '',
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
      await loadUserWorkspace({ force: true, token: data.token })

      return { ok: true }
    } catch (error) {
      return {
        ok: false,
        message: error instanceof Error ? error.message : '登录失败',
      }
    }
  }

  async function register(usernameInput, passwordInput) {
    try {
      const data = await apiRequest('/auth/register', {
        method: 'POST',
        token: '',
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
      await loadUserWorkspace({ force: true, token: data.token })

      return { ok: true }
    } catch (error) {
      return {
        ok: false,
        message: error instanceof Error ? error.message : '注册失败',
      }
    }
  }

  async function restoreSession() {
    if (!session.value?.token) return false
    try {
      const data = await apiRequest('/auth/me', {
        headers: {
          Authorization: `Bearer ${session.value.token}`,
        },
      })
      session.value = {
        loggedIn: Boolean(data.logged_in),
        username: data.username || '',
        token: session.value.token,
      }
      await loadUserWorkspace({ force: true, token: session.value.token })
      return true
    } catch {
      session.value = {
        loggedIn: false,
        username: '',
        token: '',
      }
      clearWorkspaceLoadState()
      return false
    }
  }

  async function ensureWorkspaceLoaded() {
    if (!session.value?.token || isWorkspaceLoaded()) return true
    try {
      await loadUserWorkspace({ token: session.value.token })
      return true
    } catch {
      session.value = {
        loggedIn: false,
        username: '',
        token: '',
      }
      clearWorkspaceLoadState()
      return false
    }
  }

  async function logout() {
    const token = session.value?.token
    try {
      if (token) {
        await apiRequest('/auth/logout', {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${token}`,
          },
        })
      }
    } catch (error) {
      console.warn('Logout request failed; clearing local session anyway.', error)
    } finally {
      session.value = {
        loggedIn: false,
        username: '',
        token: '',
      }
      clearWorkspaceLoadState()
    }
  }

  return {
    session,
    isLoggedIn,
    username,
    authToken,
    login,
    register,
    logout,
    restoreSession,
    ensureWorkspaceLoaded,
  }
})
