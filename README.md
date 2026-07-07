<div align="center">

# Prime TechHub
### Containerized Edge-Routed Infrastructure Orchestration Engine

**A full-stack smart home e-commerce platform engineered as a multi-container cloud-native system.**  
Built on Python · Streamlit · SQLite · Docker · Nginx · Render Cloud Pipeline

---

**[🌐 Live Cloud Prototype Interface](https://prime-techhub.onrender.com)**

> **⚠️ Cold-Start Notice — Free-Tier Cloud Container Environment**  
> This application is deployed on Render's free-tier container pipeline. When the service is inactive, the platform deallocates compute resources. Upon your first request, Render will re-provision the container — expect an initial **30 to 45 second startup delay** before the interface loads. This is a platform-level compute allocation behavior, not an application performance defect. Subsequent interactions within the same session are unaffected.

---

![Python](https://img.shields.io/badge/Python-3.14-blue?style=flat-square&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.x-red?style=flat-square&logo=streamlit)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?style=flat-square&logo=docker)
![Nginx](https://img.shields.io/badge/Nginx-Reverse%20Proxy-009639?style=flat-square&logo=nginx)
![SQLite](https://img.shields.io/badge/SQLite-Persistent%20DB-003B57?style=flat-square&logo=sqlite)
![License](https://img.shields.io/badge/License-Academic%20FYP-lightgrey?style=flat-square)

</div>

---

## Table of Contents

1. [System Profile](#system-profile)
2. [Architectural Blueprint](#architectural-blueprint)
3. [Infrastructure Stack](#infrastructure-stack)
4. [Repository Structure](#repository-structure)
5. [Deployment Methodology](#deployment-methodology)
6. [Local Setup](#local-setup)
7. [Feature Matrix](#feature-matrix)
8. [Database Schema](#database-schema)
9. [Evaluator Access Guide](#evaluator-access-guide)
10. [Scholarship & Academic Context](#scholarship--academic-context)

---

## System Profile

Prime TechHub is a Final Year Project (FYP) developed as a demonstration of production-grade containerized infrastructure engineering. The surface layer is a functional smart home device e-commerce storefront — but the project's primary technical contribution is its **infrastructure orchestration architecture**: a multi-container deployment pipeline using Docker, Nginx reverse proxying with WebSocket persistence, and a cloud-native CI/CD delivery chain routed through a managed container build engine.

The application is not presented as a commercial product. It is engineered as a **reference implementation of cloud-ready full-stack infrastructure**, demonstrating skills directly applicable to cloud infrastructure roles and graduate programs in distributed systems and IT infrastructure management.

### Core Engineering Contributions

| Domain | Implementation |
|--------|---------------|
| Containerization | Multi-layer `Dockerfile` with build-cache optimization and headless execution flags |
| Reverse Proxying | `nginx.conf` with explicit HTTP Upgrade and Connection headers for WebSocket persistence |
| Service Orchestration | `docker-compose.yml` defining two-service network topology with named volume binding |
| Database Persistence | SQLite file externalized to a named Docker volume (`techhub_data:/app/data`) |
| Cloud CI/CD Pipeline | Automated Dockerfile-driven build on Render's container platform via GitHub push triggers |
| Frontend Architecture | Multi-page Streamlit application with session-state routing, fragment isolation, and global CSS injection |
| Backend Logic | SQLite schema with `customers`, `products`, `orders` tables; full CRUD via Python `sqlite3` |

---

## Architectural Blueprint

### Local Multi-Container Data Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                     LOCAL DEPLOYMENT TOPOLOGY                        │
│                                                                       │
│   ┌────────────────┐                                                  │
│   │ External Client │                                                  │
│   │  (Evaluator)    │                                                  │
│   └───────┬────────┘                                                  │
│           │                                                            │
│           │  HTTP Request — Port 80                                   │
│           ▼                                                            │
│   ┌────────────────────────────────────────┐                          │
│   │          CONTAINER: nginx              │                          │
│   │          Image: nginx:alpine           │                          │
│   │          Public Port: 80               │                          │
│   │                                        │                          │
│   │  nginx.conf handles:                   │                          │
│   │  • HTTP Upgrade header forwarding      │                          │
│   │  • WebSocket Connection persistence    │                          │
│   │  • proxy_buffering off (streaming)     │                          │
│   │  • 86400s timeout for live sessions    │                          │
│   └────────────────┬───────────────────────┘                          │
│                    │                                                   │
│                    │  Internal Bridge Network: primetechhub_net        │
│                    │  proxy_pass → streamlit:8501                      │
│                    ▼                                                   │
│   ┌────────────────────────────────────────┐                          │
│   │         CONTAINER: streamlit           │                          │
│   │         Image: python:3.14-slim        │                          │
│   │         Internal Port: 8501 (hidden)   │                          │
│   │                                        │                          │
│   │  Runs: streamlit run app.py            │                          │
│   │  Flags: --server.headless=true         │                          │
│   │         --server.enableCORS=false      │                          │
│   │         --server.enableXsrfProtection=false                       │
│   └────────────────┬───────────────────────┘                          │
│                    │                                                   │
│                    │  Named Docker Volume                              │
│                    │  techhub_data → /app/data/                        │
│                    ▼                                                   │
│   ┌────────────────────────────────────────┐                          │
│   │    PERSISTENT STORAGE LAYER            │                          │
│   │    data/techhub.db (SQLite)            │                          │
│   │    Survives: container restart         │                          │
│   │    Survives: docker compose down       │                          │
│   │    Cleared by: --volumes flag only     │                          │
│   └────────────────────────────────────────┘                          │
└─────────────────────────────────────────────────────────────────────┘
```

### Cloud Deployment Data Flow (Render Pipeline)

```
┌─────────────────────────────────────────────────────────────────────┐
│                    CLOUD DEPLOYMENT TOPOLOGY                         │
│                                                                       │
│   ┌────────────────┐                                                  │
│   │ Client Browser │                                                  │
│   └───────┬────────┘                                                  │
│           │                                                            │
│           │  HTTPS (Port 443)                                         │
│           ▼                                                            │
│   ┌────────────────────────────────────────┐                          │
│   │     RENDER INGRESS EDGE LAYER          │                          │
│   │                                        │                          │
│   │  • Automatic SSL/TLS termination       │                          │
│   │  • Native WebSocket handshake support  │                          │
│   │  • Load balancing & DDoS protection    │                          │
│   │  • Free-tier cold-start provisioning   │                          │
│   └────────────────┬───────────────────────┘                          │
│                    │                                                   │
│                    │  Routes to containerized application             │
│                    ▼                                                   │
│   ┌────────────────────────────────────────┐                          │
│   │   AUTOMATED DOCKERFILE BUILD ENGINE    │                          │
│   │                                        │                          │
│   │  Trigger: GitHub push to main branch   │                          │
│   │  Process: docker build from Dockerfile │                          │
│   │  Base:    python:3.14-slim             │                          │
│   │  Install: requirements.txt via pip     │                          │
│   │  Expose:  Port 8501 (mapped by Render) │                          │
│   │  Entry:   streamlit run app.py         │                          │
│   └────────────────┬───────────────────────┘                          │
│                    │                                                   │
│                    ▼                                                   │
│   ┌────────────────────────────────────────┐                          │
│   │   SQLITE LOCAL WORKSPACE LAYER         │                          │
│   │   data/techhub.db                      │                          │
│   │                                        │                          │
│   │  Note: Free-tier ephemeral storage     │                          │
│   │  Database reseeds on container restart │                          │
│   │  Product catalog: seeded via           │                          │
│   │  _seed_catalog() at init_db()          │                          │
│   │  Production fix: named volume mount    │                          │
│   │  (documented in docker-compose.yml)    │                          │
│   └────────────────────────────────────────┘                          │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Infrastructure Stack

### Language & Framework

| Component | Technology | Version |
|-----------|-----------|---------|
| Backend Language | Python | 3.14 |
| Web UI Framework | Streamlit | ≥ 1.56 |
| Database Engine | SQLite | Built-in (`sqlite3`) |
| UI Components | streamlit-option-menu | Latest |

### Infrastructure & DevOps

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Containerization | Docker | Reproducible build environment |
| Service Orchestration | Docker Compose | Two-service local topology |
| Reverse Proxy | Nginx (alpine) | WebSocket routing, port abstraction |
| Cloud Pipeline | Render | Automated Dockerfile CI/CD |
| Version Control | Git + GitHub | Source of truth and deployment trigger |

---

## Repository Structure

```
Prime-TechHub/
│
├── app.py                   # Application entry point — all page routing,
│                            # session state management, CSS injection, UI logic
│
├── database.py              # SQLite interface layer — schema creation,
│                            # CRUD operations, catalog seeding, auth logic
│
├── requirements.txt         # Frozen Python dependency manifest
│                            # Generated via: pip freeze > requirements.txt
│
├── Dockerfile               # Container image definition
│                            # Base: python:3.14-slim
│                            # Installs requirements, exposes 8501
│                            # CMD: streamlit run with headless flags
│
├── docker-compose.yml       # Multi-container orchestration definition
│                            # Services: streamlit (8501) + nginx (80)
│                            # Volume: techhub_data:/app/data
│                            # Network: primetechhub_net (bridge)
│
├── nginx.conf               # Reverse proxy configuration
│                            # upstream: streamlit:8501
│                            # Upgrade + Connection headers for WebSocket
│                            # proxy_buffering off, 86400s timeouts
│
├── nginx/
│   └── Dockerfile           # Nginx service image for multi-platform deploy
│                            # Base: nginx:alpine
│                            # Copies nginx.conf to /etc/nginx/
│
├── .dockerignore            # Build exclusion manifest
│                            # Blocks: venv/, __pycache__/, .git/, media files
│
├── .streamlit/
│   └── config.toml          # Streamlit server configuration
│
└── data/
    └── .gitkeep             # Ensures data/ directory is tracked by Git
                             # techhub.db is excluded via .gitignore
                             # and managed by Docker volume at runtime
```

---

## Deployment Methodology

### Dockerfile — Build Reproducibility

The `Dockerfile` is configured from a `python:3.14-slim` base image — a Debian-based minimal Python environment that excludes development headers and documentation layers, reducing the final image size. Build instructions are sequenced to exploit Docker's layer caching behavior: `requirements.txt` is copied and installed before application source code, ensuring that a code-only change does not trigger a full dependency reinstall.

```dockerfile
# Layer order is intentional — requirements installed before source copy
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
```

Streamlit is launched with four explicit flags that are mandatory in containerized environments:

| Flag | Purpose |
|------|---------|
| `--server.headless=true` | Disables browser auto-launch behavior |
| `--server.address=0.0.0.0` | Binds to all network interfaces, not only loopback |
| `--server.enableCORS=false` | Delegates CORS handling to Nginx |
| `--server.enableXsrfProtection=false` | Required when operating behind a reverse proxy |

### .dockerignore — Image Hygiene

The `.dockerignore` file prevents local environment artifacts from entering the build context. The `venv/` directory alone can exceed 400MB; excluding it reduces build transfer time from minutes to seconds and eliminates the risk of platform-specific binary conflicts between the local Windows environment and the Linux container.

### nginx.conf — WebSocket Persistence

Streamlit uses persistent WebSocket connections for real-time UI state updates. A standard Nginx proxy configuration will fail silently: the browser connects on HTTP, Nginx accepts the request, but never forwards the `Upgrade: websocket` signal to the upstream Streamlit process. The result is an infinite loading spinner with no error output.

The configuration addresses this explicitly:

```nginx
proxy_http_version 1.1;
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "upgrade";
proxy_buffering off;
proxy_read_timeout 86400s;
```

`proxy_buffering off` is equally critical — with buffering active, Nginx holds Streamlit's streaming output in memory until a buffer fills before forwarding it to the browser, causing the page to hang.

### docker-compose.yml — Volume Persistence Strategy

SQLite stores its entire database as a single file (`data/techhub.db`). Without a persistent storage mount, this file is destroyed each time the container is stopped or rebuilt. The `docker-compose.yml` maps a named Docker volume to the `/app/data/` directory inside the Streamlit container:

```yaml
volumes:
  - techhub_data:/app/data
```

Named volumes are managed by the Docker engine independently of the container lifecycle. The file survives `docker compose down` and container rebuilds. It is only removed when explicitly requested via `docker compose down --volumes`.

### Cloud vs. Local Orchestration

The `docker-compose.yml` and `nginx.conf` files serve a dual function:

1. **Local execution**: When Docker Desktop is available on a compatible host OS (Windows 10 Build 19041+, macOS, or Linux), `docker compose up --build` launches the full two-container topology locally with a single command.

2. **Documentation artifact**: On the cloud deployment via Render, the platform's ingress routing layer handles SSL termination, WebSocket persistence, and port mapping natively. Render builds directly from the `Dockerfile` rather than executing the compose specification. The `docker-compose.yml` and `nginx.conf` remain in the repository as executable infrastructure-as-code — any evaluator can run the full stack locally on a compatible machine.

This mirrors standard enterprise practice: infrastructure definitions live in version control and serve both local developer environments and cloud orchestration pipelines.

---

## Local Setup

### Prerequisites

- Python 3.14
- Git
- Docker Desktop (Windows 10 Build 19041+ / macOS / Linux) — required for containerized mode only
- pip

### Without Docker (Development Mode)

```bash
# Clone the repository
git clone https://github.com/Aysha-Nur/Prime-TechHub.git
cd Prime-TechHub

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate        # Windows
source venv/bin/activate       # macOS / Linux

# Install dependencies
pip install -r requirements.txt

# Create data directory
mkdir data

# Run the application
streamlit run app.py
```

Access at: `http://localhost:8501`

### With Docker (Full Infrastructure Mode)

```bash
# Clone the repository
git clone https://github.com/Aysha-Nur/Prime-TechHub.git
cd Prime-TechHub

# Build and start both containers
docker compose up --build

# Access via Nginx reverse proxy
# Open: http://localhost
```

Verify container health:
```bash
docker compose ps
docker compose logs streamlit --follow
docker compose logs nginx --follow
```

Stop containers (database volume preserved):
```bash
docker compose down
```

---

## Feature Matrix

### Storefront

| Feature | Status |
|---------|--------|
| Hero banner with trust indicators | ✅ |
| Horizontal-scroll featured devices (9 categories) | ✅ |
| Category filter chips (scrollable, 10 categories) | ✅ |
| Product grid — 27 devices, 3-column layout | ✅ |
| Category thumbnail images (Unsplash CDN) | ✅ |
| Per-card stock status indicators | ✅ |
| Product detail view (name, price, specs, trust badges) | ✅ |
| Native responsive fluid layout architecture | ✅ |

### Cart & Checkout

| Feature | Status |
|---------|--------|
| Session-state dict cart (`{product_id: {qty, name, price}}`) | ✅ |
| +/− quantity controls per item | ✅ |
| Order receipt breakdown (Subtotal + GST 17% + Platform Fee) | ✅ |
| Sandbox card payment (4242 4242 4242 4242) | ✅ |
| Cash on Delivery option | ✅ |
| Digital receipt with order ID | ✅ |
| Guest cart viewing (login required at checkout only) | ✅ |

### Account System

| Feature | Status |
|---------|--------|
| Customer registration (email + password, SQLite) | ✅ |
| Customer login / logout | ✅ |
| Admin login (username: `admin`, password: `admin123`) | ✅ |
| Password change (verified against DB, SHA-plain) | ✅ |
| Order history display | ✅ |

### Admin Dashboard

| Feature | Status |
|---------|--------|
| Add product to inventory | ✅ |
| Remove product from inventory | ✅ |
| Sales ledger with revenue metric | ✅ |
| Admin-only tab visibility | ✅ |

---

## Database Schema

```sql
-- Registered customers
CREATE TABLE IF NOT EXISTS customers (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    name     TEXT    NOT NULL,
    email    TEXT    UNIQUE NOT NULL,
    password TEXT    NOT NULL
);

-- Smart home device catalog
CREATE TABLE IF NOT EXISTS products (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL,
    category    TEXT    NOT NULL,
    price       REAL    NOT NULL,
    stock       INTEGER NOT NULL,
    description TEXT
);

-- Order / sales ledger
CREATE TABLE IF NOT EXISTS orders (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id  INTEGER,
    product_name TEXT    NOT NULL,
    price        REAL    NOT NULL,
    sale_date    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

-- Admin credentials (static record, seeded at init_db)
CREATE TABLE IF NOT EXISTS users (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT    UNIQUE NOT NULL,
    password TEXT    NOT NULL,
    role     TEXT    NOT NULL
);
```

### Product Catalog

The 27-product catalog is seeded at startup via `_seed_catalog()`. The function performs a name-based existence check before inserting, making it safe to call on every application launch without producing duplicates.

Categories: Camera · Lighting · Smart Plug · Hub/Controller · Sensors · Networking · Audio · Security · Climate

---

## Evaluator Access Guide

### Standard Login (Use This for Testing)

| Role | Username / Email | Password |
|------|-----------------|----------|
| Administrator | `admin` | `admin123` |
| Test Customer | Register via Account tab | Your choice |

The application uses a local SQLite database (`data/techhub.db`) for all authentication. Registration creates a live record in the `customers` table, and login verifies against it directly.

### Note for Academic Evaluators

The **"Sign in with Google"** button visible on the Account page is configured as a production-environment OAuth 2.0 link asset. In the current deployment context (free-tier cloud and local development environments), it routes to the project's GitHub repository authentication documentation — it does not execute an OAuth token exchange flow.

**Evaluators must use the standard email/password registration flow** to interact with the persistent SQLite authentication layer. This is the intended testing path for all graded evaluation sessions.

OAuth 2.0 integration is for live production environment. The current implementation demonstrates the correct UI component placement and production link structure. Production OAUTH 2.0 integration is deliberately deffered to restrict live user data collection during demonstration phase.

---

## Scholarship & Academic Context

This project was developed as a Final Year Project in partial fulfillment of a Bachelor's degree in Computer Science / IT Infrastructure, with deliberate architectural decisions made to align with the competency profile of graduate programs in Cloud Computing and Distributed Systems Infrastructure — specifically Erasmus Mundus Joint Master's programmes and DAAD-funded research tracks.

### Engineering Decisions Mapped to Infrastructure Competencies

| Decision | Competency Demonstrated |
|----------|------------------------|
| Dockerfile with explicit layer ordering | Container image optimization; build reproducibility |
| Nginx with WebSocket Upgrade headers | Reverse proxy engineering; real-time protocol handling |
| Named Docker volume for SQLite | Stateful container persistence; ephemeral storage problem resolution |
| docker-compose.yml two-service topology | Service orchestration; internal network isolation |
| GitHub → Render CI/CD pipeline | Automated cloud deployment; infrastructure-as-code principles |
| `@st.cache_data` on database reads | Backend performance optimization; cache-aside pattern |
| Session-state routing with `page_override` | SPA-style navigation without a dedicated frontend framework |

### Project Constraints & Honest Limitations

| Constraint | Detail |
|-----------|--------|
| Database engine | SQLite — appropriate for single-instance academic deployment; production scale would require PostgreSQL + connection pooling |
| Authentication | Plain-text password storage — adequate for FYP scope; production requires `bcrypt` or `argon2` hashing |
| OAuth | UI component present; full OAuth exchange not implemented in free-tier deployment |
| Cloud persistence | Free-tier Render container resets `techhub.db` on sleep; production volume mount resolves this |
| Local Docker | Full two-container local execution requires Windows 10 Build 19041+; architecture documented and cloud-executable |

---

## Acknowledgements

Developed independently as a Final Year Project. Infrastructure architecture, session management design, database schema, and deployment pipeline engineered by the project author. UI aesthetic inspired by Apple and Samsung design system principles.

---

<div align="center">

**Prime TechHub** · Final Year Project · Academic Year 2025–2026

*Containerized Edge-Routed Infrastructure Orchestration Engine*

</div>