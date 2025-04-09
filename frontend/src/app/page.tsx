"use client";

import React, { useEffect, useState } from "react";
import DashboardStats from "@/components/DashboardStats";
import { TransactionList } from "@/components/TransactionList";
import { ThemeToggle } from "@/components/ThemeToggle";
import { 
  DashboardResponse
} from '@/types/api';
import { fetchDashboard } from '@/services/api';
import { useRouter } from 'next/navigation';

export default function Dashboard() {
  const router = useRouter();
  const [dashboardData, setDashboardData] = useState<DashboardResponse | null>(null);
  const [_loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDashboardData();
    
    // Reload data every 10 seconds
    const interval = setInterval(loadDashboardData, 10000);
    return () => clearInterval(interval);
  }, []);

  async function loadDashboardData() {
    try {
      setLoading(true);
      const data = await fetchDashboard();
      console.log("Dashboard data:", data);
      setDashboardData(data);
      setError(null);
    } catch (err) {
      console.error('Error loading dashboard:', err);
      setError('Error loading dashboard. Please try again.');
    } finally {
      setLoading(false);
    }
  }

  async function handleTransactionClick(transactionId: string) {
    router.push(`/${transactionId}`);
  }

  if (error)
    return (
      <div className="min-h-screen bg-red-50 flex items-center justify-center">
        <div className="text-red-600 text-center">
          <h2 className="text-2xl font-bold mb-2">Error</h2>
          <p>{error}</p>
          <button 
            className="ml-4 underline"
            onClick={loadDashboardData}
          >
            Retry
          </button>
        </div>
      </div>
    );

  if (!dashboardData)
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="animate-pulse text-foreground">
          <div className="flex flex-col items-center">
            <svg 
              className="animate-spin h-8 w-8 mb-4"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              ></circle>
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              ></path>
            </svg>
            <p>Loading dashboard...</p>
          </div>
        </div>
      </div>
    );

  return (
    <div className="min-h-screen bg-background text-foreground">
      <div className="max-w-[1400px] mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-card text-card-foreground rounded-lg shadow-sm p-6 mb-8">
          <div className="flex items-center justify-between mb-6">
            <h1 className="text-2xl font-bold text-foreground">
              bAIbySitter Monitor
            </h1>
            <div className="flex items-center gap-4">
              <ThemeToggle />
              <span className="px-3 py-1 text-sm text-green-700 bg-green-100 rounded-full dark:bg-accent dark:text-primary dark:terminal-text flex items-center gap-1.5">
                <span className="relative flex h-2.5 w-2.5">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-500 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-green-600"></span>
                </span>
                Live
              </span>
            </div>
          </div>

          <DashboardStats
            totalTransactions={dashboardData.total_transactions}
            activeCount={dashboardData.active_transactions.length}
            completedCount={dashboardData.completed_transactions.length}
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="bg-card text-card-foreground rounded-lg shadow-sm p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-foreground">
                Active Transactions
              </h2>
              {dashboardData?.active_transactions?.length > 0 && (
                <span className="px-2 py-1 text-sm bg-yellow-100 text-yellow-800 rounded-full dark:bg-accent dark:text-primary dark:terminal-text">
                  {dashboardData?.active_transactions?.length}
                </span>
              )}
            </div>
            <TransactionList
              transactions={dashboardData.active_transactions}
              emptyMessage="No active transactions"
              onTransactionClick={handleTransactionClick}
            />
          </div>
          <div className="bg-card text-card-foreground rounded-lg shadow-sm p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-foreground">
                Completed Transactions
              </h2>
              {dashboardData?.completed_transactions?.length > 0 && (
                <span className="px-2 py-1 text-sm bg-gray-100 text-gray-800 rounded-full dark:bg-accent dark:text-primary dark:terminal-text">
                  {dashboardData?.completed_transactions?.length}
                </span>
              )}
            </div>
            <TransactionList
              transactions={dashboardData.completed_transactions}
              emptyMessage="No completed transactions"
              onTransactionClick={handleTransactionClick}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
