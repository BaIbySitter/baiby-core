export interface SentinelStatus {
  status: string;
  result: any;
  updated_at?: string;
}

export interface TransactionData {
  chainId: number;
  from_address: string;
  to_address: string;
  data: string;
  value: string;
  reason?: string;
}

export interface ValidationResult {
  name: string;
  status: string;
  result?: {
    status: string;
    message: string;
    approved?: boolean;
    risk_level?: string;
    warnings?: string[];
    timestamp?: number;
    [key: string]: any;
  };
}

export interface RequestDetails {
  request_id: string;
  chainId: number | string;
  from_address: string;
  to_address: string;
  data: string;
  value: string;
  reason?: string;
  validations: ValidationResult[];
  created_at: string | number;
  updated_at?: string | number;
  status: string;
}

export interface StatusData {
  total_requests: number;
  active_requests: RequestDetails[];
  completed_requests: RequestDetails[];
} 