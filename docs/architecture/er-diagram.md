# Entity-Relationship Diagram

This document contains a high-level Entity-Relationship (ER) diagram for the Logistics Marketplace database. It shows the major entities and their relationships. Note that all services share the same database in this implementation, but the tables are logically grouped by service.

```mermaid
erDiagram
    USERS {
        UUID id PK
        string email
        string roles
    }

    ORGANIZATIONS {
        UUID id PK
        string name
    }

    user_organization_link {
        UUID user_id PK, FK
        UUID organization_id PK, FK
        string role
    }

    RFQS {
        UUID id PK
        UUID organization_id FK
        UUID user_id FK
        string status
    }

    OFFERS {
        UUID id PK
        UUID rfq_id FK
        UUID supplier_organization_id FK
        float price_amount
    }

    ORDERS {
        UUID id PK
        UUID client_id FK
        UUID supplier_id FK
        string status
    }

    ORDER_REVIEWS {
        UUID id PK
        UUID order_id FK
        UUID reviewer_id FK
        int rating
    }

    INVOICES {
        UUID id PK
        UUID order_id FK
        UUID organization_id FK
        string status
    }

    PAYOUTS {
        UUID id PK
        UUID order_id FK
        UUID supplier_organization_id FK
        string status
    }

    DISPUTES {
        UUID id PK
        UUID order_id FK
        UUID opened_by_id FK
        string status
    }

    DOCUMENTS {
        UUID id PK
        UUID related_entity_id
        string related_entity_type
    }

    SERVICE_OFFERINGS {
        UUID id PK
        UUID supplier_organization_id FK
        string name
    }

    USERS ||--o{ user_organization_link : "has"
    ORGANIZATIONS ||--o{ user_organization_link : "has"

    ORGANIZATIONS ||--o{ RFQS : "creates"
    ORGANIZATIONS ||--o{ SERVICE_OFFERINGS : "provides"
    ORGANIZATIONS ||--o{ OFFERS : "submits"

    RFQS ||--o{ OFFERS : "receives"

    ORDERS ||--o{ ORDER_REVIEWS : "has"
    ORDERS ||--o{ INVOICES : "generates"
    ORDERS ||--o{ PAYOUTS : "generates"
    ORDERS ||--o{ DISPUTES : "can_have"
    ORDERS ||--o{ DOCUMENTS : "can_have"
```
