// A simplified set of models for the mobile app MVP

class RFQ {
  final String id;
  final String status;
  // Simplified for MVP
  final String origin;
  final String destination;

  RFQ({required this.id, required this.status, required this.origin, required this.destination});

  factory RFQ.fromJson(Map<String, dynamic> json) {
    return RFQ(
      id: json['id'],
      status: json['status'],
      // The backend returns a nested structure, we simplify it here
      origin: json['segments']?[0]?['origin_address'] ?? 'N/A',
      destination: json['segments']?[0]?['destination_address'] ?? 'N/A',
    );
  }
}

class Order {
  final String id;
  final String status;
  final double price;
  final String currency;

  Order({required this.id, required this.status, required this.price, required this.currency});

  factory Order.fromJson(Map<String, dynamic> json) {
    return Order(
      id: json['id'],
      status: json['status'],
      price: (json['price_amount'] as num).toDouble(),
      currency: json['price_currency'],
    );
  }
}
