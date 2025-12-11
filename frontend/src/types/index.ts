export type InboxItem = {
  id: string;
  status: 'processing' | 'review' | 'done' | 'error';
  original_filename: string;
  file_path: string;
  ai_payload: any;
  created_at: string;
};