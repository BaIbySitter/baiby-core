import React from "react";

interface DashboardStatsProps {
  totalRequests: number;
  activeRequests: number;
  completedRequests: number;
}

export function DashboardStats({
  totalRequests,
  activeRequests,
  completedRequests,
}: DashboardStatsProps) {
  return (
    <div className="grid grid-cols-3 gap-6">
      <div className="bg-white dark:bg-gray-800 p-6 rounded-xl border border-gray-200 dark:border-gray-700 hover:shadow-md transition-shadow">
        <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">
          Total Requests
        </h3>
        <p className="mt-2 text-3xl font-semibold text-gray-700 dark:text-gray-300">
          {totalRequests}
        </p>
      </div>
      <div className="bg-white dark:bg-gray-800 p-6 rounded-xl border border-gray-200 dark:border-gray-700 hover:shadow-md transition-shadow">
        <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">
          Active
        </h3>
        <p className="mt-2 text-3xl font-semibold text-yellow-600 dark:text-yellow-500">
          {activeRequests}
        </p>
      </div>
      <div className="bg-white dark:bg-gray-800 p-6 rounded-xl border border-gray-200 dark:border-gray-700 hover:shadow-md transition-shadow">
        <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">
          Completed
        </h3>
        <p className="mt-2 text-3xl font-semibold text-green-600 dark:text-green-500">
          {completedRequests}
        </p>
      </div>
    </div>
  );
}
