'use client';

import { useQuery } from '@tanstack/react-query';
import { getMatters } from '@/lib/api';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

export default function MattersPage() {
  const { data: matters, isLoading, error } = useQuery({
    queryKey: ['matters'],
    queryFn: getMatters,
  });

  if (isLoading) return <div className="p-6">Loading...</div>;
  if (error) return <div className="p-6">Error loading matters</div>;

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">Matters</h1>
      <div className="space-y-4">
        {matters?.map((matter: any) => (
          <Card key={matter.id}>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-medium">{matter.title}</h3>
                  <p className="text-sm text-muted-foreground">
                    {new Date(matter.created_at).toLocaleDateString()}
                  </p>
                </div>
                <Badge>{matter.category}</Badge>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}