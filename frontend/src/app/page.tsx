"use client";

import React, { useEffect, useState } from "react";
import { DashboardStats } from "@/components/DashboardStats";
import { TransactionList } from "@/components/TransactionList";
import { StatusData } from "@/types";
import { ThemeToggle } from "@/components/ThemeToggle";

export default function Dashboard() {
  const [data, setData] = useState<StatusData | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}/dashboard`
        );
        if (!response.ok) throw new Error("Failed to fetch data");
        const json = await response.json();
        setData(json);
        setError(null);
      } catch (e) {
        setError(e instanceof Error ? e.message : "An error occurred");
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, []);

  if (error)
    return (
      <div className="min-h-screen bg-red-50 flex items-center justify-center">
        <div className="text-red-600 text-center">
          <h2 className="text-2xl font-bold mb-2">Error</h2>
          <p>{error}</p>
        </div>
      </div>
    );

  if (!data)
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-pulse text-gray-600">
          <svg
            className="animate-spin h-8 w-8 mx-auto mb-4"
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
    );

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-[1400px] mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 mb-8">
          <div className="flex items-center justify-between mb-6">
            <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
              bAIbySitter Status
            </h1>
            <div className="flex items-center gap-4">
              <ThemeToggle />
              <span className="px-3 py-1 text-sm text-green-700 bg-green-100 rounded-full">
                Live
              </span>
            </div>
          </div>

          <DashboardStats
            totalRequests={data?.total_requests}
            activeRequests={data?.active_requests?.length}
            completedRequests={data?.completed_requests?.length}
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
                Active Transactions
              </h2>
              <span className="px-2 py-1 text-sm bg-blue-100 text-blue-800 rounded-full">
                {data?.active_requests?.length || 0}
              </span>
            </div>
            <TransactionList
              transactions={data?.active_requests}
              emptyMessage="No active transactions"
            />
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
                Completed Transactions
              </h2>
              <span className="px-2 py-1 text-sm bg-green-100 text-green-800 rounded-full">
                {data?.completed_requests?.length || 0}
              </span>
            </div>
            <TransactionList
              transactions={data?.completed_requests}
              emptyMessage="No completed transactions"
            />
          </div>
        </div>
      </div>
    </div>
  );
}
