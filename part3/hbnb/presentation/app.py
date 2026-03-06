"""Flask application factory and simple REST endpoints for Part 2."""
from flask import Flask, request, jsonify
from flask_restx import Api, Namespace, Resource, fields

from ..business.facade import HBNBFacade, NotFoundError, ValidationError
from ..persistence.in_memory_repository import InMemoryRepository


def create_app(config: dict | None = None):
    app = Flask(__name__)
    app.config.update(config or {})

    api = Api(app, version="0.1", title="HBNB API", doc="/docs")

    repo = InMemoryRepository()
    facade = HBNBFacade(repo)

    ns = Namespace("objects", description="Object operations")

    obj_model = api.model("Object", {"name": fields.String(required=True)})


    @ns.route("/<string:cls_name>")
    class ObjectList(Resource):
        @ns.expect(obj_model)
        def post(self, cls_name):
            payload = request.json or {}
            obj = facade.create(cls_name, payload)
            return jsonify(obj)

        def get(self, cls_name):
            items = facade.list(cls_name)
            return jsonify(items)


    @ns.route("/<string:cls_name>/<string:obj_id>")
    class ObjectItem(Resource):
        def get(self, cls_name, obj_id):
            obj = facade.get(cls_name, obj_id)
            return jsonify(obj)

        @ns.expect(obj_model)
        def put(self, cls_name, obj_id):
            payload = request.json or {}
            obj = facade.update(cls_name, obj_id, payload)
            return jsonify(obj)

        def delete(self, cls_name, obj_id):
            facade.delete(cls_name, obj_id)
            return ("", 204)

    api.add_namespace(ns, path="/objects")

    # User-specific API
    users_ns = Namespace("users", description="User operations")

    user_model = api.model("User", {"email": fields.String(required=True), "password": fields.String(required=True)})

    def _sanitize_user(obj: dict) -> dict:
        out = dict(obj)
        out.pop("password", None)
        return out


    @users_ns.route("")
    class UsersList(Resource):
        @users_ns.expect(user_model, validate=False)
        def post(self):
            payload = request.json or {}
            # basic required fields
            if not isinstance(payload, dict):
                return {"error": "Invalid payload"}, 400
            if not payload.get("email"):
                return {"error": "Missing email"}, 400
            if not payload.get("password"):
                return {"error": "Missing password"}, 400
            try:
                obj = facade.create("User", payload)
            except ValidationError as e:
                return {"error": str(e)}, 400
            return _sanitize_user(obj), 201

        def get(self):
            items = facade.list("User")
            return jsonify([_sanitize_user(i) for i in items])


    @users_ns.route("/<string:obj_id>")
    class UsersItem(Resource):
        def get(self, obj_id):
            try:
                obj = facade.get("User", obj_id)
            except NotFoundError:
                return {"error": "Not found"}, 404
            return _sanitize_user(obj)

        @users_ns.expect(user_model, validate=False)
        def put(self, obj_id):
            payload = request.json or {}
            if not isinstance(payload, dict):
                return {"error": "Invalid payload"}, 400
            # prevent updating immutable fields
            for forbidden in ("id", "created_at"):
                payload.pop(forbidden, None)
            try:
                obj = facade.update("User", obj_id, payload)
            except NotFoundError:
                return {"error": "Not found"}, 404
            except ValidationError as e:
                return {"error": str(e)}, 400
            return _sanitize_user(obj)

    api.add_namespace(users_ns, path="/api/v1/users")

    # Amenity-specific API
    amenities_ns = Namespace("amenities", description="Amenity operations")

    amenity_model = api.model("Amenity", {"name": fields.String(required=True)})

    def _sanitize_amenity(obj: dict) -> dict:
        return dict(obj)


    @amenities_ns.route("")
    class AmenitiesList(Resource):
        @amenities_ns.expect(amenity_model, validate=False)
        def post(self):
            payload = request.json or {}
            if not isinstance(payload, dict):
                return {"error": "Invalid payload"}, 400
            if not payload.get("name"):
                return {"error": "Missing name"}, 400
            try:
                obj = facade.create("Amenity", payload)
            except ValidationError as e:
                return {"error": str(e)}, 400
            return _sanitize_amenity(obj), 201

        def get(self):
            items = facade.list("Amenity")
            return jsonify([_sanitize_amenity(i) for i in items])


    @amenities_ns.route("/<string:obj_id>")
    class AmenitiesItem(Resource):
        def get(self, obj_id):
            try:
                obj = facade.get("Amenity", obj_id)
            except NotFoundError:
                return {"error": "Not found"}, 404
            return _sanitize_amenity(obj)

        @amenities_ns.expect(amenity_model, validate=False)
        def put(self, obj_id):
            payload = request.json or {}
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

    api.add_namespace(amenities_ns, path="/api/v1/amenities")

    # Place-specific API
    places_ns = Namespace("places", description="Place operations")

    place_model = api.model("Place", {
        "name": fields.String(required=True),
        "description": fields.String(required=False),
        "number_rooms": fields.Integer(required=False),
        "number_bathrooms": fields.Integer(required=False),
        "max_guest": fields.Integer(required=False),
        "price_by_night": fields.Integer(required=False),
        "latitude": fields.Float(required=False),
        "longitude": fields.Float(required=False),
        "user_id": fields.String(required=False),
        "amenity_ids": fields.List(fields.String, required=False)
    })

    def _sanitize_place(obj: dict) -> dict:
        out = dict(obj)
        # attach owner summary if possible
        owner_id = out.pop("user_id", None)
        if owner_id:
            try:
                owner = facade.get("User", owner_id)
                out["owner"] = {"id": owner.get("id"), "email": owner.get("email" )}
            except Exception:
                out["owner"] = {"id": owner_id}
        else:
            out["owner"] = None
        # attach amenity objects
        amenity_ids = out.get("amenity_ids") or []
        amenities = []
        for aid in amenity_ids:
            try:
                a = facade.get("Amenity", aid)
                amenities.append(a)
            except Exception:
                continue
        out["amenities"] = amenities
        # attach reviews for this place
        try:
            all_reviews = facade.list("Review")
            place_reviews = [r for r in all_reviews if r.get("place_id") == out.get("id")]
        except Exception:
            place_reviews = []
        out["reviews"] = place_reviews
        return out


    @places_ns.route("")
    class PlacesList(Resource):
        @places_ns.expect(place_model, validate=False)
        def post(self):
            payload = request.json or {}
            if not isinstance(payload, dict):
                return {"error": "Invalid payload"}, 400
            # validation
            if not payload.get("name"):
                return {"error": "Missing name"}, 400
            if "price_by_night" in payload:
                try:
                    if int(payload["price_by_night"]) < 0:
                        return {"error": "price_by_night must be >= 0"}, 400
                except Exception:
                    return {"error": "price_by_night must be int"}, 400
            if "latitude" in payload:
                try:
                    float(payload["latitude"])
                except Exception:
                    return {"error": "latitude must be float"}, 400
            if "longitude" in payload:
                try:
                    float(payload["longitude"])
                except Exception:
                    return {"error": "longitude must be float"}, 400
            # user_id is required and must reference an existing User
            user_id = payload.get("user_id")
            if not user_id:
                return {"error": "Missing user_id"}, 400
            try:
                facade.get("User", user_id)
            except Exception:
                return {"error": "user_id not found"}, 400
            try:
                obj = facade.create("Place", payload)
            except ValidationError as e:
                return {"error": str(e)}, 400
            return _sanitize_place(obj), 201

        def get(self):
            items = facade.list("Place")
            return jsonify([_sanitize_place(i) for i in items])


    @places_ns.route("/<string:obj_id>")
    class PlacesItem(Resource):
        def get(self, obj_id):
            try:
                obj = facade.get("Place", obj_id)
            except NotFoundError:
                return {"error": "Not found"}, 404
            return _sanitize_place(obj)

        @places_ns.expect(place_model, validate=False)
        def put(self, obj_id):
            payload = request.json or {}
            if not isinstance(payload, dict):
                return {"error": "Invalid payload"}, 400
            for forbidden in ("id", "created_at"):
                payload.pop(forbidden, None)
            if "price_by_night" in payload:
                try:
                    if int(payload["price_by_night"]) < 0:
                        return {"error": "price_by_night must be >= 0"}, 400
                except Exception:
                    return {"error": "price_by_night must be int"}, 400
            if "latitude" in payload:
                try:
                    float(payload["latitude"])
                except Exception:
                    return {"error": "latitude must be float"}, 400
            if "longitude" in payload:
                try:
                    float(payload["longitude"])
                except Exception:
                    return {"error": "longitude must be float"}, 400
            # owner validation
            if "user_id" in payload and payload["user_id"]:
                try:
                    facade.get("User", payload["user_id"])
                except Exception:
                    return {"error": "user_id not found"}, 400
            try:
                obj = facade.update("Place", obj_id, payload)
            except NotFoundError:
                return {"error": "Not found"}, 404
            except ValidationError as e:
                return {"error": str(e)}, 400
            return _sanitize_place(obj)

    api.add_namespace(places_ns, path="/api/v1/places")

    # Review-specific API
    reviews_ns = Namespace("reviews", description="Review operations")

    review_model = api.model("Review", {
        "user_id": fields.String(required=True),
        "place_id": fields.String(required=True),
        "text": fields.String(required=True),
    })


    @reviews_ns.route("")
    class ReviewsList(Resource):
        @reviews_ns.expect(review_model, validate=False)
        def post(self):
            payload = request.json or {}
            if not isinstance(payload, dict):
                return {"error": "Invalid payload"}, 400
            if not payload.get("user_id"):
                return {"error": "Missing user_id"}, 400
            if not payload.get("place_id"):
                return {"error": "Missing place_id"}, 400
            if not payload.get("text"):
                return {"error": "Missing text"}, 400
            # verify user and place exist
            try:
                facade.get("User", payload.get("user_id"))
            except Exception:
                return {"error": "user_id not found"}, 400
            try:
                facade.get("Place", payload.get("place_id"))
            except Exception:
                return {"error": "place_id not found"}, 400
            try:
                obj = facade.create("Review", payload)
            except ValidationError as e:
                return {"error": str(e)}, 400
            return obj, 201

        def get(self):
            items = facade.list("Review")
            return jsonify(items)


    @reviews_ns.route("/<string:obj_id>")
    class ReviewsItem(Resource):
        def get(self, obj_id):
            try:
                obj = facade.get("Review", obj_id)
            except NotFoundError:
                return {"error": "Not found"}, 404
            return obj

        @reviews_ns.expect(review_model, validate=False)
        def put(self, obj_id):
            payload = request.json or {}
            if not isinstance(payload, dict):
                return {"error": "Invalid payload"}, 400
            # prevent changing relational keys
            for forbidden in ("id", "created_at", "user_id", "place_id"):
                payload.pop(forbidden, None)
            if "text" in payload and not isinstance(payload["text"], str):
                return {"error": "text must be string"}, 400
            try:
                obj = facade.update("Review", obj_id, payload)
            except NotFoundError:
                return {"error": "Not found"}, 404
            except ValidationError as e:
                return {"error": str(e)}, 400
            return obj

        def delete(self, obj_id):
            try:
                facade.delete("Review", obj_id)
            except NotFoundError:
                return {"error": "Not found"}, 404
            return ("", 204)

    api.add_namespace(reviews_ns, path="/api/v1/reviews")

    @app.route("/health")
    def health():
        return {"status": "ok"}

    return app
