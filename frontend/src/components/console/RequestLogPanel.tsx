import Card from '../common/Card'
import { useAuthStore } from '../../store/authStore'

export default function RequestLogPanel() {
  const logs = useAuthStore((state) => state.requestLogs)
  const clearLogs = useAuthStore((state) => state.clearLogs)

  return (
    <Card className="!rounded-xl !p-0 overflow-hidden">
      <div className="flex items-center justify-between border-b border-gray-800 px-5 py-4">
        <div>
          <h3 className="text-sm font-semibold text-white">Historial de requests</h3>
          <p className="text-xs text-gray-500">Se guardan los ultimos 30 eventos</p>
        </div>
        <button
          type="button"
          className="text-xs font-medium text-gray-400 hover:text-white"
          onClick={clearLogs}
        >
          Vaciar
        </button>
      </div>
      <div className="divide-y divide-gray-800">
        {logs.length === 0 ? (
          <p className="px-5 py-4 text-sm text-gray-500">Aun no hay requests en la sesion.</p>
        ) : (
          logs.map((log) => (
            <div key={log.id} className="px-5 py-4">
              <div className="flex items-center justify-between gap-3">
                <p className="text-sm font-medium text-white">
                  {log.method} {log.path}
                </p>
                <span className="text-xs text-gray-500">
                  {new Date(log.timestamp).toLocaleTimeString()}
                </span>
              </div>
              <p className="mt-1 text-xs text-gray-400">status {log.status}</p>
              <p className="mt-2 text-xs text-gray-500">{log.summary}</p>
            </div>
          ))
        )}
      </div>
    </Card>
  )
}
