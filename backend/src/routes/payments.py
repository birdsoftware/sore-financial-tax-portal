from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.services.payment_service import PaymentService
from src.models.user import User, Payment, Subscription

payments_bp = Blueprint('payments', __name__)

@payments_bp.route('/payment/plans', methods=['GET'])
def get_subscription_plans():
    """Get available subscription plans."""
    payment_service = PaymentService()
    plans = payment_service.get_subscription_plans()
    return jsonify(plans), 200

@payments_bp.route('/payment/services', methods=['GET'])
def get_service_prices():
    """Get one-time service prices."""
    payment_service = PaymentService()
    services = payment_service.get_service_prices()
    return jsonify(services), 200

@payments_bp.route('/payment/intent', methods=['POST'])
@jwt_required()
def create_payment_intent():
    """Create a payment intent for one-time payment."""
    user_id = int(get_jwt_identity())
    data = request.json
    
    if not data.get('amount'):
        return jsonify({'error': 'Amount is required'}), 400
    
    payment_service = PaymentService()
    result = payment_service.create_payment_intent(
        amount=float(data['amount']),
        currency=data.get('currency', 'usd'),
        metadata={
            'user_id': str(user_id),
            'service_type': data.get('service_type', 'custom')
        }
    )
    
    if result['success']:
        return jsonify({
            'client_secret': result['client_secret'],
            'payment_intent_id': result['payment_intent_id']
        }), 200
    else:
        return jsonify({'error': result['error']}), 400

@payments_bp.route('/payment/confirm', methods=['POST'])
@jwt_required()
def confirm_payment():
    """Confirm a payment after successful processing."""
    user_id = int(get_jwt_identity())
    data = request.json
    
    if not data.get('payment_intent_id'):
        return jsonify({'error': 'Payment intent ID is required'}), 400
    
    payment_service = PaymentService()
    result = payment_service.confirm_payment(
        payment_intent_id=data['payment_intent_id'],
        user_id=user_id,
        service_type=data.get('service_type', 'one_time')
    )
    
    if result['success']:
        return jsonify(result['payment']), 200
    else:
        return jsonify({'error': result['error']}), 400

@payments_bp.route('/payment/service', methods=['POST'])
@jwt_required()
def process_service_payment():
    """Process payment for a specific service."""
    user_id = int(get_jwt_identity())
    data = request.json
    
    required_fields = ['service_type', 'payment_method_id']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400
    
    payment_service = PaymentService()
    result = payment_service.process_one_time_payment(
        user_id=user_id,
        service_type=data['service_type'],
        payment_method_id=data['payment_method_id']
    )
    
    if result['success']:
        return jsonify(result['payment']), 200
    else:
        return jsonify({'error': result['error']}), 400

@payments_bp.route('/subscription', methods=['POST'])
@jwt_required()
def create_subscription():
    """Create a new subscription."""
    user_id = int(get_jwt_identity())
    data = request.json
    
    required_fields = ['plan_type', 'payment_method_id']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400
    
    payment_service = PaymentService()
    result = payment_service.create_subscription(
        user_id=user_id,
        plan_type=data['plan_type'],
        payment_method_id=data['payment_method_id']
    )
    
    if result['success']:
        return jsonify(result['subscription']), 201
    else:
        return jsonify({'error': result['error']}), 400

@payments_bp.route('/subscription', methods=['GET'])
@jwt_required()
def get_user_subscription():
    """Get user's current subscription."""
    user_id = int(get_jwt_identity())
    
    subscription = Subscription.query.filter_by(
        user_id=user_id,
        status='active'
    ).first()
    
    if subscription:
        return jsonify(subscription.to_dict()), 200
    else:
        return jsonify({'message': 'No active subscription'}), 404

@payments_bp.route('/subscription', methods=['DELETE'])
@jwt_required()
def cancel_subscription():
    """Cancel user's subscription."""
    user_id = int(get_jwt_identity())
    
    payment_service = PaymentService()
    result = payment_service.cancel_subscription(user_id)
    
    if result['success']:
        return jsonify({'message': result['message']}), 200
    else:
        return jsonify({'error': result['error']}), 400

@payments_bp.route('/payments/history', methods=['GET'])
@jwt_required()
def get_payment_history():
    """Get user's payment history."""
    user_id = int(get_jwt_identity())
    
    payments = Payment.query.filter_by(user_id=user_id).order_by(
        Payment.created_at.desc()
    ).all()
    
    return jsonify([payment.to_dict() for payment in payments]), 200

@payments_bp.route('/subscription/history', methods=['GET'])
@jwt_required()
def get_subscription_history():
    """Get user's subscription history."""
    user_id = int(get_jwt_identity())
    
    subscriptions = Subscription.query.filter_by(user_id=user_id).order_by(
        Subscription.start_date.desc()
    ).all()
    
    return jsonify([sub.to_dict() for sub in subscriptions]), 200
