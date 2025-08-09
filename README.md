# Enterprise SaaS - Logistics Services Marketplace

This repository contains the source code for a B2B/B2C marketplace for logistics services. It is a multi-tenant, microservices-based application built on a modern technology stack.

## About The Project

This platform connects shippers (clients) with logistics providers (suppliers). Clients can create tenders (RFQs) for their shipping needs, and suppliers can bid on these tenders. The platform aims to handle the entire lifecycle of a logistics order, from quoting and booking to tracking, documentation, and payment.

### Tech Stack

-   **Backend:** Python (FastAPI), SQLAlchemy, Pydantic
-   **Frontend:** React, TypeScript, Vite, React Query
-   **Mobile:** Flutter (Placeholder)
-   **Databases:** PostgreSQL, Redis, Elasticsearch
-   **Infrastructure:** Docker, Kubernetes (Helm), NGINX
-   **Messaging:** Kafka
-   **CI/CD:** GitHub Actions

## Getting Started

Follow these instructions to get a local copy of the project up and running for development and testing.

### Prerequisites

You must have the following software installed on your machine:
-   [Docker](https://www.docker.com/get-started)
-   [Docker Compose](https://docs.docker.com/compose/install/) (usually included with Docker Desktop)
-   `make` (optional, for using the Makefile shortcuts)

### Local Installation & Setup

1.  **Clone the repository:**
    ```sh
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  **Environment Variables:**
    The `docker-compose.yml` file is configured to use a `.env` file for sensitive data and local configuration. You can create one by copying the example:
    ```sh
    # You can create a .env file, but the docker-compose has sensible defaults.
    # For example:
    # POSTGRES_USER=admin
    # POSTGRES_PASSWORD=password
    # POSTGRES_DB=marketplace
    ```

3.  **Start the environment:**
    Use the provided `Makefile` to start all services. This command will start all the infrastructure services (Postgres, Kafka, etc.) in detached mode.
    ```sh
    make up
    ```
    To check the status of the running containers, use:
    ```sh
    make ps
    # or
    docker compose ps
    ```

4.  **Running Services:**
    Currently, the `docker-compose.yml` only starts the infrastructure. To run the backend and frontend services, you would typically add them to the `docker-compose.yml` and run `make build` and `make up`.

    **To run the `orders` service locally (example):**
    ```sh
    cd apps/backend/services/orders
    pip install -r requirements.txt
    uvicorn main:app --reload
    ```
    The service will be available at `http://localhost:8000`.

    **To run the frontend service locally:**
    ```sh
    cd apps/frontend/web
    npm install
    npm run dev
    ```
    The frontend will be available at `http://localhost:5173`.

5.  **Stopping the environment:**
    To stop all running containers, use:
    ```sh
    make down
    ```

## Monorepo Structure

The repository is organized as a monorepo with the following structure:

-   `apps/`: Contains the source code for the individual applications (microservices, frontend, mobile).
    -   `backend/services/`: Each backend microservice lives here (e.g., `orders`).
    -   `frontend/web/`: The main React web application.
-   `docs/`: Contains API specifications (OpenAPI) and architecture documents.
-   `infra/`: Contains infrastructure-as-code definitions (Docker, Kubernetes, Kafka schemas).
-   `.github/`: Contains CI/CD workflow definitions for GitHub Actions.

## Next Steps

-   Implement tests for backend and frontend services.
-   Add more services as defined in the architecture.
-   Complete the Flutter mobile application.
-   Flesh out the Helm charts for production deployment.
