import React, { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useDispute, useAddDisputeMessage } from '@/hooks/useDisputes';
import { useAuthStore } from '@/state/authStore';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';

function DisputePage() {
  const { orderId } = useParams<{ orderId: string }>();
  const { data: dispute, isLoading } = useDispute(orderId!);
  const { id: userId } = useAuthStore();
  const addMessage = useAddDisputeMessage();
  const [newMessage, setNewMessage] = useState('');

  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    if (newMessage.trim() && dispute) {
      addMessage.mutate({ disputeId: dispute.id, content: newMessage });
      setNewMessage('');
    }
  };

  if (isLoading) return <div className="p-6">Loading dispute information...</div>;
  if (!dispute) return (
    <div className="p-6">
        <p>No dispute found for this order.</p>
        {/* TODO: Add a form here to open a dispute */}
        <Link to={`/orders/${orderId}`}>
            <Button variant="link">Back to Order</Button>
        </Link>
    </div>
  );

  return (
    <div className="space-y-6 p-4 md:p-6 max-w-4xl mx-auto">
      <h2 className="text-3xl font-bold tracking-tight">Dispute for Order #{dispute.order_id.substring(0, 8)}</h2>

      <Card>
        <CardHeader>
          <CardTitle>Dispute History</CardTitle>
          <CardDescription>Status: {dispute.status}</CardDescription>
        </CardHeader>
        <CardContent className="h-96 overflow-y-auto space-y-4 p-4 border-y">
          {dispute.messages.map((msg) => (
            <div key={msg.id} className={`flex ${msg.sender_id === userId ? 'justify-end' : 'justify-start'}`}>
              <div className={`p-3 rounded-lg max-w-lg ${msg.sender_id === userId ? 'bg-primary text-primary-foreground' : 'bg-muted'}`}>
                <p className="text-sm font-semibold">User {msg.sender_id.substring(0,6)}...</p>
                <p className="text-md">{msg.content}</p>
                <p className="text-xs text-right opacity-70 mt-1">{new Date(msg.timestamp).toLocaleString()}</p>
              </div>
            </div>
          ))}
        </CardContent>
        <CardContent>
            <form onSubmit={handleSendMessage} className="flex w-full items-center space-x-2 pt-4">
                <Textarea
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    placeholder="Type your message..."
                    className="flex-grow"
                />
                <Button type="submit" disabled={addMessage.isPending}>
                    {addMessage.isPending ? 'Sending...' : 'Send'}
                </Button>
            </form>
        </CardContent>
      </Card>
    </div>
  );
}

export default DisputePage;
