# Sore Financial Group Tax Portal

A professional, full-stack web application for tax preparation and filing services, built with React frontend and Flask backend.

## 🌐 Live Demo

**Production URL:** https://p9hwiqcqxxmn.manus.space

## 📋 Overview

The Sore Financial Group Tax Portal is a comprehensive tax management platform that enables individuals and businesses to prepare and file taxes online with CPA oversight. The application provides secure document management, automated tax calculations, and seamless integration with payment processing.

## ✨ Key Features

### For Individual Users
- Secure account registration and authentication
- Tax document upload and management (W-2, 1099, receipts)
- Guided tax return preparation with real-time calculations
- Receipt organization and expense categorization
- Subscription-based service plans

### For Business Users
- Business tax document handling and organization
- Expense tracking and categorization tools
- Multi-year tax return management
- CPA collaboration and review features

### For CPA Users
- Client management dashboard
- Tax return review and approval workflow
- Direct client communication tools
- Bulk document processing capabilities

## 🏗️ Technical Architecture

### Frontend (React)
- **Framework:** React 18 with modern hooks
- **Styling:** Tailwind CSS + shadcn/ui components
- **State Management:** Context API for authentication
- **Routing:** React Router for SPA navigation
- **HTTP Client:** Axios for API communication

### Backend (Flask)
- **Framework:** Flask with SQLAlchemy ORM
- **Authentication:** JWT-based with secure password hashing
- **Database:** SQLite (production-ready, upgradeable to PostgreSQL)
- **Security:** CORS enabled, input validation, secure file uploads
- **Payment Processing:** Stripe integration

### Database Schema
- **Users:** Multi-role support (Individual, Business, CPA)
- **Tax Documents:** Secure file storage with metadata
- **Receipts:** Expense tracking with categorization
- **Tax Returns:** Draft and final return management
- **Payments & Subscriptions:** Stripe-integrated billing

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Git

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python src/main.py
```

### Frontend Setup
```bash
cd frontend
pnpm install  # or npm install
pnpm run dev  # or npm run dev
```

### Environment Variables
Create `.env` files in both backend and frontend directories:

**Backend (.env):**
```
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
STRIPE_SECRET_KEY=your-stripe-secret-key
STRIPE_PUBLISHABLE_KEY=your-stripe-publishable-key
```

**Frontend (.env):**
```
VITE_API_BASE_URL=http://localhost:5000
VITE_STRIPE_PUBLISHABLE_KEY=your-stripe-publishable-key
```

## 📁 Project Structure

```
sore-financial-tax-portal/
├── backend/                 # Flask API backend
│   ├── src/
│   │   ├── models/         # Database models
│   │   ├── routes/         # API endpoints
│   │   ├── services/       # Business logic
│   │   └── main.py         # Application entry point
│   ├── requirements.txt    # Python dependencies
│   └── README.md
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── contexts/       # React contexts
│   │   ├── pages/          # Page components
│   │   └── App.jsx         # Main app component
│   ├── package.json        # Node.js dependencies
│   └── README.md
├── docs/                   # Documentation
│   ├── technical_architecture.md
│   ├── database_schema.md
│   ├── api_specifications.md
│   └── deployment_summary.md
└── README.md              # This file
```

## 🔐 Security Features

- **JWT Authentication:** Secure token-based authentication
- **Password Security:** Bcrypt hashing with salt
- **Input Validation:** Server-side validation for all endpoints
- **File Upload Security:** Restricted file types and secure storage
- **CORS Protection:** Configured for production environment
- **SQL Injection Prevention:** SQLAlchemy ORM with parameterized queries

## 💳 Payment Integration

### Subscription Plans
- **Basic ($9.99/month):** Document storage + basic features
- **Premium ($19.99/month):** Unlimited storage + expense tracking
- **Professional ($39.99/month):** CPA collaboration + priority support

### One-time Services
- Individual Tax Return: $49.99
- Business Tax Return: $149.99
- Tax Consultation: $99.99/hour

## 🧪 Testing

The application includes comprehensive API testing:

```bash
cd backend
python test_api.py
```

**Test Coverage:**
- Health checks and frontend asset delivery
- User registration and authentication
- Protected endpoint security
- Payment system integration
- Database operations

## 📚 API Documentation

The API follows RESTful principles with the following main endpoints:

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user

### Documents
- `GET /api/documents` - List user documents
- `POST /api/documents` - Upload document
- `DELETE /api/documents/{id}` - Delete document

### Tax Returns
- `GET /api/returns` - List tax returns
- `POST /api/returns` - Create tax return
- `PUT /api/returns/{id}` - Update tax return

### Payments
- `GET /api/payment/plans` - List subscription plans
- `POST /api/payment/subscribe` - Create subscription
- `GET /api/payment/services` - List one-time services

## 🚀 Deployment

The application is deployed on Manus Cloud Platform with:
- Automatic HTTPS/SSL certificates
- CDN-optimized asset delivery
- Production-grade hosting
- Automatic scaling capabilities

### Manual Deployment
1. Build the frontend: `cd frontend && pnpm run build`
2. Copy build files to backend static directory
3. Configure production environment variables
4. Deploy using your preferred hosting platform

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Commit your changes: `git commit -am 'Add new feature'`
4. Push to the branch: `git push origin feature/new-feature`
5. Submit a pull request

## 📄 License

This project is proprietary software owned by Sore Financial Group. All rights reserved.

## 📞 Support

For support and inquiries, please contact:
- **Email:** support@sorefinancial.com
- **Website:** https://sorefinancial.com
- **Live Application:** https://p9hwiqcqxxmn.manus.space

## 🔄 Future Enhancements

- OCR integration for automatic document processing
- Email notifications and reminders
- Advanced reporting and analytics
- Integration with QuickBooks and other accounting software
- Mobile app development
- Advanced CPA collaboration tools

---

**Built with ❤️ for Sore Financial Group**
