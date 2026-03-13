"""Minimal Flask application factory for HBnB API used by tests.

This implementation intentionally keeps behavior simple and synchronous
and relies on the existing `HBNBFacade` and repository implementations.
It provides the endpoints exercised by the test suite in `tests/test_api.py`.
"""

from __future__ import annotations

from flask import Flask, request, jsonify
from flask import current_app
import os
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    verify_jwt_in_request,
    get_jwt,
    get_jwt_identity,
)

from ..business.facade import HBNBFacade, NotFoundError, ValidationError
import click
from alembic.config import Config as AlembicConfig
from alembic import command as alembic_command
from ..persistence.in_memory_repository import InMemoryRepository


def create_app(config: object | dict | None = None):
    app = Flask(__name__)
    if config:
        if isinstance(config, dict):
            app.config.update(config)
        else:
            app.config.from_object(config)

    # Use in-memory repo by default for tests and simplicity
    repo = InMemoryRepository()
    facade = HBNBFacade(repo)

    # Initialize JWT if requested in config
    if app.config.get("ENABLE_AUTH"):
        # Prefer explicit config; fall back to environment variable
        key = app.config.get("JWT_SECRET_KEY") or os.environ.get("JWT_SECRET_KEY")
        if not key:
            raise RuntimeError(
                "ENABLE_AUTH is True but JWT_SECRET_KEY is not set. "
                "Set app.config['JWT_SECRET_KEY'] or the environment variable JWT_SECRET_KEY."
            )
        # enforce minimum key length in bytes (HMAC SHA256 recommended >=32 bytes)
        if len(key.encode("utf-8")) < 32:
            raise RuntimeError(
                "JWT_SECRET_KEY is too short; must be at least 32 bytes. "
                "Set a longer secret via app.config['JWT_SECRET_KEY'] or the environment."
            )
        app.config["JWT_SECRET_KEY"] = key
        JWTManager(app)

    def _sanitize_user(obj: dict) -> dict:
        out = dict(obj)
        out.pop("password", None)
        return out

    def _sanitize_amenity(obj: dict) -> dict:
        return dict(obj)

    def _sanitize_place(obj: dict) -> dict:
        out = dict(obj)
        owner_id = out.get("user_id")
        if owner_id:
            try:
                owner = facade.get("User", owner_id)
                out["owner"] = {
                    "id": owner.get("id"),
                    "email": owner.get("email"),
                }
            except NotFoundError:
                out["owner"] = {"id": owner_id}
        else:
            out["owner"] = None

        # attach amenities
        amenity_ids = out.get("amenity_ids") or []
        amenities = []
        for aid in amenity_ids:
            try:
                a = facade.get("Amenity", aid)
                amenities.append(a)
            except NotFoundError:
                # ignore missing amenities
                pass
        out["amenities"] = amenities

        # attach reviews
        try:
            all_reviews = facade.list("Review")
            place_reviews = [
                r for r in all_reviews if r.get("place_id") == out.get("id")
            ]
        except NotFoundError:
            place_reviews = []
        out["reviews"] = place_reviews
        return out

    def _ensure_auth_allowed():
        """Verify JWT when `ENABLE_AUTH` is set; otherwise no-op."""
        if current_app.config.get("ENABLE_AUTH"):
            verify_jwt_in_request()

    def _is_admin_claim() -> bool:
        if not current_app.config.get("ENABLE_AUTH"):
            return False
        return bool(get_jwt().get("is_admin", False))

    def _current_identity() -> str | None:
        if not current_app.config.get("ENABLE_AUTH"):
            return None
        return get_jwt_identity()

    @app.cli.command("init-db")
    @click.option("--db", default=None, help="Database URI to initialize")
    def init_db(db: str | None = None):
        """Create database tables for SQLAlchemy-backed repositories.

        If `--db` is not provided the command will read
        `app.config['SQLALCHEMY_DATABASE_URI']` or fall back to
        `sqlite:///hbnb_dev.db`.
        """
        from sqlalchemy import create_engine

        uri = db or app.config.get("SQLALCHEMY_DATABASE_URI") or "sqlite:///hbnb_dev.db"

        # Create engine and create metadata for known modules
        engine = create_engine(uri, future=True)

        # Create tables for the generic object store (if present)
        try:
            from ..persistence.sqlalchemy_repository import Base as _obj_base

            _obj_base.metadata.create_all(engine)
        except ImportError:
            # ignore if module not available
            pass

        # Create tables for ORM models (if present)
        try:
            from ..persistence.models import Base as _models_base

            _models_base.metadata.create_all(engine)
        except ImportError:
            pass

        print(f"Initialized database: {uri}")

    # Alembic `flask db` wrapper
    @app.cli.group("db")
    def db_cmd():
        """Alembic database migration commands."""

    def _alembic_config():
        # locate alembic.ini in project root
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        cfg_path = os.path.join(project_root, "alembic.ini")
        cfg = AlembicConfig(cfg_path)
        # prefer an explicit SQLALCHEMY_DATABASE_URI in app config
        uri = app.config.get("SQLALCHEMY_DATABASE_URI") or os.environ.get("SQLALCHEMY_DATABASE_URI")
        if uri:
            cfg.set_main_option("sqlalchemy.url", uri)
        return cfg

    @db_cmd.command("upgrade")
    @click.option("--rev", default="head", help="Revision to upgrade to (default: head)")
    def db_upgrade(rev: str):
        """Run Alembic upgrade."""
        cfg = _alembic_config()
        alembic_command.upgrade(cfg, rev)

    @db_cmd.command("downgrade")
    @click.argument("rev")
    def db_downgrade(rev: str):
        """Run Alembic downgrade to a given revision (e.g. -1 or base)."""
        cfg = _alembic_config()
        alembic_command.downgrade(cfg, rev)

    @db_cmd.command("revision")
    @click.option("-m", "--message", required=True, help="Revision message")
    @click.option("--autogenerate", is_flag=True, help="Autogenerate migration from models")
    def db_revision(message: str, autogenerate: bool):
        """Create a new Alembic revision."""
        cfg = _alembic_config()
        alembic_command.revision(cfg, message=message, autogenerate=autogenerate)

    @db_cmd.command("stamp")
    @click.argument("rev")
    def db_stamp(rev: str):
        """Stamp the database with a revision without running migrations."""
        cfg = _alembic_config()
        alembic_command.stamp(cfg, rev)

    # Users
    @app.route("/api/v1/users", methods=["POST"])
    def create_user():
        payload = request.get_json() or {}
        if not isinstance(payload, dict):
            return {"error": "Invalid payload"}, 400
        if not payload.get("email"):
            return {"error": "Missing email"}, 400
        if not payload.get("password"):
            return {"error": "Missing password"}, 400

        # ensure unique email
        for u in facade.list("User"):
            if u.get("email") == payload.get("email"):
                return {"error": "email already exists"}, 400

        try:
            obj = facade.create("User", payload)
        except ValidationError as e:
            return {"error": str(e)}, 400
        return _sanitize_user(obj), 201

    @app.route("/api/v1/auth/login", methods=["POST"])
    def login():
        data = request.get_json() or {}
        if not data.get("email") or not data.get("password"):
            return {"error": "Missing credentials"}, 400
        # find user by email
        user = None
        for u in facade.list("User"):
            if u.get("email") == data.get("email"):
                user = u
                break
        if not user:
            return {"error": "Bad credentials"}, 401
        # stored password may be hashed; use bcrypt
        import bcrypt

        stored = user.get("password")
        if not stored or not isinstance(stored, str):
            return {"error": "Bad credentials"}, 401
        try:
            if not bcrypt.checkpw(
                data.get("password").encode("utf-8"), stored.encode("utf-8")
            ):
                return {"error": "Bad credentials"}, 401
        except (ValueError, TypeError):
            return {"error": "Bad credentials"}, 401
        # create token with is_admin claim
        token = create_access_token(
            identity=user.get("id"),
            additional_claims={"is_admin": user.get("is_admin", False)},
        )
        return {"access_token": token}, 200

    @app.route("/api/v1/users", methods=["GET"])
    def list_users():
        items = facade.list("User")
        return jsonify([_sanitize_user(i) for i in items])

    @app.route("/api/v1/users/<string:obj_id>", methods=["GET", "PUT"])
    def user_item(obj_id: str):
        if request.method == "GET":
            try:
                obj = facade.get("User", obj_id)
            except NotFoundError:
                return {"error": "Not found"}, 404
            return _sanitize_user(obj)

        # PUT
        payload = request.get_json() or {}
        if not isinstance(payload, dict):
            return {"error": "Invalid payload"}, 400
        for forbidden in ("id", "created_at"):
            payload.pop(forbidden, None)
        # enforce auth: only the user themselves or admin may update
        if current_app.config.get("ENABLE_AUTH"):
            try:
                verify_jwt_in_request()
            except Exception:
                return {"error": "Missing or invalid token"}, 401
            identity = get_jwt_identity()
            is_admin = bool(get_jwt().get("is_admin", False))
            if not is_admin and identity != obj_id:
                return {"error": "Forbidden"}, 403
        try:
            obj = facade.update("User", obj_id, payload)
        except NotFoundError:
            return {"error": "Not found"}, 404
        except ValidationError as e:
            return {"error": str(e)}, 400
        return _sanitize_user(obj)

    # Amenities
    @app.route("/api/v1/amenities", methods=["POST", "GET"])
    def amenities_list():
        if request.method == "POST":
            payload = request.get_json() or {}
            if not isinstance(payload, dict):
                return {"error": "Invalid payload"}, 400
            if not payload.get("name"):
                return {"error": "Missing name"}, 400
            try:
                obj = facade.create("Amenity", payload)
            except ValidationError as e:
                return {"error": str(e)}, 400
            return _sanitize_amenity(obj), 201
        items = facade.list("Amenity")
        return jsonify(items)

    @app.route("/api/v1/amenities/<string:obj_id>", methods=["GET", "PUT"])
    def amenity_item(obj_id: str):
        if request.method == "GET":
            try:
                obj = facade.get("Amenity", obj_id)
            except NotFoundError:
                return {"error": "Not found"}, 404
            return _sanitize_amenity(obj)
        payload = request.get_json() or {}
        if not isinstance(payload, dict):
            return {"error": "Invalid payload"}, 400
        for forbidden in ("id", "created_at"):
            payload.pop(forbidden, None)
        try:
            obj = facade.update("Amenity", obj_id, payload)
        except NotFoundError:
            return {"error": "Not found"}, 404
        except ValidationError as e:
            return {"error": str(e)}, 400
        return _sanitize_amenity(obj)

    # Places
    @app.route("/api/v1/places", methods=["POST", "GET"])
    def places_list():
        if request.method == "POST":
            payload = request.get_json() or {}
            if not isinstance(payload, dict):
                return {"error": "Invalid payload"}, 400
            # enforce auth: creator must be authenticated and owner (or admin)
            if current_app.config.get("ENABLE_AUTH"):
                try:
                    verify_jwt_in_request()
                except Exception:
                    return {"error": "Missing or invalid token"}, 401
                identity = get_jwt_identity()
                is_admin = bool(get_jwt().get("is_admin", False))
                if not is_admin and identity != payload.get("user_id"):
                    return {"error": "Forbidden"}, 403
            if not payload.get("user_id"):
                return {"error": "Missing user_id"}, 400
            if not payload.get("name"):
                return {"error": "Missing name"}, 400
            if "price_by_night" in payload:
                try:
                    if int(payload["price_by_night"]) < 0:
                        return {"error": "price_by_night must be >= 0"}, 400
                except (ValueError, TypeError):
                    return {"error": "price_by_night must be int"}, 400
            try:
                facade.get("User", payload.get("user_id"))
            except NotFoundError:
                return {"error": "user_id not found"}, 400
            try:
                obj = facade.create("Place", payload)
            except ValidationError as e:
                return {"error": str(e)}, 400
            return _sanitize_place(obj), 201
        items = facade.list("Place")
        return jsonify([_sanitize_place(i) for i in items])

    @app.route("/api/v1/places/<string:obj_id>", methods=["GET", "PUT", "DELETE"])
    def place_item(obj_id: str):
        if request.method == "GET":
            try:
                obj = facade.get("Place", obj_id)
            except NotFoundError:
                return {"error": "Not found"}, 404
            return _sanitize_place(obj)
        if request.method == "PUT":
            payload = request.get_json() or {}
            if not isinstance(payload, dict):
                return {"error": "Invalid payload"}, 400
            for forbidden in ("id", "created_at"):
                payload.pop(forbidden, None)
            # enforce auth: only owner or admin may update
            if current_app.config.get("ENABLE_AUTH"):
                try:
                    verify_jwt_in_request()
                except Exception:
                    return {"error": "Missing or invalid token"}, 401
                identity = get_jwt_identity()
                is_admin = bool(get_jwt().get("is_admin", False))
                try:
                    existing = facade.get("Place", obj_id)
                except NotFoundError:
                    return {"error": "Not found"}, 404
                if not is_admin and existing.get("user_id") != identity:
                    return {"error": "Forbidden"}, 403
            try:
                obj = facade.update("Place", obj_id, payload)
            except NotFoundError:
                return {"error": "Not found"}, 404
            except ValidationError as e:
                return {"error": str(e)}, 400
            return _sanitize_place(obj)
        # DELETE
        # DELETE: only owner or admin
        if current_app.config.get("ENABLE_AUTH"):
            try:
                verify_jwt_in_request()
            except Exception:
                return {"error": "Missing or invalid token"}, 401
            identity = get_jwt_identity()
            is_admin = bool(get_jwt().get("is_admin", False))
            try:
                existing = facade.get("Place", obj_id)
            except NotFoundError:
                return {"error": "Not found"}, 404
            if not is_admin and existing.get("user_id") != identity:
                return {"error": "Forbidden"}, 403
        try:
            facade.get("Place", obj_id)
        except NotFoundError:
            return {"error": "Not found"}, 404
        facade.delete("Place", obj_id)
        return ("", 204)

    # Reviews
    @app.route("/api/v1/reviews", methods=["POST", "GET"])
    def reviews_list():
        if request.method == "POST":
            payload = request.get_json() or {}
            if not isinstance(payload, dict):
                return {"error": "Invalid payload"}, 400
            if not payload.get("place_id"):
                return {"error": "Missing place_id"}, 400
            if not payload.get("text"):
                return {"error": "Missing text"}, 400
            try:
                facade.get("Place", payload.get("place_id"))
            except NotFoundError:
                return {"error": "place_id not found"}, 400
            # enforce auth: creator must be authenticated and owner (or admin)
            if current_app.config.get("ENABLE_AUTH"):
                try:
                    verify_jwt_in_request()
                except Exception:
                    return {"error": "Missing or invalid token"}, 401
                identity = get_jwt_identity()
                is_admin = bool(get_jwt().get("is_admin", False))
                if not is_admin and identity != payload.get("user_id"):
                    return {"error": "Forbidden"}, 403
            try:
                obj = facade.create("Review", payload)
            except ValidationError as e:
                return {"error": str(e)}, 400
            return obj, 201
        items = facade.list("Review")
        return jsonify(items)

    @app.route("/api/v1/reviews/<string:obj_id>", methods=["GET", "PUT", "DELETE"])
    def review_item(obj_id: str):
        if request.method == "GET":
            try:
                obj = facade.get("Review", obj_id)
            except NotFoundError:
                return {"error": "Not found"}, 404
            return obj
        if request.method == "PUT":
            payload = request.get_json() or {}
            if not isinstance(payload, dict):
                return {"error": "Invalid payload"}, 400
            for forbidden in ("id", "created_at", "user_id", "place_id"):
                payload.pop(forbidden, None)
            # enforce auth: only review owner or admin may update
            if current_app.config.get("ENABLE_AUTH"):
                try:
                    verify_jwt_in_request()
                except Exception:
                    return {"error": "Missing or invalid token"}, 401
                identity = get_jwt_identity()
                is_admin = bool(get_jwt().get("is_admin", False))
                try:
                    existing = facade.get("Review", obj_id)
                except NotFoundError:
                    return {"error": "Not found"}, 404
                if not is_admin and existing.get("user_id") != identity:
                    return {"error": "Forbidden"}, 403
            try:
                obj = facade.update("Review", obj_id, payload)
            except NotFoundError:
                return {"error": "Not found"}, 404
            except ValidationError as e:
                return {"error": str(e)}, 400
            return obj
        # DELETE
        # DELETE: only owner or admin
        if current_app.config.get("ENABLE_AUTH"):
            try:
                verify_jwt_in_request()
            except Exception:
                return {"error": "Missing or invalid token"}, 401
            identity = get_jwt_identity()
            is_admin = bool(get_jwt().get("is_admin", False))
            try:
                existing = facade.get("Review", obj_id)
            except NotFoundError:
                return {"error": "Not found"}, 404
            if not is_admin and existing.get("user_id") != identity:
                return {"error": "Forbidden"}, 403
        try:
            facade.get("Review", obj_id)
        except NotFoundError:
            return {"error": "Not found"}, 404
        facade.delete("Review", obj_id)
        return ("", 204)

    @app.route("/health")
    def health():
        return {"status": "ok"}

    return app
