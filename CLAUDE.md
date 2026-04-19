# MiroLaw Project - Claude Code Instructions

## Project Overview
- **Name**: MiroLaw (电商合规哨兵 - E-commerce Compliance Risk Prediction System)
- **Version**: 0.7.2
- **Tech Stack**: Python + FastAPI + pywebview + pystray
- **Repo**: https://github.com/23xxCh/Mirolaw

## Key Commands
- Run app: `python src/desktop.py`
- Run server only: `python -m uvicorn src.api:app --reload --port 8765`
- Run tests: `python -m pytest tests/ -v`
- Build exe: `python build.py`
- Create release: `git tag v0.7.x && git push origin v0.7.x`

## Architecture
- `src/desktop.py` - Desktop app entry (pywebview + pystray)
- `src/api.py` - FastAPI application (47 endpoints)
- `src/predictor.py` - Risk prediction engine
- `src/alert_system.py` - Real-time alert system
- `src/multi_agent.py` - Multi-agent coordination
- `src/vector_search.py` - Semantic search (lazy-load + keyword fallback)
- `frontend/public/` - Web UI (served by FastAPI)

## Coding Conventions
- Python 3.9+ compatible
- UTF-8 encoding, avoid Chinese quotes in Python strings
- All modules use singleton pattern (get_xxx() functions)
- Prediction history persists to ~/.mirolaw/
- Log files at ~/.mirolaw/logs/

## gstack

Always use the `/browse` skill from gstack for all web browsing tasks. Never use `mcp__claude-in-chrome__*` tools.

### Available gstack Skills
- `/office-hours` `/plan-ceo-review` `/plan-eng-review` `/plan-design-review`
- `/design-consultation` `/design-shotgun` `/design-html`
- `/review` `/ship` `/land-and-deploy` `/canary` `/benchmark`
- `/browse` `/connect-chrome` `/qa` `/qa-only` `/design-review`
- `/setup-browser-cookies` `/setup-deploy` `/retro` `/investigate`
- `/document-release` `/codex` `/cso` `/autoplan`
- `/plan-devex-review` `/devex-review` `/careful` `/freeze` `/guard` `/unfreeze`
- `/gstack-upgrade` `/learn`
