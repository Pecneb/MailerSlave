'use client';

import { useQuery } from '@tanstack/react-query';
import { emailsApi } from '@/lib/api';
import { format } from 'date-fns';

export default function EmailsPage() {
  const { data: emails, isLoading } = useQuery({
    queryKey: ['emails'],
    queryFn: () => emailsApi.list(),
  });

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-gray-900">Email Logs</h1>
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Subject</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Sent At</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {emails?.map((email) => (
              <tr key={email._id}>
                <td className="px-6 py-4 text-sm">{email.subject}</td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                    email.status === 'sent' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                  }`}>
                    {email.status}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {email.sent_at && format(new Date(email.sent_at), 'MMM d, yyyy HH:mm')}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
