# Messaging App - JWT Authentication Implementation

## Overview

This messaging app implements secure JWT (JSON Web Token) authentication using `djangorestframework-simplejwt`. The authentication system ensures that users can only access their own messages and conversations while providing secure token-based authentication.

## 🔐 Authentication Features

- **JWT Token Authentication**: Secure token-based authentication with access and refresh tokens
- **User Registration**: Create new user accounts with automatic JWT token generation
- **User Login**: Authenticate existing users and receive JWT tokens
- **Token Refresh**: Refresh expired access tokens using refresh tokens
- **Token Blacklisting**: Secure logout by blacklisting refresh tokens
- **Protected Endpoints**: All API endpoints require authentication
- **Permission-based Access**: Users can only access their own data

## 📦 Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

The required packages include:

- `Django>=4.2.0`
- `djangorestframework>=3.14.0`
- `djangorestframework-simplejwt>=5.2.0`

### 2. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Start the Development Server

```bash
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/`

## 🚀 Authentication Endpoints

### User Registration

**POST** `/api/auth/register/`

Register a new user and receive JWT tokens.

```bash
curl -X POST http://127.0.0.1:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "newuser@example.com",
    "password": "securepassword123",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

**Response:**

```json
{
  "user": {
    "user_id": "69a3e4fe-ae21-4332-93f1-81fbed817de5",
    "username": "newuser",
    "email": "newuser@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "",
    "is_online": false,
    "created_at": "2025-06-14T09:57:59.932221Z"
  },
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "message": "User registered successfully"
}
```

### User Login

**POST** `/api/auth/login/`

Authenticate existing user and receive JWT tokens.

```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "password": "securepassword123"
  }'
```

### Token Refresh

**POST** `/api/auth/token/refresh/`

Refresh an expired access token using a refresh token.

```bash
curl -X POST http://127.0.0.1:8000/api/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "your_refresh_token_here"
  }'
```

### User Logout

**POST** `/api/auth/logout/`

Logout user by blacklisting the refresh token.

```bash
curl -X POST http://127.0.0.1:8000/api/auth/logout/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_access_token_here" \
  -d '{
    "refresh": "your_refresh_token_here"
  }'
```

### User Profile

**GET** `/api/auth/profile/`

Get current user's profile information.

```bash
curl -X GET http://127.0.0.1:8000/api/auth/profile/ \
  -H "Authorization: Bearer your_access_token_here"
```

## 🔒 Protected API Endpoints

All messaging app endpoints require authentication. Include the JWT access token in the Authorization header:

```bash
Authorization: Bearer your_access_token_here
```

### Conversations

- **GET** `/api/conversations/` - List user's conversations
- **POST** `/api/conversations/` - Create new conversation
- **GET** `/api/conversations/{id}/` - Get specific conversation
- **POST** `/api/conversations/{id}/add_participant/` - Add participant
- **POST** `/api/conversations/{id}/remove_participant/` - Remove participant

### Messages

- **GET** `/api/messages/` - List user's messages
- **POST** `/api/messages/` - Send new message
- **GET** `/api/messages/{id}/` - Get specific message
- **PATCH** `/api/messages/{id}/mark_as_read/` - Mark message as read

### Users

- **GET** `/api/users/` - Search users (excluding current user)
- **GET** `/api/users/{id}/` - Get user details

## 🛡️ Security Features

### JWT Configuration

- **Access Token Lifetime**: 60 minutes
- **Refresh Token Lifetime**: 7 days
- **Token Rotation**: Enabled (new refresh token on each refresh)
- **Blacklist After Rotation**: Enabled
- **Algorithm**: HS256

### Custom Permissions

1. **IsOwnerOrReadOnly**: Users can only edit their own profile
2. **IsParticipantOrReadOnly**: Users can only access conversations they participate in
3. **IsMessageSenderOrParticipant**: Users can read messages in their conversations, edit their own messages
4. **CanAccessOwnDataOnly**: General permission ensuring users access only their data

### Data Access Control

- Users can only see conversations they participate in
- Users can only see messages from their conversations
- User search excludes the current user
- Profile updates are restricted to the owner

## 🧪 Testing Authentication

### Test Unauthenticated Access

```bash
curl -X GET http://127.0.0.1:8000/api/conversations/
```

**Expected Response:** `{"detail":"Authentication credentials were not provided."}`

### Test Authenticated Access

```bash
curl -X GET http://127.0.0.1:8000/api/conversations/ \
  -H "Authorization: Bearer your_access_token_here"
```

**Expected Response:** List of user's conversations

## 📁 Project Structure

```
messaging_app/
├── messaging_app/
│   ├── settings.py          # JWT configuration
│   └── urls.py             # Main URL configuration
├── chats/
│   ├── auth.py             # Authentication views
│   ├── permissions.py      # Custom permissions
│   ├── views.py            # API viewsets with permissions
│   ├── models.py           # User, Conversation, Message models
│   └── urls.py             # API URL patterns
└── requirements.txt        # Dependencies including simplejwt
```

## 🔧 Configuration Details

### Settings.py Key Configurations

```python
INSTALLED_APPS = [
    # ... other apps
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'chats',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'USER_ID_FIELD': 'user_id',  # Custom field for UUID primary key
}
```

## 🚨 Error Handling

Common authentication errors and their solutions:

1. **"Authentication credentials were not provided"**

   - Include `Authorization: Bearer <token>` header

2. **"Given token not valid for any token type"**

   - Token has expired, use refresh token to get new access token

3. **"User not found"**

   - Invalid username in login request

4. **"Invalid credentials"**
   - Wrong password in login request

## 📝 Development Notes

- The app uses a custom User model with UUID primary key (`user_id`)
- JWT tokens contain the user's UUID in the payload
- Token blacklisting is enabled for secure logout
- All endpoints are protected by default with `IsAuthenticated` permission
- Custom permissions ensure users can only access their own data

## 🎯 Testing Checklist

- [x] JWT authentication installed and configured
- [x] User registration with JWT token generation
- [x] User login with JWT token generation
- [x] Token refresh functionality
- [x] Protected endpoints reject unauthenticated requests
- [x] Authenticated users can access their own data
- [x] Users cannot access other users' data
- [x] Token blacklisting for secure logout
- [x] Custom permissions implemented
- [x] All authentication files created and functional

This implementation successfully meets all the requirements for JWT authentication in the messaging app, ensuring secure and proper access control for all users.
