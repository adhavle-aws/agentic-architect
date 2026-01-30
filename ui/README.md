# Agentic-Architect UI

Enhanced UI with both Quick Generate (MCP wrapper) and A2A Agents.

## Architecture

```
Browser
   ↓
Backend Proxy (Node.js)
   ├─→ MCP Server (Quick Generate)
   └─→ A2A Agents (Conversational)
```

## Features

### Quick Generate (MCP Wrapper)
- ⚡ Fast, one-shot generation
- All tabs populate instantly
- No conversation needed
- Best for: Quick prototypes

### A2A Agents (True Agents)
- 🤖 Conversational interface
- Iterative refinement
- Agent collaboration visible
- Best for: Production architectures

## Setup

### Backend

```bash
cd ui/backend
npm install
cp .env.example .env
# Update .env with your agent URLs
npm start
```

### Frontend

```bash
cd ui/frontend
# Open index.html in browser
# Or serve with:
python3 -m http.server 8000
```

## Environment Variables

See `backend/.env.example` for required configuration.

## Usage

1. Start backend: `npm start` (in backend/)
2. Open `frontend/index.html` in browser
3. Choose mode from sidebar:
   - Quick Generate: Fast generation
   - A2A Agents: Conversational design

## Development

```bash
# Backend with auto-reload
cd backend
npm run dev

# Frontend
# Just refresh browser after changes
```

## Deployment

See `../docs/UI_DEPLOYMENT.md` for production deployment guide.
