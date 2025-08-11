import axios from 'axios';
import { z } from 'zod';

// =================================
// Zod Schemas
// =================================

const MessageSchema = z.object({
  id: z.string().uuid(),
  thread_id: z.string().uuid(),
  sender_id: z.string().uuid(),
  content: z.string(),
  timestamp: z.string().datetime(),
});

const ChatThreadSchema = z.object({
    id: z.string().uuid(),
    topic: z.string(),
    created_at: z.string().datetime(),
    messages: z.array(MessageSchema),
});

export type ChatThread = z.infer<typeof ChatThreadSchema>;
export type Message = z.infer<typeof MessageSchema>;

// =================================
// API Client Setup
// =================================

const apiClient = axios.create({
  baseURL: '/api/v1/chat',
});

// Note: Auth token would be needed here in a real app, but we'll omit
// the interceptor for now as the backend also has placeholder security.

// =================================
// API Functions
// =================================

export const getChatHistory = async (topic: string): Promise<ChatThread> => {
  const response = await apiClient.get(`/history/${topic}`);
  return ChatThreadSchema.parse(response.data);
};
