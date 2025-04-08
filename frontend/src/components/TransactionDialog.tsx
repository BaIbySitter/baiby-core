import { RequestDetails } from "@/types";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "./ui/dialog";
import { formatDistanceToNow } from "date-fns";

interface TransactionDialogProps {
  transaction: RequestDetails;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function TransactionDialog({ transaction, open, onOpenChange }: TransactionDialogProps) {
  const createdAt = typeof transaction.created_at === 'string' 
    ? transaction.created_at 
    : new Date(transaction.created_at * 1000).toISOString();

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle>Transaction Details</DialogTitle>
        </DialogHeader>
        
        <div className="grid gap-4 py-4">
          <div className="space-y-4">
            <div>
              <h3 className="font-medium text-gray-900">Basic Information</h3>
              <div className="mt-2 grid grid-cols-2 gap-2 text-sm">
                <div className="text-gray-500">Status</div>
                <div className="font-medium">{transaction.status}</div>
                <div className="text-gray-500">Chain ID</div>
                <div className="font-medium">{transaction.chainId}</div>
                <div className="text-gray-500">Created</div>
                <div className="font-medium">
                  {formatDistanceToNow(new Date(createdAt), { addSuffix: true })}
                </div>
              </div>
            </div>

            <div>
              <h3 className="font-medium text-gray-900">Transaction Data</h3>
              <div className="mt-2 grid gap-2 text-sm">
                <div>
                  <span className="text-gray-500">From:</span>
                  <p className="font-mono mt-1">{transaction.from_address}</p>
                </div>
                <div>
                  <span className="text-gray-500">To:</span>
                  <p className="font-mono mt-1">{transaction.to_address}</p>
                </div>
                <div>
                  <span className="text-gray-500">Value:</span>
                  <p className="font-mono mt-1">{transaction.value}</p>
                </div>
                <div>
                  <span className="text-gray-500">Data:</span>
                  <p className="font-mono mt-1 break-all">{transaction.data}</p>
                </div>
                {transaction.reason && (
                  <div>
                    <span className="text-gray-500">Reason:</span>
                    <p className="mt-1">{transaction.reason}</p>
                  </div>
                )}
              </div>
            </div>

            <div>
              <h3 className="font-medium text-gray-900">Validations</h3>
              <div className="mt-2 space-y-3">
                {transaction.validations.map((validation) => (
                  <div key={validation.name} className="rounded-lg bg-gray-50 p-3">
                    <div className="flex items-center justify-between">
                      <span className="font-medium">{validation.name}</span>
                      <span className={`px-2 py-1 text-xs rounded-full ${
                        validation.status === 'completed' 
                          ? 'bg-green-100 text-green-800'
                          : 'bg-yellow-100 text-yellow-800'
                      }`}>
                        {validation.status}
                      </span>
                    </div>
                    {validation.result && (
                      <pre className="mt-2 text-xs overflow-auto">
                        {JSON.stringify(validation.result, null, 2)}
                      </pre>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
} 