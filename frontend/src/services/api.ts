import { DashboardResponse, TransactionDetail } from '@/types/api';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

export async function fetchDashboard(): Promise<DashboardResponse> {
  try {
    const response = await fetch(`${API_URL}/dashboard`);
    
    if (!response.ok) {
      throw new Error(`Error ${response.status}: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching dashboard data:', error);
    throw error;
  }
}

export async function fetchTransactionDetail(transactionId: string): Promise<TransactionDetail> {
  try {
    const response = await fetch(`${API_URL}/transaction/${transactionId}`);
    
    if (!response.ok) {
      throw new Error(`Error ${response.status}: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error(`Error fetching transaction details for ${transactionId}:`, error);
    throw error;
  }
} 