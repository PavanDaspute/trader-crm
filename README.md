# 📈 Trading CRM & Trader Conversion Analytics System

> A real-time, full-stack **Trader Lifecycle Management Platform** built for brokerage companies to track leads, monitor onboarding, analyze funding behavior, and optimize trader conversion funnels.

---

## 🏦 Problem Statement

Brokerage and trading platforms face a critical operational challenge: hundreds of trader leads are generated daily through Telegram campaigns, paid ads, and referrals — but without a structured system, these leads fall through the cracks.

The core problems:

1. **No centralized lifecycle view** — teams can't tell which traders have registered, funded, or gone cold.
2. **No funnel visibility** — it's unclear where traders drop off (New → Registered → Funded → Active).
3. **No deposit intelligence** — total capital deployed, average ticket size, and funding velocity are unknown.
4. **Fragmented acquisition data** — no way to know which channels (Telegram, Ads, Referral) actually convert.

This system solves all of the above with a unified backend, a conversational Telegram bot for capture, and a real-time analytics dashboard.

---

## 💡 Solution Overview

### Three-Layer Architecture

| Layer | Technology | Role |
|-------|-----------|------|
| **Acquisition** | Telegram Bot (aiogram) | Field-level trader capture via chat |
| **Core API** | FastAPI + MongoDB | Lifecycle management, deposits, aggregations |
| **Intelligence** | React Dashboard | Real-time KPIs, funnel, charts, trader table |

#### Telegram Bot
Sales/support teams interact via chat commands. The bot walks users through structured FSM (finite state machine) flows to capture trader name, contact, and source — then calls the backend REST API. No direct DB access.

#### Backend API
FastAPI handles business logic: trader creation, lifecycle updates, deposit recording. MongoDB aggregation pipelines compute KPIs like conversion rate, activation rate, and deposit metrics. Fully async with Motor.

#### React Dashboard
A dark-themed analytics dashboard updates every 30 seconds. Shows KPI cards, conversion funnel, time-series charts, status distribution, source breakdown, and a searchable, sortable, paginated trader table.

---

## 🏗️ Architecture Diagram

```
┌─────────────────────────────────────────────────────┐
│                  Telegram Clients                   │
└──────────────────────────┬──────────────────────────┘
                           │ aiogram polling
        ┌──────────────────▼─────────────────────┐
        │         Bot Service (aiogram v3)        │
        │  FSM: AddTrader / UpdateStatus /        │
        │        Deposit / Stats                  │
        └──────────────────┬──────────────────────┘
                           │ HTTP (httpx)
        ┌──────────────────▼──────────────────────┐
        │          Backend Service (FastAPI)       │
        │  /traders  /stats/overview              │
        │  /stats/funnel  /stats/timeseries       │
        │  /stats/sources                         │
        └──────────────────┬──────────────────────┘
                           │ Motor (async)
        ┌──────────────────▼──────────────────────┐
        │             MongoDB 7.0                  │
        │   Collection: traders                    │
        │   Aggregation pipelines for KPIs        │
        └─────────────────────────────────────────┘

        ┌─────────────────────────────────────────┐
        │        React Frontend (Vite + Tailwind)  │
        │  KPI Cards → Funnel → Charts → Table    │
        │         Axios → FastAPI                  │
        └─────────────────────────────────────────┘
```

---

## 🧱 Tech Stack

| Technology | Why It's Used |
|-----------|-------------|
| **FastAPI** | Async-first Python framework with automatic OpenAPI docs, Pydantic validation, and high throughput for concurrent API calls |
| **MongoDB (Motor)** | Document model fits flexible trader data; aggregation pipeline is ideal for funnel/KPI analytics without complex JOINs |
| **aiogram v3** | Modern async Telegram bot framework with FSM support — perfect for building conversational, stateful data-capture workflows |
| **React + Vite** | Fast HMR, ES module bundling, component-based UI — ideal for a real-time analytics dashboard |
| **Tailwind CSS** | Utility-first CSS with dark mode primitives, allowing rapid development of the trading UI aesthetic |
| **Recharts** | React-native chart library using SVG — smooth, responsive charts with custom tooltips |
| **Docker Compose** | Reproducible multi-service environment: one command to bring up all four services with correct networking |

---

## ✨ Key Features

### 🔄 Trader Lifecycle Tracking
Every trader follows: **New → Registered → Funded → Active**. Status transitions are recorded with timestamps, enabling time-in-stage analysis.

### 💰 Deposit Tracking
Multi-deposit support per trader. Tracks initial deposit separately from total. Aggregated to show total platform AUM and average ticket size.

### 📊 Conversion Funnel Analytics
Real-time funnel visualization with drop-off % at each stage. Powered by MongoDB `$group` aggregation.

### 🤖 Telegram Integration
Fully conversational bot with FSM. Validates every input, prevents bad data from entering the system, and shows formatted trade-style reports.

### 📈 Source Attribution
Tracks which acquisition channels (Telegram, Ads, Referral, Organic) produce the most funded traders — critical for marketing ROI measurement.

### ⚡ Live Dashboard
Auto-refreshes every 30 seconds. Animated loading states during data fetches.

---

## 📊 KPIs Explained

| KPI | Formula | Business Meaning |
|-----|---------|-----------------|
| **Conversion Rate** | `funded / total * 100` | % of leads that actually deposit — the core brokerage health metric |
| **Activation Rate** | `active / funded * 100` | % of funded traders who start trading — measures post-funding engagement |
| **Total Deposits** | `SUM(total_deposit)` | Total capital on platform — revenue indicator |
| **Avg Deposit / Trader** | `total_deposits / total_traders` | Average ticket size — proxy for trader quality |

---

## 🚀 Setup Instructions

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
- A Telegram Bot token (get one from [@BotFather](https://t.me/BotFather))

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd "trading analytics system"
```

### 2. Configure Environment
Edit `.env`:
```env
BOT_TOKEN=your_telegram_bot_token_here
MONGO_DB=trading_crm
APP_ENV=development
LOG_LEVEL=INFO
VITE_API_URL=http://localhost:8000
```

### 3. Start All Services
```bash
docker compose up --build
```

This starts:
- MongoDB on port `27017`
- Backend API on port `8000`
- Telegram Bot (polling)
- Frontend dashboard on port `3000`

### 4. Access the Dashboard
Open: [http://localhost:3000](http://localhost:3000)

### 5. View API Docs
Open: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 📡 API Documentation

### Trader Endpoints

#### `POST /traders/`
Create a new trader lead.
```json
{
  "name": "Alex Johnson",
  "contact": "alex@example.com",
  "source": "Telegram"
}
```
Response: `TraderResponse` (201)

#### `GET /traders/`
List all traders with optional filters.
```
GET /traders/?status=funded&source=Ads
```

#### `PUT /traders/{id}/status`
Advance trader lifecycle.
```json
{ "status": "registered" }
```

#### `POST /traders/{id}/deposit`
Record a deposit.
```json
{ "amount": 5000.00 }
```

---

### Analytics Endpoints

#### `GET /stats/overview`
```json
{
  "total_traders": 152,
  "registered_traders": 89,
  "funded_traders": 47,
  "active_traders": 31,
  "conversion_rate": 30.92,
  "activation_rate": 65.96,
  "total_deposits": 235000.00,
  "avg_deposit_per_trader": 1546.05
}
```

#### `GET /stats/funnel`
```json
[
  { "stage": "new",        "count": 16 },
  { "stage": "registered", "count": 89 },
  { "stage": "funded",     "count": 47 },
  { "stage": "active",     "count": 31 }
]
```

#### `GET /stats/timeseries?days=30`
```json
{
  "series": [
    { "date": "2026-03-25", "traders": 5, "deposits": 12500.00 },
    ...
  ],
  "days": 30
}
```

#### `GET /stats/sources`
```json
[
  { "source": "Telegram", "count": 80, "funded": 35, "total_deposits": 140000, "conversion_rate": 43.75 }
]
```

---

## 🤖 Telegram Bot Usage

### `/start`
Displays welcome message and all available commands.

### `/add_trader`
3-step guided flow:
1. Enter trader's **full name**
2. Enter **contact** (email, phone, or @handle)
3. Select **acquisition source** from keyboard

Returns the trader's ID for use in subsequent commands.

### `/update_status <trader_id>`
2-step flow to advance a trader's lifecycle:
1. Enter the **24-character trader ID**
2. Select the **new stage** from keyboard (new/registered/funded/active)

### `/deposit <trader_id>`
2-step flow:
1. Enter **trader ID**
2. Enter **deposit amount** in USD

### `/stats`
Displays a formatted KPI summary card:
```
📊 Trading Platform KPIs
━━━━━━━━━━━━━━━━━━
👥 Total Traders:  152
💰 Funded:          47
🚀 Active:          31
📈 Conversion Rate: 30.92%
💵 Total Deposits:  $235,000.00
```

---

## 🎨 Dashboard Overview

| Section | Content |
|---------|---------|
| **Top Nav** | App title, last-updated time, Refresh button, Add Trader button |
| **KPI Cards** | 5 metric cards with colour-coded accents and animated skeleton loading |
| **Funnel** | Horizontal bars showing trader count at each stage with drop-off % |
| **Status Donut** | Pie chart showing distribution across all statuses |
| **Traders Over Time** | Line chart of new traders per day (last 30 days) |
| **Deposits Over Time** | Bar chart of deposit volume per day |
| **Source Breakdown** | Grouped bars comparing total vs funded by acquisition channel |
| **Trader Table** | Full list with search, column sorting, pagination, and status badges |

---

## 🔮 Future Improvements

| Feature | Description |
|---------|-------------|
| **Risk Scoring** | ML model to score traders by churn probability based on activity patterns |
| **Trading Activity Integration** | Connect to broker MT4/MT5 API to pull live trade volumes per trader |
| **AI Insights** | LLM-generated weekly conversion summaries and anomaly detection |
| **WebSocket Live Updates** | Push-based dashboard updates instead of polling |
| **Role-Based Auth** | JWT-secured API with admin vs read-only roles |
| **Email Alerts** | Automatic notifications when conversion rate drops below threshold |
| **CSV Export** | One-click export of filtered trader lists for CRM integration |
| **Trader Notes** | Free-form notes per trader for sales team context |

---

## 📁 Project Structure

```
trading-analytics-system/
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI app init, CORS, lifecycle hooks
│   │   ├── config.py          # Pydantic Settings
│   │   ├── database.py        # Motor client management
│   │   ├── models/
│   │   │   └── trader.py      # Pydantic schemas + enums
│   │   ├── services/
│   │   │   ├── trader_service.py  # CRUD business logic
│   │   │   └── stats_service.py   # Aggregation pipelines
│   │   └── routes/
│   │       ├── traders.py     # /traders/* endpoints
│   │       └── stats.py       # /stats/* endpoints
│   ├── requirements.txt
│   └── Dockerfile
│
├── bot/
│   ├── main.py                # Bot init + polling
│   ├── config.py              # Bot settings
│   ├── api/
│   │   └── client.py          # httpx wrapper for backend
│   ├── states/
│   │   └── trader_states.py   # aiogram FSM state groups
│   ├── handlers/
│   │   ├── start.py
│   │   ├── add_trader.py
│   │   ├── update_status.py
│   │   ├── deposit.py
│   │   └── stats.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── api/index.js       # Axios client
│   │   ├── components/        # KPICards, FunnelChart, charts, table, modal
│   │   └── pages/Dashboard.jsx
│   ├── tailwind.config.js
│   ├── vite.config.js
│   ├── nginx.conf
│   └── Dockerfile
│
├── docker-compose.yml
├── .env
└── README.md
```

---

## 🛠️ Development (Without Docker)

### Backend
```bash
cd backend
pip install -r requirements.txt
MONGO_URL=mongodb://localhost:27017 uvicorn app.main:app --reload
```

### Bot
```bash
cd bot
pip install -r requirements.txt
BOT_TOKEN=your_token BACKEND_URL=http://localhost:8000 python main.py
```

### Frontend
```bash
cd frontend
npm install
VITE_API_URL=http://localhost:8000 npm run dev
```

---

*Built as a production-grade internal tool for brokerage platforms — clean, scalable, and interview-ready.*
