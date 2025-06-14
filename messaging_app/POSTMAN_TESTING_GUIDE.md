# Postman API Testing Guide

This document explains how to use the Postman collection to test the Messaging App API endpoints.

## Collection Overview

The `post_man-Collections` file contains comprehensive tests for:

### 1. Authentication Tests
- **Register User** - Creates new users and stores JWT tokens
- **Login User** - Authenticates existing users  
- **Get User Profile** - Tests authenticated access
- **Unauthorized Access Test** - Verifies security

### 2. Conversation Tests
- **Create Conversation** - Creates new conversations
- **List Conversations** - Tests pagination and listing
- **Get Conversation Detail** - Retrieves specific conversation
- **Add Participant** - Adds users to conversations
- **Unauthorized Conversation Access** - Tests access control

### 3. Message Tests
- **Send Message** - Creates new messages
- **Send Multiple Messages** - Creates 25+ messages for pagination testing
- **List Messages (Paginated)** - Tests 20 messages per page
- **Filter Messages by Conversation** - Tests conversation filtering
- **Filter Messages by Date Range** - Tests time range filtering
- **Filter Messages by Sender** - Tests sender filtering
- **Search Messages by Content** - Tests content search
- **Update Message** - Tests message editing
- **Mark Message as Read** - Tests read status
- **Unauthorized Message Access** - Tests permission security

### 4. Advanced Features
- **Test Pagination - Page 2** - Tests page navigation
- **Test Custom Page Size** - Tests custom page sizes
- **Combined Filters Test** - Tests multiple filters together

## Setup Instructions

### 1. Import Collection
1. Open Postman
2. Click "Import" 
3. Select the `post_man-Collections` file
4. The collection will be imported with all tests

### 2. Environment Setup
Create a new environment in Postman with these variables:
- `base_url`: `http://127.0.0.1:8000` (or your server URL)

### 3. Running Tests

#### Option A: Run Entire Collection
1. Right-click on "Messaging App API Tests" collection
2. Select "Run collection"
3. Configure run settings and click "Run"

#### Option B: Run Individual Folders
1. Navigate to specific folders (Authentication, Conversations, Messages)
2. Right-click and select "Run folder"

#### Option C: Run Individual Requests
1. Click on individual requests
2. Click "Send" to execute

## Test Sequence

**Recommended order for manual testing:**

1. **Authentication** folder (creates users and tokens)
2. **Conversations** folder (creates conversations)  
3. **Messages** folder (sends messages and tests features)
4. **Advanced Features** folder (tests pagination/filtering)

## Automatic Environment Variables

The collection automatically sets these environment variables:
- `access_token` - JWT access token for user 1
- `refresh_token` - JWT refresh token for user 1  
- `user_id` - User 1 ID
- `user2_access_token` - JWT access token for user 2
- `user2_id` - User 2 ID
- `conversation_id` - Created conversation ID
- `message_id` - Created message ID
- `today_date` - Today's date for filtering

## Expected Results

### Authentication Tests
- ✅ User registration returns 201 with tokens
- ✅ Login returns 200 with valid tokens
- ✅ Profile access works with valid token
- ✅ Unauthorized access returns 401

### Conversation Tests
- ✅ Conversation creation returns 201
- ✅ List shows paginated conversations
- ✅ Detail view shows conversation data
- ✅ Participant addition works
- ✅ Unauthorized access blocked (403/404)

### Message Tests  
- ✅ Message creation returns 201
- ✅ Pagination shows 20 messages per page
- ✅ Filtering by conversation works
- ✅ Date range filtering works
- ✅ Sender filtering works
- ✅ Content search works
- ✅ Message updates work for sender
- ✅ Read status updates work
- ✅ Unauthorized updates blocked (403)

### Advanced Features
- ✅ Page navigation works
- ✅ Custom page sizes work
- ✅ Multiple filters combine correctly

## Troubleshooting

### Common Issues

1. **401 Unauthorized**
   - Ensure you've run authentication tests first
   - Check that tokens are properly set in environment

2. **404 Not Found**
   - Verify server is running on correct port
   - Check that IDs are properly set from previous tests

3. **403 Forbidden**
   - This is expected for unauthorized access tests
   - Verify permissions are working correctly

### Server Setup
Before running tests, ensure:
```bash
cd /home/shad/Documents/ALX/alx-backend-python/messaging_app
python manage.py runserver 8000
```

### Environment Variables
If automatic variable setting fails, manually set:
- `base_url`: Your server URL
- Run authentication tests to populate other variables

## Security Testing

The collection includes specific tests for:
- JWT token validation
- Conversation access control
- Message permission checking
- Unauthorized access prevention

## Performance Testing

Global tests check:
- Response time < 5000ms
- Proper JSON content headers
- Consistent API behavior

## API Endpoints Tested

### Authentication
- `POST /api/auth/register/`
- `POST /api/auth/login/`
- `GET /api/auth/profile/`

### Conversations
- `GET /api/conversations/`
- `POST /api/conversations/`
- `GET /api/conversations/{id}/`
- `POST /api/conversations/{id}/add_participant/`

### Messages
- `GET /api/messages/`
- `POST /api/messages/`
- `PATCH /api/messages/{id}/`
- `PATCH /api/messages/{id}/mark_as_read/`

### Filtering & Pagination
- Query parameters: `page`, `page_size`
- Filters: `conversation`, `sender`, `date_from`, `date_to`, `message_body`
- Ordering: `timestamp`, `sent_at`, `is_read`
