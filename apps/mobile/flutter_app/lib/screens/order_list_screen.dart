import 'package:flutter/material.dart';
import '../api/api_service.dart';
import '../models/models.dart';

class OrderListScreen extends StatefulWidget {
  const OrderListScreen({super.key});

  @override
  _OrderListScreenState createState() => _OrderListScreenState();
}

class _OrderListScreenState extends State<OrderListScreen> {
  late Future<List<Order>> _orders;
  final _apiService = ApiService();

  @override
  void initState() {
    super.initState();
    // TODO: Get orgId from user context
    _orders = _apiService.getMyOrders("3fa85f64-5717-4562-b3fc-2c963f66afa6");
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('My Orders')),
      body: FutureBuilder<List<Order>>(
        future: _orders,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          } else if (snapshot.hasError) {
            return Center(child: Text('Error: ${snapshot.error}'));
          } else if (!snapshot.hasData || snapshot.data!.isEmpty) {
            return const Center(child: Text('No orders found.'));
          }

          final orders = snapshot.data!;
          return ListView.builder(
            itemCount: orders.length,
            itemBuilder: (context, index) {
              final order = orders[index];
              return ListTile(
                title: Text('Order #${order.id.substring(0,8)}...'),
                subtitle: Text('Status: ${order.status}'),
                trailing: Text('${order.price} ${order.currency}'),
              );
            },
          );
        },
      ),
    );
  }
}
