# 📚 Complete API Reference & Integration Examples

## 🎯 Overview

This comprehensive reference provides detailed documentation for all Turin Grad Hub API endpoints with practical integration examples, request/response formats, and error handling patterns.

**Base URL**: `http://127.0.0.1:5000`
**Authentication**: JWT Bearer tokens
**Content Type**: `application/json`

## 🔐 Authentication Endpoints

### 1. User Login

**Endpoint**: `POST /api/auth/login`

**Description**: Authenticate user with email, phone, or student ID

**Request:**
```typescript
interface LoginRequest {
  identifier: string; // email, phone (+998XXXXXXXXX), or student ID (8 digits)
  password: string;
}
```

**Response:**
```typescript
interface LoginResponse {
  success: boolean;
  user: {
    id: string;
    firstName: string;
    lastName: string;
    middleName?: string;
    email: string;
    phone?: string;
    studentId?: string;
    role: 'admin' | 'teacher' | 'student';
    faculty?: string;
    direction?: string;
    avatar?: string;
    verified: boolean;
    blocked: boolean;
    lastLogin: string;
  };
  token: string;
  refreshToken: string;
}
```

**Example:**
```javascript
// Login with email
const response = await fetch('/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    identifier: 'student@ttpu.uz',
    password: 'password123'
  })
});

// Login with phone
const response = await fetch('/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    identifier: '+998901234567',
    password: 'password123'
  })
});

// Login with student ID
const response = await fetch('/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    identifier: '12345678',
    password: 'password123'
  })
});
```

**Curl Example:**
```bash
curl -X POST http://127.0.0.1:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "identifier": "admin@ttpu.uz",
    "password": "admin123"
  }'
```

### 2. User Registration

**Endpoint**: `POST /api/auth/register`

**Request:**
```typescript
interface RegisterRequest {
  firstName: string;
  lastName: string;
  middleName?: string;
  email: string;
  phone: string; // Format: +998XXXXXXXXX
  studentId: string; // 8 digits
  password: string; // Min 8 characters
  faculty: string;
  direction: string;
}
```

**Example:**
```javascript
const response = await fetch('/api/auth/register', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    firstName: 'John',
    lastName: 'Doe',
    middleName: 'Alexander',
    email: 'john.doe@student.ttpu.uz',
    phone: '+998901234567',
    studentId: '12345678',
    password: 'securePassword123',
    faculty: 'Computer Science',
    direction: 'Software Engineering'
  })
});
```

### 3. Token Refresh

**Endpoint**: `POST /api/auth/refresh`

**Request:**
```typescript
{
  refreshToken: string;
}
```

**Example:**
```javascript
const response = await fetch('/api/auth/refresh', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    refreshToken: localStorage.getItem('refreshToken')
  })
});
```

### 4. Password Reset Flow

**Endpoint**: `POST /api/auth/forgot-password`

**Request:**
```typescript
{
  identifier: string; // email or phone
}
```

**Reset Password**: `POST /api/auth/reset-password`

**Request:**
```typescript
{
  token: string; // from email/SMS
  newPassword: string;
}
```

### 5. Email Verification

**Endpoint**: `POST /api/auth/verify-email`

**Request:**
```typescript
{
  token: string; // from verification email
}
```

### 6. SMS Verification

**Send Code**: `POST /api/auth/send-sms`
```typescript
{
  phone: string; // +998XXXXXXXXX
}
```

**Verify Code**: `POST /api/auth/verify-sms`
```typescript
{
  phone: string;
  code: string; // 6-digit code
}
```

### 7. Logout

**Endpoint**: `POST /api/auth/logout`

**Headers**: `Authorization: Bearer <token>`

**Request:**
```typescript
{
  refreshToken: string;
}
```

---

## 👤 Profile Management Endpoints

### 1. Get Current User Profile

**Endpoint**: `GET /api/profile`

**Headers**: `Authorization: Bearer <token>`

**Response:**
```typescript
{
  success: boolean;
  data: {
    id: string;
    firstName: string;
    lastName: string;
    middleName?: string;
    email: string;
    phone?: string;
    studentId?: string;
    role: string;
    faculty?: string;
    direction?: string;
    bio?: string;
    avatar?: string;
    website?: string;
    birthDate?: string;
    address?: string;
    admissionYear?: number;
    graduationYear?: number;
    financingType?: 'budget' | 'contract';
    verified: boolean;
    blocked: boolean;
    createdAt: string;
    updatedAt: string;
  }
}
```

**Example:**
```javascript
const response = await fetch('/api/profile', {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
  }
});
const data = await response.json();
console.log('Current user:', data.data);
```

### 2. Update Profile

**Endpoint**: `PUT /api/profile`

**Headers**: `Authorization: Bearer <token>`

**Request:**
```typescript
{
  firstName?: string;
  lastName?: string;
  middleName?: string;
  phone?: string;
  bio?: string;
  website?: string;
  birthDate?: string;
  address?: string;
  // Other updatable fields...
}
```

**Example:**
```javascript
const response = await fetch('/api/profile', {
  method: 'PUT',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
  },
  body: JSON.stringify({
    firstName: 'John',
    lastName: 'Smith',
    bio: 'Computer Science student passionate about AI and machine learning.',
    website: 'https://johnsmith.dev'
  })
});
```

### 3. Work Experience Management

**Get Work Experience**: `GET /api/profile/work-experience`

**Response:**
```typescript
{
  success: boolean;
  data: Array<{
    id: string;
    company: string;
    position: string;
    startDate: string; // YYYY-MM-DD
    endDate?: string; // YYYY-MM-DD or null for current
    description?: string;
    userId: string;
    createdAt: string;
    updatedAt: string;
  }>
}
```

**Add Work Experience**: `POST /api/profile/work-experience`

**Request:**
```typescript
{
  company: string;
  position: string;
  startDate: string; // YYYY-MM-DD
  endDate?: string; // YYYY-MM-DD or null for current job
  description?: string;
}
```

**Example:**
```javascript
const response = await fetch('/api/profile/work-experience', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
  },
  body: JSON.stringify({
    company: 'TechCorp Solutions',
    position: 'Junior Developer',
    startDate: '2023-06-01',
    endDate: '2024-01-15',
    description: 'Developed web applications using React and Node.js. Collaborated with senior developers on various projects.'
  })
});
```

### 4. Education Goals Management

**Get Education Goals**: `GET /api/profile/education-goals`

**Add Education Goal**: `POST /api/profile/education-goals`

**Request:**
```typescript
{
  year: number;
  goal: string;
}
```

**Example:**
```javascript
const response = await fetch('/api/profile/education-goals', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
  },
  body: JSON.stringify({
    year: 2025,
    goal: 'Complete Master\'s degree in Computer Science with focus on Machine Learning'
  })
});
```

---

## 👨‍🎓 Students Management Endpoints

### 1. Get Students List

**Endpoint**: `GET /api/students`

**Headers**: `Authorization: Bearer <token>`

**Access**: Admin (all students), Teacher (assigned students only)

**Query Parameters:**
- `page`: number (default: 1)
- `limit`: number (default: 20, max: 100)
- `search`: string (search in name, email, student ID)
- `faculty`: string (filter by faculty)
- `direction`: string (filter by direction)
- `admissionYear`: number
- `graduationYear`: number
- `financingType`: 'budget' | 'contract'
- `verified`: boolean

**Response:**
```typescript
{
  success: boolean;
  data: Array<{
    id: string;
    firstName: string;
    lastName: string;
    middleName?: string;
    email: string;
    studentId: string;
    faculty: string;
    direction: string;
    admissionYear?: number;
    graduationYear?: number;
    avatar?: string;
    verified: boolean;
    blocked: boolean;
  }>;
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  }
}
```

**Example:**
```javascript
// Get all students
const response = await fetch('/api/students?page=1&limit=20', {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
  }
});

// Search students
const response = await fetch('/api/students?search=John&faculty=Computer Science', {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
  }
});

// Filter by graduation year
const response = await fetch('/api/students?graduationYear=2024&verified=true', {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
  }
});
```

---

## 👨‍🏫 Teachers Management Endpoints

### 1. Get Teachers List

**Endpoint**: `GET /api/teachers`

**Headers**: `Authorization: Bearer <token>`

**Query Parameters:**
- `page`, `limit`, `search`, `faculty`

**Response:**
```typescript
{
  success: boolean;
  data: Array<{
    id: string;
    firstName: string;
    lastName: string;
    middleName?: string;
    email: string;
    faculty: string;
    position?: string;
    avatar?: string;
    verified: boolean;
  }>
}
```

---

## 🔍 Search Endpoints

### 1. Global Search

**Endpoint**: `GET /api/search`

**Headers**: `Authorization: Bearer <token>`

**Query Parameters:**
- `q`: string (required, min 3 characters)
- `type`: 'all' | 'users' | 'students' | 'teachers' | 'companies'
- `page`, `limit`

**Response:**
```typescript
{
  success: boolean;
  data: Array<{
    id: string;
    type: 'user' | 'student' | 'teacher' | 'company';
    title: string;
    subtitle?: string;
    avatar?: string;
    url?: string;
    relevance?: number;
  }>
}
```

**Example:**
```javascript
// Search all types
const response = await fetch('/api/search?q=John&type=all', {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
  }
});

// Search only students
const response = await fetch('/api/search?q=Computer&type=students', {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
  }
});
```

### 2. Advanced Student Search

**Endpoint**: `GET /api/search/students`

**Query Parameters:**
- `q`: string
- `faculty`, `direction`, `admissionYear`, `graduationYear`, `company`

**Example:**
```javascript
const response = await fetch('/api/search/students?q=AI&faculty=Computer Science&graduationYear=2024', {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
  }
});
```

---

## 🔔 Notifications Endpoints

### 1. Get Notifications

**Endpoint**: `GET /api/notifications`

**Headers**: `Authorization: Bearer <token>`

**Query Parameters:**
- `page`, `limit`
- `read`: boolean (filter by read status)
- `type`: string (notification type)

**Response:**
```typescript
{
  success: boolean;
  data: Array<{
    id: string;
    title: string;
    message: string;
    type: 'info' | 'warning' | 'success' | 'error';
    read: boolean;
    createdAt: string;
    updatedAt: string;
  }>
}
```

### 2. Mark Notification as Read

**Endpoint**: `PATCH /api/notifications/{id}/read`

**Headers**: `Authorization: Bearer <token>`

### 3. Mark All as Read

**Endpoint**: `PATCH /api/notifications/mark-all-read`

**Headers**: `Authorization: Bearer <token>`

**Example:**
```javascript
// Get unread notifications
const response = await fetch('/api/notifications?read=false', {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
  }
});

// Mark specific notification as read
await fetch('/api/notifications/123/read', {
  method: 'PATCH',
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
  }
});

// Mark all as read
await fetch('/api/notifications/mark-all-read', {
  method: 'PATCH',
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
  }
});
```

---

## 📚 Dictionary Endpoints

### 1. Get Faculties

**Endpoint**: `GET /api/dictionaries/faculties`

**Headers**: `Authorization: Bearer <token>`

**Response:**
```typescript
{
  success: boolean;
  data: Array<{
    id: string;
    name: string;
    description?: string;
    createdAt: string;
  }>
}
```

### 2. Get Directions

**Endpoint**: `GET /api/dictionaries/directions`

**Query Parameters:**
- `facultyId`: string (optional filter)

**Response:**
```typescript
{
  success: boolean;
  data: Array<{
    id: string;
    name: string;
    facultyId: string;
    description?: string;
    createdAt: string;
  }>
}
```

### 3. Get Companies

**Endpoint**: `GET /api/dictionaries/companies`

**Response:**
```typescript
{
  success: boolean;
  data: Array<{
    id: string;
    name: string;
    website?: string;
    industry?: string;
    location?: string;
    createdAt: string;
  }>
}
```

### 4. Add Company

**Endpoint**: `POST /api/dictionaries/companies`

**Headers**: `Authorization: Bearer <token>`

**Request:**
```typescript
{
  name: string;
  website?: string;
  industry?: string;
  location?: string;
}
```

**Example:**
```javascript
// Get faculties and directions
const faculties = await fetch('/api/dictionaries/faculties', {
  headers: { 'Authorization': `Bearer ${token}` }
}).then(r => r.json());

const directions = await fetch('/api/dictionaries/directions?facultyId=cs-faculty-id', {
  headers: { 'Authorization': `Bearer ${token}` }
}).then(r => r.json());

// Add a new company
const response = await fetch('/api/dictionaries/companies', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({
    name: 'TechStartup Inc.',
    website: 'https://techstartup.com',
    industry: 'Information Technology',
    location: 'Tashkent, Uzbekistan'
  })
});
```

---

## 🛡️ Admin Endpoints

### 1. User Management

**Get All Users**: `GET /api/admin/users`

**Query Parameters:**
- `page`, `limit`, `search`
- `role`: 'admin' | 'teacher' | 'student'
- `faculty`: string
- `verified`: boolean

**Response:**
```typescript
{
  success: boolean;
  data: Array<{
    id: string;
    firstName: string;
    lastName: string;
    email: string;
    role: string;
    faculty?: string;
    studentId?: string;
    verified: boolean;
    blocked: boolean;
    lastLogin?: string;
    createdAt: string;
  }>;
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  }
}
```

**Create User**: `POST /api/admin/users`

**Request:**
```typescript
{
  firstName: string;
  lastName: string;
  middleName?: string;
  email: string;
  phone?: string;
  role: 'admin' | 'teacher' | 'student';
  studentId?: string; // required for students
  faculty?: string;
  direction?: string;
  password: string;
}
```

**Update User**: `PUT /api/admin/users/{id}`

**Delete User**: `DELETE /api/admin/users/{id}`

**Verify User**: `PATCH /api/admin/users/{id}/verify`

**Block/Unblock User**: `PATCH /api/admin/users/{id}/block`

**Request:**
```typescript
{
  blocked: boolean;
  reason?: string;
}
```

**Example:**
```javascript
// Get all unverified students
const response = await fetch('/api/admin/users?role=student&verified=false', {
  headers: {
    'Authorization': `Bearer ${adminToken}`
  }
});

// Verify a user
await fetch('/api/admin/users/user-id-123/verify', {
  method: 'PATCH',
  headers: {
    'Authorization': `Bearer ${adminToken}`
  }
});

// Block a user
await fetch('/api/admin/users/user-id-456/block', {
  method: 'PATCH',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${adminToken}`
  },
  body: JSON.stringify({
    blocked: true,
    reason: 'Violation of terms of service'
  })
});

// Create a new teacher
await fetch('/api/admin/users', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${adminToken}`
  },
  body: JSON.stringify({
    firstName: 'Jane',
    lastName: 'Smith',
    email: 'jane.smith@ttpu.uz',
    phone: '+998901111111',
    role: 'teacher',
    faculty: 'Computer Science',
    password: 'temporaryPassword123'
  })
});
```

### 2. Activity Logs

**Endpoint**: `GET /api/admin/activity-logs`

**Query Parameters:**
- `page`, `limit`
- `userId`: string
- `action`: string
- `startDate`, `endDate`: ISO date strings

**Response:**
```typescript
{
  success: boolean;
  data: Array<{
    id: string;
    userId: string;
    action: string;
    targetId?: string;
    targetType?: string;
    details?: string;
    ipAddress?: string;
    userAgent?: string;
    createdAt: string;
  }>
}
```

**Example:**
```javascript
// Get recent activity logs
const response = await fetch('/api/admin/activity-logs?page=1&limit=50', {
  headers: {
    'Authorization': `Bearer ${adminToken}`
  }
});

// Get logs for specific user
const userLogs = await fetch('/api/admin/activity-logs?userId=user-123', {
  headers: {
    'Authorization': `Bearer ${adminToken}`
  }
});

// Get logs for date range
const dateRangeLogs = await fetch('/api/admin/activity-logs?startDate=2024-01-01&endDate=2024-01-31', {
  headers: {
    'Authorization': `Bearer ${adminToken}`
  }
});
```

---

## ⚙️ System Endpoints

### 1. Health Check

**Endpoint**: `GET /api/health`

**Response:**
```typescript
{
  success: boolean;
  data: {
    status: 'healthy' | 'unhealthy';
    timestamp: string;
    uptime?: number;
  }
}
```

### 2. API Information

**Endpoint**: `GET /api/info`

**Response:**
```typescript
{
  success: boolean;
  data: {
    name: string;
    version: string;
    description: string;
    environment: string;
  }
}
```

### 3. Client Configuration

**Endpoint**: `GET /api/config`

**Headers**: `Authorization: Bearer <token>`

**Response:**
```typescript
{
  success: boolean;
  data: {
    features: {
      emailVerification: boolean;
      smsVerification: boolean;
      fileUpload: boolean;
    };
    limits: {
      maxFileSize: number;
      allowedFileTypes: string[];
    };
    ui: {
      theme: object;
      branding: object;
    }
  }
}
```

---

## 🔧 Error Handling Examples

### Standard Error Response Format

```typescript
{
  success: false;
  error: {
    code: string;
    message: string;
    details?: any;
  }
}
```

### Common Error Codes

**HTTP 400 - Bad Request:**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed",
    "details": [
      {
        "field": "email",
        "message": "Email is required"
      }
    ]
  }
}
```

**HTTP 401 - Unauthorized:**
```json
{
  "success": false,
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Invalid credentials"
  }
}
```

**HTTP 403 - Forbidden:**
```json
{
  "success": false,
  "error": {
    "code": "FORBIDDEN",
    "message": "Access denied. Admin role required."
  }
}
```

**HTTP 404 - Not Found:**
```json
{
  "success": false,
  "error": {
    "code": "NOT_FOUND",
    "message": "User not found"
  }
}
```

### Error Handling in Frontend

```typescript
// Generic error handler
async function handleApiCall<T>(apiCall: () => Promise<Response>): Promise<T> {
  try {
    const response = await apiCall();
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new ApiError(
        errorData.error?.message || 'Request failed',
        response.status,
        errorData.error?.code
      );
    }
    
    return await response.json();
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    
    // Network or other errors
    throw new ApiError('Network error occurred', 0, 'NETWORK_ERROR');
  }
}

class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public code?: string,
    public details?: any
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

// Usage example
try {
  const user = await handleApiCall(() => 
    fetch('/api/profile', {
      headers: { 'Authorization': `Bearer ${token}` }
    })
  );
  console.log('User profile:', user.data);
} catch (error) {
  if (error instanceof ApiError) {
    switch (error.status) {
      case 401:
        // Redirect to login
        window.location.href = '/login';
        break;
      case 403:
        // Show access denied message
        showNotification('Access denied', 'error');
        break;
      case 404:
        // Show not found message
        showNotification('Resource not found', 'warning');
        break;
      default:
        // Show generic error
        showNotification(error.message, 'error');
    }
  }
}
```

---

## 🧪 Test Data & Accounts

### Available Test Accounts

**Admin Account:**
```json
{
  "identifier": "admin@ttpu.uz",
  "password": "admin123"
}
```

**Teacher Accounts:**
```json
{
  "identifier": "d.karimov@ttpu.uz",
  "password": "password123"
},
{
  "identifier": "s.nazarova@ttpu.uz",  
  "password": "password123"
}
```

**Student Accounts:**
```json
{
  "identifier": "a.rahmonov@student.ttpu.uz",
  "password": "password123"
},
{
  "identifier": "m.usmanova@student.ttpu.uz",
  "password": "password123"
},
{
  "identifier": "b.tursunov@student.ttpu.uz",
  "password": "password123"
}
```

**Alternative Login Methods:**
```json
// By phone
{
  "identifier": "+998901234567",
  "password": "password123"
}

// By student ID  
{
  "identifier": "12345678",
  "password": "password123"
}
```

---

## 📊 Integration Patterns

### 1. Authentication Flow

```typescript
class AuthenticationFlow {
  async login(identifier: string, password: string) {
    // 1. Login request
    const response = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ identifier, password })
    });

    if (!response.ok) {
      throw new Error('Login failed');
    }

    const data = await response.json();
    
    // 2. Store tokens
    localStorage.setItem('accessToken', data.token);
    localStorage.setItem('refreshToken', data.refreshToken);
    
    // 3. Store user data
    localStorage.setItem('currentUser', JSON.stringify(data.user));
    
    // 4. Setup token refresh
    this.setupTokenRefresh();
    
    return data.user;
  }

  setupTokenRefresh() {
    // Refresh token before expiry
    setInterval(async () => {
      try {
        await this.refreshToken();
      } catch (error) {
        console.error('Token refresh failed:', error);
        this.logout();
      }
    }, 50 * 60 * 1000); // 50 minutes
  }

  async refreshToken() {
    const refreshToken = localStorage.getItem('refreshToken');
    
    const response = await fetch('/api/auth/refresh', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refreshToken })
    });

    if (response.ok) {
      const data = await response.json();
      localStorage.setItem('accessToken', data.token);
      if (data.refreshToken) {
        localStorage.setItem('refreshToken', data.refreshToken);
      }
    } else {
      throw new Error('Token refresh failed');
    }
  }

  logout() {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('currentUser');
    window.location.href = '/login';
  }
}
```

### 2. Data Fetching Pattern

```typescript
class DataService {
  private baseUrl = 'http://127.0.0.1:5000';

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const token = localStorage.getItem('accessToken');
    
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(token && { Authorization: `Bearer ${token}` }),
        ...options.headers,
      },
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error?.message || 'Request failed');
    }

    return response.json();
  }

  // Profile methods
  async getProfile() {
    return this.request('/api/profile');
  }

  async updateProfile(data: any) {
    return this.request('/api/profile', {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  // Students methods
  async getStudents(params: any = {}) {
    const query = new URLSearchParams(params).toString();
    return this.request(`/api/students?${query}`);
  }

  // Search methods
  async search(query: string, type: string = 'all') {
    return this.request(`/api/search?q=${encodeURIComponent(query)}&type=${type}`);
  }

  // Admin methods (with role check)
  async getUsers(params: any = {}) {
    const query = new URLSearchParams(params).toString();
    return this.request(`/api/admin/users?${query}`);
  }

  async verifyUser(userId: string) {
    return this.request(`/api/admin/users/${userId}/verify`, {
      method: 'PATCH',
    });
  }
}
```

This comprehensive API reference provides all the information needed to successfully integrate with the Turin Grad Hub backend. Each endpoint includes detailed examples, request/response formats, and error handling patterns for production-ready frontend implementation.