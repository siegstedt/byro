'use client';

import { useState, useEffect } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import dynamic from 'next/dynamic';
import { InboxItem } from '@/types';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { createMatter, attachDocument } from '@/lib/api';

const PdfViewer = dynamic(() => import('@/components/ui/pdf-viewer').then(mod => mod.PdfViewer), { ssr: false });

interface TriageWorkspaceProps {
  activeItem: InboxItem;
}

export function TriageWorkspace({ activeItem }: TriageWorkspaceProps) {
  const [title, setTitle] = useState('');
  const [date, setDate] = useState('');
  const [amount, setAmount] = useState('');
  const [mode, setMode] = useState<'new' | 'existing'>('new');
  const queryClient = useQueryClient();

  // Populate form when item becomes review
  useEffect(() => {
    if (activeItem.status === 'review' && activeItem.ai_payload) {
      setTitle(activeItem.ai_payload.title || '');
      setDate(activeItem.ai_payload.document_date || '');
      const amountValue = activeItem.ai_payload.total_value;
      // Only set amount if it's a valid number
      if (typeof amountValue === 'number' && !isNaN(amountValue)) {
        setAmount(amountValue.toString());
      } else {
        setAmount('');
      }
    }
  }, [activeItem]);

  const createMutation = useMutation({
    mutationFn: ({ data, inboxItemId }: { data: any; inboxItemId: string }) =>
      createMatter(data, inboxItemId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['inbox'] });
      alert('Matter created successfully!');
    },
  });

  const attachMutation = useMutation({
    mutationFn: ({ matterId, inboxItemId }: { matterId: string; inboxItemId: string }) =>
      attachDocument(matterId, inboxItemId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['inbox'] });
      alert('Document attached successfully!');
    },
  });

  const handleSave = () => {
    if (mode === 'new') {
      // Prepare attributes, filtering out empty values
      const attributes: any = {};
      if (date) attributes.date = date;
      if (amount) attributes.amount = parseFloat(amount) || amount;

      createMutation.mutate({
        data: {
          title,
          category: activeItem.ai_payload?.category || 'contract',
          attributes: Object.keys(attributes).length > 0 ? attributes : undefined,
        },
        inboxItemId: activeItem.id,
      });
    } else {
      // For existing, hardcode a matter id for now
      attachMutation.mutate({
        matterId: 'some-matter-id',
        inboxItemId: activeItem.id,
      });
    }
  };

  return (
    <div className="grid grid-cols-2 h-full">
      {/* Left Panel - Document Viewer */}
      <div className="border-r border-slate-200 dark:border-slate-700 p-6">
        <PdfViewer url={`http://localhost:8000/static/${activeItem.file_path}`} />
      </div>

      {/* Right Panel - Extraction Form */}
      <div className="p-6">
        <h2 className="text-xl font-semibold mb-6">Extract Information</h2>
        <Tabs value={mode} onValueChange={(value) => setMode(value as 'new' | 'existing')}>
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="new">Create New Matter</TabsTrigger>
            <TabsTrigger value="existing">Attach to Existing</TabsTrigger>
          </TabsList>
          <TabsContent value="new" className="space-y-4 mt-6">
            <div>
              <Label htmlFor="title">Matter Title</Label>
              <Input
                id="title"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Document title"
              />
            </div>
            <div>
              <Label htmlFor="date">Date</Label>
              <Input
                id="date"
                type="date"
                value={date}
                onChange={(e) => setDate(e.target.value)}
              />
            </div>
            <div>
              <Label htmlFor="amount">Amount</Label>
              <Input
                id="amount"
                type="number"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                placeholder="0.00"
              />
            </div>
            <Button onClick={handleSave} className="w-full">
              Confirm & Save
            </Button>
          </TabsContent>
          <TabsContent value="existing" className="space-y-4 mt-6">
            <div>
              <Label htmlFor="matter">Select Existing Matter</Label>
              <select id="matter" className="w-full p-2 border rounded">
                <option>Contract with ABC Corp</option>
                <option>Lease Agreement</option>
                <option>Invoice #123</option>
              </select>
            </div>
            <Button onClick={handleSave} className="w-full">
              Confirm & Save
            </Button>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}