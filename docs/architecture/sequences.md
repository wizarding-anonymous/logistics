# Sequence Diagrams

This document illustrates the sequence of interactions between containers for key business flows.

## Flow 1: RFQ Creation to Order Creation

This diagram shows how a client creates an RFQ, a supplier bids on it, the client accepts the offer, and an order is created via an event-driven process.

```mermaid
sequenceDiagram
    participant Client
    participant Frontend
    participant RFQ_Service
    participant Orders_Service
    participant Kafka

    Client->>+Frontend: Submits "Create RFQ" form
    Frontend->>+RFQ_Service: POST /rfqs (Create RFQ)
    RFQ_Service-->>-Frontend: RFQ Created (201)
    Frontend-->>-Client: Shows success message

    Note over Client, Frontend: Time passes... Supplier browses RFQs.

    participant Supplier
    Supplier->>+Frontend: Submits "Offer" form on RFQ details page
    Frontend->>+RFQ_Service: POST /rfqs/{id}/offers
    RFQ_Service-->>-Frontend: Offer Created (201)
    Frontend-->>-Supplier: Shows success message

    Note over Client, Frontend: Time passes... Client reviews offers.

    Client->>+Frontend: Clicks "Accept Offer"
    Frontend->>+RFQ_Service: POST /offers/{id}/accept
    RFQ_Service->>RFQ_Service: Update RFQ status to 'closed', update offer statuses
    RFQ_Service->>+Kafka: Publishes "offer_accepted" event
    RFQ_Service-->>-Frontend: Offer Accepted (200)
    Frontend-->>-Client: Shows success, updates UI

    Kafka-->>+Orders_Service: Consumes "offer_accepted" event
    Orders_Service->>Orders_Service: Creates new Order in database
    deactivate Orders_Service
    deactivate Kafka
```

## Flow 2: Order Completion and Payout

This diagram shows how an order being completed by a supplier triggers the invoicing and payout flow.

```mermaid
sequenceDiagram
    participant Supplier
    participant Frontend
    participant Orders_Service
    participant Payments_Service
    participant Kafka

    Supplier->>+Frontend: Clicks "Update Status" to 'POD_CONFIRMED'
    Frontend->>+Orders_Service: PATCH /orders/{id}/status
    Orders_Service->>Orders_Service: Updates Order status, creates history record
    Orders_Service->>+Kafka: Publishes "order_completed" event
    Orders_Service-->>-Frontend: Order Updated (200)
    Frontend-->>-Supplier: Shows success message

    Kafka-->>+Payments_Service: Consumes "order_completed" event
    Payments_Service->>Payments_Service: Creates Invoice for client
    Payments_Service->>Payments_Service: Creates Payout for supplier with 'PENDING' status
    deactivate Payments_Service
    deactivate Kafka

    Note over Frontend, Payments_Service: Time passes... Admin reviews pending payouts.

    participant Admin
    Admin->>+Frontend: Clicks "Approve Payout" in admin panel
    Frontend->>+Payments_Service: POST /payouts/{id}/approve
    Payments_Service->>Payments_Service: Updates Payout status to 'COMPLETED'
    Payments_Service-->>-Frontend: Payout Approved (200)
    Frontend-->>-Admin: Shows success message
```
