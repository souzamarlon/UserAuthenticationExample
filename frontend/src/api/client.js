/**
 * Secure API client: credentials (cookies) sent automatically; never attach tokens manually.
 * CSRF token sent in header for cookie-based auth; all requests over HTTPS in production.
 */

const getCsrfToken = () => {
  const name = 'csrftoken'
  const cookies = document.cookie.split(';')
  for (let c of cookies) {
    c = c.trim()
    if (c.startsWith(name + '=')) return c.slice(name.length + 1)
  }
  return null
}

const baseUrl = '/api'

export async function apiRequest(path, options = {}) {
  const url = path.startsWith('http') ? path : `${baseUrl}${path}`
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  }
  const csrf = getCsrfToken()
  if (csrf) headers['X-CSRFToken'] = csrf
  const res = await fetch(url, {
    ...options,
    credentials: 'include',
    headers,
  })
  const data = await res.json().catch(() => ({}))
  if (!res.ok) throw { status: res.status, ...data }
  return data
}

export async function ensureCsrfCookie() {
  await fetch(`${baseUrl}/auth/csrf/`, { method: 'GET', credentials: 'include' })
}

export const authApi = {
  login: (username, password) =>
    apiRequest('/auth/login/', { method: 'POST', body: JSON.stringify({ username, password }) }),
  logout: () => apiRequest('/auth/logout/', { method: 'POST' }),
  refresh: () => apiRequest('/auth/refresh/', { method: 'POST', body: JSON.stringify({}) }),
  me: () => apiRequest('/auth/me/'),
}
