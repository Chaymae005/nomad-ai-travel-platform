const API_URL = 'http://127.0.0.1:8000'

export function fetchAvecAuth(chemin, options = {}) {
  const token = localStorage.getItem('token')
  return fetch(`${API_URL}${chemin}`, {
    ...options,
    headers: {
      ...(options.body ? { 'Content-Type': 'application/json' } : {}),
      Authorization: `Bearer ${token}`,
      ...options.headers,
    },
  })
}

export { API_URL }