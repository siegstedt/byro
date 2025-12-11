'use client';

import { useState, useRef, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getInboxItems, getInboxItem, uploadFile } from '@/lib/api';
import { InboxItem } from '@/types';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { TriageWorkspace } from '@/features/triage/TriageWorkspace';

export default function InboxPage() {
  const [selectedItem, setSelectedItem] = useState<InboxItem | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const queryClient = useQueryClient();

  const { data: items, isLoading, error } = useQuery({
    queryKey: ['inbox'],
    queryFn: getInboxItems,
  });

  const { data: polledItem } = useQuery({
    queryKey: ['inbox-item', selectedItem?.id],
    queryFn: () => selectedItem ? getInboxItem(selectedItem.id) : null,
    enabled: !!selectedItem && selectedItem.status === 'processing',
    refetchInterval: 2000,
  });

  // Update selectedItem when polled item changes
  useEffect(() => {
    if (polledItem) {
      setSelectedItem(polledItem);
    }
  }, [polledItem]);

  const uploadMutation = useMutation({
    mutationFn: uploadFile,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['inbox'] });
    },
  });

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      uploadMutation.mutate(file);
    }
  };

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  if (isLoading) return <div className="p-6">Loading...</div>;
  if (error) return <div className="p-6">Error loading inbox</div>;

  const inboxList = (
    <div className="space-y-4">
      {items?.map((item: InboxItem) => (
        <Card
          key={item.id}
          className="cursor-pointer hover:shadow-md transition-shadow"
          onClick={() => setSelectedItem(item)}
        >
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-medium">{item.original_filename}</h3>
                <p className="text-sm text-muted-foreground">
                  {new Date(item.created_at).toLocaleDateString()}
                </p>
              </div>
              <Badge
                variant={
                  item.status === 'done'
                    ? 'default'
                    : item.status === 'review'
                    ? 'secondary'
                    : 'destructive'
                }
              >
                {item.status}
              </Badge>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );

  if (selectedItem) {
    return (
      <div className="h-full">
        <div className="grid grid-cols-3 h-full">
          <div className="col-span-1 border-r border-slate-200 dark:border-slate-700 p-6">
            <h1 className="text-2xl font-bold mb-6">Inbox</h1>
            <Button
              onClick={() => setSelectedItem(null)}
              variant="outline"
              className="mb-4"
            >
              Back to List
            </Button>
            {inboxList}
          </div>
          <div className="col-span-2">
            <TriageWorkspace activeItem={selectedItem} />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">Inbox</h1>
      <div className="mb-6">
        <Button onClick={handleUploadClick} disabled={uploadMutation.isPending}>
          {uploadMutation.isPending ? 'Uploading...' : 'Upload Document'}
        </Button>
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.txt"
          onChange={handleFileSelect}
          className="hidden"
        />
      </div>
      {inboxList}
    </div>
  );
}