import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { ResponseSnapshot, SessionState, UserProfile } from '../types'

const defaultBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001'
const defaultAppName = import.meta.env.VITE_APP_NAME || 'Nivo API Console'
const defaultEnvironment = import.meta.env.VITE_ENVIRONMENT || 'development'

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null
}

function summarizePayload(payload: unknown): string {
  if (typeof payload === 'string') return payload.slice(0, 140)
  try {
    return JSON.stringify(payload).slice(0, 140)
  } catch {
    return 'Respuesta recibida'
  }
}

function toTimestamp() {
  return new Date().toISOString()
}

export const useAuthStore = create<SessionState>()(
  persist<SessionState>(
    (set) => ({
      appName: defaultAppName,
      environment: defaultEnvironment,
      baseUrl: defaultBaseUrl,
      apiKey: '',
      accessToken: '',
      refreshToken: '',
      isAuthenticated: false,
      profile: null as UserProfile | null,
      lastOtp: '',
      lastTxId: '',
      lastBankAccountId: '',
      lastVerificationAmount: '',
      lastSignature: '',
      lastPublicKey: '',
      lastResponse: null,
      requestLogs: [],

      setBaseUrl: (value: string) => set({ baseUrl: value.trim() || defaultBaseUrl }),
      setApiKey: (value: string) => set({ apiKey: value.trim() }),
      setEnvironment: (value: string) => set({ environment: value }),
      setTokens: (accessToken: string, refreshToken = '') =>
        set({
          accessToken,
          refreshToken: refreshToken || useAuthStore.getState().refreshToken,
          isAuthenticated: Boolean(accessToken),
        }),
      setProfile: (profile: UserProfile | null) => set({ profile }),
      clearSession: () =>
        set({
          accessToken: '',
          refreshToken: '',
          isAuthenticated: false,
          profile: null,
          lastOtp: '',
          lastTxId: '',
          lastBankAccountId: '',
          lastVerificationAmount: '',
          lastSignature: '',
          lastPublicKey: '',
        }),
      addLog: (log) =>
        set((state) => ({
          requestLogs: [
            {
              ...log,
              id: crypto.randomUUID(),
              timestamp: toTimestamp(),
            },
            ...state.requestLogs,
          ].slice(0, 30),
        })),
      setResponse: (response) =>
        set({
          lastResponse: {
            ...response,
            timestamp: toTimestamp(),
          },
        }),
      clearLogs: () => set({ requestLogs: [] }),
      clearResponse: () => set({ lastResponse: null }),
      ingestPayload: (path: string, payload: unknown) =>
        set((state) => {
          const next: Partial<SessionState> = {}
          if (!isRecord(payload)) return next

          if (typeof payload.access_token === 'string') {
            next.accessToken = payload.access_token
            next.isAuthenticated = true
          }

          if (typeof payload.refresh_token === 'string') {
            next.refreshToken = payload.refresh_token
          }

          if (typeof payload.dev_otp === 'string') {
            next.lastOtp = payload.dev_otp
          }

          if (typeof payload.tx_id === 'string') {
            next.lastTxId = payload.tx_id
          }

          if (typeof payload.bank_account_id === 'string') {
            next.lastBankAccountId = payload.bank_account_id
          }

          if (
            typeof payload.verification_amount_cop === 'number' ||
            typeof payload.verification_amount_cop === 'string'
          ) {
            next.lastVerificationAmount = String(payload.verification_amount_cop)
          }

          if (typeof payload.signature_hex === 'string') {
            next.lastSignature = payload.signature_hex
          }

          if (typeof payload.public_key_hex === 'string') {
            next.lastPublicKey = payload.public_key_hex
          }

          if (path === '/api/v1/dev/seed' && isRecord(payload.sender)) {
            if (typeof payload.sender.access_token === 'string') {
              next.accessToken = payload.sender.access_token
              next.isAuthenticated = true
            }
            if (typeof payload.sender.refresh_token === 'string') {
              next.refreshToken = payload.sender.refresh_token
            }
          }

          if (path === '/api/v1/users/me') {
            next.profile = payload as unknown as UserProfile
          }

          if (path === '/api/v1/auth/logout') {
            next.refreshToken = ''
            next.accessToken = ''
            next.isAuthenticated = false
            next.profile = null
          }

          return { ...state, ...next }
        }),
    }),
    {
      name: 'nivo-console-session',
    }
  )
)

export function recordLocalResponse(response: Omit<ResponseSnapshot, 'timestamp'>) {
  useAuthStore.getState().setResponse(response)
  useAuthStore.getState().addLog({
    method: response.method,
    path: response.path,
    status: response.status,
    summary: summarizePayload(response.payload),
  })
}
