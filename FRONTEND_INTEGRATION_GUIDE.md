# 🚀 Turin Grad Hub - Frontend Integration Guide

## AI Prompt for Frontend Development

**Primary Objective:** Create a comprehensive, modern frontend application that seamlessly integrates with the Turin Grad Hub backend API to provide an intuitive user experience for students, teachers, and administrators.

### 🎯 Core Requirements

**You are tasked with building a modern, responsive frontend application for the Turin Grad Hub system - a graduate management platform for Turin Polytechnic University of Tashkent (TTPU). The backend API is fully implemented and documented at http://127.0.0.1:5000/api/docs/**

## 📋 Project Specifications

### 🏗️ Technology Stack Recommendations

**Primary Options:**
- **React.js** with TypeScript + Vite/Create React App
- **Vue.js 3** with TypeScript + Vue CLI/Vite  
- **Angular** with TypeScript
- **Next.js** for full-stack React with SSR capabilities

**State Management:**
- Redux Toolkit (React) / Pinia (Vue) / NgRx (Angular)
- React Query/TanStack Query for server state
- Zustand (lightweight alternative for React)

**UI Framework:**
- **Material-UI (MUI)** for professional academic look
- **Ant Design** for comprehensive component library
- **Chakra UI** for modern, accessible components
- **Tailwind CSS** + Headless UI for custom design

**HTTP Client:**
- Axios with interceptors for API calls
- Native fetch with custom wrapper
- TanStack Query for caching and synchronization

### 🔐 Authentication & Security Implementation

```typescript
// API Client Setup Example
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://127.0.0.1:5000';

// Create axios instance with base configuration
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('accessToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const refreshToken = localStorage.getItem('refreshToken');
        const response = await axios.post(`${API_BASE_URL}/api/auth/refresh`, {
          refreshToken
        });
        
        const { token } = response.data;
        localStorage.setItem('accessToken', token);
        
        // Retry original request with new token
        originalRequest.headers.Authorization = `Bearer ${token}`;
        return apiClient(originalRequest);
      } catch (refreshError) {
        // Refresh failed, redirect to login
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);

export default apiClient;
```

### 🏛️ Application Architecture

#### 📁 Recommended Folder Structure

```
src/
├── components/           # Reusable UI components
│   ├── common/          # Generic components
│   ├── forms/           # Form components
│   ├── layout/          # Layout components
│   └── ui/              # Base UI components
├── pages/               # Page components
│   ├── auth/            # Authentication pages
│   ├── admin/           # Admin dashboard pages
│   ├── student/         # Student portal pages
│   ├── teacher/         # Teacher portal pages
│   └── profile/         # Profile management
├── services/            # API service functions
│   ├── auth.service.ts
│   ├── admin.service.ts
│   ├── profile.service.ts
│   └── students.service.ts
├── hooks/               # Custom React hooks
├── store/               # State management
├── types/               # TypeScript type definitions
├── utils/               # Utility functions
├── constants/           # Application constants
└── assets/              # Static assets
```

### 🔧 API Service Layer Implementation

```typescript
// types/api.types.ts
export interface User {
  id: string;
  firstName: string;
  lastName: string;
  email: string;
  role: 'admin' | 'teacher' | 'student';
  avatar?: string;
  verified: boolean;
  blocked: boolean;
}

export interface LoginRequest {
  identifier: string; // email, phone, or student ID
  password: string;
}

export interface LoginResponse {
  success: boolean;
  user: User;
  token: string;
  refreshToken: string;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: any;
  };
}

// services/auth.service.ts
import apiClient from '../utils/apiClient';
import { LoginRequest, LoginResponse, User } from '../types/api.types';

export class AuthService {
  static async login(credentials: LoginRequest): Promise<LoginResponse> {
    const response = await apiClient.post('/api/auth/login', credentials);
    return response.data;
  }

  static async register(userData: RegisterRequest): Promise<ApiResponse<User>> {
    const response = await apiClient.post('/api/auth/register', userData);
    return response.data;
  }

  static async logout(): Promise<void> {
    const refreshToken = localStorage.getItem('refreshToken');
    await apiClient.post('/api/auth/logout', { refreshToken });
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
  }

  static async getCurrentUser(): Promise<User> {
    const response = await apiClient.get('/api/profile');
    return response.data.data;
  }

  static async forgotPassword(identifier: string): Promise<ApiResponse<void>> {
    const response = await apiClient.post('/api/auth/forgot-password', { identifier });
    return response.data;
  }

  static async resetPassword(token: string, newPassword: string): Promise<ApiResponse<void>> {
    const response = await apiClient.post('/api/auth/reset-password', {
      token,
      newPassword
    });
    return response.data;
  }
}
```

### 🎨 Component Implementation Patterns

#### 🔒 Authentication Components

```typescript
// components/auth/LoginForm.tsx
import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useMutation } from '@tanstack/react-query';
import { AuthService } from '../../services/auth.service';
import { useAuthStore } from '../../store/authStore';

interface LoginFormData {
  identifier: string;
  password: string;
  rememberMe: boolean;
}

export const LoginForm: React.FC = () => {
  const { register, handleSubmit, formState: { errors } } = useForm<LoginFormData>();
  const { setUser, setTokens } = useAuthStore();

  const loginMutation = useMutation({
    mutationFn: AuthService.login,
    onSuccess: (data) => {
      setUser(data.user);
      setTokens(data.token, data.refreshToken);
      // Redirect based on user role
      const redirectPath = data.user.role === 'admin' ? '/admin' : 
                          data.user.role === 'teacher' ? '/teacher' : '/student';
      window.location.href = redirectPath;
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error?.message || 'Login failed');
    }
  });

  const onSubmit = (data: LoginFormData) => {
    loginMutation.mutate({
      identifier: data.identifier,
      password: data.password
    });
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700">
          Email, Phone, or Student ID
        </label>
        <input
          {...register('identifier', { required: 'This field is required' })}
          type="text"
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
          placeholder="Enter your email, phone, or student ID"
        />
        {errors.identifier && (
          <p className="mt-1 text-sm text-red-600">{errors.identifier.message}</p>
        )}
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">
          Password
        </label>
        <input
          {...register('password', { required: 'Password is required' })}
          type="password"
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
        />
        {errors.password && (
          <p className="mt-1 text-sm text-red-600">{errors.password.message}</p>
        )}
      </div>

      <div className="flex items-center justify-between">
        <label className="flex items-center">
          <input
            {...register('rememberMe')}
            type="checkbox"
            className="rounded border-gray-300"
          />
          <span className="ml-2 text-sm text-gray-600">Remember me</span>
        </label>
        <Link to="/forgot-password" className="text-sm text-blue-600 hover:text-blue-500">
          Forgot password?
        </Link>
      </div>

      <button
        type="submit"
        disabled={loginMutation.isPending}
        className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50"
      >
        {loginMutation.isPending ? 'Signing in...' : 'Sign in'}
      </button>
    </form>
  );
};
```

#### 🛡️ Role-Based Route Protection

```typescript
// components/auth/ProtectedRoute.tsx
import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';

interface ProtectedRouteProps {
  children: React.ReactNode;
  allowedRoles?: string[];
  requireAuth?: boolean;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  allowedRoles = [],
  requireAuth = true
}) => {
  const { user, isAuthenticated } = useAuthStore();

  if (requireAuth && !isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (allowedRoles.length > 0 && user && !allowedRoles.includes(user.role)) {
    return <Navigate to="/unauthorized" replace />;
  }

  return <>{children}</>;
};
```

### 📊 State Management with Zustand

```typescript
// store/authStore.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { User } from '../types/api.types';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  accessToken: string | null;
  refreshToken: string | null;
  
  setUser: (user: User) => void;
  setTokens: (accessToken: string, refreshToken: string) => void;
  logout: () => void;
  updateUser: (userData: Partial<User>) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      isAuthenticated: false,
      accessToken: null,
      refreshToken: null,

      setUser: (user) => set({ user, isAuthenticated: true }),
      
      setTokens: (accessToken, refreshToken) => {
        set({ accessToken, refreshToken });
        localStorage.setItem('accessToken', accessToken);
        localStorage.setItem('refreshToken', refreshToken);
      },

      logout: () => {
        set({
          user: null,
          isAuthenticated: false,
          accessToken: null,
          refreshToken: null
        });
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
      },

      updateUser: (userData) => {
        const currentUser = get().user;
        if (currentUser) {
          set({ user: { ...currentUser, ...userData } });
        }
      }
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ 
        user: state.user, 
        isAuthenticated: state.isAuthenticated 
      })
    }
  )
);
```

### 📋 Advanced Form Handling

```typescript
// components/profile/ProfileForm.tsx
import React from 'react';
import { useForm, Controller } from 'react-hook-form';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { ProfileService } from '../../services/profile.service';
import { useAuthStore } from '../../store/authStore';

interface ProfileFormData {
  firstName: string;
  lastName: string;
  middleName?: string;
  email: string;
  phone: string;
  faculty: string;
  direction: string;
  bio?: string;
}

export const ProfileForm: React.FC = () => {
  const { user, updateUser } = useAuthStore();
  const queryClient = useQueryClient();
  
  const { control, handleSubmit, formState: { errors } } = useForm<ProfileFormData>({
    defaultValues: {
      firstName: user?.firstName || '',
      lastName: user?.lastName || '',
      email: user?.email || '',
      // ... other defaults
    }
  });

  const updateProfileMutation = useMutation({
    mutationFn: ProfileService.updateProfile,
    onSuccess: (data) => {
      updateUser(data.data);
      queryClient.invalidateQueries({ queryKey: ['profile'] });
      toast.success('Profile updated successfully!');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error?.message || 'Update failed');
    }
  });

  const onSubmit = (data: ProfileFormData) => {
    updateProfileMutation.mutate(data);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Controller
          name="firstName"
          control={control}
          rules={{ required: 'First name is required' }}
          render={({ field }) => (
            <div>
              <label className="block text-sm font-medium text-gray-700">
                First Name *
              </label>
              <input
                {...field}
                type="text"
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              />
              {errors.firstName && (
                <p className="mt-1 text-sm text-red-600">{errors.firstName.message}</p>
              )}
            </div>
          )}
        />

        <Controller
          name="lastName"
          control={control}
          rules={{ required: 'Last name is required' }}
          render={({ field }) => (
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Last Name *
              </label>
              <input
                {...field}
                type="text"
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              />
              {errors.lastName && (
                <p className="mt-1 text-sm text-red-600">{errors.lastName.message}</p>
              )}
            </div>
          )}
        />
      </div>

      {/* Additional form fields... */}

      <div className="flex justify-end space-x-3">
        <button
          type="button"
          className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
        >
          Cancel
        </button>
        <button
          type="submit"
          disabled={updateProfileMutation.isPending}
          className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50"
        >
          {updateProfileMutation.isPending ? 'Updating...' : 'Save Changes'}
        </button>
      </div>
    </form>
  );
};
```

### 🏫 Role-Specific Dashboards

#### 👨‍🎓 Student Dashboard

```typescript
// pages/student/StudentDashboard.tsx
import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { ProfileService } from '../../services/profile.service';
import { StatsCard } from '../../components/common/StatsCard';
import { RecentActivities } from '../../components/student/RecentActivities';
import { UpcomingEvents } from '../../components/student/UpcomingEvents';

export const StudentDashboard: React.FC = () => {
  const { data: profile, isLoading } = useQuery({
    queryKey: ['profile'],
    queryFn: ProfileService.getCurrentProfile
  });

  const { data: workExperience } = useQuery({
    queryKey: ['work-experience'],
    queryFn: ProfileService.getWorkExperience
  });

  const { data: educationGoals } = useQuery({
    queryKey: ['education-goals'],
    queryFn: ProfileService.getEducationGoals
  });

  if (isLoading) {
    return <div className="flex justify-center items-center h-64">Loading...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Welcome Header */}
      <div className="bg-white shadow rounded-lg p-6">
        <h1 className="text-2xl font-bold text-gray-900">
          Welcome back, {profile?.firstName}!
        </h1>
        <p className="text-gray-600 mt-1">
          {profile?.faculty} - {profile?.direction}
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <StatsCard
          title="Work Experience"
          value={workExperience?.length || 0}
          subtitle="positions"
          icon="briefcase"
          color="blue"
        />
        <StatsCard
          title="Education Goals"
          value={educationGoals?.length || 0}
          subtitle="goals set"
          icon="target"
          color="green"
        />
        <StatsCard
          title="Profile Completion"
          value="85%"
          subtitle="completed"
          icon="user"
          color="yellow"
        />
      </div>

      {/* Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <RecentActivities />
        <UpcomingEvents />
      </div>
    </div>
  );
};
```

#### 👨‍🏫 Teacher Dashboard

```typescript
// pages/teacher/TeacherDashboard.tsx
import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { TeacherService } from '../../services/teacher.service';
import { StudentsList } from '../../components/teacher/StudentsList';
import { PerformanceChart } from '../../components/teacher/PerformanceChart';

export const TeacherDashboard: React.FC = () => {
  const { data: students } = useQuery({
    queryKey: ['my-students'],
    queryFn: TeacherService.getMyStudents
  });

  const { data: analytics } = useQuery({
    queryKey: ['teacher-analytics'],
    queryFn: TeacherService.getAnalytics
  });

  return (
    <div className="space-y-6">
      <div className="bg-white shadow rounded-lg p-6">
        <h1 className="text-2xl font-bold text-gray-900">Teacher Dashboard</h1>
        <p className="text-gray-600 mt-1">
          Managing {students?.length || 0} students
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <StudentsList students={students} />
        </div>
        <div>
          <PerformanceChart data={analytics} />
        </div>
      </div>
    </div>
  );
};
```

### 📊 Data Fetching and Caching Strategy

```typescript
// hooks/useStudents.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { StudentService } from '../services/student.service';
import { Student, StudentFilters } from '../types/api.types';

export const useStudents = (filters?: StudentFilters) => {
  return useQuery({
    queryKey: ['students', filters],
    queryFn: () => StudentService.getStudents(filters),
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
  });
};

export const useStudentById = (id: string) => {
  return useQuery({
    queryKey: ['student', id],
    queryFn: () => StudentService.getStudentById(id),
    enabled: !!id,
  });
};

export const useUpdateStudent = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Student> }) =>
      StudentService.updateStudent(id, data),
    onSuccess: (updatedStudent, { id }) => {
      // Update the student in the cache
      queryClient.setQueryData(['student', id], updatedStudent);
      
      // Invalidate and refetch students list
      queryClient.invalidateQueries({ queryKey: ['students'] });
      
      toast.success('Student updated successfully');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error?.message || 'Update failed');
    }
  });
};
```

### 🔍 Advanced Search Implementation

```typescript
// components/search/AdvancedSearch.tsx
import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useDebounce } from '../../hooks/useDebounce';
import { SearchService } from '../../services/search.service';

interface SearchFilters {
  query: string;
  type: 'all' | 'students' | 'teachers' | 'companies';
  faculty?: string;
  direction?: string;
  graduationYear?: number;
}

export const AdvancedSearch: React.FC = () => {
  const [filters, setFilters] = useState<SearchFilters>({
    query: '',
    type: 'all'
  });

  const debouncedQuery = useDebounce(filters.query, 300);

  const { data: searchResults, isLoading } = useQuery({
    queryKey: ['search', debouncedQuery, filters.type, filters.faculty, filters.direction],
    queryFn: () => SearchService.globalSearch(filters),
    enabled: debouncedQuery.length > 2,
  });

  const { data: faculties } = useQuery({
    queryKey: ['faculties'],
    queryFn: () => DictionaryService.getFaculties(),
  });

  return (
    <div className="space-y-6">
      {/* Search Input */}
      <div className="relative">
        <input
          type="text"
          placeholder="Search students, teachers, companies..."
          value={filters.query}
          onChange={(e) => setFilters(prev => ({ ...prev, query: e.target.value }))}
          className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center">
          <SearchIcon className="h-5 w-5 text-gray-400" />
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-4">
        <select
          value={filters.type}
          onChange={(e) => setFilters(prev => ({ ...prev, type: e.target.value as any }))}
          className="border border-gray-300 rounded-md px-3 py-2"
        >
          <option value="all">All Types</option>
          <option value="students">Students</option>
          <option value="teachers">Teachers</option>
          <option value="companies">Companies</option>
        </select>

        <select
          value={filters.faculty || ''}
          onChange={(e) => setFilters(prev => ({ ...prev, faculty: e.target.value || undefined }))}
          className="border border-gray-300 rounded-md px-3 py-2"
        >
          <option value="">All Faculties</option>
          {faculties?.map(faculty => (
            <option key={faculty.id} value={faculty.id}>
              {faculty.name}
            </option>
          ))}
        </select>
      </div>

      {/* Search Results */}
      <div className="space-y-4">
        {isLoading && debouncedQuery.length > 2 && (
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-2 text-gray-600">Searching...</p>
          </div>
        )}

        {searchResults && searchResults.length > 0 && (
          <div className="space-y-3">
            {searchResults.map((result, index) => (
              <SearchResultCard key={index} result={result} />
            ))}
          </div>
        )}

        {searchResults && searchResults.length === 0 && debouncedQuery.length > 2 && (
          <div className="text-center py-8">
            <p className="text-gray-600">No results found for "{debouncedQuery}"</p>
          </div>
        )}
      </div>
    </div>
  );
};
```

## 🎨 UI/UX Guidelines

### 🎨 Design System

```typescript
// styles/theme.ts
export const theme = {
  colors: {
    primary: {
      50: '#eff6ff',
      500: '#3b82f6',
      600: '#2563eb',
      700: '#1d4ed8',
    },
    success: {
      50: '#f0fdf4',
      500: '#22c55e',
      600: '#16a34a',
    },
    warning: {
      50: '#fffbeb',
      500: '#f59e0b',
      600: '#d97706',
    },
    error: {
      50: '#fef2f2',
      500: '#ef4444',
      600: '#dc2626',
    },
    gray: {
      50: '#f9fafb',
      100: '#f3f4f6',
      200: '#e5e7eb',
      300: '#d1d5db',
      400: '#9ca3af',
      500: '#6b7280',
      600: '#4b5563',
      700: '#374151',
      800: '#1f2937',
      900: '#111827',
    }
  },
  typography: {
    fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
    fontSize: {
      xs: '0.75rem',
      sm: '0.875rem',
      base: '1rem',
      lg: '1.125rem',
      xl: '1.25rem',
      '2xl': '1.5rem',
      '3xl': '1.875rem',
      '4xl': '2.25rem',
    }
  },
  spacing: {
    xs: '0.5rem',
    sm: '1rem',
    md: '1.5rem',
    lg: '2rem',
    xl: '3rem',
  },
  borderRadius: {
    sm: '0.375rem',
    md: '0.5rem',
    lg: '0.75rem',
    xl: '1rem',
  }
};
```

### 📱 Responsive Design

```css
/* styles/responsive.css */
@media (max-width: 640px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
  
  .nav-desktop {
    display: none;
  }
  
  .nav-mobile {
    display: block;
  }
}

@media (min-width: 768px) {
  .dashboard-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1024px) {
  .dashboard-grid {
    grid-template-columns: repeat(3, 1fr);
  }
  
  .nav-desktop {
    display: block;
  }
  
  .nav-mobile {
    display: none;
  }
}
```

## 🧪 Testing Strategy

### 🧪 Unit Testing with Jest & React Testing Library

```typescript
// __tests__/components/auth/LoginForm.test.tsx
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { LoginForm } from '../../../components/auth/LoginForm';
import { AuthService } from '../../../services/auth.service';

// Mock the auth service
jest.mock('../../../services/auth.service');
const mockAuthService = AuthService as jest.Mocked<typeof AuthService>;

const createTestQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

const renderWithProviders = (component: React.ReactElement) => {
  const queryClient = createTestQueryClient();
  return render(
    <QueryClientProvider client={queryClient}>
      {component}
    </QueryClientProvider>
  );
};

describe('LoginForm', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders login form correctly', () => {
    renderWithProviders(<LoginForm />);
    
    expect(screen.getByLabelText(/email, phone, or student id/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
  });

  it('submits form with correct data', async () => {
    const mockLogin = mockAuthService.login.mockResolvedValue({
      success: true,
      user: { id: '1', firstName: 'John', lastName: 'Doe', email: 'john@test.com', role: 'student' },
      token: 'mock-token',
      refreshToken: 'mock-refresh-token'
    });

    renderWithProviders(<LoginForm />);
    
    fireEvent.change(screen.getByLabelText(/email, phone, or student id/i), {
      target: { value: 'john@test.com' }
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: 'password123' }
    });
    
    fireEvent.click(screen.getByRole('button', { name: /sign in/i }));

    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith({
        identifier: 'john@test.com',
        password: 'password123'
      });
    });
  });

  it('displays error message on login failure', async () => {
    const mockLogin = mockAuthService.login.mockRejectedValue({
      response: {
        data: {
          error: {
            message: 'Invalid credentials'
          }
        }
      }
    });

    renderWithProviders(<LoginForm />);
    
    fireEvent.change(screen.getByLabelText(/email, phone, or student id/i), {
      target: { value: 'wrong@test.com' }
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: 'wrongpassword' }
    });
    
    fireEvent.click(screen.getByRole('button', { name: /sign in/i }));

    await waitFor(() => {
      expect(screen.getByText(/invalid credentials/i)).toBeInTheDocument();
    });
  });
});
```

### 🔧 Integration Testing

```typescript
// __tests__/integration/auth-flow.test.tsx
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { App } from '../../App';
import { server } from '../mocks/server';

// Setup MSW server for API mocking
beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe('Authentication Flow', () => {
  it('completes full login flow', async () => {
    const queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false }, mutations: { retry: false } }
    });

    render(
      <BrowserRouter>
        <QueryClientProvider client={queryClient}>
          <App />
        </QueryClientProvider>
      </BrowserRouter>
    );

    // Should start on login page
    expect(screen.getByText(/sign in to your account/i)).toBeInTheDocument();

    // Fill in login form
    fireEvent.change(screen.getByLabelText(/email, phone, or student id/i), {
      target: { value: 'student@ttpu.uz' }
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: 'password123' }
    });

    // Submit form
    fireEvent.click(screen.getByRole('button', { name: /sign in/i }));

    // Should redirect to dashboard
    await waitFor(() => {
      expect(screen.getByText(/welcome back/i)).toBeInTheDocument();
    });

    // Should show user profile
    expect(screen.getByText(/student dashboard/i)).toBeInTheDocument();
  });
});
```

## 🚀 Performance Optimization

### 📦 Code Splitting & Lazy Loading

```typescript
// App.tsx
import React, { Suspense } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { LoadingSpinner } from './components/common/LoadingSpinner';
import { ProtectedRoute } from './components/auth/ProtectedRoute';

// Lazy load pages for better performance
const Login = React.lazy(() => import('./pages/auth/Login'));
const StudentDashboard = React.lazy(() => import('./pages/student/StudentDashboard'));
const TeacherDashboard = React.lazy(() => import('./pages/teacher/TeacherDashboard'));
const AdminDashboard = React.lazy(() => import('./pages/admin/AdminDashboard'));
const Profile = React.lazy(() => import('./pages/profile/Profile'));

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      gcTime: 10 * 60 * 1000, // 10 minutes
      refetchOnWindowFocus: false,
    },
  },
});

export const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Suspense fallback={<LoadingSpinner />}>
          <Routes>
            <Route path="/login" element={<Login />} />
            
            <Route
              path="/student/*"
              element={
                <ProtectedRoute allowedRoles={['student']}>
                  <StudentDashboard />
                </ProtectedRoute>
              }
            />
            
            <Route
              path="/teacher/*"
              element={
                <ProtectedRoute allowedRoles={['teacher']}>
                  <TeacherDashboard />
                </ProtectedRoute>
              }
            />
            
            <Route
              path="/admin/*"
              element={
                <ProtectedRoute allowedRoles={['admin']}>
                  <AdminDashboard />
                </ProtectedRoute>
              }
            />
            
            <Route
              path="/profile"
              element={
                <ProtectedRoute>
                  <Profile />
                </ProtectedRoute>
              }
            />
          </Routes>
        </Suspense>
      </BrowserRouter>
      
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
};
```

### ⚡ Performance Hooks

```typescript
// hooks/useVirtualization.ts
import { useMemo } from 'react';
import { useVirtualizer } from '@tanstack/react-virtual';

export const useStudentVirtualization = (
  students: Student[],
  containerRef: React.RefObject<HTMLElement>
) => {
  const virtualizer = useVirtualizer({
    count: students.length,
    getScrollElement: () => containerRef.current,
    estimateSize: () => 80, // Estimated height of each student row
    overscan: 5,
  });

  const virtualItems = virtualizer.getVirtualItems();

  const visibleStudents = useMemo(() => {
    return virtualItems.map(virtualRow => ({
      ...virtualRow,
      student: students[virtualRow.index]
    }));
  }, [virtualItems, students]);

  return {
    virtualizer,
    visibleStudents,
    totalSize: virtualizer.getTotalSize(),
  };
};
```

## 📱 Progressive Web App Features

### 📱 PWA Configuration

```json
// public/manifest.json
{
  "name": "Turin Grad Hub",
  "short_name": "TurinGrad",
  "description": "Graduate management system for Turin Polytechnic University of Tashkent",
  "start_url": "/",
  "display": "standalone",
  "theme_color": "#3b82f6",
  "background_color": "#ffffff",
  "icons": [
    {
      "src": "/icons/icon-192x192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "/icons/icon-512x512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ]
}
```

## 🔒 Security Best Practices

### 🛡️ Security Implementations

```typescript
// utils/security.ts
export class SecurityUtils {
  // Sanitize user input
  static sanitizeInput(input: string): string {
    return input
      .replace(/[<>]/g, '') // Remove potential HTML tags
      .trim()
      .substring(0, 1000); // Limit length
  }

  // Validate file uploads
  static validateFileUpload(file: File, allowedTypes: string[], maxSize: number): boolean {
    if (!allowedTypes.includes(file.type)) {
      throw new Error('File type not allowed');
    }
    
    if (file.size > maxSize) {
      throw new Error('File size too large');
    }
    
    return true;
  }

  // Generate secure file names
  static generateSecureFileName(originalName: string): string {
    const extension = originalName.split('.').pop();
    const timestamp = Date.now();
    const random = Math.random().toString(36).substring(2);
    return `${timestamp}_${random}.${extension}`;
  }
}
```

## 📚 Key Implementation Notes

### ✅ Must-Have Features:
1. **Authentication Flow** - Complete login/logout with JWT tokens
2. **Role-Based Access** - Admin, Teacher, Student dashboards
3. **Profile Management** - View/edit profiles, work experience, education goals
4. **Search Functionality** - Global search with advanced filters
5. **Responsive Design** - Mobile-first approach
6. **Error Handling** - Comprehensive error boundaries and user feedback
7. **Loading States** - Skeleton loaders and progress indicators
8. **Notifications** - Real-time notifications system

### 🎯 Advanced Features:
1. **Real-time Updates** - WebSocket integration for live data
2. **Offline Support** - PWA with service workers
3. **File Uploads** - Avatar, CV, diploma management
4. **Data Export** - CSV/Excel export functionality
5. **Analytics Dashboard** - Charts and statistics
6. **Advanced Search** - Elasticsearch integration
7. **Internationalization** - Multi-language support
8. **Dark Mode** - Theme switching capability

### 🚀 Performance Targets:
- **First Contentful Paint**: < 1.5s
- **Time to Interactive**: < 3s
- **Lighthouse Score**: > 90
- **Bundle Size**: < 300KB (gzipped)

## 🔗 API Integration Examples

All API endpoints are available at `http://127.0.0.1:5000/api/docs/` with comprehensive documentation. Key endpoints include:

- **Authentication**: `/api/auth/*`
- **Profile Management**: `/api/profile/*`
- **Admin Functions**: `/api/admin/*`
- **Search**: `/api/search/*`
- **Notifications**: `/api/notifications/*`
- **Dictionaries**: `/api/dictionaries/*`

Refer to the Swagger documentation for complete API specifications, request/response formats, and authentication requirements.

---

**Remember**: This guide provides a comprehensive foundation for integrating with the Turin Grad Hub backend. Focus on creating a user-friendly, performant, and secure frontend that serves the needs of students, teachers, and administrators effectively.