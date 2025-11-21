'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { campaignsApi, templatesApi, contactsApi } from '@/lib/api';
import { ArrowLeft, Send, Calendar, Users, FileText } from 'lucide-react';
import Link from 'next/link';
import { toast } from 'sonner';
import type { CampaignCreate } from '@/lib/types';

export default function NewCampaignPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    template_id: '',
    scheduled_at: '',
  });
  const [selectedContacts, setSelectedContacts] = useState<string[]>([]);
  const [selectAll, setSelectAll] = useState(false);

  // Fetch templates and contacts
  const { data: templates, isLoading: templatesLoading } = useQuery({
    queryKey: ['templates'],
    queryFn: () => templatesApi.list(),
  });

  const { data: contacts, isLoading: contactsLoading } = useQuery({
    queryKey: ['contacts'],
    queryFn: () => contactsApi.list(),
  });

  const [sendImmediately, setSendImmediately] = useState(false);

  // Create campaign mutation
  const createMutation = useMutation({
    mutationFn: async (campaign: CampaignCreate) => {
      const created = await campaignsApi.create(campaign);
      
      // If no scheduled date and sendImmediately is true, send right away
      if (sendImmediately && !campaign.scheduled_at) {
        await campaignsApi.send(created._id, { dry_run: false });
      }
      
      return created;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['campaigns'] });
      if (sendImmediately && !formData.scheduled_at) {
        toast.success('Campaign created and sending started');
      } else {
        toast.success('Campaign created successfully');
      }
      router.push(`/campaigns/${data._id}`);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to create campaign');
    },
  });

  const handleSelectAll = () => {
    if (selectAll) {
      setSelectedContacts([]);
    } else {
      setSelectedContacts(contacts?.map(c => c._id) || []);
    }
    setSelectAll(!selectAll);
  };

  const handleContactToggle = (contactId: string) => {
    if (selectedContacts.includes(contactId)) {
      setSelectedContacts(selectedContacts.filter(id => id !== contactId));
    } else {
      setSelectedContacts([...selectedContacts, contactId]);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (selectedContacts.length === 0) {
      toast.error('Please select at least one contact');
      return;
    }

    const campaign: CampaignCreate = {
      name: formData.name,
      template_id: formData.template_id,
      contact_ids: selectedContacts,
      description: formData.description || undefined,
      scheduled_at: formData.scheduled_at || undefined,
    };

    createMutation.mutate(campaign);
  };

  const isLoading = templatesLoading || contactsLoading;

  return (
    <div className="space-y-6 max-w-4xl">
      <div className="flex items-center space-x-4">
        <Link 
          href="/campaigns" 
          className="text-gray-600 hover:text-gray-900"
        >
          <ArrowLeft className="h-6 w-6" />
        </Link>
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Create New Campaign</h1>
          <p className="mt-2 text-gray-600">Set up a new email campaign</p>
        </div>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center h-96">
          <div className="text-gray-500">Loading...</div>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-8">
          {/* Basic Information */}
          <div className="bg-white rounded-lg shadow p-6 space-y-4">
            <h2 className="text-xl font-semibold text-gray-900 flex items-center">
              <FileText className="mr-2 h-5 w-5" />
              Campaign Details
            </h2>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Campaign Name *
              </label>
              <input
                type="text"
                required
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="e.g., Spring 2024 Newsletter"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 text-gray-900"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Description
              </label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="Optional description of this campaign"
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 text-gray-900"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Email Template *
              </label>
              <select
                required
                value={formData.template_id}
                onChange={(e) => setFormData({ ...formData, template_id: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 text-gray-900"
              >
                <option value="">Select a template</option>
                {templates?.map((template) => (
                  <option key={template._id} value={template._id}>
                    {template.name} {template.use_llm ? '(AI)' : ''}
                  </option>
                ))}
              </select>
              {templates?.length === 0 && (
                <p className="mt-1 text-sm text-amber-600">
                  No templates available. <Link href="/templates" className="underline">Create one first</Link>.
                </p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                <Calendar className="inline h-4 w-4 mr-1" />
                Schedule Send (Optional)
              </label>
              <input
                type="datetime-local"
                value={formData.scheduled_at}
                onChange={(e) => setFormData({ ...formData, scheduled_at: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 text-gray-900"
              />
              <p className="mt-1 text-xs text-gray-500">
                Schedule for later or leave empty
              </p>
            </div>

            {!formData.scheduled_at && (
              <div className="border-t border-gray-200 pt-4">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={sendImmediately}
                    onChange={(e) => setSendImmediately(e.target.checked)}
                    className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                  />
                  <span className="ml-2 text-sm text-gray-700">
                    <Send className="inline h-4 w-4 mr-1" />
                    Send immediately after creating campaign
                  </span>
                </label>
                <p className="mt-1 ml-6 text-xs text-gray-500">
                  Emails will start sending right away to all selected recipients
                </p>
              </div>
            )}
          </div>

          {/* Contact Selection */}
          <div className="bg-white rounded-lg shadow p-6 space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-semibold text-gray-900 flex items-center">
                <Users className="mr-2 h-5 w-5" />
                Select Recipients
              </h2>
              <div className="text-sm text-gray-600">
                {selectedContacts.length} of {contacts?.length || 0} selected
              </div>
            </div>

            {contacts && contacts.length > 0 ? (
              <>
                <div className="flex items-center border-b border-gray-200 pb-3">
                  <input
                    type="checkbox"
                    checked={selectAll}
                    onChange={handleSelectAll}
                    className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                  />
                  <label className="ml-2 text-sm font-medium text-gray-700">
                    Select All Contacts
                  </label>
                </div>

                <div className="max-h-96 overflow-y-auto space-y-2">
                  {contacts.map((contact) => (
                    <div
                      key={contact._id}
                      className="flex items-center p-3 hover:bg-gray-50 rounded-md"
                    >
                      <input
                        type="checkbox"
                        checked={selectedContacts.includes(contact._id)}
                        onChange={() => handleContactToggle(contact._id)}
                        className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                      />
                      <div className="ml-3 flex-1">
                        <div className="text-sm font-medium text-gray-900">
                          {contact.first_name && contact.last_name
                            ? `${contact.first_name} ${contact.last_name}`
                            : contact.email}
                        </div>
                        <div className="text-xs text-gray-500">{contact.email}</div>
                      </div>
                      {!contact.active && (
                        <span className="text-xs text-red-600">Inactive</span>
                      )}
                    </div>
                  ))}
                </div>
              </>
            ) : (
              <div className="text-center py-8">
                <p className="text-gray-500">No contacts available.</p>
                <Link 
                  href="/contacts" 
                  className="mt-2 inline-block text-primary-600 hover:text-primary-700 underline"
                >
                  Add contacts first
                </Link>
              </div>
            )}
          </div>

          {/* Submit Buttons */}
          <div className="flex items-center justify-end space-x-3">
            <Link
              href="/campaigns"
              className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
            >
              Cancel
            </Link>
            <button
              type="submit"
              disabled={createMutation.isPending || selectedContacts.length === 0}
              className="inline-flex items-center px-6 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Send className="mr-2 h-4 w-4" />
              {createMutation.isPending 
                ? (sendImmediately && !formData.scheduled_at ? 'Creating & Sending...' : 'Creating...') 
                : (sendImmediately && !formData.scheduled_at ? 'Create & Send' : 'Create Campaign')}
            </button>
          </div>
        </form>
      )}
    </div>
  );
}
