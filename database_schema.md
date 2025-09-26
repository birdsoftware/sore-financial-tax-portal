# Database Schema: Sore Financial Group Tax Portal

This document defines the database schema for the Sore Financial Group Tax Portal. The schema is designed to support all the features outlined in the PRD.

## 1. ERD (Entity-Relationship Diagram)

A visual representation of the database schema will be created in a later stage.

## 2. Tables

### 2.1. `users`

Stores information about all users of the platform.

| Column          | Data Type     | Constraints              | Description                                         |
| --------------- | ------------- | ------------------------ | --------------------------------------------------- |
| `id`            | SERIAL        | PRIMARY KEY              | Unique identifier for the user.                     |
| `email`         | VARCHAR(255)  | UNIQUE, NOT NULL         | User's email address.                               |
| `password_hash` | VARCHAR(255)  | NOT NULL                 | Hashed password for email/password authentication.  |
| `phone_number`  | VARCHAR(20)   | NULL                     | User's phone number for OTP authentication.         |
| `user_type`     | VARCHAR(20)   | NOT NULL                 | Type of user: `individual`, `business`, or `cpa`.   |
| `profile`       | JSONB         | NULL                     | Stores personal or business profile information.    |
| `created_at`    | TIMESTAMPTZ   | NOT NULL, DEFAULT NOW()  | Timestamp of user creation.                         |
| `updated_at`    | TIMESTAMPTZ   | NOT NULL, DEFAULT NOW()  | Timestamp of last user update.                      |

### 2.2. `tax_documents`

Stores uploaded tax documents.

| Column           | Data Type     | Constraints              | Description                                      |
| ---------------- | ------------- | ------------------------ | ------------------------------------------------ |
| `id`             | SERIAL        | PRIMARY KEY              | Unique identifier for the document.              |
| `user_id`        | INTEGER       | FOREIGN KEY (users.id)   | The user who uploaded the document.              |
| `document_type`  | VARCHAR(50)   | NOT NULL                 | Type of tax document (e.g., W-2, 1099).          |
| `file_path`      | VARCHAR(255)  | NOT NULL                 | Path to the stored document file.                |
| `extracted_data` | JSONB         | NULL                     | Data extracted from the document via OCR.        |
| `uploaded_at`    | TIMESTAMPTZ   | NOT NULL, DEFAULT NOW()  | Timestamp of document upload.                    |

### 2.3. `receipts`

Stores uploaded receipts for expense tracking.

| Column        | Data Type     | Constraints              | Description                                      |
| ------------- | ------------- | ------------------------ | ------------------------------------------------ |
| `id`          | SERIAL        | PRIMARY KEY              | Unique identifier for the receipt.               |
| `user_id`     | INTEGER       | FOREIGN KEY (users.id)   | The user who uploaded the receipt.               |
| `file_path`   | VARCHAR(255)  | NOT NULL                 | Path to the stored receipt file.                 |
| `category`    | VARCHAR(100)  | NULL                     | Expense category for the receipt.                |
| `amount`      | DECIMAL(10, 2)| NOT NULL                 | Amount of the expense.                           |
| `date`        | DATE          | NOT NULL                 | Date of the expense.                             |
| `uploaded_at` | TIMESTAMPTZ   | NOT NULL, DEFAULT NOW()  | Timestamp of receipt upload.                     |

### 2.4. `tax_returns`

Stores information about tax returns.

| Column        | Data Type     | Constraints              | Description                                      |
| ------------- | ------------- | ------------------------ | ------------------------------------------------ |
| `id`          | SERIAL        | PRIMARY KEY              | Unique identifier for the tax return.            |
| `user_id`     | INTEGER       | FOREIGN KEY (users.id)   | The user associated with the tax return.         |
| `cpa_id`      | INTEGER       | FOREIGN KEY (users.id)   | The CPA reviewing the tax return (nullable).     |
| `year`        | INTEGER       | NOT NULL                 | The tax year of the return.                      |
| `status`      | VARCHAR(20)   | NOT NULL                 | Status of the return: `draft`, `in_review`, `filed`. |
| `return_data` | JSONB         | NULL                     | The complete tax return data.                    |
| `created_at`  | TIMESTAMPTZ   | NOT NULL, DEFAULT NOW()  | Timestamp of tax return creation.                |
| `updated_at`  | TIMESTAMPTZ   | NOT NULL, DEFAULT NOW()  | Timestamp of last tax return update.             |

### 2.5. `subscriptions`

Stores user subscriptions.

| Column      | Data Type     | Constraints              | Description                                      |
| ----------- | ------------- | ------------------------ | ------------------------------------------------ |
| `id`        | SERIAL        | PRIMARY KEY              | Unique identifier for the subscription.          |
| `user_id`   | INTEGER       | FOREIGN KEY (users.id)   | The user who owns the subscription.              |
| `plan_type` | VARCHAR(50)   | NOT NULL                 | Type of subscription plan.                       |
| `start_date`| TIMESTAMPTZ   | NOT NULL                 | Start date of the subscription.                  |
| `end_date`  | TIMESTAMPTZ   | NOT NULL                 | End date of the subscription.                    |
| `status`    | VARCHAR(20)   | NOT NULL                 | Status of the subscription: `active`, `canceled`.|

### 2.6. `payments`

Stores payment and transaction information.

| Column           | Data Type     | Constraints              | Description                                      |
| ---------------- | ------------- | ------------------------ | ------------------------------------------------ |
| `id`             | SERIAL        | PRIMARY KEY              | Unique identifier for the payment.               |
| `user_id`        | INTEGER       | FOREIGN KEY (users.id)   | The user who made the payment.                   |
| `amount`         | DECIMAL(10, 2)| NOT NULL                 | The payment amount.                              |
| `currency`       | VARCHAR(3)    | NOT NULL                 | The currency of the payment (e.g., USD).         |
| `payment_method` | VARCHAR(20)   | NOT NULL                 | The payment method used (e.g., `stripe`, `paypal`).|
| `transaction_id` | VARCHAR(255)  | NOT NULL                 | The transaction ID from the payment gateway.     |
| `status`         | VARCHAR(20)   | NOT NULL                 | The status of the payment: `succeeded`, `failed`.|
| `created_at`     | TIMESTAMPTZ   | NOT NULL, DEFAULT NOW()  | Timestamp of the payment.                        |

