import { computed, ref } from 'vue'
import { api, getToken, removeToken } from '../services/api'

const tokenRef = ref(getToken())

export function useAuth() {
  const isAuthed = computed(() => !!tokenRef.value)

  async function login(username, password) {
    const data = await api.login(username, password)
    tokenRef.value = getToken()
    return data
  }

  function logout() {
    removeToken()
    tokenRef.value = null
  }

  return { isAuthed, login, logout }
}
