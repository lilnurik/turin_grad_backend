# 🚀 Quick Start Guide: Frontend Integration

## 📋 Overview

This guide provides immediate, actionable steps to integrate a frontend application with the Turin Grad Hub backend API. Perfect for developers who want to get up and running quickly.

## 🎯 Backend API Status

- **Status**: ✅ Fully Operational
- **Base URL**: `http://127.0.0.1:5000`
- **Documentation**: [Swagger UI](http://127.0.0.1:5000/api/docs/)
- **Authentication**: JWT Bearer tokens
- **Endpoints**: 40+ fully implemented endpoints

## ⚡ 5-Minute Integration Setup

### Step 1: Test API Connection

```bash
# Test if backend is running
curl http://127.0.0.1:5000/api/health

# Expected response:
# {"success": true, "data": {"status": "healthy"}}
```

### Step 2: Initialize Frontend Project

```bash
# Create React project with TypeScript
npm create vite@latest turin-grad-frontend -- --template react-ts
cd turin-grad-frontend

# Install essential dependencies
npm install axios @tanstack/react-query zustand react-router-dom react-hook-form

# Install UI dependencies
npm install tailwindcss @headlessui/react lucide-react react-hot-toast

# Start development server
npm run dev
```

### Step 3: Basic API Client Setup

```typescript
// src/utils/apiClient.ts
import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:5000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('accessToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default apiClient;
```

### Step 4: Authentication Service

```typescript
// src/services/auth.service.ts
import apiClient from '../utils/apiClient';

export interface LoginRequest {
  identifier: string; // email, phone, or student ID
  password: string;
}

export interface User {
  id: string;
  firstName: string;
  lastName: string;
  email: string;
  role: 'admin' | 'teacher' | 'student';
  verified: boolean;
}

export class AuthService {
  static async login(credentials: LoginRequest) {
    const response = await apiClient.post('/api/auth/login', credentials);
    const { user, token, refreshToken } = response.data;
    
    localStorage.setItem('accessToken', token);
    localStorage.setItem('refreshToken', refreshToken);
    
    return { user, token };
  }

  static async getCurrentUser(): Promise<User> {
    const response = await apiClient.get('/api/profile');
    return response.data.data;
  }

  static logout() {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
  }
}
```

### Step 5: Simple Login Component

```typescript
// src/components/LoginForm.tsx
import React, { useState } from 'react';
import { AuthService } from '../services/auth.service';

export const LoginForm: React.FC = () => {
  const [identifier, setIdentifier] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const { user } = await AuthService.login({ identifier, password });
      console.log('Logged in user:', user);
      // Redirect based on role
      window.location.href = user.role === 'admin' ? '/admin' : `/${user.role}`;
    } catch (err: any) {
      setError(err.response?.data?.error?.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 max-w-md mx-auto p-6 bg-white rounded-lg shadow">
      <h2 className="text-2xl font-bold text-center">Login to Turin Grad Hub</h2>
      
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      <div>
        <label className="block text-sm font-medium text-gray-700">
          Email, Phone, or Student ID
        </label>
        <input
          type="text"
          value={identifier}
          onChange={(e) => setIdentifier(e.target.value)}
          className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          placeholder="Enter your email, phone, or student ID"
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">Password</label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          required
        />
      </div>

      <button
        type="submit"
        disabled={loading}
        className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
      >
        {loading ? 'Signing in...' : 'Sign In'}
      </button>
    </form>
  );
};
```

## 🔐 Authentication Examples

### Login with Different Identifier Types

```typescript
// Login with email
await AuthService.login({
  identifier: 'student@ttpu.uz',
  password: 'password123'
});

// Login with phone
await AuthService.login({
  identifier: '+998901234567',
  password: 'password123'
});

// Login with student ID
await AuthService.login({
  identifier: '12345678',
  password: 'password123'
});
```

### Test Accounts (from sample data)

```typescript
// Admin Account
{
  identifier: 'admin@ttpu.uz',
  password: 'admin123'
}

// Teacher Account
{
  identifier: 'd.karimov@ttpu.uz',
  password: 'password123'
}

// Student Account
{
  identifier: 'a.rahmonov@student.ttpu.uz',
  password: 'password123'
}
```

## 📊 Data Fetching Examples

### Get User Profile

```typescript
// src/services/profile.service.ts
import apiClient from '../utils/apiClient';

export class ProfileService {
  static async getProfile() {
    const response = await apiClient.get('/api/profile');
    return response.data.data;
  }

  static async updateProfile(data: any) {
    const response = await apiClient.put('/api/profile', data);
    return response.data.data;
  }

  static async getWorkExperience() {
    const response = await apiClient.get('/api/profile/work-experience');
    return response.data.data;
  }

  static async addWorkExperience(data: any) {
    const response = await apiClient.post('/api/profile/work-experience', data);
    return response.data.data;
  }
}
```

### Get Students List (Teacher/Admin)

```typescript
// src/services/student.service.ts
export class StudentService {
  static async getStudents(params = {}) {
    const response = await apiClient.get('/api/students', { params });
    return response.data.data;
  }

  static async getStudentById(id: string) {
    const response = await apiClient.get(`/api/students/${id}`);
    return response.data.data;
  }
}

// Usage with filters
const students = await StudentService.getStudents({
  page: 1,
  limit: 20,
  faculty: 'Computer Science',
  search: 'John'
});
```

### Search Functionality

```typescript
// src/services/search.service.ts
export class SearchService {
  static async globalSearch(query: string, type = 'all') {
    const response = await apiClient.get('/api/search', {
      params: { q: query, type }
    });
    return response.data.data;
  }

  static async searchStudents(params: any) {
    const response = await apiClient.get('/api/search/students', { params });
    return response.data.data;
  }
}

// Usage
const results = await SearchService.globalSearch('John Doe', 'students');
```

## 🔧 Admin Operations Examples

### User Management

```typescript
// src/services/admin.service.ts
export class AdminService {
  static async getUsers(params = {}) {
    const response = await apiClient.get('/api/admin/users', { params });
    return response.data;
  }

  static async createUser(userData: any) {
    const response = await apiClient.post('/api/admin/users', userData);
    return response.data.data;
  }

  static async verifyUser(userId: string) {
    const response = await apiClient.patch(`/api/admin/users/${userId}/verify`);
    return response.data;
  }

  static async blockUser(userId: string, reason: string) {
    const response = await apiClient.patch(`/api/admin/users/${userId}/block`, {
      blocked: true,
      reason
    });
    return response.data;
  }

  static async getActivityLogs(params = {}) {
    const response = await apiClient.get('/api/admin/activity-logs', { params });
    return response.data;
  }
}
```

## 🔔 Notifications Examples

```typescript
// src/services/notification.service.ts
export class NotificationService {
  static async getNotifications(params = {}) {
    const response = await apiClient.get('/api/notifications', { params });
    return response.data;
  }

  static async markAsRead(notificationId: string) {
    const response = await apiClient.patch(`/api/notifications/${notificationId}/read`);
    return response.data;
  }

  static async markAllAsRead() {
    const response = await apiClient.patch('/api/notifications/mark-all-read');
    return response.data;
  }
}
```

## 📚 Reference Data Examples

```typescript
// src/services/dictionary.service.ts
export class DictionaryService {
  static async getFaculties() {
    const response = await apiClient.get('/api/dictionaries/faculties');
    return response.data.data;
  }

  static async getDirections(facultyId?: string) {
    const params = facultyId ? { facultyId } : {};
    const response = await apiClient.get('/api/dictionaries/directions', { params });
    return response.data.data;
  }

  static async getCompanies() {
    const response = await apiClient.get('/api/dictionaries/companies');
    return response.data.data;
  }

  static async addCompany(companyData: any) {
    const response = await apiClient.post('/api/dictionaries/companies', companyData);
    return response.data.data;
  }
}
```

## 🎨 UI Components with API Integration

### User Profile Card

```typescript
// src/components/UserProfileCard.tsx
import React, { useEffect, useState } from 'react';
import { ProfileService } from '../services/profile.service';

interface User {
  id: string;
  firstName: string;
  lastName: string;
  email: string;
  role: string;
  faculty?: string;
  direction?: string;
}

export const UserProfileCard: React.FC = () => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const profile = await ProfileService.getProfile();
        setUser(profile);
      } catch (error) {
        console.error('Failed to fetch profile:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, []);

  if (loading) {
    return <div className="animate-pulse bg-gray-200 h-32 rounded-lg"></div>;
  }

  if (!user) {
    return <div className="text-red-500">Failed to load profile</div>;
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center space-x-4">
        <div className="w-16 h-16 bg-blue-500 rounded-full flex items-center justify-center text-white font-bold text-xl">
          {user.firstName[0]}{user.lastName[0]}
        </div>
        <div>
          <h3 className="text-lg font-semibold">{user.firstName} {user.lastName}</h3>
          <p className="text-gray-600">{user.email}</p>
          <p className="text-sm text-gray-500 capitalize">{user.role}</p>
          {user.faculty && (
            <p className="text-sm text-gray-500">{user.faculty} - {user.direction}</p>
          )}
        </div>
      </div>
    </div>
  );
};
```

### Students List Component

```typescript
// src/components/StudentsList.tsx
import React, { useEffect, useState } from 'react';
import { StudentService } from '../services/student.service';

export const StudentsList: React.FC = () => {
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  useEffect(() => {
    const fetchStudents = async () => {
      try {
        const data = await StudentService.getStudents({ search, limit: 10 });
        setStudents(data.data || []);
      } catch (error) {
        console.error('Failed to fetch students:', error);
      } finally {
        setLoading(false);
      }
    };

    const timeoutId = setTimeout(fetchStudents, 300); // Debounce search
    return () => clearTimeout(timeoutId);
  }, [search]);

  return (
    <div className="space-y-4">
      <input
        type="text"
        placeholder="Search students..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
      />

      {loading ? (
        <div className="space-y-2">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="animate-pulse bg-gray-200 h-16 rounded-lg"></div>
          ))}
        </div>
      ) : (
        <div className="space-y-2">
          {students.map((student: any) => (
            <div key={student.id} className="bg-white rounded-lg shadow p-4 flex items-center space-x-4">
              <div className="w-12 h-12 bg-green-500 rounded-full flex items-center justify-center text-white font-bold">
                {student.firstName[0]}{student.lastName[0]}
              </div>
              <div className="flex-1">
                <h4 className="font-semibold">{student.firstName} {student.lastName}</h4>
                <p className="text-gray-600 text-sm">{student.email}</p>
                <p className="text-gray-500 text-sm">{student.faculty} - {student.direction}</p>
              </div>
              <div className="text-right">
                <span className={`px-2 py-1 text-xs rounded-full ${
                  student.verified ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                }`}>
                  {student.verified ? 'Verified' : 'Pending'}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
```

## 🚨 Error Handling Examples

### API Error Handler

```typescript
// src/utils/errorHandler.ts
export class ErrorHandler {
  static handle(error: any): string {
    if (error.response?.data?.error?.message) {
      return error.response.data.error.message;
    }
    
    if (error.response?.status === 401) {
      return 'Please log in to continue';
    }
    
    if (error.response?.status === 403) {
      return 'You do not have permission to perform this action';
    }
    
    if (error.response?.status === 404) {
      return 'The requested resource was not found';
    }
    
    if (error.response?.status >= 500) {
      return 'Server error. Please try again later';
    }
    
    return 'An unexpected error occurred';
  }
}
```

### Error Boundary Component

```typescript
// src/components/ErrorBoundary.tsx
import React, { Component, ReactNode } from 'react';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: any) {
    console.error('Error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50">
          <div className="max-w-md w-full bg-white shadow rounded-lg p-6">
            <div className="text-center">
              <h2 className="text-lg font-semibold text-gray-900 mb-2">
                Something went wrong
              </h2>
              <p className="text-gray-600 mb-4">
                We're sorry, but something unexpected happened.
              </p>
              <button
                onClick={() => window.location.reload()}
                className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
              >
                Reload Page
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
```

## 📱 Quick Mobile-First Component

```typescript
// src/components/MobileNavigation.tsx
import React, { useState } from 'react';
import { Menu, X, User, Search, Bell } from 'lucide-react';

export const MobileNavigation: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="lg:hidden">
      <div className="flex items-center justify-between p-4 bg-white shadow">
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="p-2 rounded-md text-gray-600 hover:text-gray-900"
        >
          {isOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
        
        <h1 className="text-lg font-semibold">Turin Grad Hub</h1>
        
        <div className="flex items-center space-x-2">
          <button className="p-2 rounded-md text-gray-600">
            <Search size={20} />
          </button>
          <button className="p-2 rounded-md text-gray-600">
            <Bell size={20} />
          </button>
          <button className="p-2 rounded-md text-gray-600">
            <User size={20} />
          </button>
        </div>
      </div>

      {isOpen && (
        <div className="bg-white shadow-lg">
          <nav className="px-4 py-2 space-y-2">
            <a href="/dashboard" className="block py-2 px-4 text-gray-700 hover:bg-gray-100 rounded">
              Dashboard
            </a>
            <a href="/profile" className="block py-2 px-4 text-gray-700 hover:bg-gray-100 rounded">
              Profile
            </a>
            <a href="/search" className="block py-2 px-4 text-gray-700 hover:bg-gray-100 rounded">
              Search
            </a>
            <a href="/notifications" className="block py-2 px-4 text-gray-700 hover:bg-gray-100 rounded">
              Notifications
            </a>
          </nav>
        </div>
      )}
    </div>
  );
};
```

## 🎯 Next Steps

1. **Implement the basic login form** and test authentication
2. **Create a simple dashboard** to display user information
3. **Add role-based routing** for different user types
4. **Implement data fetching** for student/teacher lists
5. **Add search functionality** with the search endpoints
6. **Create profile management** features
7. **Add notifications** and real-time updates

## 📋 Complete API Endpoints Reference

### Authentication Endpoints
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `POST /api/auth/logout` - User logout
- `POST /api/auth/refresh` - Refresh token
- `POST /api/auth/forgot-password` - Request password reset
- `POST /api/auth/reset-password` - Reset password
- `POST /api/auth/verify-email` - Verify email
- `POST /api/auth/send-sms` - Send SMS code
- `POST /api/auth/verify-sms` - Verify SMS code

### Profile Endpoints
- `GET /api/profile` - Get current user profile
- `PUT /api/profile` - Update profile
- `GET /api/profile/work-experience` - Get work experience
- `POST /api/profile/work-experience` - Add work experience
- `GET /api/profile/education-goals` - Get education goals
- `POST /api/profile/education-goals` - Add education goal

### Admin Endpoints
- `GET /api/admin/users` - Get all users
- `POST /api/admin/users` - Create user
- `GET /api/admin/users/:id` - Get user by ID
- `PUT /api/admin/users/:id` - Update user
- `DELETE /api/admin/users/:id` - Delete user
- `PATCH /api/admin/users/:id/verify` - Verify user
- `PATCH /api/admin/users/:id/block` - Block/unblock user
- `GET /api/admin/activity-logs` - Get activity logs

### Student & Teacher Endpoints
- `GET /api/students` - Get students list
- `GET /api/teachers` - Get teachers list

### Search Endpoints
- `GET /api/search` - Global search
- `GET /api/search/students` - Search students

### Notification Endpoints
- `GET /api/notifications` - Get notifications
- `PATCH /api/notifications/:id/read` - Mark as read
- `PATCH /api/notifications/mark-all-read` - Mark all as read

### Dictionary Endpoints
- `GET /api/dictionaries/faculties` - Get faculties
- `GET /api/dictionaries/directions` - Get directions
- `GET /api/dictionaries/companies` - Get companies
- `POST /api/dictionaries/companies` - Add company

### System Endpoints
- `GET /api/health` - Health check
- `GET /api/info` - API information
- `GET /api/config` - Client configuration

---

This quick start guide provides everything needed to begin integrating with the Turin Grad Hub backend API. The backend is production-ready and waiting for your frontend implementation! 🚀