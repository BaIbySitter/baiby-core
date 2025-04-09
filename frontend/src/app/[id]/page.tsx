"use client";

import { useEffect, useState } from "react";
import { fetchTransactionDetail } from "@/services/api";
import { TransactionDetail } from "@/types/api";
import { ArrowLeft } from "lucide-react";
import Link from "next/link";

export default function TransactionDetailPage({ params }: { params: { id: string } }) {
  // State to store transaction details
  const [transaction, setTransaction] = useState<TransactionDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Effect to load transaction data
  useEffect(() => {
    async function loadTransactionDetail() {
      try {
        setLoading(true);
        const data = await fetchTransactionDetail(params.id);
        setTransaction(data);
      } catch (err) {
        console.error("Error loading transaction details:", err);
        setError("Error loading transaction details");
      } finally {
        setLoading(false);
      }
    }

    loadTransactionDetail();
  }, [params.id]);

  // If loading, show a loader
  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="animate-pulse text-foreground dark:terminal-text">
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
            <p className="dark:typing-effect">Loading transaction details...</p>
          </div>
        </div>
      </div>
    );
  }

  // If there's an error, show error message
  if (error) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-destructive text-center">
          <h2 className="text-2xl font-bold mb-2 dark:terminal-text">Error</h2>
          <p className="dark:terminal-text">{error}</p>
          <Link href="/" className="mt-4 inline-block underline text-foreground dark:terminal-text">
            Back to dashboard
          </Link>
        </div>
      </div>
    );
  }

  // If no transaction data
  if (!transaction) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold mb-2 text-foreground dark:terminal-text">Transaction not found</h2>
          <Link href="/" className="mt-4 inline-block underline text-foreground dark:terminal-text">
            Back to dashboard
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background text-foreground">
      <div className="max-w-[1200px] mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-6">
          <Link href="/" className="flex items-center text-foreground hover:text-primary dark:terminal-text">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to dashboard
          </Link>
        </div>

        <div className="bg-card text-card-foreground rounded-lg shadow p-6 mb-8 dark:with-scanline">
          <div className="flex flex-col md:flex-row md:items-center justify-between">
            <h2 className="text-xl font-semibold mb-4 dark:terminal-text">Transaction Details</h2>
            <div className="mt-4 md:mt-0">
              <span className={`px-3 py-1 text-sm rounded-full ${
                transaction.status === "completed" 
                  ? "bg-gray-100 text-gray-800 dark:bg-accent dark:text-primary dark:terminal-text" 
                  : "bg-yellow-100 text-yellow-800 dark:bg-amber-950 dark:text-amber-400 dark:terminal-text"
              }`}>
                {transaction.status}
              </span>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <p className="text-sm text-muted-foreground dark:terminal-text mb-1">Transaction ID:</p>
              <div className="p-3 bg-muted rounded-md dark:border dark:border-accent">
                <p className="font-mono text-foreground text-sm dark:terminal-text">{transaction.transaction_id}</p>
              </div>
            </div>
            <div>
              <p className="text-sm text-muted-foreground dark:terminal-text mb-1">Chain ID:</p>
              <div className="p-3 bg-muted rounded-md dark:border dark:border-accent">
                <p className="text-sm dark:terminal-text">{transaction.chainId}</p>
              </div>
            </div>
            <div>
              <p className="text-sm text-muted-foreground dark:terminal-text mb-1">From:</p>
              <div className="p-3 bg-muted rounded-md dark:border dark:border-accent overflow-x-auto">
                <p className="font-mono text-foreground text-sm dark:terminal-text">{transaction.from_address}</p>
              </div>
            </div>
            <div>
              <p className="text-sm text-muted-foreground dark:terminal-text mb-1">To:</p>
              <div className="p-3 bg-muted rounded-md dark:border dark:border-accent overflow-x-auto">
                <p className="font-mono text-foreground text-sm dark:terminal-text">{transaction.to_address}</p>
              </div>
            </div>
            <div>
              <p className="text-sm text-muted-foreground dark:terminal-text mb-1">Value:</p>
              <div className="p-3 bg-muted rounded-md dark:border dark:border-accent">
                <p className="text-sm dark:terminal-text">{transaction.value} Wei</p>
              </div>
            </div>
            <div>
              <p className="text-sm text-muted-foreground dark:terminal-text mb-1">Created:</p>
              <div className="p-3 bg-muted rounded-md dark:border dark:border-accent">
                <p className="text-sm dark:terminal-text">{transaction?.created_at && new Date(transaction.created_at).toLocaleString()}</p>
              </div>
            </div>
          </div>

          {transaction.data && (
            <div className="mb-4">
              <p className="text-sm text-muted-foreground dark:terminal-text mb-1">Transaction Data:</p>
              <div className="p-3 bg-muted rounded-md dark:border dark:border-accent">
                <pre className="font-mono text-foreground text-sm dark:terminal-text whitespace-pre-wrap break-all">{transaction.data}</pre>
              </div>
            </div>
          )}
          
          {transaction.reason && (
            <div className="mb-4">
              <p className="text-sm text-muted-foreground dark:terminal-text mb-1">Reason:</p>
              <div className="p-3 bg-muted rounded-md dark:border dark:border-accent">
                <pre className="whitespace-pre-wrap text-foreground text-sm dark:terminal-text break-all">{transaction.reason}</pre>
              </div>
            </div>
          )}
        </div>

        {/* Simplified Validations */}
        {transaction.validations && transaction.validations.length > 0 && (
          <div className="bg-card text-card-foreground rounded-lg shadow p-6 mb-4 dark:with-scanline">
            <h2 className="text-xl font-semibold mb-4 dark:terminal-text">Validations</h2>
            <div className="space-y-4">
              {transaction.validations.map((validation, index) => (
                <div key={index} className="border border-border rounded-md p-4 dark:border-accent">
                  <div className="flex justify-between items-center mb-2">
                    <h3 className="font-medium dark:terminal-text">{validation.name}</h3>
                    <span className={`px-2 py-1 text-xs rounded-full ${
                      validation.result?.status === "success"
                        ? "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300" 
                        : "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300"
                    }`}>
                      {validation.result?.status}
                    </span>
                  </div>
                  <p className="text-sm text-muted-foreground mb-3 dark:terminal-text">{validation.result?.message}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
} 