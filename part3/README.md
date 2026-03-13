# HBnB Project – Part 2  
## Business Logic & API Implementation

This part of the **HBnB Project** focuses on implementing the core functionality of the application using **Python**, **Flask**, and **flask-restx**.

Based on the architecture designed in Part 1, we build the:

- **Business Logic Layer** (models and relationships)
- **Presentation Layer** (RESTful API endpoints)

The application supports the management of:

- Users  
- Places  
- Reviews  
- Amenities  

CRUD operations are implemented for each entity, and related data (such as place owner and amenities) is properly serialized in API responses.

At this stage, the project focuses only on core functionality.  
Authentication and role-based access control will be implemented in **Part 3**.

Authentication (enable/runtime)
-------------------------------

This project supports optional JWT-based authentication. To enable it at
runtime set `ENABLE_AUTH` to `True` in the Flask configuration and provide a
secret key via `app.config['JWT_SECRET_KEY']` or the environment variable
`JWT_SECRET_KEY`. The application will refuse to start if `ENABLE_AUTH` is
enabled but no secret key is configured.

Examples:

Set via environment and run the Flask CLI:

```bash
export JWT_SECRET_KEY='a-strong-secret'
export FLASK_APP=hbnb
flask run
```

Or enable in test/dev config when creating the app:

```py
from hbnb import create_app
long_secret = "A" * 40
app = create_app({"ENABLE_AUTH": True, "JWT_SECRET_KEY": long_secret})
```

Security note: the application now enforces a minimum secret length of 32 bytes
for `JWT_SECRET_KEY` (HMAC SHA256 recommendation). When enabling auth in
production provide a cryptographically strong secret (store it in CI/hosting
secrets and do not commit it to the repository).

Database migrations
-------------------

This project includes Alembic for migrations. You can manage migrations via the
Flask CLI shims provided by the application. Examples:

```bash
# Upgrade to latest
export FLASK_APP=hbnb
flask db upgrade

# Create an autogenerate revision (inspect models)
flask db revision -m "add users table" --autogenerate

# Stamp DB at a specific revision without running migrations
flask db stamp head

# Downgrade
flask db downgrade -1
```

By default the Alembic config uses `SQLALCHEMY_DATABASE_URI` from environment
or `alembic.ini`. You can pass a different URI by setting the
`SQLALCHEMY_DATABASE_URI` env var or `app.config` before running commands.

