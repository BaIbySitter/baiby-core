'use client';

import { useEffect, useState } from 'react';
import { RequestDetails } from '@/types';
import { formatDistanceToNow } from 'date-fns';
import Link from 'next/link';

export default function TransactionDetail({ params }: { params: { id: string } }) {
  const [transaction, setTransaction] = useState<RequestDetails | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchTransaction = async () => {
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/transaction/${params.id}`);
        if (!response.ok) throw new Error('Transaction not found');
        const data = await response.json();
        setTransaction(data);
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Failed to load transaction');
      }
    };

    fetchTransaction();
  }, [params.id]);

  if (error) return (
    <div className="min-h-screen bg-red-50 flex items-center justify-center">
      <div className="text-red-600 text-center">
        <h2 className="text-2xl font-bold mb-2">Error</h2>
        <p>{error}</p>
        <Link href="/" className="mt-4 text-red-800 hover:underline">
          Return to Dashboard
        </Link>
      </div>
    </div>
  );

  if (!transaction) return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="animate-pulse text-gray-600">Loading transaction details...</div>
    </div>
  );

  const createdAt = typeof transaction.created_at === 'string' 
    ? transaction.created_at 
    : new Date(transaction.created_at * 1000).toISOString();

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="mb-6 flex items-center justify-between">
          <Link href="/" className="text-blue-600 dark:text-blue-400 hover:underline">
            &larr; Back to Dashboard
          </Link>
          <span className={`px-2 py-1 text-sm rounded-full ${
            transaction.status === 'completed' 
              ? 'bg-green-100 text-green-800'
              : 'bg-yellow-100 text-yellow-800'
          }`}>
            {transaction.status}
          </span>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 space-y-8">
          <div>
            <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">Basic Information</h2>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div className="text-gray-500 dark:text-gray-400">Transaction ID</div>
              <div className="font-mono text-gray-900 dark:text-gray-100">{transaction.request_id}</div>
              <div className="text-gray-500 dark:text-gray-400">Chain ID</div>
              <div className="font-medium text-gray-900 dark:text-gray-100">{transaction.chainId}</div>
              <div className="text-gray-500 dark:text-gray-400">Created</div>
              <div className="font-medium text-gray-900 dark:text-gray-100">
                {formatDistanceToNow(new Date(createdAt), { addSuffix: true })}
              </div>
            </div>
          </div>

          <div>
            <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">Transaction Data</h2>
            <div className="space-y-4">
              <div>
                <span className="text-gray-500 dark:text-gray-400">From:</span>
                <p className="font-mono mt-1 bg-gray-50 dark:bg-gray-700 p-2 rounded text-gray-900 dark:text-gray-100">{transaction.from_address}</p>
              </div>
              <div>
                <span className="text-gray-500 dark:text-gray-400">To:</span>
                <p className="font-mono mt-1 bg-gray-50 dark:bg-gray-700 p-2 rounded text-gray-900 dark:text-gray-100">{transaction.to_address}</p>
              </div>
              <div>
                <span className="text-gray-500 dark:text-gray-400">Value:</span>
                <p className="font-mono mt-1 bg-gray-50 dark:bg-gray-700 p-2 rounded text-gray-900 dark:text-gray-100">{transaction.value}</p>
              </div>
              <div>
                <span className="text-gray-500 dark:text-gray-400">Data:</span>
                <p className="font-mono mt-1 bg-gray-50 dark:bg-gray-700 p-2 rounded text-gray-900 dark:text-gray-100 break-all">{transaction.data}</p>
              </div>
              {transaction.reason && (
                <div>
                  <span className="text-gray-500 dark:text-gray-400">Reason:</span>
                  <p className="mt-1 bg-gray-50 dark:bg-gray-700 p-2 rounded text-gray-900 dark:text-gray-100">{transaction.reason}</p>
                </div>
              )}
            </div>
          </div>

          <div>
            <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">Validations</h2>
            <div className="space-y-4">
              {transaction.validations.map((validation) => (
                <div key={validation.name} className="border dark:border-gray-700 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-medium text-gray-900 dark:text-gray-100">{validation.name}</span>
                    <span className={`px-2 py-1 text-xs rounded-full ${
                      validation.status === 'completed' 
                        ? 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-100'
                        : 'bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-100'
                    }`}>
                      {validation.status}
                    </span>
                  </div>
                  {validation.result && (
                    <pre className="mt-2 text-sm bg-gray-50 dark:bg-gray-700 p-3 rounded overflow-auto text-gray-900 dark:text-gray-100">
                      {JSON.stringify(validation.result, null, 2)}
                    </pre>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 