### Folder Structure

```
backend/
├── app/                              # Main app folder
│	│   ├── __init__.py               # Makes app/ a package
│   ├── api/                          # API Endpoints
│   │   ├── __init__.py
│	│   │   ├── v1/                   # Version 1 of API
│   │   │   ├── __init__.py
│   │   │   ├── endpoints/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── auth.py          # Login/register
│   │   │   │   ├── documents.py     # Upload/manage docs
│   │   │   │   ├── verification.py  # Check docs for fraud
│   │   │   │   ├── users.py         # User info
│   │   │   │   ├── admin.py         # Admin controls
│   │   │   │   ├── support.py       # Help/troubleshooting
│   ├── core/                        # Core tools
│   │   ├── __init__.py
│   │   ├── config.py                # Settings
│   │   ├── security.py              # Password/JWT stuff
│   │   ├── dependencies.py          # Helpers for DB/auth
│   │   ├── exceptions.py            # Error handling
│   ├── db/                          # Database stuff
│   │   ├── __init__.py
│   │   ├── base.py                  # Base for models
│   │   ├── session.py               # DB connection
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py              # User table
│   │   │   ├── document.py          # Document table
│   │   │   ├── verification.py      # Verification table
│   │   │   ├── audit_log.py         # Log actions
│   │   ├── crud/
│   │   │   ├── __init__.py
│   │   │   ├── user.py              # User actions
│   │   │   ├── document.py          # Document actions
│   │   │   ├── verification.py      # Verification actions
│   │   ├── migrations/
│   │   │   ├── __init__.py
│   │   │   ├── env.py               # Migration setup
│   │   │   ├── script.py.mako       # Migration template
│   │   │   ├── versions/            # Migration scripts
│   │   │   │   ├── __init__.py
│   │   │   │   ├── (generated files)
│   │   ├── seed_data.py             # Sample data
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py                  # User data rules
│   │   ├── document.py              # Document data rules
│   │   ├── verification.py          # Verification data rules
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth/
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py      # Auth logic
│   │   │   ├── jwt_handler.py       # Token handling
│   │   ├── ml 
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── file_utils.py            # File handling
│   │   ├── logging.py               # Logging setup
│   │   ├── response_utils.py        # API responses
├── scripts/
│   ├── __init__.py
│   ├── run_migrations.sh            # Migration script
│   ├── create_admin.py              # Admin user creator
│   ├── db_init.py                   # DB initializer
├── main.py                          # Starts the app
├── alembic.ini                      # Migration config
├── .env                             # Settings file
```