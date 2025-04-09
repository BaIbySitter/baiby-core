// Tipos para la API
export interface TransactionSummary {
  transaction_id: string;
  from_address: string;
  created_at: string;
  status: string;
}

export interface TransactionDetail {
  transaction_id: string;
  chainId: number;
  from_address: string;
  to_address: string;
  data: string;
  value: number;
  reason?: string;
  status: string;
  created_at: string;
  validations: ValidationResult[];
}

export interface ValidationResult {
  name: string;
  status: string;
  result: { status: string, message?: string };
}

export interface DashboardResponse {
  total_transactions: number;
  active_transactions: TransactionSummary[];
  completed_transactions: TransactionSummary[];
}

export interface TransactionResponse {
  transaction_id: string;
  status: string;
  result: any;
}

export interface TransactionRequest {
  chainId: number;
  from_address: string;
  to_address: string;
  data: string;
  value: string;
  reason?: string;
} 