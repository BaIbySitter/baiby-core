import React from 'react';
import { SentinelStatus as SentinelStatusType } from '../types';

interface SentinelStatusProps {
  name: string;
  status: SentinelStatusType;
}

export function SentinelStatus({ name, status }: SentinelStatusProps) {
  const statusColor = status.status === 'completed' 
    ? 'bg-green-100 text-green-800'
    : status.status === 'error'
    ? 'bg-red-100 text-red-800'
    : 'bg-yellow-100 text-yellow-800';

  return (
    <div className="p-3 rounded-lg bg-gray-50">
      <div className="text-sm font-medium text-gray-700">{name}</div>
      <span className={`mt-1 inline-block px-2 py-1 rounded text-xs ${statusColor}`}>
        {status.status}
      </span>
      {status.result && (
        <div className="mt-2 text-xs text-gray-500">
          {JSON.stringify(status.result, null, 2)}
        </div>
      )}
    </div>
  );
} 