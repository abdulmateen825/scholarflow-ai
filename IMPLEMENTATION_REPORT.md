# ScholarFlow AI — Version 1 Implementation Report

## A. Project overview

ScholarFlow AI has a modular FastAPI backend and a responsive React/Vite dashboard. It supports assignments, saved memories, PDF/DOCX storage and text extraction, configurable AI analysis and web research providers, and an integration boundary for Google’s official Classroom and Drive remote MCP services. Assignment and memory records are stored in `data/scholarflow.sqlite3`; uploaded files are stored under `uploads/`. These local stores are intended for a single-user development instance. Existing `data/assignments.json` records are imported once when the SQLite database is initialized.

## B. Implemented features

- FastAPI application setup, `/api/v1` router, local frontend CORS, structured HTTP errors, logging, health and API info.
- Assignment creation, listing, details, due date/course/description, local status, and SQLite persistence.
- Saved memory creation, listing, and deletion with input validation.
- Feature-specific API routers, service and repository layers, and OpenAI/Tavily provider adapters.
- PDF/DOCX uploads, extension allowlist, per-file 15 MB cap, generated storage names, extraction via PyMuPDF/python-docx, and clear extraction failures.
- Assignment analysis via OpenAI when configured; otherwise a clear setup response.
- Web search service interface via Tavily when configured; otherwise a clear setup response.
- Google Classroom and Drive Streamable HTTP MCP endpoint configuration, auth header support, availability check, tool discovery and tool invocation methods.
- Dashboard overview, assignment list/details/create, integration status, loading/error/empty states, responsive styling, and API-backed forms.
- Environment examples and ignore rules for local secrets, environments, uploaded files, and generated output.

## C. Files created and modified

- `backend/app/main.py`: FastAPI app, middleware, exception handlers and root/health routes.
- `backend/app/core/config.py`, `errors.py`: settings and centralized error responses.
- `backend/app/api/router.py` and `backend/app/api/routes/`: versioned API composition and feature-specific route handlers.
- `backend/app/schemas/assignment.py`: assignment and analysis validation models.
- `backend/app/services/`: business logic and document extraction.
- `backend/app/repositories/`, `backend/app/db/`: SQLite repositories and database schema initialization.
- `backend/app/integrations/ai/`: OpenAI and Tavily adapters.
- `backend/app/integrations/google_mcp.py`: Google MCP remote HTTP client, status/tool discovery/call.
- `backend/requirements.txt`: backend dependency manifest.
- `backend/mcp.example.json`: endpoint/transport/auth reference for the remote services.
- `.env.example`, `frontend/.env.example`, `.gitignore`: configuration and local artifact exclusions.
- `frontend/src/App.tsx`, `App.css`, `index.css`: functional dashboard and visual system.
- `frontend/vite.config.ts`: API development proxy configuration.

The existing `backend/.env` was inspected. Its app name was aligned to ScholarFlow AI; other credential/configuration values were preserved. The existing frontend package manifest was retained; it already includes React, TypeScript, Vite, and Tailwind CSS. The app uses the browser `fetch` API, so no Axios dependency was needed.

## D. Technology stack

- Frontend: React 19, TypeScript, Vite, Tailwind CSS 4 (with custom responsive CSS).
- Backend: Python, FastAPI, Pydantic Settings, Uvicorn, HTTPX.
- AI: OpenAI Python client, configured through `OPENAI_API_KEY` and `OPENAI_MODEL`.
- Research: Tavily Python client, configured through `TAVILY_API_KEY`.
- Documents: PyMuPDF for PDF; python-docx for DOCX.
- Google integration: Google Workspace remote MCP servers over Streamable HTTP; OAuth 2.0 user delegated auth is required by Google.

## E. Google MCP integration

### Selected servers

The project targets the official Google Workspace remote MCP services, rather than a third-party repository or an invented package:

- [Google Classroom MCP server](https://classroommcp.googleapis.com/mcp/v1), official [tool reference](https://developers.google.com/workspace/classroom/reference/mcp).
- [Google Drive MCP server](https://drivemcp.googleapis.com/mcp/v1), official [tool reference](https://developers.google.com/workspace/drive/api/reference/mcp).
- Google’s official configuration guide: [Configure the Google Workspace MCP servers](https://developers.google.com/workspace/guides/configure-mcp-servers).

Google documents Classroom tools such as `list_courses`, `list_course_work_summaries`, `get_course_work`, and `list_course_work_submissions`. Drive tools include `search_files`, `read_file_content`, `download_file_content`, `list_recent_files`, `get_file_metadata`, and file creation/copy operations. These names/capabilities are from current official tool references; the project has **not** authenticated to the live endpoints or executed those tools. The status API will report a live check only when it receives a successful MCP response.

### Setup

1. Enroll the Google account/project in the [Google Workspace Developer Preview Program](https://developers.google.com/workspace/guides/configure-mcp-servers).
2. In Google Cloud, enable Classroom API and Classroom MCP API (`classroom.googleapis.com`, `classroommcp.googleapis.com`) and Drive API and Drive MCP API (`drive.googleapis.com`, `drivemcp.googleapis.com`).
3. Configure the OAuth consent screen and a user delegated Web OAuth client. Google requires selecting **Use this client for an AI-powered agent** for clients calling Workspace MCP. Request only appropriate scopes: Classroom course read (`classroom.courses.readonly`) plus the exact course-work scopes required by enabled tools (`classroom.coursework.students` as applicable); Drive read (`drive.readonly`). Google’s MCP preview may require additional product-specific scopes and approval. Keep these scopes as narrow as the product allows.
4. Set the endpoints in `backend/.env` (defaults are already the official URLs). Configure the OAuth client through a compatible MCP host/client that performs Google’s authorization-code flow and offline refresh, then configure an access token for backend service use if your deployment supports securely refreshing it. Do not use a static bearer token in production: the current backend setting is a development hook, and the backend does not yet implement encrypted per-user refresh-token storage or an OAuth callback flow.
5. Start the backend and check `GET /api/v1/integrations/`. `backend/mcp.example.json` records the server URLs and Streamable HTTP transport.

The official services are hosted by Google; there is no `npm install` or local MCP server process to start. Google’s docs describe the services as Developer Preview and require preview eligibility, project/API/MCP service enablement, OAuth consent configuration, and account permissions. Classroom access can also be constrained by course role, API scopes and test class setup. The practical fallback is the [Google Classroom REST API](https://developers.google.com/workspace/classroom), using OAuth 2.0 and the official Google API Python client; that direct API synchronization is not implemented in this version. No live Google authentication was possible in this environment, and the implementation does not claim it is connected.

## F. API documentation

All examples use `http://localhost:8000`.

| Method and path | Purpose |
|---|---|
| `GET /` | Application status and docs URL. |
| `GET /health` | Health check. |
| `GET /api/v1/` | API name/version. |
| `GET /api/v1/integrations/` | Google MCP status and OpenAI/Tavily configuration flags. |
| `GET /api/v1/classroom/status` | Classroom remote MCP availability. |
| `GET /api/v1/assignments/` | List local assignments. |
| `POST /api/v1/assignments/` | Create an assignment. |
| `GET /api/v1/assignments/{assignment_id}` | Read assignment details. |
| `POST /api/v1/assignments/{assignment_id}/upload` | Upload one or more PDF/DOCX files (multipart `files`). |
| `POST /api/v1/assignments/analyze` | Analyze assignment text using configured OpenAI credentials. |
| `POST /api/v1/research/search` | Search topic using configured Tavily credentials. |

Example create request:

```json
{"title":"Ethics of AI","description":"Discuss two ethical frameworks.","course":"Philosophy","due_date":"2026-12-15"}
```

Example response (IDs/timestamps vary):

```json
{"id":"<id>","title":"Ethics of AI","description":"Discuss two ethical frameworks.","course":"Philosophy","due_date":"2026-12-15","status":"Not started","created_at":"<UTC timestamp>","attachment_names":[],"extracted_text":""}
```

Example analysis request: `{"assignment_id":"<id>"}`. Without a key, the response has `configured:false`, an empty summary and a configuration message. With a key, it returns a structured summary and requirement list.

Example research request: `{"query":"academic perspectives on AI ethics"}`. Without a key, it returns `configured:false`, an empty result list and a configuration message.

Errors use `{"error":{"message":"..."}}`; validation errors follow FastAPI/Pydantic’s standard validation response.

## G. Environment configuration

Copy `.env.example` to `backend/.env`.

- `OPENAI_API_KEY`, `OPENAI_MODEL`: API key from the OpenAI platform and model selection.
- `TAVILY_API_KEY`: key from Tavily for search.
- `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`: OAuth credentials created in Google Cloud; not yet consumed by a backend OAuth flow in V1.
- `GOOGLE_REDIRECT_URI`: reserved callback URI for the planned app-owned OAuth flow; must exactly match a registered redirect URI.
- `GOOGLE_CLASSROOM_MCP_URL`, `GOOGLE_DRIVE_MCP_URL`: official remote endpoint URLs.
- `GOOGLE_MCP_ACCESS_TOKEN`: optional development bearer token only; do not commit or log. Refresh and secure per-user token storage remain incomplete.
- `FRONTEND_URL`, `BACKEND_URL`: local app origins/addresses.
- `MAX_UPLOAD_MB`: per-file upload limit (default 15).
- `VITE_API_URL` in `frontend/.env`: backend URL; it is public configuration, never a secret.

Google credentials and app verification/preview access are managed in Google Cloud Console / Google Auth Platform. OpenAI and Tavily credentials are obtained from their respective developer dashboards. No secret is needed to run the local assignment workflow.

## H. How to run the application

PowerShell, from the repository root:

```powershell
cd .\backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item ..\.env.example .env
# Edit .env with any provider credentials you have; assignment features work without them.
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

In a second PowerShell window:

```powershell
cd .\frontend
npm install
npm run dev
```

Open `http://localhost:5173`; API docs are at `http://localhost:8000/docs`. Google MCP services are remote, so there is no separate local MCP startup command. Configure OAuth in Google Cloud and an OAuth-capable host/client as described above. The sample endpoint configuration is in `backend/mcp.example.json`.

## I. Testing results

- Frontend production build: **passed** (`npm.cmd run build`; TypeScript and Vite completed successfully).
- Backend imports/dependency smoke check: **passed** for FastAPI, Pydantic Settings, PyMuPDF, python-docx and HTTPX in the existing `backend/venv`.
- Backend dependency installation (`python -m pip install -r requirements.txt`): **passed** against the existing environment. No separate MCP SDK is used because the remote HTTP client uses HTTPX. No provider keys were supplied.
- Backend runtime: Uvicorn started successfully; live local requests to `/health` and `/api/v1/` returned HTTP 200.
- API smoke checks: root, health, API information, assignment create/list/details, DOCX upload/text extraction and PDF upload/text extraction all passed using FastAPI TestClient. Test records/files were removed afterward.
- Frontend lint (`npm.cmd run lint`): **passed**. Frontend production build (`npm.cmd run build`): **passed**.
- Google MCP availability check: the API returned HTTP 200 with clear unavailable statuses; outbound connections to the Google endpoints failed in this environment. Google MCP tool names/capabilities were reviewed in the official references; no authenticated live tool invocation was possible.
- OpenAI/Tavily: no live provider requests because credentials were not supplied.

## J. Remaining work

- Implement app-owned Google OAuth authorization-code flow, CSRF/state handling, encrypted per-user token storage, revocation and refresh; bind MCP requests to the signed-in user. `GOOGLE_CLIENT_ID` and secret are currently documented but unused.
- Finish and exercise full MCP transport/session behavior against an authorized preview project; Google’s official references document tool listing, but no real call was tested here.
- Add direct Classroom API fallback/sync and store imported course assignments.
- Add user identity before multi-user deployment; the current local SQLite store is single-user.
- Add frontend assignment editing/status workflow and display analysis/research in UI.
- Add automated tests, DOCX/PDF export, richer citation checking and production deployment/security hardening.

## K. Version 2 roadmap

1. Complete secure Google OAuth and sync Classroom courses/assignment instructions/attachments, with REST API fallback.
2. Add rubric-aware AI analysis into structured requirements and completeness checks.
3. Add Tavily-based cited research, source deduplication and verifiable reference metadata.
4. Generate structured outlines and draft sections with citation provenance and user review checkpoints.
5. Add editing/readability feedback and assignment status tracking.
6. Export styled DOCX/PDF and save deliverables to user-authorized Drive folders.
