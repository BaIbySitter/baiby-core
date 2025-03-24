import { RequestDetails } from "@/types";
import { formatDistanceToNow } from "date-fns";
import Link from "next/link";

interface TransactionListProps {
  transactions?: RequestDetails[];
  emptyMessage?: string;
}

export function TransactionList({
  transactions = [],
  emptyMessage = "No transactions",
}: TransactionListProps) {
  if (!transactions?.length) {
    return (
      <div className="text-center py-8 text-gray-500">
        <p>{emptyMessage}</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {transactions.map((tx) => (
        <Link
          key={tx.request_id}
          href={`/transaction/${tx.request_id}`}
          className="block border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
        >
          <div className="flex items-start justify-between mb-2">
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
                To: {tx.data.to_address}
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-400 truncate">
                From: {tx.data.from_address}
              </p>
            </div>
            <span
              className={`px-2 py-1 text-xs rounded-full ${
                tx.status === "completed"
                  ? "bg-green-100 text-green-800"
                  : "bg-yellow-100 text-yellow-800"
              }`}
            >
              {tx.status}
            </span>
          </div>
          <div className="flex items-center justify-between text-sm text-gray-500">
            <span>Chain ID: {tx.data.chainId}</span>
            <span>
              {formatDistanceToNow(new Date(tx.created_at), {
                addSuffix: true,
              })}
            </span>
          </div>
          {tx.data.reason && (
            <p className="mt-2 text-sm text-gray-600 dark:text-gray-300 bg-gray-50 dark:bg-gray-700 rounded p-2">
              {tx.data.reason}
            </p>
          )}
        </Link>
      ))}
    </div>
  );
}
