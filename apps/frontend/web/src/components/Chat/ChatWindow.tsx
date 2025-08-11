import React, { useEffect, useState } from 'react';
import { useChatHistory, useChatWebSocket } from '@/hooks/useChat';
import { useAuthStore } from '@/state/authStore';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';

export function ChatWindow({ topic }: { topic: string }) {
  const { id: userId } = useAuthStore();
  const { data: history, isLoading } = useChatHistory(topic);
  const { messages: realTimeMessages, sendMessage } = useChatWebSocket(topic, userId || '');

  const [newMessage, setNewMessage] = useState('');
  const [allMessages, setAllMessages] = useState(history?.messages || []);

  // Combine historical and real-time messages
  useEffect(() => {
    if (history?.messages) {
      setAllMessages(history.messages);
    }
  }, [history]);

  useEffect(() => {
    if (realTimeMessages.length > 0) {
      setAllMessages((prev) => [...prev, ...realTimeMessages]);
    }
  }, [realTimeMessages]);

  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    if (newMessage.trim()) {
      sendMessage(newMessage);
      setNewMessage('');
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Chat (Topic: {topic.substring(0,8)}...)</CardTitle>
      </CardHeader>
      <CardContent className="h-64 overflow-y-auto space-y-4 p-4 border-y">
        {isLoading && <p>Loading chat history...</p>}
        {allMessages.map((msg) => (
          <div key={msg.id} className={`flex ${msg.sender_id === userId ? 'justify-end' : 'justify-start'}`}>
            <div className={`p-2 rounded-lg ${msg.sender_id === userId ? 'bg-primary text-primary-foreground' : 'bg-muted'}`}>
              <p className="text-sm">{msg.content}</p>
              <p className="text-xs text-right opacity-70">{new Date(msg.timestamp).toLocaleTimeString()}</p>
            </div>
          </div>
        ))}
      </CardContent>
      <CardFooter>
        <form onSubmit={handleSendMessage} className="flex w-full items-center space-x-2">
            <Input
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                placeholder="Type your message..."
            />
            <Button type="submit">Send</Button>
        </form>
      </CardFooter>
    </Card>
  );
}
