import stripe
import os
from datetime import datetime, timedelta
from typing import Dict, Optional
from src.models.user import Payment, Subscription, db

class PaymentService:
    """Service for handling payment processing with Stripe."""
    
    def __init__(self):
        # Set Stripe API key (use test key for development)
        stripe.api_key = os.getenv('STRIPE_SECRET_KEY', 'sk_test_...')  # Replace with actual test key
        
        # Subscription plans
        self.subscription_plans = {
            'basic': {
                'name': 'Basic Plan',
                'price': 9.99,
                'features': ['Document storage', 'Basic OCR', 'Email support']
            },
            'premium': {
                'name': 'Premium Plan',
                'price': 19.99,
                'features': ['Unlimited storage', 'Advanced OCR', 'Priority support', 'Bank integration']
            },
            'professional': {
                'name': 'Professional Plan',
                'price': 49.99,
                'features': ['All Premium features', 'CPA collaboration', 'Advanced reporting', 'API access']
            }
        }
        
        # One-time service prices
        self.service_prices = {
            'individual_tax_return': 99.99,
            'business_tax_return': 199.99,
            'tax_consultation': 150.00,
            'document_review': 75.00
        }
    
    def create_payment_intent(self, amount: float, currency: str = 'usd', 
                            metadata: Optional[Dict] = None) -> Dict:
        """Create a Stripe payment intent."""
        try:
            intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),  # Stripe uses cents
                currency=currency,
                metadata=metadata or {},
                automatic_payment_methods={'enabled': True}
            )
            
            return {
                'success': True,
                'client_secret': intent.client_secret,
                'payment_intent_id': intent.id
            }
        except stripe.error.StripeError as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def confirm_payment(self, payment_intent_id: str, user_id: int, 
                       service_type: str = 'one_time') -> Dict:
        """Confirm a payment and record it in the database."""
        try:
            # Retrieve the payment intent from Stripe
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            if intent.status == 'succeeded':
                # Record payment in database
                payment = Payment(
                    user_id=user_id,
                    amount=intent.amount / 100,  # Convert from cents
                    currency=intent.currency,
                    payment_method='stripe',
                    transaction_id=payment_intent_id,
                    status='succeeded'
                )
                
                db.session.add(payment)
                db.session.commit()
                
                return {
                    'success': True,
                    'payment': payment.to_dict()
                }
            else:
                return {
                    'success': False,
                    'error': f'Payment status: {intent.status}'
                }
                
        except stripe.error.StripeError as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_subscription(self, user_id: int, plan_type: str, 
                          payment_method_id: str) -> Dict:
        """Create a subscription for a user."""
        try:
            if plan_type not in self.subscription_plans:
                return {
                    'success': False,
                    'error': 'Invalid subscription plan'
                }
            
            plan = self.subscription_plans[plan_type]
            
            # Create Stripe customer
            customer = stripe.Customer.create(
                payment_method=payment_method_id,
                invoice_settings={'default_payment_method': payment_method_id}
            )
            
            # Create Stripe subscription
            subscription = stripe.Subscription.create(
                customer=customer.id,
                items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {'name': plan['name']},
                        'unit_amount': int(plan['price'] * 100),
                        'recurring': {'interval': 'month'}
                    }
                }],
                expand=['latest_invoice.payment_intent']
            )
            
            # Record subscription in database
            start_date = datetime.utcnow()
            end_date = start_date + timedelta(days=30)  # Monthly subscription
            
            db_subscription = Subscription(
                user_id=user_id,
                plan_type=plan_type,
                start_date=start_date,
                end_date=end_date,
                status='active'
            )
            
            db.session.add(db_subscription)
            db.session.commit()
            
            return {
                'success': True,
                'subscription': db_subscription.to_dict(),
                'stripe_subscription_id': subscription.id
            }
            
        except stripe.error.StripeError as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def cancel_subscription(self, user_id: int) -> Dict:
        """Cancel a user's subscription."""
        try:
            # Find active subscription
            subscription = Subscription.query.filter_by(
                user_id=user_id, 
                status='active'
            ).first()
            
            if not subscription:
                return {
                    'success': False,
                    'error': 'No active subscription found'
                }
            
            # Update subscription status
            subscription.status = 'canceled'
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Subscription canceled successfully'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_subscription_plans(self) -> Dict:
        """Get available subscription plans."""
        return self.subscription_plans
    
    def get_service_prices(self) -> Dict:
        """Get one-time service prices."""
        return self.service_prices
    
    def process_one_time_payment(self, user_id: int, service_type: str, 
                                payment_method_id: str) -> Dict:
        """Process a one-time payment for a service."""
        try:
            if service_type not in self.service_prices:
                return {
                    'success': False,
                    'error': 'Invalid service type'
                }
            
            amount = self.service_prices[service_type]
            
            # Create payment intent
            intent_result = self.create_payment_intent(
                amount=amount,
                metadata={
                    'user_id': str(user_id),
                    'service_type': service_type
                }
            )
            
            if not intent_result['success']:
                return intent_result
            
            # Confirm payment immediately with payment method
            try:
                intent = stripe.PaymentIntent.confirm(
                    intent_result['payment_intent_id'],
                    payment_method=payment_method_id
                )
                
                if intent.status == 'succeeded':
                    return self.confirm_payment(
                        intent.id, 
                        user_id, 
                        service_type
                    )
                else:
                    return {
                        'success': False,
                        'error': f'Payment failed: {intent.status}'
                    }
                    
            except stripe.error.StripeError as e:
                return {
                    'success': False,
                    'error': str(e)
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
