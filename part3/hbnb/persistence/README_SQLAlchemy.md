SQLAlchemy Repository Integration Notes

This repo ships a SQLAlchemy-based repository implementation at
`hbnb.persistence.sqlalchemy_repository.SQLAlchemyRepository` that stores
objects generically in a simple `objects` table with columns:

- `id` (string PK)
- `cls_name` (string)
- `data` (JSON)
- `created_at` / `updated_at` (datetime)

Integration instructions

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Configure the application to use SQLAlchemy by setting either:

- `app.config['USE_SQLALCHEMY'] = True` or
- `app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dev.db'`

When `create_app()` sees these settings it will instantiate
`SQLAlchemyRepository` and use it for persistence.

3. Initialize the database schema (NEXT TASK):

   The repository intentionally does NOT call `Base.metadata.create_all()`.
   Create the `objects` table (and later model tables) in a controlled
   initialization step (migration or explicit create) to avoid unintended
   schema creation during import or testing.

4. After DB models are introduced, you can replace the generic JSON
   storage with full ORM mapping for each class. The repository interface
   remains the same, so the rest of the application should not need
   changes beyond switching to model-backed operations.

Notes

- At this stage the SQLAlchemy repository persists arbitrary JSON blobs,
  so it works as a drop-in replacement for the existing in-memory repo
  while you implement model mapping and migrations in subsequent tasks.
