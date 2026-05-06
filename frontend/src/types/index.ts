export type KycStatus = 'pending' | 'verified' | 'rejected'

export interface UserProfile {
  id: string
  phone_number: string
  plan: string
  kyc_status: KycStatus
  pqc_key_fingerprint: string | null
}

export interface WalletSummary {
  balance_cop: number
  balance_display: string
  currency: string
  is_frozen: boolean
  custody_mode: string
  is_legal_balance: boolean
  provider_account_ref: string | null
}

export interface PaymentHistoryItem {
  tx_id: string
  status: string
  amount_cop: number
  amount_display: string
  direction: 'sent' | 'received' | 'all' | string
  created_at: string
  confirmed_at: string | null
  ml_dsa_signature_fingerprint: string
  provider_reference: string | null
  settlement_status: string
  rail: string
}

export interface BankAccountSummary {
  id: string
  bank_code: string
  account_type: string
  account_number_last4: string
  account_holder_name: string
  is_verified: boolean
  created_at: string
}

export interface RequestLogItem {
  id: string
  timestamp: string
  method: string
  path: string
  status: number | 'local'
  summary: string
}

export interface ResponseSnapshot {
  title: string
  method: string
  path: string
  status: number | 'local'
  payload: unknown
  timestamp: string
}

export interface SessionState {
  appName: string
  environment: string
  baseUrl: string
  apiKey: string
  accessToken: string
  refreshToken: string
  isAuthenticated: boolean
  profile: UserProfile | null
  lastOtp: string
  lastTxId: string
  lastBankAccountId: string
  lastVerificationAmount: string
  lastSignature: string
  lastPublicKey: string
  lastResponse: ResponseSnapshot | null
  requestLogs: RequestLogItem[]
  setBaseUrl: (value: string) => void
  setApiKey: (value: string) => void
  setEnvironment: (value: string) => void
  setTokens: (accessToken: string, refreshToken?: string) => void
  setProfile: (profile: UserProfile | null) => void
  clearSession: () => void
  addLog: (log: Omit<RequestLogItem, 'id' | 'timestamp'>) => void
  setResponse: (response: Omit<ResponseSnapshot, 'timestamp'>) => void
  clearLogs: () => void
  clearResponse: () => void
  ingestPayload: (path: string, payload: unknown) => void
}
