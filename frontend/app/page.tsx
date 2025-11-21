'use client';

import { useQuery } from '@tanstack/react-query';
import { dashboardApi } from '@/lib/api';
import { Users, FileText, Send, Mail, TrendingUp, Activity } from 'lucide-react';
import Link from 'next/link';
import { format } from 'date-fns';

export default function DashboardPage() {
  const { data: stats, isLoading, error } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: dashboardApi.getStats,
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-gray-500">Loading dashboard...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-800">Failed to load dashboard data</p>
      </div>
    );
  }

  const statCards = [
    { label: 'Total Contacts', value: stats?.total_contacts || 0, icon: Users, color: 'blue' },
    { label: 'Templates', value: stats?.total_templates || 0, icon: FileText, color: 'green' },
    { label: 'Total Campaigns', value: stats?.total_campaigns || 0, icon: Send, color: 'purple' },
    { label: 'Active Campaigns', value: stats?.active_campaigns || 0, icon: Activity, color: 'orange' },
    { label: 'Emails Sent (Total)', value: stats?.total_emails_sent || 0, icon: Mail, color: 'indigo' },
    { label: 'Emails Sent (Today)', value: stats?.emails_sent_today || 0, icon: TrendingUp, color: 'pink' },
  ];

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-2 text-gray-600">Overview of your email campaigns</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {statCards.map((stat) => {
          const Icon = stat.icon;
          return (
            <div key={stat.label} className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">{stat.label}</p>
                  <p className="mt-2 text-3xl font-semibold text-gray-900">{stat.value}</p>
                </div>
                <div className={`p-3 bg-${stat.color}-100 rounded-full`}>
                  <Icon className={`h-6 w-6 text-${stat.color}-600`} />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Recent Campaigns */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Recent Campaigns</h2>
        </div>
        <div className="divide-y divide-gray-200">
          {stats?.recent_campaigns && stats.recent_campaigns.length > 0 ? (
            stats.recent_campaigns.map((campaign) => (
              <Link
                key={campaign._id}
                href={`/campaigns/${campaign._id}`}
                className="block px-6 py-4 hover:bg-gray-50 transition"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-sm font-medium text-gray-900">{campaign.name}</h3>
                    <p className="mt-1 text-sm text-gray-500">
                      {campaign.sent_count} / {campaign.total_emails} emails sent
                    </p>
                  </div>
                  <div className="flex items-center space-x-4">
                    <StatusBadge status={campaign.status} />
                    <span className="text-sm text-gray-500">
                      {format(new Date(campaign.created_at), 'MMM d, yyyy')}
                    </span>
                  </div>
                </div>
              </Link>
            ))
          ) : (
            <div className="px-6 py-8 text-center text-gray-500">
              No campaigns yet. <Link href="/campaigns/new" className="text-primary-600 hover:text-primary-700">Create your first campaign</Link>
            </div>
          )}
        </div>
      </div>

      {/* Recent Emails */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Recent Email Logs</h2>
        </div>
        <div className="divide-y divide-gray-200">
          {stats?.recent_emails && stats.recent_emails.length > 0 ? (
            stats.recent_emails.slice(0, 5).map((email) => (
              <div key={email._id} className="px-6 py-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-900">{email.subject}</p>
                    <p className="mt-1 text-sm text-gray-500">Campaign: {email.campaign_id}</p>
                  </div>
                  <div className="flex items-center space-x-4">
                    <EmailStatusBadge status={email.status} />
                    <span className="text-sm text-gray-500">
                      {email.sent_at && format(new Date(email.sent_at), 'MMM d, HH:mm')}
                    </span>
                  </div>
                </div>
              </div>
            ))
          ) : (
            <div className="px-6 py-8 text-center text-gray-500">
              No emails sent yet
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const colors: Record<string, string> = {
    draft: 'bg-gray-100 text-gray-800',
    in_progress: 'bg-blue-100 text-blue-800',
    completed: 'bg-green-100 text-green-800',
    failed: 'bg-red-100 text-red-800',
    paused: 'bg-yellow-100 text-yellow-800',
  };

  return (
    <span className={`px-2 py-1 text-xs font-medium rounded-full ${colors[status] || colors.draft}`}>
      {status.replace('_', ' ')}
    </span>
  );
}

function EmailStatusBadge({ status }: { status: string }) {
  const colors: Record<string, string> = {
    pending: 'bg-yellow-100 text-yellow-800',
    sent: 'bg-green-100 text-green-800',
    failed: 'bg-red-100 text-red-800',
    bounced: 'bg-orange-100 text-orange-800',
  };

  return (
    <span className={`px-2 py-1 text-xs font-medium rounded-full ${colors[status] || colors.pending}`}>
      {status}
    </span>
  );
}
