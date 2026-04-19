import { useAuthStore } from '../store/authStore'

type RequestConfig = {
  label: string
  method: string
  path: string
  request: () => Promise<unknown>
}

export function useApiAction() {
  const addLog = useAuthStore((state) => state.addLog)
  const setResponse = useAuthStore((state) => state.setResponse)
  const ingestPayload = useAuthStore((state) => state.ingestPayload)

  async function execute<T = unknown>({ label, method, path, request }: RequestConfig) {
    try {
      const payload = (await request()) as T
      setResponse({
        title: label,
        method,
        path,
        status: 200,
        payload,
      })
      addLog({
        method,
        path,
        status: 200,
        summary: JSON.stringify(payload).slice(0, 140),
      })
      ingestPayload(path, payload)
      return payload
    } catch (error: unknown) {
      const status =
        typeof error === 'object' &&
        error !== null &&
        'status' in error &&
        typeof error.status === 'number'
          ? error.status
          : 500
      const payload =
        typeof error === 'object' && error !== null && 'payload' in error
          ? error.payload
          : { detail: error instanceof Error ? error.message : 'Error inesperado' }
      const summary =
        typeof payload === 'string' ? payload : JSON.stringify(payload).slice(0, 140)

      setResponse({
        title: `${label} · error`,
        method,
        path,
        status,
        payload,
      })
      addLog({
        method,
        path,
        status,
        summary,
      })
      throw error
    }
  }

  return { execute }
}
