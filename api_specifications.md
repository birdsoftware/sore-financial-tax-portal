_# API Specifications: Sore Financial Group Tax Portal

This document outlines the API endpoints for the Sore Financial Group Tax Portal. The API is designed to be RESTful and will be implemented using Flask.

## 1. Authentication

### 1.1. `POST /auth/register`

Register a new user.

*   **Request Body:**
    *   `email` (string, required)
    *   `password` (string, required)
    *   `user_type` (string, required) - `individual`, `business`, or `cpa`
*   **Response:**
    *   `token` (string) - JWT for authentication.

### 1.2. `POST /auth/login`

Log in an existing user.

*   **Request Body:**
    *   `email` (string, required)
    *   `password` (string, required)
*   **Response:**
    *   `token` (string) - JWT for authentication.

### 1.3. `POST /auth/social`

Authenticate with a social provider.

*   **Request Body:**
    *   `provider` (string, required) - `google`, `apple`, `facebook`
    *   `token` (string, required) - The token from the social provider.
*   **Response:**
    *   `token` (string) - JWT for authentication.

## 2. Users

### 2.1. `GET /users/me`

Get the current user's profile.

*   **Authentication:** Required
*   **Response:**
    *   User object (without password hash).

### 2.2. `PUT /users/me`

Update the current user's profile.

*   **Authentication:** Required
*   **Request Body:**
    *   `profile` (object) - The user's profile data.
*   **Response:**
    *   Updated user object.

## 3. Tax Documents

### 3.1. `POST /documents`

Upload a tax document.

*   **Authentication:** Required
*   **Request:** `multipart/form-data` with the file.
*   **Response:**
    *   Document object with extracted data (if OCR is successful).

### 3.2. `GET /documents`

Get a list of the user's tax documents.

*   **Authentication:** Required
*   **Response:**
    *   Array of document objects.

### 3.3. `GET /documents/:id`

Get a specific tax document.

*   **Authentication:** Required
*   **Response:**
    *   Document object.

## 4. Tax Returns

### 4.1. `POST /returns`

Create a new tax return.

*   **Authentication:** Required
*   **Request Body:**
    *   `year` (integer, required)
*   **Response:**
    *   Tax return object.

### 4.2. `GET /returns`

Get a list of the user's tax returns.

*   **Authentication:** Required
*   **Response:**
    *   Array of tax return objects.

### 4.3. `PUT /returns/:id`

Update a tax return.

*   **Authentication:** Required
*   **Request Body:**
    *   `return_data` (object)
*   **Response:**
    *   Updated tax return object.

## 5. CPA

### 5.1. `GET /cpa/clients`

Get a list of a CPA's clients.

*   **Authentication:** Required (CPA user)
*   **Response:**
    *   Array of user objects.

### 5.2. `GET /cpa/clients/:client_id/documents`

Get a client's tax documents.

*   **Authentication:** Required (CPA user)
*   **Response:**
    *   Array of document objects.

## 6. Payments and Subscriptions

### 6.1. `POST /payments/charge`

Process a payment.

*   **Authentication:** Required
*   **Request Body:**
    *   `amount` (number, required)
    *   `token` (string, required) - Payment token from Stripe/PayPal.
*   **Response:**
    *   Payment object.

### 6.2. `POST /subscriptions`

Create a new subscription.

*   **Authentication:** Required
*   **Request Body:**
    *   `plan_type` (string, required)
    *   `token` (string, required) - Payment token from Stripe/PayPal.
*   **Response:**
    *   Subscription object.

