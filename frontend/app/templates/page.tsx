'use client';

import { useQuery } from '@tanstack/react-query';
import { templatesApi } from '@/lib/api';
import { Plus } from 'lucide-react';

export default function TemplatesPage() {
  const { data: templates, isLoading } = useQuery({
    queryKey: ['templates'],
    queryFn: () => templatesApi.list(),
  });

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Templates</h1>
        <button className="inline-flex items-center px-4 py-2 bg-primary-600 text-white rounded-md">
          <Plus className="mr-2 h-4 w-4" />
          New Template
        </button>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {templates?.map((template) => (
          <div key={template._id} className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold">{template.name}</h3>
            <p className="text-sm text-gray-500 mt-2">{template.subject}</p>
            <div className="mt-4 flex items-center text-xs text-gray-400">
              <span>{template.use_llm ? 'AI-Generated' : 'Template'}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
