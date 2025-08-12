# 🔧 Advanced Technical Specifications & Integration Patterns

## 📋 Complete API Integration Reference

This document provides advanced technical specifications for integrating with the Turin Grad Hub backend API, including detailed patterns, best practices, and production-ready implementations.

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend Application                      │
├─────────────────────────────────────────────────────────────┤
│  React/Vue/Angular + TypeScript + State Management          │
│  ├── Authentication Layer (JWT + Role-based Access)         │
│  ├── API Client Layer (HTTP + Interceptors)                 │
│  ├── Component Layer (UI + Business Logic)                  │
│  └── State Management (Client + Server State)               │
└─────────────────────────────────────────────────────────────┘
                                │
                           HTTP/HTTPS
                                │
┌─────────────────────────────────────────────────────────────┐
│                    Backend API Server                       │
├─────────────────────────────────────────────────────────────┤
│  Flask + SQLAlchemy + JWT + CORS + Swagger                  │
│  ├── Authentication & Authorization                         │
│  ├── Role-based Access Control (Admin/Teacher/Student)      │
│  ├── RESTful API Endpoints (40+ implemented)                │
│  ├── Database Layer (SQLite/PostgreSQL)                     │
│  └── File Upload & Management                               │
└─────────────────────────────────────────────────────────────┘
```

## 🔐 Advanced Authentication Patterns

### Complete Authentication Flow Implementation

```typescript
// types/auth.types.ts
export interface AuthTokens {
  accessToken: string;
  refreshToken: string;
  expiresIn: number;
}

export interface AuthUser {
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
  lastLogin?: string;
  createdAt: string;
  updatedAt: string;
}

export interface LoginResponse {
  success: boolean;
  user: AuthUser;
  token: string;
  refreshToken: string;
}

export interface RegisterRequest {
  firstName: string;
  lastName: string;
  middleName?: string;
  email: string;
  phone: string;
  studentId: string;
  password: string;
  faculty: string;
  direction: string;
}

// services/auth.service.ts - Production Implementation
import axios, { AxiosError } from 'axios';
import { AuthTokens, AuthUser, LoginResponse, RegisterRequest } from '../types/auth.types';

export class AuthService {
  private static readonly TOKEN_KEY = 'accessToken';
  private static readonly REFRESH_TOKEN_KEY = 'refreshToken';
  private static readonly USER_KEY = 'currentUser';

  // Login with comprehensive error handling
  static async login(identifier: string, password: string): Promise<LoginResponse> {
    try {
      const response = await axios.post('/api/auth/login', {
        identifier: identifier.trim(),
        password: password
      });

      if (response.data.success) {
        const { user, token, refreshToken } = response.data;
        
        // Store tokens securely
        this.setTokens(token, refreshToken);
        this.setUser(user);
        
        // Log successful login
        console.log(`User ${user.email} logged in successfully as ${user.role}`);
        
        return response.data;
      }
      
      throw new Error('Login failed');
    } catch (error) {
      this.handleAuthError(error as AxiosError);
      throw error;
    }
  }

  // Registration with validation
  static async register(userData: RegisterRequest): Promise<AuthUser> {
    try {
      // Validate required fields
      this.validateRegistrationData(userData);
      
      const response = await axios.post('/api/auth/register', userData);
      
      if (response.data.success) {
        return response.data.data;
      }
      
      throw new Error('Registration failed');
    } catch (error) {
      this.handleAuthError(error as AxiosError);
      throw error;
    }
  }

  // Token refresh mechanism
  static async refreshTokens(): Promise<AuthTokens> {
    const refreshToken = this.getRefreshToken();
    
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    try {
      const response = await axios.post('/api/auth/refresh', {
        refreshToken
      });

      if (response.data.success) {
        const { token, refreshToken: newRefreshToken } = response.data;
        this.setTokens(token, newRefreshToken);
        return { accessToken: token, refreshToken: newRefreshToken, expiresIn: 3600 };
      }
      
      throw new Error('Token refresh failed');
    } catch (error) {
      // If refresh fails, logout user
      this.logout();
      throw error;
    }
  }

  // Logout with cleanup
  static async logout(): Promise<void> {
    const refreshToken = this.getRefreshToken();
    
    try {
      if (refreshToken) {
        await axios.post('/api/auth/logout', { refreshToken });
      }
    } catch (error) {
      console.warn('Logout request failed:', error);
    } finally {
      // Always clean up local storage
      this.clearAuth();
    }
  }

  // Password reset flow
  static async forgotPassword(identifier: string): Promise<void> {
    try {
      await axios.post('/api/auth/forgot-password', {
        identifier: identifier.trim()
      });
    } catch (error) {
      this.handleAuthError(error as AxiosError);
      throw error;
    }
  }

  static async resetPassword(token: string, newPassword: string): Promise<void> {
    try {
      await axios.post('/api/auth/reset-password', {
        token,
        newPassword
      });
    } catch (error) {
      this.handleAuthError(error as AxiosError);
      throw error;
    }
  }

  // SMS verification
  static async sendSMSCode(phone: string): Promise<void> {
    try {
      await axios.post('/api/auth/send-sms', {
        phone: phone.trim()
      });
    } catch (error) {
      this.handleAuthError(error as AxiosError);
      throw error;
    }
  }

  static async verifySMSCode(phone: string, code: string): Promise<void> {
    try {
      await axios.post('/api/auth/verify-sms', {
        phone: phone.trim(),
        code: code.trim()
      });
    } catch (error) {
      this.handleAuthError(error as AxiosError);
      throw error;
    }
  }

  // Email verification
  static async verifyEmail(token: string): Promise<void> {
    try {
      await axios.post('/api/auth/verify-email', { token });
    } catch (error) {
      this.handleAuthError(error as AxiosError);
      throw error;
    }
  }

  // Utility methods
  static getAccessToken(): string | null {
    return localStorage.getItem(this.TOKEN_KEY);
  }

  static getRefreshToken(): string | null {
    return localStorage.getItem(this.REFRESH_TOKEN_KEY);
  }

  static getCurrentUser(): AuthUser | null {
    const userData = localStorage.getItem(this.USER_KEY);
    return userData ? JSON.parse(userData) : null;
  }

  static isAuthenticated(): boolean {
    return !!this.getAccessToken() && !!this.getCurrentUser();
  }

  static hasRole(role: string): boolean {
    const user = this.getCurrentUser();
    return user?.role === role;
  }

  static hasAnyRole(roles: string[]): boolean {
    const user = this.getCurrentUser();
    return user ? roles.includes(user.role) : false;
  }

  // Private helper methods
  private static setTokens(accessToken: string, refreshToken: string): void {
    localStorage.setItem(this.TOKEN_KEY, accessToken);
    localStorage.setItem(this.REFRESH_TOKEN_KEY, refreshToken);
  }

  private static setUser(user: AuthUser): void {
    localStorage.setItem(this.USER_KEY, JSON.stringify(user));
  }

  private static clearAuth(): void {
    localStorage.removeItem(this.TOKEN_KEY);
    localStorage.removeItem(this.REFRESH_TOKEN_KEY);
    localStorage.removeItem(this.USER_KEY);
  }

  private static validateRegistrationData(data: RegisterRequest): void {
    const required = ['firstName', 'lastName', 'email', 'phone', 'studentId', 'password', 'faculty', 'direction'];
    
    for (const field of required) {
      if (!data[field as keyof RegisterRequest]) {
        throw new Error(`${field} is required`);
      }
    }

    // Email validation
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.email)) {
      throw new Error('Invalid email format');
    }

    // Phone validation (basic)
    if (!/^\+\d{12}$/.test(data.phone)) {
      throw new Error('Invalid phone format. Use +998XXXXXXXXX');
    }

    // Student ID validation
    if (!/^\d{8}$/.test(data.studentId)) {
      throw new Error('Student ID must be 8 digits');
    }

    // Password validation
    if (data.password.length < 8) {
      throw new Error('Password must be at least 8 characters');
    }
  }

  private static handleAuthError(error: AxiosError): void {
    if (error.response?.status === 401) {
      this.clearAuth();
      window.location.href = '/login';
    }
    
    console.error('Authentication error:', error.response?.data || error.message);
  }
}
```

### Advanced API Client with Interceptors

```typescript
// utils/apiClient.ts - Production Implementation
import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios';
import { AuthService } from '../services/auth.service';

class APIClient {
  private client: AxiosInstance;
  private isRefreshing = false;
  private refreshSubscribers: ((token: string) => void)[] = [];

  constructor() {
    this.client = axios.create({
      baseURL: process.env.REACT_APP_API_URL || 'http://127.0.0.1:5000',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors(): void {
    // Request interceptor
    this.client.interceptors.request.use(
      (config: AxiosRequestConfig) => {
        const token = AuthService.getAccessToken();
        
        if (token) {
          config.headers = {
            ...config.headers,
            Authorization: `Bearer ${token}`,
          };
        }

        // Log request in development
        if (process.env.NODE_ENV === 'development') {
          console.log(`🚀 ${config.method?.toUpperCase()} ${config.url}`, config.data);
        }

        return config;
      },
      (error: AxiosError) => {
        console.error('Request error:', error);
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response: AxiosResponse) => {
        // Log response in development
        if (process.env.NODE_ENV === 'development') {
          console.log(`✅ ${response.config.method?.toUpperCase()} ${response.config.url}`, response.data);
        }

        return response;
      },
      async (error: AxiosError) => {
        const originalRequest = error.config as AxiosRequestConfig & { _retry?: boolean };

        // Handle 401 errors with token refresh
        if (error.response?.status === 401 && !originalRequest._retry) {
          if (this.isRefreshing) {
            // Queue request while refresh is in progress
            return new Promise((resolve) => {
              this.refreshSubscribers.push((token: string) => {
                originalRequest.headers = {
                  ...originalRequest.headers,
                  Authorization: `Bearer ${token}`,
                };
                resolve(this.client(originalRequest));
              });
            });
          }

          originalRequest._retry = true;
          this.isRefreshing = true;

          try {
            const { accessToken } = await AuthService.refreshTokens();
            
            // Notify all waiting requests
            this.refreshSubscribers.forEach(callback => callback(accessToken));
            this.refreshSubscribers = [];

            // Retry original request
            originalRequest.headers = {
              ...originalRequest.headers,
              Authorization: `Bearer ${accessToken}`,
            };

            return this.client(originalRequest);
          } catch (refreshError) {
            // Refresh failed, redirect to login
            AuthService.logout();
            window.location.href = '/login';
            return Promise.reject(refreshError);
          } finally {
            this.isRefreshing = false;
          }
        }

        // Log error in development
        if (process.env.NODE_ENV === 'development') {
          console.error(`❌ ${error.config?.method?.toUpperCase()} ${error.config?.url}`, error.response?.data);
        }

        return Promise.reject(error);
      }
    );
  }

  // HTTP Methods
  async get<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.get(url, config);
    return response.data;
  }

  async post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.post(url, data, config);
    return response.data;
  }

  async put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.put(url, data, config);
    return response.data;
  }

  async patch<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.patch(url, data, config);
    return response.data;
  }

  async delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.delete(url, config);
    return response.data;
  }

  // File upload method
  async uploadFile<T = any>(url: string, file: File, onProgress?: (progress: number) => void): Promise<T> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await this.client.post(url, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(progress);
        }
      },
    });

    return response.data;
  }

  // Download file method
  async downloadFile(url: string, filename?: string): Promise<void> {
    const response = await this.client.get(url, {
      responseType: 'blob',
    });

    // Create blob link to download
    const blob = new Blob([response.data]);
    const link = document.createElement('a');
    link.href = window.URL.createObjectURL(blob);
    link.download = filename || 'download';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }
}

// Export singleton instance
export const apiClient = new APIClient();
export default apiClient;
```

## 📊 Advanced State Management Patterns

### Zustand Store with Persistence and Middleware

```typescript
// store/authStore.ts - Advanced Implementation
import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { subscribeWithSelector } from 'zustand/middleware';
import { AuthUser } from '../types/auth.types';
import { AuthService } from '../services/auth.service';

interface AuthState {
  // State
  user: AuthUser | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  login: (identifier: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  register: (userData: any) => Promise<void>;
  updateUser: (userData: Partial<AuthUser>) => void;
  clearError: () => void;
  setLoading: (loading: boolean) => void;
  
  // Computed getters
  hasRole: (role: string) => boolean;
  hasAnyRole: (roles: string[]) => boolean;
  isAdmin: () => boolean;
  isTeacher: () => boolean;
  isStudent: () => boolean;
}

export const useAuthStore = create<AuthState>()(
  subscribeWithSelector(
    persist(
      (set, get) => ({
        // Initial state
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: null,

        // Actions
        login: async (identifier: string, password: string) => {
          set({ isLoading: true, error: null });
          
          try {
            const response = await AuthService.login(identifier, password);
            
            set({
              user: response.user,
              isAuthenticated: true,
              isLoading: false,
              error: null,
            });
            
            // Redirect based on role
            const redirectPath = response.user.role === 'admin' ? '/admin' :
                               response.user.role === 'teacher' ? '/teacher' : '/student';
            window.location.href = redirectPath;
          } catch (error: any) {
            set({
              isLoading: false,
              error: error.response?.data?.error?.message || 'Login failed',
            });
            throw error;
          }
        },

        logout: async () => {
          set({ isLoading: true });
          
          try {
            await AuthService.logout();
          } catch (error) {
            console.warn('Logout error:', error);
          } finally {
            set({
              user: null,
              isAuthenticated: false,
              isLoading: false,
              error: null,
            });
            
            window.location.href = '/login';
          }
        },

        register: async (userData: any) => {
          set({ isLoading: true, error: null });
          
          try {
            await AuthService.register(userData);
            set({ isLoading: false });
          } catch (error: any) {
            set({
              isLoading: false,
              error: error.response?.data?.error?.message || 'Registration failed',
            });
            throw error;
          }
        },

        updateUser: (userData: Partial<AuthUser>) => {
          set((state) => ({
            user: state.user ? { ...state.user, ...userData } : null,
          }));
        },

        clearError: () => set({ error: null }),
        setLoading: (loading: boolean) => set({ isLoading: loading }),

        // Computed getters
        hasRole: (role: string) => {
          const { user } = get();
          return user?.role === role;
        },

        hasAnyRole: (roles: string[]) => {
          const { user } = get();
          return user ? roles.includes(user.role) : false;
        },

        isAdmin: () => get().hasRole('admin'),
        isTeacher: () => get().hasRole('teacher'),
        isStudent: () => get().hasRole('student'),
      }),
      {
        name: 'auth-storage',
        storage: createJSONStorage(() => localStorage),
        partialize: (state) => ({
          user: state.user,
          isAuthenticated: state.isAuthenticated,
        }),
      }
    )
  )
);

// Auth store selectors for performance optimization
export const useAuthUser = () => useAuthStore(state => state.user);
export const useIsAuthenticated = () => useAuthStore(state => state.isAuthenticated);
export const useAuthLoading = () => useAuthStore(state => state.isLoading);
export const useAuthError = () => useAuthStore(state => state.error);
export const useAuthActions = () => useAuthStore(state => ({
  login: state.login,
  logout: state.logout,
  register: state.register,
  updateUser: state.updateUser,
  clearError: state.clearError,
}));

// Subscribe to auth changes
useAuthStore.subscribe(
  (state) => state.isAuthenticated,
  (isAuthenticated) => {
    console.log('Auth status changed:', isAuthenticated);
  }
);
```

### TanStack Query Setup with Advanced Caching

```typescript
// hooks/queryClient.ts
import { QueryClient, DefaultOptions } from '@tanstack/react-query';
import { toast } from 'react-hot-toast';

const queryConfig: DefaultOptions = {
  queries: {
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes (formerly cacheTime)
    retry: (failureCount, error: any) => {
      // Don't retry on 4xx errors
      if (error?.response?.status >= 400 && error?.response?.status < 500) {
        return false;
      }
      return failureCount < 3;
    },
    refetchOnWindowFocus: false,
    refetchOnReconnect: 'always',
  },
  mutations: {
    retry: 1,
    onError: (error: any) => {
      const message = error?.response?.data?.error?.message || 'An error occurred';
      toast.error(message);
    },
  },
};

export const queryClient = new QueryClient({
  defaultOptions: queryConfig,
});

// Query keys factory for consistency
export const queryKeys = {
  // Auth
  profile: () => ['profile'] as const,
  
  // Users
  users: (filters?: any) => ['users', filters] as const,
  user: (id: string) => ['user', id] as const,
  
  // Students
  students: (filters?: any) => ['students', filters] as const,
  student: (id: string) => ['student', id] as const,
  
  // Teachers
  teachers: (filters?: any) => ['teachers', filters] as const,
  teacher: (id: string) => ['teacher', id] as const,
  
  // Profile data
  workExperience: () => ['work-experience'] as const,
  educationGoals: () => ['education-goals'] as const,
  
  // Search
  search: (query: string, type?: string) => ['search', query, type] as const,
  
  // Notifications
  notifications: (filters?: any) => ['notifications', filters] as const,
  
  // Dictionaries
  faculties: () => ['faculties'] as const,
  directions: (facultyId?: string) => ['directions', facultyId] as const,
  companies: () => ['companies'] as const,
  
  // Admin
  activityLogs: (filters?: any) => ['activity-logs', filters] as const,
} as const;
```

### Custom React Hooks for Data Fetching

```typescript
// hooks/useProfile.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { ProfileService } from '../services/profile.service';
import { queryKeys } from './queryClient';
import { useAuthStore } from '../store/authStore';
import { toast } from 'react-hot-toast';

export const useProfile = () => {
  const isAuthenticated = useAuthStore(state => state.isAuthenticated);
  
  return useQuery({
    queryKey: queryKeys.profile(),
    queryFn: ProfileService.getProfile,
    enabled: isAuthenticated,
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
};

export const useUpdateProfile = () => {
  const queryClient = useQueryClient();
  const updateUser = useAuthStore(state => state.updateUser);
  
  return useMutation({
    mutationFn: ProfileService.updateProfile,
    onSuccess: (data) => {
      // Update cache
      queryClient.setQueryData(queryKeys.profile(), data);
      
      // Update auth store
      updateUser(data);
      
      toast.success('Profile updated successfully');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error?.message || 'Failed to update profile');
    },
  });
};

export const useWorkExperience = () => {
  return useQuery({
    queryKey: queryKeys.workExperience(),
    queryFn: ProfileService.getWorkExperience,
  });
};

export const useAddWorkExperience = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ProfileService.addWorkExperience,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.workExperience() });
      toast.success('Work experience added successfully');
    },
  });
};

export const useEducationGoals = () => {
  return useQuery({
    queryKey: queryKeys.educationGoals(),
    queryFn: ProfileService.getEducationGoals,
  });
};

export const useAddEducationGoal = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ProfileService.addEducationGoal,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.educationGoals() });
      toast.success('Education goal added successfully');
    },
  });
};
```

```typescript
// hooks/useStudents.ts
import { useQuery, useMutation, useQueryClient, useInfiniteQuery } from '@tanstack/react-query';
import { StudentService } from '../services/student.service';
import { queryKeys } from './queryClient';
import { toast } from 'react-hot-toast';

interface StudentFilters {
  page?: number;
  limit?: number;
  search?: string;
  faculty?: string;
  direction?: string;
  admissionYear?: number;
  graduationYear?: number;
  verified?: boolean;
}

export const useStudents = (filters: StudentFilters = {}) => {
  return useQuery({
    queryKey: queryKeys.students(filters),
    queryFn: () => StudentService.getStudents(filters),
    keepPreviousData: true, // Keep previous data while fetching new
  });
};

export const useStudentsInfinite = (filters: Omit<StudentFilters, 'page'> = {}) => {
  return useInfiniteQuery({
    queryKey: ['students-infinite', filters],
    queryFn: ({ pageParam = 1 }) => 
      StudentService.getStudents({ ...filters, page: pageParam }),
    getNextPageParam: (lastPage, allPages) => {
      const nextPage = allPages.length + 1;
      return lastPage.pagination?.hasMore ? nextPage : undefined;
    },
    initialPageParam: 1,
  });
};

export const useStudent = (id: string) => {
  return useQuery({
    queryKey: queryKeys.student(id),
    queryFn: () => StudentService.getStudentById(id),
    enabled: !!id,
  });
};

export const useUpdateStudent = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: any }) =>
      StudentService.updateStudent(id, data),
    onSuccess: (updatedStudent, { id }) => {
      // Update individual student cache
      queryClient.setQueryData(queryKeys.student(id), updatedStudent);
      
      // Invalidate students list
      queryClient.invalidateQueries({ queryKey: ['students'] });
      
      toast.success('Student updated successfully');
    },
  });
};
```

```typescript
// hooks/useSearch.ts
import { useQuery } from '@tanstack/react-query';
import { useDebounce } from './useDebounce';
import { SearchService } from '../services/search.service';
import { queryKeys } from './queryClient';

export const useGlobalSearch = (query: string, type: string = 'all') => {
  const debouncedQuery = useDebounce(query, 300);
  
  return useQuery({
    queryKey: queryKeys.search(debouncedQuery, type),
    queryFn: () => SearchService.globalSearch(debouncedQuery, type),
    enabled: debouncedQuery.length > 2,
    staleTime: 2 * 60 * 1000, // 2 minutes for search results
  });
};

export const useStudentSearch = (filters: any) => {
  const debouncedFilters = useDebounce(filters, 300);
  
  return useQuery({
    queryKey: ['search-students', debouncedFilters],
    queryFn: () => SearchService.searchStudents(debouncedFilters),
    enabled: Object.keys(debouncedFilters).length > 0,
  });
};
```

## 🎨 Advanced Component Patterns

### Higher-Order Component for Role-Based Access

```typescript
// components/hoc/withRoleAccess.tsx
import React from 'react';
import { useAuthStore } from '../../store/authStore';

interface WithRoleAccessProps {
  allowedRoles?: string[];
  fallback?: React.ComponentType;
  requireAuth?: boolean;
}

export function withRoleAccess<P extends object>(
  WrappedComponent: React.ComponentType<P>,
  options: WithRoleAccessProps = {}
) {
  const {
    allowedRoles = [],
    fallback: FallbackComponent,
    requireAuth = true,
  } = options;

  return function WithRoleAccessComponent(props: P) {
    const { user, isAuthenticated, hasAnyRole } = useAuthStore();

    // Check authentication
    if (requireAuth && !isAuthenticated) {
      return FallbackComponent ? (
        <FallbackComponent />
      ) : (
        <div className="text-center py-8">
          <p className="text-gray-600">Please log in to access this content.</p>
        </div>
      );
    }

    // Check role permissions
    if (allowedRoles.length > 0 && user && !hasAnyRole(allowedRoles)) {
      return FallbackComponent ? (
        <FallbackComponent />
      ) : (
        <div className="text-center py-8">
          <p className="text-gray-600">You don't have permission to access this content.</p>
        </div>
      );
    }

    return <WrappedComponent {...props} />;
  };
}

// Usage example
const AdminOnlyComponent = withRoleAccess(SomeComponent, {
  allowedRoles: ['admin'],
  fallback: UnauthorizedComponent,
});
```

### Advanced Form Component with Validation

```typescript
// components/forms/ProfileForm.tsx
import React from 'react';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useProfile, useUpdateProfile } from '../../hooks/useProfile';
import { useFaculties, useDirections } from '../../hooks/useDictionaries';
import { LoadingSpinner } from '../ui/LoadingSpinner';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import { Select } from '../ui/Select';
import { TextArea } from '../ui/TextArea';

// Validation schema
const profileSchema = z.object({
  firstName: z.string().min(2, 'First name must be at least 2 characters'),
  lastName: z.string().min(2, 'Last name must be at least 2 characters'),
  middleName: z.string().optional(),
  email: z.string().email('Invalid email address'),
  phone: z.string().regex(/^\+998\d{9}$/, 'Phone must be in format +998XXXXXXXXX'),
  faculty: z.string().min(1, 'Faculty is required'),
  direction: z.string().min(1, 'Direction is required'),
  bio: z.string().max(500, 'Bio must be less than 500 characters').optional(),
  birthDate: z.string().optional(),
  address: z.string().optional(),
  website: z.string().url('Invalid URL').optional().or(z.literal('')),
});

type ProfileFormData = z.infer<typeof profileSchema>;

export const ProfileForm: React.FC = () => {
  const { data: profile, isLoading: profileLoading } = useProfile();
  const { data: faculties } = useFaculties();
  const updateProfileMutation = useUpdateProfile();

  const {
    control,
    handleSubmit,
    watch,
    formState: { errors, isDirty, isValid },
    reset,
  } = useForm<ProfileFormData>({
    resolver: zodResolver(profileSchema),
    mode: 'onChange',
    defaultValues: {
      firstName: '',
      lastName: '',
      middleName: '',
      email: '',
      phone: '',
      faculty: '',
      direction: '',
      bio: '',
      birthDate: '',
      address: '',
      website: '',
    },
  });

  const selectedFaculty = watch('faculty');
  const { data: directions } = useDirections(selectedFaculty);

  // Reset form when profile data loads
  React.useEffect(() => {
    if (profile) {
      reset({
        firstName: profile.firstName || '',
        lastName: profile.lastName || '',
        middleName: profile.middleName || '',
        email: profile.email || '',
        phone: profile.phone || '',
        faculty: profile.faculty || '',
        direction: profile.direction || '',
        bio: profile.bio || '',
        birthDate: profile.birthDate || '',
        address: profile.address || '',
        website: profile.website || '',
      });
    }
  }, [profile, reset]);

  const onSubmit = async (data: ProfileFormData) => {
    try {
      await updateProfileMutation.mutateAsync(data);
      reset(data); // Reset form with new data to clear dirty state
    } catch (error) {
      console.error('Failed to update profile:', error);
    }
  };

  if (profileLoading) {
    return <LoadingSpinner />;
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Profile Information</h2>
        
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          {/* Personal Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <Controller
              name="firstName"
              control={control}
              render={({ field }) => (
                <Input
                  {...field}
                  label="First Name *"
                  error={errors.firstName?.message}
                />
              )}
            />

            <Controller
              name="lastName"
              control={control}
              render={({ field }) => (
                <Input
                  {...field}
                  label="Last Name *"
                  error={errors.lastName?.message}
                />
              )}
            />

            <Controller
              name="middleName"
              control={control}
              render={({ field }) => (
                <Input
                  {...field}
                  label="Middle Name"
                  error={errors.middleName?.message}
                />
              )}
            />
          </div>

          {/* Contact Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Controller
              name="email"
              control={control}
              render={({ field }) => (
                <Input
                  {...field}
                  type="email"
                  label="Email Address *"
                  error={errors.email?.message}
                  disabled
                />
              )}
            />

            <Controller
              name="phone"
              control={control}
              render={({ field }) => (
                <Input
                  {...field}
                  type="tel"
                  label="Phone Number *"
                  placeholder="+998XXXXXXXXX"
                  error={errors.phone?.message}
                />
              )}
            />
          </div>

          {/* Academic Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Controller
              name="faculty"
              control={control}
              render={({ field }) => (
                <Select
                  {...field}
                  label="Faculty *"
                  error={errors.faculty?.message}
                  options={faculties?.map(f => ({ value: f.id, label: f.name })) || []}
                />
              )}
            />

            <Controller
              name="direction"
              control={control}
              render={({ field }) => (
                <Select
                  {...field}
                  label="Direction *"
                  error={errors.direction?.message}
                  options={directions?.map(d => ({ value: d.id, label: d.name })) || []}
                  disabled={!selectedFaculty}
                />
              )}
            />
          </div>

          {/* Additional Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Controller
              name="birthDate"
              control={control}
              render={({ field }) => (
                <Input
                  {...field}
                  type="date"
                  label="Birth Date"
                  error={errors.birthDate?.message}
                />
              )}
            />

            <Controller
              name="website"
              control={control}
              render={({ field }) => (
                <Input
                  {...field}
                  type="url"
                  label="Website"
                  placeholder="https://example.com"
                  error={errors.website?.message}
                />
              )}
            />
          </div>

          <Controller
            name="address"
            control={control}
            render={({ field }) => (
              <Input
                {...field}
                label="Address"
                error={errors.address?.message}
              />
            )}
          />

          <Controller
            name="bio"
            control={control}
            render={({ field }) => (
              <TextArea
                {...field}
                label="Bio"
                placeholder="Tell us about yourself..."
                rows={4}
                maxLength={500}
                error={errors.bio?.message}
              />
            )}
          />

          {/* Form Actions */}
          <div className="flex justify-end space-x-3 pt-6 border-t">
            <Button
              type="button"
              variant="outline"
              onClick={() => reset()}
              disabled={!isDirty}
            >
              Reset
            </Button>
            
            <Button
              type="submit"
              loading={updateProfileMutation.isPending}
              disabled={!isDirty || !isValid}
            >
              Save Changes
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};
```

## 🔍 Advanced Search Implementation

### Comprehensive Search Component

```typescript
// components/search/AdvancedSearchForm.tsx
import React, { useState, useMemo } from 'react';
import { useForm, Controller } from 'react-hook-form';
import { useGlobalSearch, useStudentSearch } from '../../hooks/useSearch';
import { useFaculties, useDirections, useCompanies } from '../../hooks/useDictionaries';
import { SearchResults } from './SearchResults';
import { SearchFilters } from './SearchFilters';
import { useDebounce } from '../../hooks/useDebounce';

interface SearchFormData {
  query: string;
  type: 'all' | 'students' | 'teachers' | 'companies';
  faculty?: string;
  direction?: string;
  admissionYear?: number;
  graduationYear?: number;
  company?: string;
  verified?: boolean;
}

export const AdvancedSearchForm: React.FC = () => {
  const [showAdvanced, setShowAdvanced] = useState(false);
  
  const { control, watch, setValue } = useForm<SearchFormData>({
    defaultValues: {
      query: '',
      type: 'all',
      faculty: '',
      direction: '',
      admissionYear: undefined,
      graduationYear: undefined,
      company: '',
      verified: undefined,
    },
  });

  const formData = watch();
  const debouncedQuery = useDebounce(formData.query, 300);
  const debouncedFilters = useDebounce(formData, 300);

  // Data fetching
  const { data: faculties } = useFaculties();
  const { data: directions } = useDirections(formData.faculty);
  const { data: companies } = useCompanies();

  // Search queries
  const globalSearchQuery = useGlobalSearch(
    debouncedQuery,
    formData.type,
    {
      enabled: debouncedQuery.length > 2,
    }
  );

  const studentSearchQuery = useStudentSearch(
    debouncedFilters,
    {
      enabled: formData.type === 'students' && debouncedQuery.length > 2,
    }
  );

  // Determine which results to show
  const searchResults = useMemo(() => {
    if (formData.type === 'students' && studentSearchQuery.data) {
      return studentSearchQuery.data;
    }
    return globalSearchQuery.data;
  }, [formData.type, globalSearchQuery.data, studentSearchQuery.data]);

  const isLoading = globalSearchQuery.isLoading || studentSearchQuery.isLoading;

  // Generate year options
  const currentYear = new Date().getFullYear();
  const yearOptions = Array.from({ length: 20 }, (_, i) => {
    const year = currentYear - i;
    return { value: year, label: year.toString() };
  });

  return (
    <div className="space-y-6">
      {/* Main Search Input */}
      <div className="relative">
        <Controller
          name="query"
          control={control}
          render={({ field }) => (
            <div className="relative">
              <input
                {...field}
                type="text"
                placeholder="Search students, teachers, companies..."
                className="w-full pl-12 pr-4 py-4 text-lg border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent shadow-sm"
              />
              <div className="absolute inset-y-0 left-0 pl-4 flex items-center">
                <SearchIcon className="h-6 w-6 text-gray-400" />
              </div>
              {isLoading && (
                <div className="absolute inset-y-0 right-0 pr-4 flex items-center">
                  <LoadingSpinner size="sm" />
                </div>
              )}
            </div>
          )}
        />
      </div>

      {/* Search Type Tabs */}
      <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg">
        {[
          { value: 'all', label: 'All' },
          { value: 'students', label: 'Students' },
          { value: 'teachers', label: 'Teachers' },
          { value: 'companies', label: 'Companies' },
        ].map((option) => (
          <button
            key={option.value}
            onClick={() => setValue('type', option.value as any)}
            className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
              formData.type === option.value
                ? 'bg-white text-blue-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            {option.label}
          </button>
        ))}
      </div>

      {/* Advanced Filters Toggle */}
      <div className="flex justify-between items-center">
        <button
          onClick={() => setShowAdvanced(!showAdvanced)}
          className="flex items-center space-x-2 text-blue-600 hover:text-blue-700"
        >
          <FilterIcon className="h-4 w-4" />
          <span>Advanced Filters</span>
          <ChevronDownIcon 
            className={`h-4 w-4 transition-transform ${showAdvanced ? 'rotate-180' : ''}`}
          />
        </button>

        {/* Results Count */}
        {searchResults && debouncedQuery.length > 2 && (
          <span className="text-sm text-gray-600">
            {searchResults.length} results found
          </span>
        )}
      </div>

      {/* Advanced Filters */}
      {showAdvanced && (
        <div className="bg-gray-50 rounded-lg p-6 space-y-4">
          <h3 className="text-lg font-medium text-gray-900">Advanced Filters</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {/* Faculty Filter */}
            <Controller
              name="faculty"
              control={control}
              render={({ field }) => (
                <Select
                  {...field}
                  label="Faculty"
                  placeholder="Select faculty"
                  options={[
                    { value: '', label: 'All Faculties' },
                    ...(faculties?.map(f => ({ value: f.id, label: f.name })) || [])
                  ]}
                />
              )}
            />

            {/* Direction Filter */}
            <Controller
              name="direction"
              control={control}
              render={({ field }) => (
                <Select
                  {...field}
                  label="Direction"
                  placeholder="Select direction"
                  disabled={!formData.faculty}
                  options={[
                    { value: '', label: 'All Directions' },
                    ...(directions?.map(d => ({ value: d.id, label: d.name })) || [])
                  ]}
                />
              )}
            />

            {/* Admission Year */}
            {formData.type === 'students' && (
              <Controller
                name="admissionYear"
                control={control}
                render={({ field }) => (
                  <Select
                    {...field}
                    value={field.value?.toString() || ''}
                    onChange={(value) => field.onChange(value ? parseInt(value) : undefined)}
                    label="Admission Year"
                    placeholder="Select year"
                    options={[
                      { value: '', label: 'All Years' },
                      ...yearOptions
                    ]}
                  />
                )}
              />
            )}

            {/* Graduation Year */}
            {formData.type === 'students' && (
              <Controller
                name="graduationYear"
                control={control}
                render={({ field }) => (
                  <Select
                    {...field}
                    value={field.value?.toString() || ''}
                    onChange={(value) => field.onChange(value ? parseInt(value) : undefined)}
                    label="Graduation Year"
                    placeholder="Select year"
                    options={[
                      { value: '', label: 'All Years' },
                      ...yearOptions
                    ]}
                  />
                )}
              />
            )}

            {/* Company Filter */}
            {formData.type === 'students' && (
              <Controller
                name="company"
                control={control}
                render={({ field }) => (
                  <Select
                    {...field}
                    label="Company"
                    placeholder="Select company"
                    options={[
                      { value: '', label: 'All Companies' },
                      ...(companies?.map(c => ({ value: c.id, label: c.name })) || [])
                    ]}
                  />
                )}
              />
            )}

            {/* Verification Status */}
            <Controller
              name="verified"
              control={control}
              render={({ field }) => (
                <Select
                  {...field}
                  value={field.value?.toString() || ''}
                  onChange={(value) => {
                    if (value === '') field.onChange(undefined);
                    else field.onChange(value === 'true');
                  }}
                  label="Verification Status"
                  placeholder="Select status"
                  options={[
                    { value: '', label: 'All Statuses' },
                    { value: 'true', label: 'Verified' },
                    { value: 'false', label: 'Unverified' },
                  ]}
                />
              )}
            />
          </div>

          {/* Clear Filters */}
          <div className="pt-4 border-t border-gray-200">
            <button
              onClick={() => {
                setValue('faculty', '');
                setValue('direction', '');
                setValue('admissionYear', undefined);
                setValue('graduationYear', undefined);
                setValue('company', '');
                setValue('verified', undefined);
              }}
              className="text-sm text-gray-600 hover:text-gray-900"
            >
              Clear all filters
            </button>
          </div>
        </div>
      )}

      {/* Search Results */}
      <SearchResults
        results={searchResults}
        loading={isLoading}
        query={debouncedQuery}
        type={formData.type}
      />
    </div>
  );
};
```

This comprehensive technical specification provides production-ready patterns for integrating with the Turin Grad Hub backend API. The implementation covers advanced authentication, state management, data fetching, and component patterns that can be directly used in a frontend application.