# Secure-Programming-BIBIFI
## Purpose



## Team

| Name | Role / Focus |
|------|--------------|
| Wil  | Docker, backend, web app |
| Charlie | Database |

## Tech Stack

| Need | Choice |
|------|--------|
| Framework | Flask |
| Database | PostgreSQL 16 (in Docker) |
| DB access | SQLAlchemy / psycopg with parameterized queries |
| Templates | Jinja2 (auto-escaping on) |
| Password hashing | argon2-cffi (Argon2id) |
| Sessions/auth | Flask-Login, signed session cookie |
| CSRF | Flask-WTF (CSRFProtect) |
| Rate limiting | Flask-Limiter |
| Security headers | Flask-Talisman (CSP, HSTS, etc.) |
| Server | Gunicorn inside Docker |
| Testing | pytest |

## Architecture

```
Browser -> Flask web app (Gunicorn, port 8000) -> PostgreSQL (internal Docker network only)
```

- The `web` container serves pages and the API.
- The `db` container is **not** exposed to the host. Only `web` can reach it.
- The web app is published only on `127.0.0.1:8000`.

## Repository Layout

```
project-root/
  src/backend/      Flask app, Dockerfile, requirements.txt
  src/frontend/     Jinja templates (templates/) and static files (static/)
  database/         schema.sql, seed.sql
  tests/            functional/, security/
  docs/             design_document.pdf, diagrams
  docker-compose.yml
  .env.example      Template for secrets (copy to .env)
  README.md
```

## Installation (first-time setup)

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and **running**
- Git

### Steps

1. **Clone the repo**
   ```bash
   git clone <repo-url>
   cd Secure-Programming-BIBIFI
   ```

2. **Create your `.env` file** from the template. This file holds secrets and
   is git-ignored. **Never commit it.**
   ```bash
   cp .env.example .env          # Mac/Linux/Git Bash
   copy .env.example .env        # Windows cmd
   ```

3. **Generate a secret key**
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

4. **Edit `.env`** and fill in the values:
   ```
   POSTGRES_DB=gallery
   POSTGRES_USER=gallery_app
   POSTGRES_PASSWORD=<your own password, letters and digits only>
   SECRET_KEY=<output from step 3>
   FORCE_HTTPS=false
   ```
   Rules: no quotes, no spaces around `=`, and no special characters in the
   password (it is embedded in a connection URL). Each teammate uses their own
   values.

5. **Confirm `.env` is ignored by git**
   ```bash
   git check-ignore .env
   ```
   It should print `.env`. If it prints nothing, add `.env` to `.gitignore`
   before committing anything.

6. **Build and start**
   ```bash
   docker compose up --build -d
   ```

7. **Verify it works**
   ```powershell
   docker compose ps                       # db should say (healthy), web should say Up
   curl.exe http://localhost:8000/health   # expect {"status":"ok"}
   ```
   On Windows PowerShell, `curl` is an alias for `Invoke-WebRequest`. Use
   `curl.exe` (or open the URL in a browser) to avoid a confirmation prompt.

   Then open <http://localhost:8000/> in your browser.

## Database Setup

- `database/schema.sql` and `database/seed.sql` are mounted into Postgres's
  init directory and run automatically, **only when the database volume is
  created for the first time**.
- After changing either SQL file, or changing the values in `.env`, reset the
  database:
  ```bash
  docker compose down -v      # deletes the database volume (all data)
  docker compose up --build -d
  ```
- Seed users must store password **hashes** (Argon2id), never plaintext.

## Day-to-Day Development

| Task | Command |
|------|---------|
| Start | `docker compose up -d` |
| Rebuild after code changes | `docker compose up --build -d` |
| View web logs | `docker compose logs web --tail 50` |
| View db logs | `docker compose logs db --tail 50` |
| Stop | `docker compose down` |
| Stop and wipe database | `docker compose down -v` |

Code is copied into the image at build time, so **changes do not appear until
you rebuild**.

Templates go in `src/frontend/templates/`, and JavaScript/CSS in
`src/frontend/static/`. The Content Security Policy is `default-src 'self'`,
so inline `<script>`, inline `<style>`, and `onclick=` attributes are blocked.
Always render data with `{{ variable }}` in Jinja, never by building HTML
strings.

## Roles

| Role | Capabilities |
|------|--------------|
| User/Guest | Login/logout, view authorized information |
| Employee | Record authorized gallery events, view permitted information |
| Administrator | Manage users/roles and administrative information |

Authorization is enforced on the server side.

## API Endpoints

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/health` | Health check (verifies DB connection) | None |
| GET | `/` | Home page | None |

_More endpoints will be added as features are built._

## Testing

```bash
docker compose exec web pytest
```