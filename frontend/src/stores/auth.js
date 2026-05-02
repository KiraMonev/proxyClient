import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../api/client'

export const useAuthStore = defineStore('auth', () => {
  const accessToken = ref(localStorage.getItem('access_token') || null)
  const refreshToken = ref(localStorage.getItem('refresh_token') || null)

  const isAuthenticated = computed(() => !!accessToken.value)

  function setTokens(access, refresh) {
    accessToken.value = access
    refreshToken.value = refresh
    localStorage.setItem('access_token', access)
    localStorage.setItem('refresh_token', refresh)
  }

  function clearTokens() {
    accessToken.value = null
    refreshToken.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  async function login(email, password) {
    const response = await api.post('/api/auth/login', { email, password })
    setTokens(response.data.access_token, response.data.refresh_token)
    return response.data
  }

  async function register(email, password, passwordConfirm) {
    const response = await api.post('/api/auth/register', {
      email,
      password,
      password_confirm: passwordConfirm,
    })
    return response.data
  }

  async function refreshAccessToken() {
    try {
      const response = await api.post('/api/auth/refresh', {
        refresh_token: refreshToken.value,
      })
      setTokens(response.data.access_token, response.data.refresh_token)
      return response.data.access_token
    } catch {
      clearTokens()
      throw new Error('Session expired')
    }
  }

  function logout() {
    clearTokens()
  }

  return {
    accessToken,
    refreshToken,
    isAuthenticated,
    setTokens,
    clearTokens,
    login,
    register,
    refreshAccessToken,
    logout,
  }
})
