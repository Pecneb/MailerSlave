'use client';

import { useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { campaignsApi, templatesApi, contactsApi, emailsApi } from '@/lib/api';
import { ArrowLeft, Send, Pause, Trash2, Calendar, Users, FileText, Mail, AlertCircle, CheckCircle, XCircle } from 'lucide-react';
import Link from 'next/link';
import { toast } from 'sonner';
import { format } from 'date-fns';

export default function CampaignDetailPage() {
  const params = useParams();
  const router = useRouter();
  const queryClient = useQueryClient();
  const campaignId = params.id as string;
  
  const [showSendModal, setShowSendModal] = useState(false);
  const [dryRun, setDryRun] = useState(false);

  // Fetch campaign details
  const { data: campaign, isLoading: campaignLoading } = useQuery({
    queryKey: ['campaigns', campaignId],
    queryFn: () => campaignsApi.get(campaignId),
  });

  // Fetch template
  const { data: template } = useQuery({
    queryKey: ['templates', campaign?.template_id],
    queryFn: () => templatesApi.get(campaign!.template_id),
    enabled: !!campaign?.template_id,
  });

  // Fetch email logs for this campaign
  const { data: emailLogs } = useQuery({
    queryKey: ['emails', 'campaign', campaignId],
    queryFn: () => emailsApi.list(0, 1000, campaignId),
  });

  // Send campaign mutation
  const sendMutation = useMutation({
    mutationFn: () => campaignsApi.send(campaignId, { dry_run: dryRun }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['campaigns', campaignId] });
      queryClient.invalidateQueries({ queryKey: ['campaigns'] });
      toast.success(dryRun ? 'Dry run completed' : 'Campaign sending started');
      setShowSendModal(false);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to send campaign');
    },
  });

  // Delete campaign mutation
  const deleteMutation = useMutation({
    mutationFn: () => campaignsApi.delete(campaignId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['campaigns'] });
      toast.success('Campaign deleted');
      router.push('/campaigns');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to delete campaign');
    },
  });

  const handleSend = () => {
    sendMutation.mutate();
  };

  const handleDelete = () => {
    if (confirm('Are you sure you want to delete this campaign? This action cannot be undone.')) {
      deleteMutation.mutate();
    }
  };

  if (campaignLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-gray-500">Loading campaign...</div>
      </div>
    );
  }

  if (!campaign) {
    return (
      <div className="space-y-6">
        <div className="flex items-center space-x-4">
          <Link href="/campaigns" className="text-gray-600 hover:text-gray-900">
            <ArrowLeft className="h-6 w-6" />
          </Link>
          <h1 className="text-3xl font-bold text-gray-900">Campaign Not Found</h1>
        </div>
      </div>
    );
  }

  const canSend = campaign.status === 'draft' || campaign.status === 'paused';
  const canDelete = campaign.status !== 'in_progress';

  const statusColor = {
    draft: 'bg-gray-100 text-gray-800',
    scheduled: 'bg-blue-100 text-blue-800',
    in_progress: 'bg-yellow-100 text-yellow-800',
    completed: 'bg-green-100 text-green-800',
    failed: 'bg-red-100 text-red-800',
    paused: 'bg-orange-100 text-orange-800',
  }[campaign.status] || 'bg-gray-100 text-gray-800';

  return (
    <div className="space-y-6 max-w-6xl">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Link href="/campaigns" className="text-gray-600 hover:text-gray-900">
            <ArrowLeft className="h-6 w-6" />
          </Link>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{campaign.name}</h1>
            <p className="mt-1 text-gray-600">{campaign.description}</p>
          </div>
        </div>
        <div className="flex items-center space-x-3">
          {canSend && (
            <button
              onClick={() => setShowSendModal(true)}
              className="inline-flex items-center px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700"
            >
              <Send className="mr-2 h-4 w-4" />
              Send Now
            </button>
          )}
          {canDelete && (
            <button
              onClick={handleDelete}
              disabled={deleteMutation.isPending}
              className="inline-flex items-center px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 disabled:opacity-50"
            >
              <Trash2 className="mr-2 h-4 w-4" />
              Delete
            </button>
          )}
        </div>
      </div>

      {/* Status & Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Status</p>
              <p className={`mt-2 inline-block px-3 py-1 text-sm font-medium rounded-full ${statusColor}`}>
                {campaign.status}
              </p>
            </div>
            <AlertCircle className="h-8 w-8 text-gray-400" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Recipients</p>
              <p className="mt-2 text-3xl font-bold text-gray-900">{campaign.total_emails}</p>
            </div>
            <Users className="h-8 w-8 text-blue-400" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Sent</p>
              <p className="mt-2 text-3xl font-bold text-green-600">{campaign.sent_count}</p>
            </div>
            <CheckCircle className="h-8 w-8 text-green-400" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Failed</p>
              <p className="mt-2 text-3xl font-bold text-red-600">{campaign.failed_count}</p>
            </div>
            <XCircle className="h-8 w-8 text-red-400" />
          </div>
        </div>
      </div>

      {/* Campaign Details */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Template Info */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
            <FileText className="mr-2 h-5 w-5" />
            Template
          </h2>
          {template ? (
            <div className="space-y-3">
              <div>
                <span className="text-sm text-gray-600">Name:</span>
                <p className="font-medium text-gray-900">{template.name}</p>
              </div>
              <div>
                <span className="text-sm text-gray-600">Subject:</span>
                <p className="font-medium text-gray-900">{template.subject}</p>
              </div>
              <div>
                <span className="text-sm text-gray-600">Type:</span>
                <span className={`ml-2 px-2 py-1 text-xs font-medium rounded-full ${
                  template.use_llm ? 'bg-purple-100 text-purple-800' : 'bg-gray-100 text-gray-800'
                }`}>
                  {template.use_llm ? 'AI-Generated' : 'Standard'}
                </span>
              </div>
              <div>
                <span className="text-sm text-gray-600">Variables:</span>
                <div className="mt-1 flex flex-wrap gap-1">
                  {template.placeholders.map((placeholder) => (
                    <span key={placeholder} className="px-2 py-1 bg-blue-50 text-blue-700 text-xs rounded">
                      ${placeholder}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <p className="text-gray-500">Loading template...</p>
          )}
        </div>

        {/* Timeline */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
            <Calendar className="mr-2 h-5 w-5" />
            Timeline
          </h2>
          <div className="space-y-3">
            <div>
              <span className="text-sm text-gray-600">Created:</span>
              <p className="font-medium text-gray-900">{format(new Date(campaign.created_at), 'PPpp')}</p>
            </div>
            {campaign.scheduled_at && (
              <div>
                <span className="text-sm text-gray-600">Scheduled:</span>
                <p className="font-medium text-gray-900">{format(new Date(campaign.scheduled_at), 'PPpp')}</p>
              </div>
            )}
            {campaign.started_at && (
              <div>
                <span className="text-sm text-gray-600">Started:</span>
                <p className="font-medium text-gray-900">{format(new Date(campaign.started_at), 'PPpp')}</p>
              </div>
            )}
            {campaign.completed_at && (
              <div>
                <span className="text-sm text-gray-600">Completed:</span>
                <p className="font-medium text-gray-900">{format(new Date(campaign.completed_at), 'PPpp')}</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Email Logs */}
      {emailLogs && emailLogs.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
            <Mail className="mr-2 h-5 w-5" />
            Email Logs ({emailLogs.length})
          </h2>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead>
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Recipient</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Subject</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Sent At</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {emailLogs.slice(0, 10).map((log) => (
                  <tr key={log._id}>
                    <td className="px-4 py-3 text-sm text-gray-900">{log.contact_id}</td>
                    <td className="px-4 py-3 text-sm text-gray-900">{log.subject}</td>
                    <td className="px-4 py-3 text-sm">
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                        log.status === 'sent' ? 'bg-green-100 text-green-800' :
                        log.status === 'failed' ? 'bg-red-100 text-red-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {log.status}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-500">
                      {log.sent_at ? format(new Date(log.sent_at), 'PPpp') : '-'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {emailLogs.length > 10 && (
              <p className="mt-3 text-sm text-gray-500 text-center">
                Showing 10 of {emailLogs.length} emails
              </p>
            )}
          </div>
        </div>
      )}

      {/* Send Confirmation Modal */}
      {showSendModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
            <h3 className="text-xl font-semibold text-gray-900 mb-4">Send Campaign</h3>
            <p className="text-gray-600 mb-4">
              Are you sure you want to send this campaign to {campaign.total_emails} recipients?
            </p>
            
            <div className="mb-6">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={dryRun}
                  onChange={(e) => setDryRun(e.target.checked)}
                  className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                />
                <span className="ml-2 text-sm text-gray-700">
                  Dry run (test without actually sending emails)
                </span>
              </label>
            </div>

            <div className="flex space-x-3">
              <button
                onClick={handleSend}
                disabled={sendMutation.isPending}
                className="flex-1 px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:opacity-50"
              >
                {sendMutation.isPending ? 'Sending...' : dryRun ? 'Run Test' : 'Send Now'}
              </button>
              <button
                onClick={() => setShowSendModal(false)}
                className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
