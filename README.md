# Math Tools Platform

A Django-based educational platform for math tools (Grades 1-3 Prep).

## Local Development

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run migrations:
   ```bash
   python manage.py migrate
   ```
3. Initialize tools:
   ```bash
   python init_tools.py
   ```
4. Run server:
   ```bash
   python manage.py runserver
   ```

## Deployment

### GitHub

1. Initialize Git:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   ```
2. Push to GitHub:
   ```bash
   git remote add origin <your-repo-url>
   git push -u origin main
   ```

### Fly.io

1. Install Fly CLI: https://fly.io/docs/hands-on/install-flyctl/
2. Login:
   ```bash
   fly auth login
   ```
3. Launch app (autodetects Dockerfile):
   ```bash
   fly launch
   ```
   - Follow the prompts.
   - Say **Yes** to copy configuration to `fly.toml`.
   - You can choose to set up a Postgres database or use SQLite (for SQLite, you need to set up volumes, but for a start, the Dockerfile works with ephemeral storage. For persistence, use Fly Volumes or Postgres).
   
   **Note for SQLite on Fly:**
   If you want to keep the database between restarts using SQLite, you need to mount a volume.
   
4. Set Secrets:
   ```bash
   fly secrets set SECRET_KEY="your-secure-secret-key" DEBUG=False
   ```

5. Deploy:
   ```bash
   fly deploy
   ```

## Configuration

The project is configured to use Environment Variables for production:
- `SECRET_KEY`: Django secret key.
- `DEBUG`: Set to `False` in production.
- `DATABASE_URL`: Database connection string (automatically set by Fly if using Postgres).
- `ALLOWED_HOSTS`: Comma-separated list of hosts.
- `CSRF_TRUSTED_ORIGINS`: For HTTPS support (default allows `https://*.fly.dev`).
