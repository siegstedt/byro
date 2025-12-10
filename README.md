# Byro

The Digital Chief of Staff for the Modern Family Office

> **Mission:** To create a centralized, sovereign "Active Intelligence" layer that sits between the Family Office and the chaos of the outside world. Byro translates the noise of legal administration into structured clarity, ensuring that no obligation is missed and no right is forfeited.

-----

## 📜 Table of Contents

1. [Product Vision](https://www.google.com/search?q=%23product-vision)
2. [Core Concepts](https://www.google.com/search?q=%23core-concepts)
3. [Technical Architecture](https://www.google.com/search?q=%23technical-architecture)
4. [Data & Storage Strategy](https://www.google.com/search?q=%23data--storage-strategy)
5. [Technology Stack](https://www.google.com/search?q=%23technology-stack)
6. [Getting Started (Development)](https://www.google.com/search?q=%23getting-started-development)
7. [Deployment (Home Server)](https://www.google.com/search?q=%23deployment-home-server)
8. [Roadmap](https://www.google.com/search?q=%23roadmap)

-----

## 🔮 Product Vision

Wealth and assets do not just generate returns; they generate **entropy**. Every property, investment vehicle, private equity stake, and luxury asset creates a "liability tail"—a stream of contracts, invoices, compliance notices, and deadlines.

Byro is **not** an accounting tool. It is the **Risk Management Engine**. It captures the "Dark Data" that accounting software misses: the clause in a lease, the warranty on a vehicle, the non-compete in an employment contract, and the renewal window of an insurance policy.

### The Three Horizons

1. **The Sovereign Archive:** A unified, searchable repository for every legal document and correspondence.
2. **The Sentinel:** Proactive monitoring of deadlines, renewal dates, and compliance obligations.
3. **The Agent:** A semi-autonomous actor capable of drafting correspondence, verifying invoices against contracts, and executing administrative tasks.

-----

## 🧠 Core Concepts

To develop for Byro, you must understand its domain language:

* **The Inbox (Triage):** The entry point. Raw files (PDFs, Emails) land here. They are "Unprocessed" until the AI extracts metadata and a human reviews it.
* **Matters:** The central container. A Matter represents a real-world entity or topic (e.g., *"The Munich Apartment Lease"*, *"2024 Tax Audit"*, *"Family Trust Governance"*).
  * *Note:* A Matter is dynamic. Its schema changes based on its **Category** (e.g., a "Lease" has `rent_amount`, an "Insurance Policy" has `deductible`).
* **Documents:** The evidence. These are the immutable files linked to a Matter (The signed contract, the amendment, the angry letter).
* **Events:** Time-based triggers derived from documents (e.g., *"Lease Expiry Date"*, *"Payment Due Date"*).
* **Liabilities:** Financial obligations tracked against a contract. Not a bank ledger, but a "Promise to Pay" ledger.

-----

## 🏗 Technical Architecture

Byro is designed as a distributed, containerized system. It decouples the **Storage** of files from the **Logic** of the application, allowing for future hardware scaling.

```mermaid
graph TD
    User[User (MacBook/iPad)] -->|Tailscale VPN| Nginx[Nginx Reverse Proxy]
    
    subgraph "Docker Compose Network"
        Nginx -->|/api| API[FastAPI Backend]
        Nginx -->|/| UI[Next.js Frontend]
        
        API --> DB[(PostgreSQL + pgvector)]
        API --> Redis[(Redis Cache)]
        
        API -->|Enqueue Task| Worker[Celery Worker]
        Worker -->|Read Task| Redis
        Worker -->|Store Result| DB
        
        %% External Services
        Worker -->|API Call| LLM[OpenAI / Anthropic]
        
        %% Storage Abstraction
        API -->|File I/O| Storage[Storage Service]
        Storage -.->|Currently| LocalVol[Local Docker Volume]
        Storage -.->|Future| NAS[Synology NAS / S3]
    end
```

### Key Design Decisions

1. **Schema-Driven UI (SDUI):** The backend defines the "shape" of data (Templates). The frontend renders generic components based on these definitions. This allows us to add new Contract Categories without rewriting frontend code.
2. **Asynchronous Processing:** OCR and LLM extraction take time (5-30s). We use **Celery** to handle these background tasks so the HTTP API remains lightning fast.
3. **Hybrid AI approach:** We use cloud-based LLMs (OpenAI `gpt-4o`) for high-reasoning tasks (Extraction) to compensate for limited home-server hardware, while keeping the database and files strictly local.

-----

## 💾 Data & Storage Strategy

### Database (PostgreSQL)

We use a **Hybrid Relational/Document** model.

* **Strict Tables:** Users, Permissions, IDs, Timestamps.
* **Flexible Columns:** `jsonb` is used for the `attributes` of a Matter. This allows infinite flexibility for different contract types.
* **Vector Embeddings:** We use `pgvector` to store embeddings of document text, powering the semantic search ("The Oracle").

### File Storage (The Abstraction Layer)

Currently, files are stored on the VM's disk. However, the architecture anticipates a migration to a Synology NAS.

* **Current State:** `LocalFileSystemService`. Files are saved to `/app/data/uploads` inside the Docker container, mapped to a physical directory on the host VM.
* **Future State:** `S3StorageService`. When the Synology NAS is ready, we will enable its S3-compatible MinIO service. We will then swap the storage backend in Byro configuration to point to the NAS.
* **Implication:** Code must *never* use `open('path/to/file')` directly. It must use the `storage_service.save()` and `storage_service.get()` abstraction methods.

-----

## 🛠 Technology Stack

### Application Layer

* **Frontend:** [Next.js 16+](https://nextjs.org/) (App Router), TypeScript, Tailwind CSS, React Query.
* **Backend:** [FastAPI](https://fastapi.tiangolo.com/) (Python 3.13+).
* **ORM:** [SQLAlchemy](https://www.sqlalchemy.org/) (Async).
* **Schema Validation:** [Pydantic](https://www.google.com/search?q=https://docs.pydantic.dev/).

### Intelligence Layer

* **LLM Orchestration:** [LangChain](https://www.langchain.com/).
* **OCR:** `Unstructured.io` / `PyPDF2`.
* **Embeddings:** OpenAI `text-embedding-3-small`.

### Infrastructure

* **Containerization:** Docker & Docker Compose.
* **Host OS:** Ubuntu Server 24.04 LTS (Proxmox VM).
* **Networking:** Tailscale (Mesh VPN).

-----

## 🚀 Getting Started (Development)

Follow these steps to set up the project on your local MacBook for development.

### 1\. Prerequisites

* Docker Desktop installed.
* Git.
* An OpenAI API Key.

### 2\. Clone & Config

```bash
git clone https://github.com/siegstedt/byro.git
cd byro

# Create the environment file
cp .env.example .env
```

**Configure your `.env` file:**

```ini
# Core
PROJECT_NAME="Byro Dev"
ENV="development"

# AI Provider
OPENAI_API_KEY="sk-..."

# Database (Default Docker credentials)
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=byro
POSTGRES_HOST=db

# Storage
STORAGE_BACKEND="local" # Options: local, s3
UPLOAD_DIR="/data/uploads"
```

### 3\. Run with Docker Compose

This spins up the entire stack: Frontend, Backend, DB, Redis, and Worker.

```bash
docker-compose up --build
```

### 4\. Access the App

* **Frontend:** `http://localhost:3000`
* **Backend Docs (Swagger):** `http://localhost:8000/docs`
* **Database GUI (pgAdmin):** `http://localhost:5050`

-----

## 📡 Deployment (Home Server)

To deploy to your Proxmox Ubuntu VM.

1. **SSH into the VM** (via Tailscale or Local IP).
2. **Clone the Repo:**

    ```bash
    git clone https://github.com/siegstedt/byro.git /opt/byro
    ```

3. **Setup Production Config:**
    Create a `.env.prod` file. Ensure `ENV="production"`.
4. **Data Persistence:**
    Ensure the `docker-compose.prod.yml` maps the volumes to a persistent path on the host, e.g., `/mnt/data/byro_uploads`.
5. **Run:**

    ```bash
    docker-compose -f docker-compose.prod.yml up -d
    ```

6. **Update Strategy:**

    ```bash
    git pull
    docker-compose -f docker-compose.prod.yml up -d --build
    ```

-----

## 🗺 Roadmap

### Phase 1: The Foundation (Current)

* [ ] Dockerized Environment Setup.
* [ ] Database Schema Design (Matters, Documents, Triage).
* [ ] Basic File Ingestion (Upload & OCR).
* [ ] LLM Extraction Pipeline (The "Triage" View).

### Phase 2: The Core Experience

* [ ] "Matters" Dashboard with Timeline View.
* [ ] Dynamic Attribute Rendering (Schema-Driven UI).
* [ ] Semantic Search Implementation.

### Phase 3: The Connected Home (Hardware Integration)

* [ ] **Synology NAS Integration:** Migrating `LocalFileSystemService` to `S3StorageService`.
* [ ] Calendar Export (.ics feed).

### Phase 4: Agentic Capabilities

* [ ] Automated "Draft Email" generation.
* [ ] "Chat with Document" interface.

-----

## 📄 License

**Private & Proprietary.**
Designed exclusively for private Family Office usage. Not for public distribution.
