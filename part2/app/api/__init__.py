from flask import Blueprint, jsonify

blueprint = Blueprint('api', __name__)

@blueprint.route('/api/health', methods=['GET'])
def health_check():

from flask import Blueprint, jsonify, request

from app.facade import HBnBFacade
from app.models.base import BaseModel

blueprint = Blueprint('api', __name__)

# Facade instance (simple module-scoped singleton for demonstration)
facade = HBnBFacade()

@blueprint.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'message': 'HBnB API (in-memory persistence)'})

@blueprint.route('/api/objects', methods=['GET'])
def list_objects():
    return jsonify(facade.list())

@blueprint.route('/api/objects', methods=['POST'])
def create_object():
    # For now, objects are simple BaseModel instances; request body is ignored.
    obj = BaseModel()
    created = facade.create(obj)
    return jsonify(created), 201
