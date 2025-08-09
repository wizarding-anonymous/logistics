import { useParams } from 'react-router-dom';
import { useOrder } from '@/hooks/useOrder';

function OrderDetailsPage() {
  const { orderId } = useParams<{ orderId: string }>();

  // Ensure orderId is not undefined before passing to the hook
  const { data: order, isLoading, isError, error } = useOrder(orderId || '');

  if (isLoading) {
    return <div>Загрузка данных о заказе...</div>;
  }

  if (isError) {
    return <div>Ошибка при загрузке заказа: {error?.message}</div>;
  }

  if (!order) {
    return <div>Заказ не найден.</div>;
  }

  return (
    <div>
      <h1>Детали Заказа: {order.id}</h1>
      <pre
        style={{
          backgroundColor: '#eee',
          padding: '1rem',
          borderRadius: '8px',
          whiteSpace: 'pre-wrap',
        }}
      >
        {JSON.stringify(order, null, 2)}
      </pre>
      <div style={{ marginTop: '1rem' }}>
        <Link to={`/orders/${order.id}/invoice`}>View Invoice</Link>
      </div>
    </div>
  );
}

export default OrderDetailsPage;
