# Architecture Sequence Diagrams

This document contains sequence diagrams for key business processes in the Logistics Marketplace, as specified in the technical requirements. These diagrams are written in Mermaid syntax.

---

## 1. RFQ Creation and Order Booking Flow

This diagram illustrates the process from a client creating a Request for Quotation (RFQ) to a supplier's offer being accepted and an order being created.

```mermaid
sequenceDiagram
    participant Client
    participant Frontend
    participant API Gateway
    participant RFQ Service
    participant Supplier
    participant Order Service

    Client->>+Frontend: Fills out and submits RFQ form
    Frontend->>+API Gateway: POST /api/v1/rfq (RFQ data)
    API Gateway->>+RFQ Service: create_rfq(data)
    RFQ Service-->>-API Gateway: { rfqId: "..." }
    API Gateway-->>-Frontend: RFQ created successfully
    Frontend-->>-Client: Shows success message and RFQ details

    Note over RFQ Service: System identifies and notifies relevant suppliers.

    Supplier->>+Frontend: Views new RFQ and submits an offer
    Frontend->>+API Gateway: POST /api/v1/rfq/{rfqId}/offers (Offer data)
    API Gateway->>+RFQ Service: create_offer(rfqId, data)
    RFQ Service-->>-API Gateway: { offerId: "..." }
    API Gateway-->>-Frontend: Offer submitted
    Frontend-->>-Supplier: Shows success message

    Note over Client, Supplier: Client reviews offers from one or more suppliers.

    Client->>+Frontend: Accepts a specific offer
    Frontend->>+API Gateway: POST /api/v1/offers/{offerId}/accept
    API Gateway->>+Order Service: create_order_from_offer(offerId)
    Note over Order Service: Fetches offer details, creates a new order, sets status to "created".
    Order Service->>Order Service: Publishes "OrderCreated" event to Kafka
    Order Service-->>-API Gateway: { orderId: "...", status: "created" }
    API Gateway-->>-Frontend: Order created successfully
    Frontend-->>-Client: Redirects to the new order's page
```

---

## 2. Order Completion and Escrow Payment Flow

This diagram shows the process after an order is delivered, leading to the automatic payout to the supplier.

```mermaid
sequenceDiagram
    participant Supplier
    participant Client
    participant Frontend
    participant Order Service
    participant Payment Service
    participant Kafka

    Supplier->>+Frontend: Updates order status to "Delivered" and uploads Proof of Delivery (POD)
    Frontend->>+API Gateway: PATCH /api/v1/orders/{orderId}/status (status: "delivered")
    Frontend->>+API Gateway: POST /api/v1/orders/{orderId}/documents (POD file)

    API Gateway->>+Order Service: update_status(orderId, "delivered")
    Order Service-->>-API Gateway: Success
    API Gateway-->>-Frontend: Status updated

    Note over Client, Frontend: Client receives notification and confirms the delivery.

    Client->>+Frontend: Confirms POD
    Frontend->>+API Gateway: POST /api/v1/orders/{orderId}/confirm-pod
    API Gateway->>+Order Service: confirm_pod(orderId)
    Order Service->>Order Service: Updates order status to "pod_confirmed"
    Order Service->>+Kafka: Publishes "OrderPodConfirmed" event
    Order Service-->>-API Gateway: Success
    API Gateway-->>-Frontend: POD Confirmed

    Kafka->>+Payment Service: Consumes "OrderPodConfirmed" event
    Note over Payment Service: The service now initiates the payout process.
    Payment Service->>Payment Service: 1. Get order details (price, supplier)
    Payment Service->>Payment Service: 2. Calculate marketplace commission
    Payment Service->>Payment Service: 3. Initiate transfer from escrow to supplier's account
    Payment Service->>Payment Service: 4. Record transaction and generate invoices
    Payment Service->>+Kafka: Publishes "PayoutSuccessful" event
```
