import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

import '../models/models.dart';

class ApiService {
  // TODO: Move base URL to a config file
  final String _authBaseUrl = "http://localhost:8080/api/v1/auth";
  final String _rfqBaseUrl = "http://localhost:8080/api/v1/rfqs";
  final String _ordersBaseUrl = "http://localhost:8080/api/v1/orders";
  final _storage = const FlutterSecureStorage();

  Future<Map<String, String>> _getHeaders() async {
    final token = await _storage.read(key: 'access_token');
    return {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer $token',
    };
  }

  Future<bool> login(String email, String password) async {
    final response = await http.post(
      Uri.parse('$_authBaseUrl/token'),
      headers: {'Content-Type': 'application/x-www-form-urlencoded'},
      body: {'username': email, 'password': password},
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      await _storage.write(key: 'access_token', value: data['access_token']);
      await _storage.write(key: 'refresh_token', value: data['refresh_token']);
      return true;
    } else {
      // TODO: Handle errors properly
      print('Failed to login: ${response.body}');
      return false;
    }
  }

  Future<bool> register(String email, String password, String role) async {
    final response = await http.post(
      Uri.parse('$_authBaseUrl/register'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'email': email,
        'password': password,
        'roles': [role],
        'recaptcha_token': 'mock_token_for_dev', // Mocking for mobile
      }),
    );

    if (response.statusCode == 201) {
      return true;
    } else {
      print('Failed to register: ${response.body}');
      return false;
    }
  }

  Future<void> logout() async {
    await _storage.deleteAll();
  }

  Future<String?> getAccessToken() async {
    return await _storage.read(key: 'access_token');
  }

  // RFQ Service
  Future<List<RFQ>> getMyRfqs(String orgId) async {
    final response = await http.get(
      Uri.parse('$_rfqBaseUrl/?org_id=$orgId'),
      headers: await _getHeaders(),
    );
    if (response.statusCode == 200) {
      final List<dynamic> data = jsonDecode(response.body);
      return data.map((json) => RFQ.fromJson(json)).toList();
    } else {
      throw Exception('Failed to load RFQs');
    }
  }

  // Order Service
  Future<List<Order>> getMyOrders(String orgId) async {
    // TODO: The backend needs to be updated to filter orders by orgId
    final response = await http.get(
      Uri.parse('$_ordersBaseUrl/orders'),
      headers: await _getHeaders(),
    );
    if (response.statusCode == 200) {
      final List<dynamic> data = jsonDecode(response.body);
      return data.map((json) => Order.fromJson(json)).toList();
    } else {
      throw Exception('Failed to load Orders');
    }
  }
}
