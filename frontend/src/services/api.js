const API_BASE = '/api'

export function getToken() {
  return localStorage.getItem('access_token')
}

export function setToken(token) {
  localStorage.setItem('access_token', token)
}

export function removeToken() {
  localStorage.removeItem('access_token')
}

export function isAuthenticated() {
  return !!getToken()
}

function authHeaders(extra = {}) {
  const headers = { ...extra }
  const token = getToken()
  if (token) headers.Authorization = `Bearer ${token}`
  return headers
}

async function request(path, { method = 'GET', body = null, form = false } = {}) {
  const options = { method, headers: authHeaders() }
  if (body != null) {
    if (form) {
      options.body = body
    } else {
      options.headers['Content-Type'] = 'application/json'
      options.body = JSON.stringify(body)
    }
  }
  const res = await fetch(`${API_BASE}${path}`, options)
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || res.statusText || 'Request failed')
  }
  if (res.status === 204) return null
  return res.json()
}

function query(params = {}) {
  const search = new URLSearchParams()
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') search.append(key, value)
  })
  const qs = search.toString()
  return qs ? `?${qs}` : ''
}

export const api = {
  login: async (username, password) => {
    const formData = new URLSearchParams()
    formData.append('username', username)
    formData.append('password', password)
    const res = await fetch(`${API_BASE}/auth/token`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: formData,
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || 'Login failed')
    }
    const data = await res.json()
    setToken(data.access_token)
    return data
  },

  getSite: () => request('/site'),
  getStats: () => request('/stats'),
  getTree: () => request('/tree'),

  getPersons: (params = {}) => request(`/persons${query(params)}`),
  getPerson: (id) => request(`/persons/${id}`),
  createPerson: (data) => request('/persons', { method: 'POST', body: data }),
  updatePerson: (id, data) => request(`/persons/${id}`, { method: 'PUT', body: data }),
  deletePerson: (id) => request(`/persons/${id}`, { method: 'DELETE' }),

  getUnions: () => request('/unions'),
  createUnion: (data) => request('/unions', { method: 'POST', body: data }),
  updateUnion: (id, data) => request(`/unions/${id}`, { method: 'PUT', body: data }),
  deleteUnion: (id) => request(`/unions/${id}`, { method: 'DELETE' }),

  uploadPhoto: (personId, file, caption = '') => {
    const formData = new FormData()
    formData.append('file', file)
    if (caption) formData.append('caption', caption)
    return request(`/persons/${personId}/photos`, { method: 'POST', body: formData, form: true })
  },
  updatePhoto: (id, data) => request(`/photos/${id}`, { method: 'PUT', body: data }),
  setPrimaryPhoto: (id) => request(`/photos/${id}/primary`, { method: 'PUT' }),
  reorderPhotos: (personId, order) =>
    request(`/persons/${personId}/photos/reorder`, { method: 'PUT', body: { order } }),
  deletePhoto: (id) => request(`/photos/${id}`, { method: 'DELETE' }),

  createStory: (personId, data) =>
    request(`/persons/${personId}/stories`, { method: 'POST', body: data }),
  updateStory: (id, data) => request(`/stories/${id}`, { method: 'PUT', body: data }),
  deleteStory: (id) => request(`/stories/${id}`, { method: 'DELETE' }),
}
