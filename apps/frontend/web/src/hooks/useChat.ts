import { useQuery } from '@tanstack/react-query';
import { getChatHistory, Message } from '@/services/chatService';
import { useEffect, useState, useRef } from 'react';

export function useChatHistory(topic: string) {
  return useQuery({
    queryKey: ['chatHistory', topic],
    queryFn: () => getChatHistory(topic),
    enabled: !!topic,
  });
}

export function useChatWebSocket(topic: string, userId: string) {
    const [messages, setMessages] = useState<Message[]>([]);
    const websocket = useRef<WebSocket | null>(null);

    useEffect(() => {
        if (!topic || !userId) return;

        // Determine WebSocket protocol
        const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${wsProtocol}//${window.location.host}/api/v1/chat/ws/${topic}/${userId}`;

        const ws = new WebSocket(wsUrl);
        websocket.current = ws;

        ws.onopen = () => {
            console.log(`Connected to WebSocket for topic: ${topic}`);
        };

        ws.onmessage = (event) => {
            const newMessage = JSON.parse(event.data);
            setMessages((prevMessages) => [...prevMessages, newMessage]);
        };

        ws.onclose = () => {
            console.log(`Disconnected from WebSocket for topic: ${topic}`);
        };

        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };

        // Cleanup on component unmount
        return () => {
            ws.close();
        };
    }, [topic, userId]);

    const sendMessage = (content: string) => {
        if (websocket.current?.readyState === WebSocket.OPEN) {
            websocket.current.send(JSON.stringify({ content }));
        }
    };

    return { messages, sendMessage };
}
