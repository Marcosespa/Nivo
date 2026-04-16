export interface User {
  id: string
  phone: string
  full_name: string
  email?: string
  kyc_status: 'pending' | 'verified' | 'rejected'
  created_at: string
}

export interface Wallet {
  id: string
  balance: number
  currency: string
  account_number: string
}

export interface Transaction {
  id: string
  amount: number
  currency: string
  type: 'credit' | 'debit'
  status: 'pending' | 'completed' | 'failed'
  description: string
  counterpart_name?: string
  created_at: string
}

export interface AuthState {
  token: string | null
  user: User | null
  isAuthenticated: boolean
  login: (token: string, user: User) => void
  logout: () => void
}

export interface OtpRequest {
  phone: string
}

export interface OtpVerify {
  phone: string
  otp: string
}

export interface PaymentRequest {
  recipient_phone: string
  amount: number
  description?: string
}

export interface ApiError {
  detail: string
}
