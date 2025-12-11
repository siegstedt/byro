import axios from 'axios';
import { InboxItem } from '../types';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
});

export const getInboxItems = async (): Promise<InboxItem[]> => {
  const response = await api.get('/inbox');
  return response.data;
};

export const getInboxItem = async (id: string): Promise<InboxItem> => {
  const response = await api.get(`/inbox/${id}`);
  return response.data;
};

export const createMatter = async (data: { title: string; category: string; attributes?: any }, inboxItemId: string) => {
  const response = await api.post(`/matters?inbox_item_id=${inboxItemId}`, data);
  return response.data;
};

export const attachDocument = async (matterId: string, inboxItemId: string) => {
  const response = await api.post(`/matters/${matterId}/documents`, { inbox_item_id: inboxItemId });
  return response.data;
};

export const getMatters = async () => {
  const response = await api.get('/matters');
  return response.data;
};

export const uploadFile = async (file: File): Promise<InboxItem> => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await api.post('/inbox/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};