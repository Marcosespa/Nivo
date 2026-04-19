import Card from '../common/Card'
import { useAuthStore } from '../../store/authStore'

export default function JsonPanel() {
  const lastResponse = useAuthStore((state) => state.lastResponse)
  const clearResponse = useAuthStore((state) => state.clearResponse)

  return (
    <Card className="!rounded-xl !p-0 overflow-hidden">
      <div className="flex items-center justify-between border-b border-gray-800 px-5 py-4">
        <div>
          <h3 className="text-sm font-semibold text-white">Ultima respuesta</h3>
          <p className="text-xs text-gray-500">
            {lastResponse
              ? `${lastResponse.method} ${lastResponse.path} · ${lastResponse.status}`
              : 'Todavia no se ha ejecutado ningun request'}
          </p>
        </div>
        <button
          type="button"
          className="text-xs font-medium text-gray-400 hover:text-white"
          onClick={clearResponse}
        >
          Limpiar
        </button>
      </div>
      <pre className="max-h-[420px] overflow-auto whitespace-pre-wrap break-words px-5 py-4 text-xs leading-6 text-teal-100">
        {lastResponse ? JSON.stringify(lastResponse.payload, null, 2) : 'Sin datos'}
      </pre>
    </Card>
  )
}
