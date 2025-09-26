import React, { useState, useEffect } from 'react';
import { loadStripe } from '@stripe/stripe-js';
import { Elements, CardElement, useStripe, useElements } from '@stripe/react-stripe-js';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  CreditCard, 
  Check, 
  X, 
  Loader2, 
  Crown, 
  Star,
  Zap
} from 'lucide-react';
import axios from 'axios';

// Initialize Stripe (use your publishable key)
const stripePromise = loadStripe('pk_test_...');  // Replace with actual publishable key

const SubscriptionForm = ({ plan, onSuccess, onError }) => {
  const stripe = useStripe();
  const elements = useElements();
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    
    if (!stripe || !elements) {
      return;
    }

    setLoading(true);

    const cardElement = elements.getElement(CardElement);

    try {
      // Create payment method
      const { error, paymentMethod } = await stripe.createPaymentMethod({
        type: 'card',
        card: cardElement,
      });

      if (error) {
        onError(error.message);
        setLoading(false);
        return;
      }

      // Create subscription
      const response = await axios.post('/api/subscription', {
        plan_type: plan.id,
        payment_method_id: paymentMethod.id
      });

      onSuccess(response.data);
    } catch (error) {
      onError(error.response?.data?.error || 'Subscription failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="p-4 border rounded-lg">
        <CardElement
          options={{
            style: {
              base: {
                fontSize: '16px',
                color: '#424770',
                '::placeholder': {
                  color: '#aab7c4',
                },
              },
            },
          }}
        />
      </div>
      
      <Button type="submit" disabled={!stripe || loading} className="w-full">
        {loading ? (
          <>
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            Processing...
          </>
        ) : (
          <>
            <CreditCard className="mr-2 h-4 w-4" />
            Subscribe to {plan.name}
          </>
        )}
      </Button>
    </form>
  );
};

const PlanCard = ({ plan, isCurrentPlan, onSelectPlan }) => {
  const planIcons = {
    basic: <Zap className="h-6 w-6" />,
    premium: <Star className="h-6 w-6" />,
    professional: <Crown className="h-6 w-6" />
  };

  const planColors = {
    basic: 'border-blue-200 bg-blue-50',
    premium: 'border-purple-200 bg-purple-50',
    professional: 'border-gold-200 bg-yellow-50'
  };

  return (
    <Card className={`relative ${planColors[plan.id] || ''} ${isCurrentPlan ? 'ring-2 ring-primary' : ''}`}>
      {isCurrentPlan && (
        <Badge className="absolute -top-2 left-1/2 transform -translate-x-1/2">
          Current Plan
        </Badge>
      )}
      
      <CardHeader className="text-center">
        <div className="mx-auto mb-2 p-2 rounded-full bg-white">
          {planIcons[plan.id]}
        </div>
        <CardTitle className="text-xl">{plan.name}</CardTitle>
        <CardDescription>
          <span className="text-3xl font-bold">${plan.price}</span>
          <span className="text-muted-foreground">/month</span>
        </CardDescription>
      </CardHeader>
      
      <CardContent className="space-y-4">
        <ul className="space-y-2">
          {plan.features.map((feature, index) => (
            <li key={index} className="flex items-center gap-2">
              <Check className="h-4 w-4 text-green-500" />
              <span className="text-sm">{feature}</span>
            </li>
          ))}
        </ul>
        
        {!isCurrentPlan && (
          <Button onClick={() => onSelectPlan(plan)} className="w-full">
            Select Plan
          </Button>
        )}
      </CardContent>
    </Card>
  );
};

const ServiceCard = ({ service, onPurchase }) => {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">{service.name}</CardTitle>
        <CardDescription>
          <span className="text-2xl font-bold">${service.price}</span>
        </CardDescription>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-muted-foreground mb-4">{service.description}</p>
        <Button onClick={() => onPurchase(service)} className="w-full">
          Purchase Service
        </Button>
      </CardContent>
    </Card>
  );
};

const SubscriptionManager = () => {
  const [plans, setPlans] = useState({});
  const [services, setServices] = useState({});
  const [currentSubscription, setCurrentSubscription] = useState(null);
  const [selectedPlan, setSelectedPlan] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [plansRes, servicesRes, subscriptionRes] = await Promise.all([
        axios.get('/api/payment/plans'),
        axios.get('/api/payment/services'),
        axios.get('/api/subscription').catch(() => ({ data: null }))
      ]);

      // Transform plans data
      const transformedPlans = Object.entries(plansRes.data).map(([id, plan]) => ({
        id,
        ...plan
      }));
      setPlans(transformedPlans);

      // Transform services data
      const transformedServices = Object.entries(servicesRes.data).map(([id, price]) => ({
        id,
        name: id.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()),
        price,
        description: getServiceDescription(id)
      }));
      setServices(transformedServices);

      setCurrentSubscription(subscriptionRes.data);
    } catch (error) {
      setError('Failed to load subscription data');
    } finally {
      setLoading(false);
    }
  };

  const getServiceDescription = (serviceId) => {
    const descriptions = {
      individual_tax_return: 'Complete individual tax return preparation and filing',
      business_tax_return: 'Comprehensive business tax return preparation and filing',
      tax_consultation: 'One-on-one consultation with a certified tax professional',
      document_review: 'Professional review of your tax documents and forms'
    };
    return descriptions[serviceId] || 'Professional tax service';
  };

  const handlePlanSelect = (plan) => {
    setSelectedPlan(plan);
    setError('');
    setSuccess('');
  };

  const handleSubscriptionSuccess = (subscription) => {
    setCurrentSubscription(subscription);
    setSelectedPlan(null);
    setSuccess('Subscription created successfully!');
    setTimeout(() => setSuccess(''), 5000);
  };

  const handleSubscriptionError = (errorMessage) => {
    setError(errorMessage);
    setTimeout(() => setError(''), 5000);
  };

  const handleCancelSubscription = async () => {
    try {
      await axios.delete('/api/subscription');
      setCurrentSubscription(null);
      setSuccess('Subscription canceled successfully');
      setTimeout(() => setSuccess(''), 5000);
    } catch (error) {
      setError('Failed to cancel subscription');
      setTimeout(() => setError(''), 5000);
    }
  };

  const handleServicePurchase = async (service) => {
    // This would typically open a payment modal
    // For now, we'll just show an alert
    alert(`Purchase ${service.name} for $${service.price} - Feature coming soon!`);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {error && (
        <Alert variant="destructive">
          <X className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {success && (
        <Alert>
          <Check className="h-4 w-4" />
          <AlertDescription>{success}</AlertDescription>
        </Alert>
      )}

      <Tabs defaultValue="subscriptions" className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="subscriptions">Subscriptions</TabsTrigger>
          <TabsTrigger value="services">One-Time Services</TabsTrigger>
        </TabsList>

        <TabsContent value="subscriptions" className="space-y-6">
          {currentSubscription && (
            <Card>
              <CardHeader>
                <CardTitle>Current Subscription</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex justify-between items-center">
                  <div>
                    <p className="font-medium">{currentSubscription.plan_type} Plan</p>
                    <p className="text-sm text-muted-foreground">
                      Active until {new Date(currentSubscription.end_date).toLocaleDateString()}
                    </p>
                  </div>
                  <Badge variant="success">Active</Badge>
                </div>
                <Button variant="destructive" onClick={handleCancelSubscription}>
                  Cancel Subscription
                </Button>
              </CardContent>
            </Card>
          )}

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {plans.map((plan) => (
              <PlanCard
                key={plan.id}
                plan={plan}
                isCurrentPlan={currentSubscription?.plan_type === plan.id}
                onSelectPlan={handlePlanSelect}
              />
            ))}
          </div>

          {selectedPlan && (
            <Card>
              <CardHeader>
                <CardTitle>Subscribe to {selectedPlan.name}</CardTitle>
                <CardDescription>
                  Enter your payment information to start your subscription
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Elements stripe={stripePromise}>
                  <SubscriptionForm
                    plan={selectedPlan}
                    onSuccess={handleSubscriptionSuccess}
                    onError={handleSubscriptionError}
                  />
                </Elements>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="services" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {services.map((service) => (
              <ServiceCard
                key={service.id}
                service={service}
                onPurchase={handleServicePurchase}
              />
            ))}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default SubscriptionManager;
