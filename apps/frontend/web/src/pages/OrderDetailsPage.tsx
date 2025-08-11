import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useOrder, useUpdateOrderStatus, useSubmitReview } from '@/hooks/useOrder';
import { useDispute } from '@/hooks/useDisputes';
import { useDocuments } from '@/hooks/useDocs';
import { useAuthStore } from '@/state/authStore';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { ChatWindow } from '@/components/Chat/ChatWindow';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { LeaveReviewForm } from '@/components/Reviews/LeaveReviewForm';
import { Link } from 'react-router-dom';
import { DocumentUpload } from '@/components/Documents/DocumentUpload';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';

function UpdateStatusForm({ orderId, currentStatus }: { orderId: string, currentStatus: string }) {
    const { mutate: updateStatus, isPending } = useUpdateOrderStatus();
    const [newStatus, setNewStatus] = useState(currentStatus);

    const handleUpdate = () => {
        if (newStatus !== currentStatus) {
            updateStatus({ orderId, status: newStatus });
        }
    };

    // Example statuses a supplier can set
    const availableStatuses = ["in_transit", "delivered"];

    return (
        <Card className="mt-6">
            <CardHeader>
                <CardTitle>Update Order Status</CardTitle>
            </CardHeader>
            <CardContent className="flex items-center gap-4">
                <Select value={newStatus} onValueChange={setNewStatus}>
                    <SelectTrigger className="w-[180px]">
                        <SelectValue placeholder="Select status" />
                    </SelectTrigger>
                    <SelectContent>
                        {availableStatuses.map(status => (
                            <SelectItem key={status} value={status}>{status.replace('_', ' ')}</SelectItem>
                        ))}
                    </SelectContent>
                </Select>
                <Button onClick={handleUpdate} disabled={isPending || newStatus === currentStatus}>
                    {isPending ? 'Updating...' : 'Update Status'}
                </Button>
            </CardContent>
        </Card>
    );
}


function OrderDetailsPage() {
  const { orderId } = useParams<{ orderId: string }>();
  const { data: order, isLoading, isError, error } = useOrder(orderId!);
  const { data: dispute } = useDispute(orderId!);
  const { data: documents } = useDocuments('order', orderId!);
  const { organizationId, id: userId } = useAuthStore();

  const isSupplierForOrder = order?.supplier_id === organizationId;
  const isClientForOrder = order?.client_id === organizationId;
  const isOrderComplete = order?.status === 'closed' || order?.status === 'pod_confirmed';

  if (isLoading) return <div className="p-6">Loading order details...</div>;
  if (isError) return <div className="p-6 text-red-500">Error: {error.message}</div>;
  if (!order) return <div className="p-6">Order not found.</div>;

  return (
    <div className="space-y-6 p-4 md:p-6 max-w-4xl mx-auto">
        <div className="flex justify-between items-start">
            <div>
                <h2 className="text-3xl font-bold tracking-tight">Order #{order.id.substring(0, 8)}</h2>
                <p className="text-muted-foreground">Status: <span className="font-semibold">{order.status}</span></p>
            </div>
            <div className="flex flex-col items-end gap-2">
                {isSupplierForOrder && <UpdateStatusForm orderId={order.id} currentStatus={order.status} />}
                <Link to={`/orders/${order.id}/dispute`}>
                    <Button variant="destructive">{dispute ? 'View Dispute' : 'Open Dispute'}</Button>
                </Link>
            </div>
        </div>

        <Tabs defaultValue="details" className="w-full">
            <TabsList className="grid w-full grid-cols-3">
                <TabsTrigger value="details">Details</TabsTrigger>
                <TabsTrigger value="documents">Documents</TabsTrigger>
                <TabsTrigger value="chat">Chat</TabsTrigger>
            </TabsList>
            <TabsContent value="details">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-4">
                    <Card>
                        <CardHeader><CardTitle>Shipment Info</CardTitle></CardHeader>
                        <CardContent className="space-y-2">
                            <p><strong>Client:</strong> {order.client_id.substring(0,8)}...</p>
                            <p><strong>Supplier:</strong> {order.supplier_id.substring(0,8)}...</p>
                            <p><strong>Price:</strong> {order.price_amount} {order.price_currency}</p>
                        </CardContent>
                    </Card>
                    <Card>
                        <CardHeader><CardTitle>Tracking History</CardTitle></CardHeader>
                        <CardContent>
                            <ul className="space-y-4">
                                {order.status_history.map((history, index) => (
                                    <li key={index} className="flex gap-4">
                                        <div className="font-semibold">{new Date(history.timestamp).toLocaleTimeString()}</div>
                                        <div>
                                            <p>{history.status.replace('_', ' ')}</p>
                                            {history.notes && <p className="text-sm text-muted-foreground">{history.notes}</p>}
                                        </div>
                                    </li>
                                ))}
                            </ul>
                        </CardContent>
                    </Card>
                </div>
            </TabsContent>
            <TabsContent value="documents">
                <Card className="mt-4">
                    <CardHeader><CardTitle>Order Documents</CardTitle></CardHeader>
                    <CardContent>
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead>Filename</TableHead>
                                    <TableHead>Type</TableHead>
                                    <TableHead className="text-right">Actions</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {documents?.map(doc => (
                                    <TableRow key={doc.id}>
                                        <TableCell>{doc.filename}</TableCell>
                                        <TableCell>{doc.document_type.toUpperCase()}</TableCell>
                                        <TableCell className="text-right">
                                            <a href={doc.download_url} target="_blank" rel="noopener noreferrer">
                                                <Button variant="outline" size="sm">Download</Button>
                                            </a>
                                        </TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                        {isSupplierForOrder && <DocumentUpload entityType="order" entityId={order.id} documentType="pod" />}
                    </CardContent>
                </Card>
            </TabsContent>
            <TabsContent value="chat">
                <ChatWindow topic={order.id} />
            </TabsContent>
        </Tabs>

        {isClientForOrder && isOrderComplete && !order.review && (
            <LeaveReviewForm orderId={order.id} />
        )}

        {order.review && (
            <Card className="mt-6">
                <CardHeader><CardTitle>Your Review</CardTitle></CardHeader>
                <CardContent>
                    <p><strong>Rating:</strong> {order.review.rating} / 5</p>
                    <p className="text-muted-foreground mt-2">{order.review.comment}</p>
                </CardContent>
            </Card>
        )}
    </div>
  );
}

export default OrderDetailsPage;
