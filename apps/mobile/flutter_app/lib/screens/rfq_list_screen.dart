import 'package:flutter/material.dart';
import '../api/api_service.dart';
import '../models/models.dart';

class RfqListScreen extends StatefulWidget {
  const RfqListScreen({super.key});

  @override
  _RfqListScreenState createState() => _RfqListScreenState();
}

class _RfqListScreenState extends State<RfqListScreen> {
  late Future<List<RFQ>> _rfqs;
  final _apiService = ApiService();

  @override
  void initState() {
    super.initState();
    // TODO: Get orgId from user context
    _rfqs = _apiService.getMyRfqs("3fa85f64-5717-4562-b3fc-2c963f66afa6");
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('My RFQs')),
      body: FutureBuilder<List<RFQ>>(
        future: _rfqs,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          } else if (snapshot.hasError) {
            return Center(child: Text('Error: ${snapshot.error}'));
          } else if (!snapshot.hasData || snapshot.data!.isEmpty) {
            return const Center(child: Text('No RFQs found.'));
          }

          final rfqs = snapshot.data!;
          return ListView.builder(
            itemCount: rfqs.length,
            itemBuilder: (context, index) {
              final rfq = rfqs[index];
              return ListTile(
                title: Text('${rfq.origin} to ${rfq.destination}'),
                subtitle: Text('Status: ${rfq.status}'),
              );
            },
          );
        },
      ),
    );
  }
}
