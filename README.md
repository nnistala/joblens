# 🔍 JobLens — India-First Unified Job Aggregator

> **Stop missing jobs because they're only on one platform.**

JobLens aggregates job listings from company career pages, ATS platforms (Greenhouse, Lever, Workday, Taleo), and public job boards into a single, deduplicated, searchable feed — built specifically for the Indian job market.

[![Live Prototype](https://img.shields.io/badge/Live%20Demo-GitHub%20Pages-blue?style=for-the-badge&logo=github)](https://nnistala.github.io/joblens-prototype/)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Planning%20%2F%20Scaffolding-yellow?style=for-the-badge)]()

---

## 🚀 Why JobLens?

Amazon has ~2,200 active openings. Here's how they're distributed across platforms:

| Platform | Listings | Coverage |
|----------|----------|----------|
| LinkedIn | 820 | 37% |
| Indeed | 610 | 28% |
| Naukri | 140 | 6% |
| Other boards | 320 | 15% |
| **Common across all** | 120 | **5%** |

**You need ALL sources to see the complete picture.** JobLens does that.

---

## ✨ Features (Planned)

- 🕷️ **Multi-source crawling** — Career pages, Greenhouse, Lever, Workday, Taleo, Indeed, Glassdoor
- 🔄 **Smart deduplication** — Exact hash → Fuzzy title match → Semantic similarity (future)
- 🔍 **Full-text search** — Powered by OpenSearch
- 📬 **Job alerts** — Get notified when new matching jobs appear
- 🏢 **HR Direct Portal** — Companies can self-register their career page URLs
- 🔐 **Auth** — Google & LinkedIn OAuth2
- 💰 **Freemium** — Free for job seekers, premium for advanced features

---

## 🧱 Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend** | FastAPI (Python 3.12+), SQLAlchemy 2.0, Alembic |
| **Crawling** | Scrapy + Playwright |
| **Queue** | Celery + Redis |
| **Database** | PostgreSQL 16, OpenSearch 8, Redis |
| **Frontend** | Next.js 14, TypeScript, Tailwind CSS, shadcn/ui |
| **Auth** | JWT + OAuth2 (Google, LinkedIn) |
| **Infra** | Docker, Terraform, GitHub Actions, AWS (ECS, RDS, ElastiCache) |

---

## 📁 Project Structure

```
joblens/
├── backend/
│   ├── app/              # FastAPI application
│   │   ├── api/v1/       # REST API routes
│   │   ├── core/         # Config, deps, security
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # Business logic
│   │   └── crud/         # Database operations
│   ├── crawlers/         # Scrapy spiders
│   │   ├── spiders/      # Greenhouse, Lever, generic, Indeed
│   │   └── pipelines/    # Data normalization
│   └── tasks/            # Celery tasks (crawl, dedup, alerts)
├── frontend/
│   └── src/
│       ├── app/          # Next.js App Router pages
│       ├── components/   # UI components
│       └── lib/          # API client, utilities
├── infra/
│   ├── terraform/        # AWS infrastructure as code
│   └── scripts/          # Seed scripts (70+ Indian companies)
├── prototype/            # 🎨 Live UI prototype (GitHub Pages)
├── docs/                 # Architecture & API documentation
└── docker-compose.yml    # Local development stack
```

---

## 🏃 Quick Start (Local Dev)

### Prerequisites
- Docker & Docker Compose
- Python 3.12+
- Node.js 20+

### Run the stack

```bash
# Copy environment variables
cp .env.example .env

# Start all services (PostgreSQL, Redis, OpenSearch)
docker compose up -d

# Backend
cd backend
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

---

## 📊 Database Schema (Key Tables)

- `companies` — Indian company registry (70+ seeded)
- `jobs` — Normalized job listings
- `job_sources` — Source tracking per listing
- `users` — Job seeker accounts
- `saved_jobs` — User bookmarks
- `job_alerts` — Saved search alerts
- `hr_company_registrations` — HR direct portal registrations

---

## ⚖️ Legal Approach

We follow a **tiered scraping strategy**:

1. **✅ Safe** — Public company career pages, Google for Jobs structured data, opt-in HR partnerships
2. **⚠️ Cautious** — Public job board listings (no login), with attribution and robots.txt respect
3. **❌ Avoided** — Login-wall content, bypassing anti-bot measures, storing full copyrighted JDs

Key precedents: *hiQ Labs v. LinkedIn (2022)*, *Meta v. Bright Data (2024)*, *India DPDPA 2023*.

---

## 🗺️ Roadmap

- **Phase 1 (Wk 1–4)**: Scaffolding, DB setup, first 3 crawlers, search API, basic frontend
- **Phase 2 (Wk 5–8)**: Auth, alerts, HR portal, more crawlers, fuzzy dedup
- **Phase 3 (Wk 9–12)**: Premium tier, payments, SEO, admin dashboard, PWA

---

## 🤝 Contributing

This project is currently in early development. Contributions, ideas, and feedback are welcome!

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<p align="center">Built with ❤️ for the Indian job market</p>
