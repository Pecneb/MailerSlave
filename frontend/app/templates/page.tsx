'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { templatesApi } from '@/lib/api';
import { Plus, FileText, X, Edit } from 'lucide-react';
import { useState } from 'react';
import { toast } from 'sonner';
import type { TemplateCreate } from '@/lib/types';

export default function TemplatesPage() {
  const queryClient = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState<any>(null);

  const { data: templates, isLoading, error } = useQuery({
    queryKey: ['templates'],
    queryFn: () => templatesApi.list(),
  });

  const createMutation = useMutation({
    mutationFn: templatesApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['templates'] });
      toast.success('Template created successfully');
      setShowForm(false);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to create template');
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<TemplateCreate> }) => 
      templatesApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['templates'] });
      toast.success('Template updated successfully');
      setEditingTemplate(null);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to update template');
    },
  });

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    const template: TemplateCreate = {
      name: formData.get('name') as string,
      subject: formData.get('subject') as string,
      content: formData.get('content') as string,
      description: formData.get('description') as string,
      use_llm: formData.get('use_llm') === 'on',
    };
    
    if (editingTemplate) {
      updateMutation.mutate({ id: editingTemplate._id, data: template });
    } else {
      createMutation.mutate(template);
    }
  };

  const handleEdit = (template: any) => {
    setEditingTemplate(template);
  };

  const handleCloseForm = () => {
    setShowForm(false);
    setEditingTemplate(null);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-gray-500">Loading templates...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-6">
        <h1 className="text-3xl font-bold text-gray-900">Templates</h1>
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">Failed to load templates. Make sure the backend is running.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Templates</h1>
          <p className="mt-2 text-gray-600">Create and manage email templates</p>
        </div>
        <button 
          onClick={() => setShowForm(true)}
          className="inline-flex items-center px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700"
        >
          <Plus className="mr-2 h-4 w-4" />
          New Template
        </button>
      </div>

      {/* Create/Edit Template Modal */}
      {(showForm || editingTemplate) && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex justify-between items-center">
              <h2 className="text-xl font-semibold text-gray-900">
                {editingTemplate ? 'Edit Template' : 'Create New Template'}
              </h2>
              <button 
                onClick={handleCloseForm}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
            
            <form onSubmit={handleSubmit} className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Template Name *
                </label>
                <input
                  type="text"
                  name="name"
                  required
                  defaultValue={editingTemplate?.name || ''}
                  placeholder="e.g., Welcome Email"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 text-gray-900"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Email Subject *
                </label>
                <input
                  type="text"
                  name="subject"
                  required
                  defaultValue={editingTemplate?.subject || ''}
                  placeholder="e.g., Welcome to our platform!"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 text-gray-900"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Description
                </label>
                <input
                  type="text"
                  name="description"
                  defaultValue={editingTemplate?.description || ''}
                  placeholder="Optional description for this template"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 text-gray-900"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Email Content *
                </label>
                <textarea
                  name="content"
                  required
                  rows={10}
                  defaultValue={editingTemplate?.content || ''}
                  placeholder="Hi $first_name,&#10;&#10;Welcome to our platform!&#10;&#10;You can use variables like $first_name, $last_name, $company, etc."
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 font-mono text-sm text-gray-900"
                />
                <p className="mt-1 text-xs text-gray-500">
                  Use $variable_name or ${'{variable_name}'} for placeholders
                </p>
              </div>

              <div className="flex items-center">
                <input
                  type="checkbox"
                  name="use_llm"
                  id="use_llm"
                  defaultChecked={editingTemplate?.use_llm || false}
                  className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                />
                <label htmlFor="use_llm" className="ml-2 block text-sm text-gray-700">
                  Use AI (Ollama) to generate personalized variations
                </label>
              </div>

              <div className="flex space-x-3 pt-4">
                <button
                  type="submit"
                  disabled={createMutation.isPending || updateMutation.isPending}
                  className="flex-1 px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {editingTemplate 
                    ? (updateMutation.isPending ? 'Updating...' : 'Update Template')
                    : (createMutation.isPending ? 'Creating...' : 'Create Template')
                  }
                </button>
                <button
                  type="button"
                  onClick={handleCloseForm}
                  className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {templates && templates.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {templates.map((template) => (
            <div key={template._id} className="bg-white rounded-lg shadow hover:shadow-lg transition p-6">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900">{template.name}</h3>
                  <p className="text-sm text-gray-500 mt-2">{template.subject}</p>
                  {template.description && (
                    <p className="text-xs text-gray-400 mt-1">{template.description}</p>
                  )}
                </div>
                <FileText className="h-5 w-5 text-gray-400" />
              </div>
              <div className="mt-4 flex items-center justify-between">
                <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                  template.use_llm 
                    ? 'bg-purple-100 text-purple-800' 
                    : 'bg-gray-100 text-gray-800'
                }`}>
                  {template.use_llm ? 'AI-Generated' : 'Standard'}
                </span>
                <span className="text-xs text-gray-400">
                  {template.placeholders.length} variables
                </span>
              </div>
              <div className="mt-4 pt-4 border-t border-gray-200">
                <button
                  onClick={() => handleEdit(template)}
                  className="w-full inline-flex items-center justify-center px-3 py-2 text-sm text-blue-600 hover:text-blue-700 hover:bg-blue-50 rounded-md transition"
                >
                  <Edit className="h-4 w-4 mr-2" />
                  Edit Template
                </button>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <FileText className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-4 text-lg font-medium text-gray-900">No templates yet</h3>
          <p className="mt-2 text-sm text-gray-500">
            Get started by creating your first email template.
          </p>
          <button 
            onClick={() => setShowForm(true)}
            className="mt-6 inline-flex items-center px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700"
          >
            <Plus className="mr-2 h-4 w-4" />
            Create Template
          </button>
        </div>
      )}
    </div>
  );
}
