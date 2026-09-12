// Environment variable se Backend URL uthayega, local dev ke liye fallback 127.0.0.1:8000 rahega
const API_BASE = import.meta.env.VITE_BACKEND_URL || 'http://127.0.0.1:8000'

async function request<T>(path: string, method = 'GET', body?: unknown): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    method,
    headers: { 'Content-Type': 'application/json' },
    body: body ? JSON.stringify(body) : undefined,
  })

  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`)
  }

  return response.json() as Promise<T>
}

export const api = {
  createSimulation: () => request<any>('/api/simulation/create', 'POST'),
  fullDemo: () => request<any>('/api/simulation/full-demo', 'POST'),
  discover: (id: string) => request<any>(`/api/simulation/${id}/discover`, 'POST'),
  injectFailure: (id: string, scenario: string) => request<any>(`/api/simulation/${id}/failure?scenario=${encodeURIComponent(scenario)}`, 'POST'),
  recover: (id: string) => request<any>(`/api/simulation/${id}/recover`, 'POST'),
  chaos: (id: string) => request<any>(`/api/simulation/${id}/chaos`, 'POST'),
  verify: (id: string) => request<any>(`/api/simulation/${id}/verify`, 'POST'),
  getSimulation: (id: string) => request<any>(`/api/simulation/${id}`),
  getIncidents: () => request<any[]>('/api/incidents'),
  getRisks: () => request<any[]>('/api/risks'),
  getMemory: () => request<any[]>('/api/memory'),
  getMetrics: () => request<any>('/api/metrics'),
}
