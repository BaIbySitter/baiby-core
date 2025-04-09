import React from "react";

interface DashboardStatsProps {
  totalTransactions: number;
  activeCount: number;
  completedCount: number;
}

export default function DashboardStats({
  totalTransactions,
  activeCount,
  completedCount,
}: DashboardStatsProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div className="bg-card text-card-foreground rounded-lg p-6 shadow dark:with-scanline">
        <h3 className="text-muted-foreground text-sm dark:terminal-text">Total Transactions</h3>
        <p className="text-3xl font-bold text-card-foreground dark:terminal-text dark:terminal-cursor">{totalTransactions}</p>
      </div>
      
      <div className="bg-card text-card-foreground rounded-lg p-6 shadow dark:with-scanline">
        <h3 className="text-muted-foreground text-sm dark:terminal-text">Active Transactions</h3>
        <p className="text-3xl font-bold text-card-foreground dark:terminal-text">{activeCount}</p>
      </div>
      
      <div className="bg-card text-card-foreground rounded-lg p-6 shadow dark:with-scanline">
        <h3 className="text-muted-foreground text-sm dark:terminal-text">Completed Transactions</h3>
        <p className="text-3xl font-bold text-card-foreground dark:terminal-text">{completedCount}</p>
      </div>
    </div>
  );
}