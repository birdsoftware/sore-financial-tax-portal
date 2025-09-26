from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import TaxReturn, User, db

tax_returns_bp = Blueprint('tax_returns', __name__)

@tax_returns_bp.route('/returns', methods=['POST'])
@jwt_required()
def create_tax_return():
    user_id = int(get_jwt_identity())
    data = request.json
    
    if not data.get('year'):
        return jsonify({'error': 'Year is required'}), 400
    
    # Check if tax return for this year already exists
    existing_return = TaxReturn.query.filter_by(user_id=user_id, year=data['year']).first()
    if existing_return:
        return jsonify({'error': 'Tax return for this year already exists'}), 400
    
    tax_return = TaxReturn(
        user_id=user_id,
        year=data['year'],
        status='draft',
        return_data=data.get('return_data', {})
    )
    
    db.session.add(tax_return)
    db.session.commit()
    
    return jsonify(tax_return.to_dict()), 201

@tax_returns_bp.route('/returns', methods=['GET'])
@jwt_required()
def get_tax_returns():
    user_id = int(get_jwt_identity())
    tax_returns = TaxReturn.query.filter_by(user_id=user_id).all()
    return jsonify([tr.to_dict() for tr in tax_returns]), 200

@tax_returns_bp.route('/returns/<int:return_id>', methods=['GET'])
@jwt_required()
def get_tax_return(return_id):
    user_id = int(get_jwt_identity())
    tax_return = TaxReturn.query.filter_by(id=return_id, user_id=user_id).first()
    
    if not tax_return:
        return jsonify({'error': 'Tax return not found'}), 404
    
    return jsonify(tax_return.to_dict()), 200

@tax_returns_bp.route('/returns/<int:return_id>', methods=['PUT'])
@jwt_required()
def update_tax_return(return_id):
    user_id = int(get_jwt_identity())
    tax_return = TaxReturn.query.filter_by(id=return_id, user_id=user_id).first()
    
    if not tax_return:
        return jsonify({'error': 'Tax return not found'}), 404
    
    data = request.json
    
    if 'return_data' in data:
        tax_return.return_data = data['return_data']
    if 'status' in data:
        tax_return.status = data['status']
    
    db.session.commit()
    
    return jsonify(tax_return.to_dict()), 200

# CPA routes for managing client tax returns
@tax_returns_bp.route('/cpa/clients', methods=['GET'])
@jwt_required()
def get_cpa_clients():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    # Check if current user is a CPA
    if not user or user.user_type != 'cpa':
        return jsonify({'error': 'Access denied'}), 403
    
    # Get all clients (users who are not CPAs)
    clients = User.query.filter(User.user_type.in_(['individual', 'business'])).all()
    return jsonify([client.to_dict() for client in clients]), 200

@tax_returns_bp.route('/cpa/clients/<int:client_id>/returns', methods=['GET'])
@jwt_required()
def get_client_tax_returns(client_id):
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    # Check if current user is a CPA
    if not user or user.user_type != 'cpa':
        return jsonify({'error': 'Access denied'}), 403
    
    tax_returns = TaxReturn.query.filter_by(user_id=client_id).all()
    return jsonify([tr.to_dict() for tr in tax_returns]), 200

@tax_returns_bp.route('/cpa/returns/<int:return_id>/assign', methods=['PUT'])
@jwt_required()
def assign_cpa_to_return(return_id):
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    # Check if current user is a CPA
    if not user or user.user_type != 'cpa':
        return jsonify({'error': 'Access denied'}), 403
    
    tax_return = TaxReturn.query.get(return_id)
    if not tax_return:
        return jsonify({'error': 'Tax return not found'}), 404
    
    tax_return.cpa_id = user_id
    tax_return.status = 'in_review'
    
    db.session.commit()
    
    return jsonify(tax_return.to_dict()), 200

@tax_returns_bp.route('/cpa/returns/<int:return_id>/file', methods=['PUT'])
@jwt_required()
def file_tax_return(return_id):
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    # Check if current user is a CPA
    if not user or user.user_type != 'cpa':
        return jsonify({'error': 'Access denied'}), 403
    
    tax_return = TaxReturn.query.get(return_id)
    if not tax_return:
        return jsonify({'error': 'Tax return not found'}), 404
    
    if tax_return.cpa_id != user_id:
        return jsonify({'error': 'You are not assigned to this tax return'}), 403
    
    tax_return.status = 'filed'
    
    db.session.commit()
    
    return jsonify(tax_return.to_dict()), 200
