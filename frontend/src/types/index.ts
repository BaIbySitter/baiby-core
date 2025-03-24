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

export interface RequestDetails {
  request_id: string;
  status: string;
  data: TransactionData;
  created_at: string;
  updated_at?: string;
  sentinel_statuses: Record<string, SentinelStatus>;
}

export interface StatusData {
  total_requests: number;
  active_requests: RequestDetails[];
  completed_requests: RequestDetails[];
} 