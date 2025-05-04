# Devflow Finance Service API Documentation

## Overview

The Devflow Finance Service is a microservice for managing payments, subscriptions, and financial transactions within the Devflow platform. It integrates with Stripe for payment processing and provides endpoints for subscription management.

## Base URL

```
/api/v1
```

## Authentication

All API endpoints require authentication using JSON Web Tokens (JWT). Include the JWT token in the Authorization header:

```
Authorization: Bearer <token>
```

## API Endpoints

### Payment Controller

#### Process Payment

Processes a payment for the specified plan.

- **URL**: `/payment/process`
- **Method**: `POST`
- **Auth Required**: Yes
- **Request Body**:
  ```json
  {
    "planId": "plan_id",
    "paymentMethod": "card"
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "message": "Payment processed successfully",
    "data": {
      "clientSecret": "stripe_client_secret",
      "paymentIntentId": "pi_12345"
    }
  }
  ```

#### Verify Payment

Verifies a payment after processing.

- **URL**: `/payment/verify`
- **Method**: `POST`
- **Auth Required**: Yes
- **Request Body**:
  ```json
  {
    "paymentIntentId": "pi_12345"
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "message": "Payment verified successfully",
    "data": {
      "status": "succeeded",
      "transactionId": "transaction_id"
    }
  }
  ```

#### Create Checkout Session

Creates a Stripe checkout session for payment.

- **URL**: `/payment/create-checkout-session`
- **Method**: `POST`
- **Auth Required**: Yes
- **Request Body**:
  ```json
  {
    "planId": "plan_id"
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "data": {
      "sessionId": "cs_test_12345",
      "url": "https://checkout.stripe.com/pay/cs_test_12345"
    }
  }
  ```

#### Handle Webhook

Handles Stripe webhook events.

- **URL**: `/payment/webhook`
- **Method**: `POST`
- **Auth Required**: No (Stripe signature verification used instead)
- **Headers**:
  ```
  Stripe-Signature: t=timestamp,v1=signature
  ```
- **Response**:
  ```json
  {
    "success": true,
    "message": "Webhook processed successfully"
  }
  ```

### Plan Controller

#### Get All Plans

Retrieves all available subscription plans.

- **URL**: `/plans`
- **Method**: `GET`
- **Auth Required**: No
- **Response**:
  ```json
  {
    "success": true,
    "data": [
      {
        "_id": "plan_id",
        "name": "Basic",
        "description": "Basic plan for individuals",
        "price": 9.99,
        "currency": "USD",
        "duration": 30,
        "features": [
          "5 projects",
          "Basic support",
          "1GB storage"
        ],
        "createdAt": "2023-09-15T10:00:00.000Z",
        "updatedAt": "2023-09-15T10:00:00.000Z"
      }
    ]
  }
  ```

#### Get Plan by ID

Retrieves a specific plan by its ID.

- **URL**: `/plans/:id`
- **Method**: `GET`
- **Auth Required**: No
- **URL Parameters**: `id=[string]` (Plan ID)
- **Response**:
  ```json
  {
    "success": true,
    "data": {
      "_id": "plan_id",
      "name": "Basic",
      "description": "Basic plan for individuals",
      "price": 9.99,
      "currency": "USD",
      "duration": 30,
      "features": [
        "5 projects",
        "Basic support",
        "1GB storage"
      ],
      "createdAt": "2023-09-15T10:00:00.000Z",
      "updatedAt": "2023-09-15T10:00:00.000Z"
    }
  }
  ```

#### Create Plan (Admin only)

Creates a new subscription plan.

- **URL**: `/plans`
- **Method**: `POST`
- **Auth Required**: Yes (Admin)
- **Request Body**:
  ```json
  {
    "name": "Premium",
    "description": "Premium plan for teams",
    "price": 29.99,
    "currency": "USD",
    "duration": 30,
    "features": [
      "Unlimited projects",
      "Premium support",
      "10GB storage"
    ]
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "message": "Plan created successfully",
    "data": {
      "_id": "new_plan_id",
      "name": "Premium",
      "description": "Premium plan for teams",
      "price": 29.99,
      "currency": "USD",
      "duration": 30,
      "features": [
        "Unlimited projects",
        "Premium support",
        "10GB storage"
      ],
      "createdAt": "2023-09-15T10:00:00.000Z",
      "updatedAt": "2023-09-15T10:00:00.000Z"
    }
  }
  ```

#### Update Plan (Admin only)

Updates an existing subscription plan.

- **URL**: `/plans/:id`
- **Method**: `PUT`
- **Auth Required**: Yes (Admin)
- **URL Parameters**: `id=[string]` (Plan ID)
- **Request Body**:
  ```json
  {
    "name": "Premium Plus",
    "price": 39.99,
    "features": [
      "Unlimited projects",
      "Premium support",
      "20GB storage",
      "Advanced analytics"
    ]
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "message": "Plan updated successfully",
    "data": {
      "_id": "plan_id",
      "name": "Premium Plus",
      "description": "Premium plan for teams",
      "price": 39.99,
      "currency": "USD",
      "duration": 30,
      "features": [
        "Unlimited projects",
        "Premium support",
        "20GB storage",
        "Advanced analytics"
      ],
      "createdAt": "2023-09-15T10:00:00.000Z",
      "updatedAt": "2023-09-16T11:00:00.000Z"
    }
  }
  ```

#### Delete Plan (Admin only)

Deletes a subscription plan.

- **URL**: `/plans/:id`
- **Method**: `DELETE`
- **Auth Required**: Yes (Admin)
- **URL Parameters**: `id=[string]` (Plan ID)
- **Response**:
  ```json
  {
    "success": true,
    "message": "Plan deleted successfully"
  }
  ```

### Subscription Controller

#### Get User Subscriptions

Retrieves all subscriptions for the authenticated user.

- **URL**: `/subscriptions/user`
- **Method**: `GET`
- **Auth Required**: Yes
- **Response**:
  ```json
  {
    "success": true,
    "data": [
      {
        "_id": "subscription_id",
        "userId": "user_id",
        "planId": {
          "_id": "plan_id",
          "name": "Premium",
          "price": 29.99
        },
        "startDate": "2023-09-15T10:00:00.000Z",
        "endDate": "2023-10-15T10:00:00.000Z",
        "status": "active",
        "stripeSubscriptionId": "sub_12345",
        "createdAt": "2023-09-15T10:00:00.000Z",
        "updatedAt": "2023-09-15T10:00:00.000Z"
      }
    ]
  }
  ```

#### Get Subscription by ID

Retrieves a specific subscription by its ID.

- **URL**: `/subscriptions/:id`
- **Method**: `GET`
- **Auth Required**: Yes
- **URL Parameters**: `id=[string]` (Subscription ID)
- **Response**:
  ```json
  {
    "success": true,
    "data": {
      "_id": "subscription_id",
      "userId": "user_id",
      "planId": {
        "_id": "plan_id",
        "name": "Premium",
        "price": 29.99
      },
      "startDate": "2023-09-15T10:00:00.000Z",
      "endDate": "2023-10-15T10:00:00.000Z",
      "status": "active",
      "stripeSubscriptionId": "sub_12345",
      "createdAt": "2023-09-15T10:00:00.000Z",
      "updatedAt": "2023-09-15T10:00:00.000Z"
    }
  }
  ```

#### Create Subscription

Creates a new subscription for the authenticated user.

- **URL**: `/subscriptions`
- **Method**: `POST`
- **Auth Required**: Yes
- **Request Body**:
  ```json
  {
    "planId": "plan_id",
    "paymentMethodId": "pm_12345"
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "message": "Subscription created successfully",
    "data": {
      "_id": "subscription_id",
      "userId": "user_id",
      "planId": "plan_id",
      "startDate": "2023-09-15T10:00:00.000Z",
      "endDate": "2023-10-15T10:00:00.000Z",
      "status": "active",
      "stripeSubscriptionId": "sub_12345",
      "createdAt": "2023-09-15T10:00:00.000Z",
      "updatedAt": "2023-09-15T10:00:00.000Z"
    }
  }
  ```

#### Cancel Subscription

Cancels an active subscription.

- **URL**: `/subscriptions/:id/cancel`
- **Method**: `POST`
- **Auth Required**: Yes
- **URL Parameters**: `id=[string]` (Subscription ID)
- **Response**:
  ```json
  {
    "success": true,
    "message": "Subscription cancelled successfully",
    "data": {
      "_id": "subscription_id",
      "status": "cancelled",
      "updatedAt": "2023-09-16T11:00:00.000Z"
    }
  }
  ```

### Transaction Controller

#### Get User Transactions

Retrieves all transactions for the authenticated user.

- **URL**: `/transactions/user`
- **Method**: `GET`
- **Auth Required**: Yes
- **Query Parameters**:
  - `page=[integer]` (Optional, default: 1)
  - `limit=[integer]` (Optional, default: 10)
- **Response**:
  ```json
  {
    "success": true,
    "data": [
      {
        "_id": "transaction_id",
        "userId": "user_id",
        "planId": "plan_id",
        "amount": 29.99,
        "currency": "USD",
        "status": "completed",
        "stripePaymentIntentId": "pi_12345",
        "type": "subscription",
        "createdAt": "2023-09-15T10:00:00.000Z",
        "updatedAt": "2023-09-15T10:00:00.000Z"
      }
    ],
    "pagination": {
      "totalItems": 5,
      "currentPage": 1,
      "totalPages": 1,
      "itemsPerPage": 10
    }
  }
  ```

#### Get Transaction by ID

Retrieves a specific transaction by its ID.

- **URL**: `/transactions/:id`
- **Method**: `GET`
- **Auth Required**: Yes
- **URL Parameters**: `id=[string]` (Transaction ID)
- **Response**:
  ```json
  {
    "success": true,
    "data": {
      "_id": "transaction_id",
      "userId": "user_id",
      "planId": "plan_id",
      "amount": 29.99,
      "currency": "USD",
      "status": "completed",
      "stripePaymentIntentId": "pi_12345",
      "type": "subscription",
      "createdAt": "2023-09-15T10:00:00.000Z",
      "updatedAt": "2023-09-15T10:00:00.000Z"
    }
  }
  ```

### Invoice Controller

#### Get User Invoices

Retrieves all invoices for the authenticated user.

- **URL**: `/invoices/user`
- **Method**: `GET`
- **Auth Required**: Yes
- **Query Parameters**:
  - `page=[integer]` (Optional, default: 1)
  - `limit=[integer]` (Optional, default: 10)
- **Response**:
  ```json
  {
    "success": true,
    "data": [
      {
        "_id": "invoice_id",
        "userId": "user_id",
        "subscriptionId": "subscription_id",
        "transactionId": "transaction_id",
        "amount": 29.99,
        "currency": "USD",
        "status": "paid",
        "invoiceNumber": "INV-2023-001",
        "invoiceDate": "2023-09-15T10:00:00.000Z",
        "dueDate": "2023-09-22T10:00:00.000Z",
        "items": [
          {
            "description": "Premium Subscription",
            "quantity": 1,
            "unitPrice": 29.99,
            "amount": 29.99
          }
        ],
        "createdAt": "2023-09-15T10:00:00.000Z",
        "updatedAt": "2023-09-15T10:00:00.000Z"
      }
    ],
    "pagination": {
      "totalItems": 3,
      "currentPage": 1,
      "totalPages": 1,
      "itemsPerPage": 10
    }
  }
  ```

#### Get Invoice by ID

Retrieves a specific invoice by its ID.

- **URL**: `/invoices/:id`
- **Method**: `GET`
- **Auth Required**: Yes
- **URL Parameters**: `id=[string]` (Invoice ID)
- **Response**:
  ```json
  {
    "success": true,
    "data": {
      "_id": "invoice_id",
      "userId": "user_id",
      "subscriptionId": "subscription_id",
      "transactionId": "transaction_id",
      "amount": 29.99,
      "currency": "USD",
      "status": "paid",
      "invoiceNumber": "INV-2023-001",
      "invoiceDate": "2023-09-15T10:00:00.000Z",
      "dueDate": "2023-09-22T10:00:00.000Z",
      "items": [
        {
          "description": "Premium Subscription",
          "quantity": 1,
          "unitPrice": 29.99,
          "amount": 29.99
        }
      ],
      "createdAt": "2023-09-15T10:00:00.000Z",
      "updatedAt": "2023-09-15T10:00:00.000Z"
    }
  }
  ```

#### Generate Invoice PDF

Generates a PDF version of an invoice.

- **URL**: `/invoices/:id/pdf`
- **Method**: `GET`
- **Auth Required**: Yes
- **URL Parameters**: `id=[string]` (Invoice ID)
- **Response**: PDF file stream

### Statistics Controller

#### Get User Payment Statistics

Retrieves payment statistics for the authenticated user.

- **URL**: `/stats/payments`
- **Method**: `GET`
- **Auth Required**: Yes
- **Query Parameters**:
  - `period=[month|year]` (Optional, default: month)
- **Response**:
  ```json
  {
    "success": true,
    "data": {
      "totalSpent": 89.97,
      "currentPlan": {
        "name": "Premium",
        "price": 29.99,
        "renewalDate": "2023-10-15T10:00:00.000Z"
      },
      "transactionsByMonth": [
        {
          "month": "September 2023",
          "amount": 29.99
        },
        {
          "month": "August 2023",
          "amount": 29.99
        },
        {
          "month": "July 2023",
          "amount": 29.99
        }
      ]
    }
  }
  ```

#### Get Admin Dashboard Statistics (Admin only)

Retrieves statistics for the admin dashboard.

- **URL**: `/stats/admin/dashboard`
- **Method**: `GET`
- **Auth Required**: Yes (Admin)
- **Response**:
  ```json
  {
    "success": true,
    "data": {
      "totalRevenue": 5249.75,
      "activeSubscriptions": 175,
      "mostPopularPlan": {
        "name": "Premium",
        "subscribers": 95
      },
      "revenueByMonth": [
        {
          "month": "September 2023",
          "amount": 1799.40
        },
        {
          "month": "August 2023",
          "amount": 1749.42
        },
        {
          "month": "July 2023",
          "amount": 1700.93
        }
      ]
    }
  }
  ```

## Error Responses

All endpoints return error responses in the following format:

```json
{
  "success": false,
  "message": "Error message",
  "error": {
    "code": "ERROR_CODE",
    "details": "Detailed error information"
  }
}
```

### Common Error Codes

- `INVALID_INPUT`: Invalid request parameters or body
- `AUTHENTICATION_ERROR`: Authentication failed
- `AUTHORIZATION_ERROR`: User is not authorized to perform the action
- `RESOURCE_NOT_FOUND`: Requested resource was not found
- `PAYMENT_PROCESSING_ERROR`: Error during payment processing
- `STRIPE_API_ERROR`: Error from Stripe API
- `INTERNAL_SERVER_ERROR`: Unexpected server error

## Rate Limiting

The API implements rate limiting to prevent abuse. When a rate limit is exceeded, the API returns a 429 Too Many Requests response.
