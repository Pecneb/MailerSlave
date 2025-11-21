'use client';

import { useQuery } from '@tanstack/react-query';
import { campaignsApi } from '@/lib/api';
import { Plus } from 'lucide-react';
import Link from 'next/link';
import { format } from 'date-fns';

export default function CampaignsPage() {
  const { data: campaigns, isLoading } = useQuery({
    queryKey: ['campaigns'],
    queryFn: () => campaignsApi.list(),
  });

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Campaigns</h1>
        <Link
          href="/campaigns/new"
          className="inline-flex items-center px-4 py-2 bg-primary-600 text-white rounded-md"
        >
          <Plus className="mr-2 h-4 w-4" />
          New Campaign
        </Link>
      </div>
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Progress</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Created</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {campaigns?.map((campaign) => (
              <tr key={campaign._id}>
                <td className="px-6 py-4 whitespace-nowrap">
                  <Link href={`/campaigns/${campaign._id}`} className="text-primary-600 hover:text-primary-900">
                    {campaign.name}
                  </Link>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className="px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800">
                    {campaign.status}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">
                  {campaign.sent_count} / {campaign.total_emails}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {format(new Date(campaign.created_at), 'MMM d, yyyy')}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
