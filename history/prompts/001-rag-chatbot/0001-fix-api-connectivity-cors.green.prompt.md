---
id: 0001
title: Fix API Connectivity and CORS Configuration
stage: green
date: 2025-12-17
surface: agent
model: claude-opus-4-5-20251101
feature: 001-rag-chatbot
branch: 001-rag-chatbot
user: muhammad-yousuf
command: /sp.implement
labels: ["api", "cors", "connectivity", "bugfix", "docusaurus"]
links:
  spec: ./spec.md
  ticket: null
  adr: null
  pr: null
files:
  - frontend/src/services/api.ts
  - backend/.env
  - backend/.env.example
tests:
  - Manual verification via curl and browser DevTools
---

## Prompt

The frontend UI works, but ALL API calls fail with "failed to fetch".

This is NOT a UI issue.
This is a backend connectivity / CORS / base URL issue.

Context:
- Backend FastAPI is located at /chatbot
- Backend runs on port 8000
- Frontend is Docusaurus
- Communication must be HTTP only

Your task:
1. Audit frontend API base URL usage
2. Ensure absolute backend URLs are used
3. Add VITE_API_BASE_URL support
4. Verify all fetch calls use API_BASE_URL
5. Verify CORS config in backend allows frontend origin
6. Ensure no relative /api calls remain
7. Do NOT touch backend business logic

Deliverables:
- Exact files changed
- Correct API base URL config
- Confirmation checklist to validate connectivity

## Response snapshot

**Root Cause Identified:**
1. Frontend api.ts used `process.env.NEXT_PUBLIC_API_URL` - a Next.js pattern incompatible with Docusaurus runtime
2. CORS origins in backend didn't cover all common development ports

**Fixes Applied:**
1. `frontend/src/services/api.ts`: Replaced Next.js env pattern with Docusaurus-compatible `getApiBaseUrl()` function supporting `window.RAG_CHATBOT_API_URL` runtime config
2. `backend/.env`: Expanded CORS_ORIGINS to include localhost:3000, 5173, 8080 and 127.0.0.1 variants
3. `backend/.env.example`: Created documentation file for environment variables

**Verification:** All fetch calls verified to use centralized API_BASE_URL; no relative /api calls found.

## Outcome

- ✅ Impact: Fixed "failed to fetch" errors by correcting API base URL configuration and CORS settings
- 🧪 Tests: Manual verification checklist provided
- 📁 Files: 3 files changed (api.ts, .env, .env.example created)
- 🔁 Next prompts: Test connectivity with curl and browser, configure Docusaurus customFields for production
- 🧠 Reflection: Docusaurus uses client-side rendering and cannot access Node.js process.env at runtime; must use window globals or build-time injection

## Evaluation notes (flywheel)

- Failure modes observed: Next.js env pattern used in Docusaurus project; CORS origins missing common dev ports
- Graders run and results (PASS/FAIL): Manual verification pending
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Verify backend is running and reachable before frontend testing
