import { TransactionSummary } from "@/types/api";
import { formatDistanceToNow } from "date-fns";
import Link from 'next/link';

interface TransactionListProps {
  transactions: TransactionSummary[];
  emptyMessage: string;
  onTransactionClick: (transactionId: string) => void;
}

export function TransactionList({
  transactions,
  emptyMessage,
  onTransactionClick,
}: TransactionListProps) {
  if (transactions.length === 0) {
    return (
      <div className="text-center py-8 text-muted-foreground dark:terminal-text">
        {emptyMessage}
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {transactions
      .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
      .map((tx) => {
        // Safe date conversion
        let dateDisplay;
        try {
          dateDisplay = formatDistanceToNow(new Date(tx.created_at), { addSuffix: true });
        } catch (e) {
          dateDisplay = "Unknown date";
        }

        return (
          <div
            key={tx.transaction_id}
            onClick={() => onTransactionClick(tx.transaction_id)}
            className="block border border-border rounded-lg p-4 hover:bg-muted transition-colors cursor-pointer dark:with-scanline dark:hover:border-primary"
          >
            <div className="flex items-start justify-between mb-2">
              <div className="flex-1">
                <p className="text-sm text-muted-foreground dark:terminal-text">
                  From: {tx.from_address || "Unknown address"}
                </p>
              </div>
              <span
                className={`px-2 py-1 text-xs rounded-full ${
                  tx.status === "completed"
                    ? "bg-gray-100 text-gray-800 dark:bg-accent dark:text-primary"
                    : "bg-yellow-100 text-yellow-800 dark:bg-amber-950 dark:text-amber-400"
                }`}
              >
                {tx.status}
              </span>
            </div>
            <div className="flex items-center justify-between text-sm text-muted-foreground dark:terminal-text">
              <span className="font-mono">ID: {tx.transaction_id}</span>
              <span>{dateDisplay}</span>
            </div>
          </div>
        );
      })}
    </div>
  );
}