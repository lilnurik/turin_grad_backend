# 🤖 AI Development Prompts for Turin Grad Hub Frontend

## 🎯 Master Prompt for AI Agents

**You are an expert frontend developer tasked with building a comprehensive, modern web application for the Turin Grad Hub - a graduate management system for Turin Polytechnic University of Tashkent (TTPU). You will create a production-ready frontend that seamlessly integrates with the existing backend API.**

### 📋 Project Context

**Backend API**: Fully functional Flask REST API with 40+ endpoints
**Documentation**: Available at `http://127.0.0.1:5000/api/docs/` (Swagger UI)
**Authentication**: JWT-based with role-based access control (Admin, Teacher, Student)
**Database**: SQLAlchemy models with comprehensive user management

### 🎨 Primary Technology Stack
- **Frontend Framework**: React 18+ with TypeScript
- **Build Tool**: Vite for fast development and optimized builds
- **State Management**: Zustand + TanStack Query for client/server state
- **UI Library**: Tailwind CSS + Headless UI for modern, accessible components
- **HTTP Client**: Axios with comprehensive interceptors
- **Form Handling**: React Hook Form with validation
- **Routing**: React Router v6 with protected routes
- **Testing**: Jest + React Testing Library + MSW

---

## 🚀 Phase 1: Project Setup & Architecture

### Prompt 1: Initialize Project Structure

```
Create a modern React TypeScript application using Vite with the following specifications:

1. Project name: "turin-grad-frontend"
2. Setup Tailwind CSS with custom configuration
3. Configure absolute imports using @ alias
4. Install and configure the following dependencies:
   - @tanstack/react-query for server state management
   - zustand for client state management
   - react-router-dom v6 for routing
   - react-hook-form for form handling
   - axios for HTTP requests
   - @headlessui/react for accessible UI components
   - lucide-react for icons
   - react-hot-toast for notifications

Create the following folder structure:
```
src/
├── components/
│   ├── common/
│   ├── forms/
│   ├── layout/
│   └── ui/
├── pages/
│   ├── auth/
│   ├── admin/
│   ├── student/
│   ├── teacher/
│   └── profile/
├── services/
├── hooks/
├── store/
├── types/
├── utils/
└── constants/
```

Also create TypeScript interfaces for the main entities based on the API documentation:
- User, Student, Teacher, Admin types
- API response types
- Authentication types
- Profile and work experience types
```

### Prompt 2: Setup API Client & Authentication

```
Create a robust API client setup with the following features:

1. **Base API Client** (`utils/apiClient.ts`):
   - Axios instance with base URL configuration
   - Request interceptors for adding JWT tokens
   - Response interceptors for token refresh logic
   - Error handling for common HTTP status codes
   - Request/response logging in development

2. **Authentication Store** (`store/authStore.ts`):
   - Zustand store with persistence
   - User state management
   - Token management (access & refresh)
   - Login/logout actions
   - Role-based permission checks

3. **Auth Service** (`services/auth.service.ts`):
   - Login function supporting email/phone/studentId
   - Registration with validation
   - Password reset flow
   - Token refresh mechanism
   - Logout with token cleanup

Base URL: `http://127.0.0.1:5000`
API Endpoints: Refer to `/api/auth/*` endpoints from the Swagger documentation

Include proper TypeScript interfaces and error handling for all authentication flows.
```

### Prompt 3: Create Protected Routing System

```
Implement a comprehensive routing system with role-based access control:

1. **Route Protection Component** (`components/auth/ProtectedRoute.tsx`):
   - Check authentication status
   - Verify user roles for route access
   - Redirect unauthenticated users to login
   - Handle unauthorized access attempts

2. **Main App Router** (`App.tsx`):
   - Public routes: /login, /register, /forgot-password
   - Protected student routes: /student/*
   - Protected teacher routes: /teacher/*
   - Protected admin routes: /admin/*
   - Shared routes: /profile, /search

3. **Navigation Components**:
   - Responsive sidebar navigation
   - Role-based menu items
   - User profile dropdown
   - Mobile hamburger menu

4. **Layout Components**:
   - AdminLayout for admin pages
   - TeacherLayout for teacher pages
   - StudentLayout for student pages
   - AuthLayout for authentication pages

Use React Router v6 with proper TypeScript typing and implement lazy loading for better performance.
```

---

## 🔐 Phase 2: Authentication & User Management

### Prompt 4: Build Authentication Pages

```
Create comprehensive authentication pages with modern UI/UX:

1. **Login Page** (`pages/auth/Login.tsx`):
   - Support login via email, phone, or student ID
   - Form validation with React Hook Form
   - Loading states and error handling
   - Remember me functionality
   - Links to registration and password reset

2. **Registration Page** (`pages/auth/Register.tsx`):
   - Student registration form
   - Multi-step form with validation
   - Real-time field validation
   - Faculty and direction selection
   - Terms and conditions acceptance

3. **Password Reset Flow**:
   - Forgot password page with email/phone input
   - Reset password page with token validation
   - Success confirmation pages

4. **Email Verification**:
   - Email verification page
   - Resend verification email functionality

Design Requirements:
- Mobile-responsive design
- Accessibility compliance (WCAG 2.1)
- Modern, professional appearance
- Loading states and micro-interactions
- Form validation with clear error messages

Use Tailwind CSS for styling and ensure all forms follow the university's professional aesthetic.
```

### Prompt 5: User Profile Management

```
Build comprehensive profile management features:

1. **Profile Page** (`pages/profile/Profile.tsx`):
   - View/edit personal information
   - Avatar upload with preview
   - Account settings management
   - Security settings (password change)

2. **Work Experience Management**:
   - Add/edit/delete work experiences
   - Timeline view of experiences
   - Company search and validation
   - Date range validation

3. **Education Goals Management**:
   - Create and manage education goals
   - Progress tracking
   - Goal categories and priorities

4. **Document Management**:
   - CV/Resume upload
   - Diploma upload (for students)
   - File preview and download
   - Document version management

API Integration:
- Use `/api/profile/*` endpoints
- Implement proper file upload handling
- Handle form validation and error states
- Provide real-time updates with optimistic UI

Include proper TypeScript interfaces and comprehensive error handling.
```

---

## 🏛️ Phase 3: Role-Specific Dashboards

### Prompt 6: Student Dashboard & Features

```
Create a comprehensive student portal with the following features:

1. **Student Dashboard** (`pages/student/StudentDashboard.tsx`):
   - Welcome header with user info
   - Statistics cards (profile completion, goals, experiences)
   - Recent activities timeline
   - Quick actions panel
   - Upcoming events/deadlines

2. **Student Directory** (`pages/student/StudentDirectory.tsx`):
   - Browse other students by faculty/direction
   - Advanced search and filtering
   - Student profile cards with contact info
   - Export contact lists

3. **Teacher Directory** (`pages/student/TeacherDirectory.tsx`):
   - Browse teachers by faculty
   - Teacher profile pages with bio and contact
   - Rate and review teachers (if applicable)

4. **Career Center** (`pages/student/CareerCenter.tsx`):
   - Job opportunities board
   - Career guidance resources
   - Industry connections
   - Alumni network access

Features to implement:
- Real-time data fetching with TanStack Query
- Infinite scrolling for large lists
- Search with debouncing
- Responsive grid layouts
- Loading skeletons
- Error boundaries

Use proper caching strategies and implement optimistic updates where appropriate.
```

### Prompt 7: Teacher Dashboard & Student Management

```
Build a comprehensive teacher portal for managing students:

1. **Teacher Dashboard** (`pages/teacher/TeacherDashboard.tsx`):
   - Overview of assigned students
   - Student performance analytics
   - Recent student activities
   - Communication center

2. **Student Management** (`pages/teacher/StudentManagement.tsx`):
   - List of assigned students with detailed profiles
   - Student progress tracking
   - Add notes and comments about students
   - Communication tools (messages, announcements)

3. **Reports & Analytics** (`pages/teacher/Reports.tsx`):
   - Generate student progress reports
   - Export data to Excel/PDF
   - Performance charts and graphs
   - Graduation tracking

4. **Communication Tools**:
   - Send notifications to students
   - Group messaging functionality
   - Announcement system
   - Email integration

API Integration:
- Use `/api/teachers/*` endpoints
- Implement data visualization with charts
- Handle large datasets with pagination
- Provide real-time updates for communications

Include comprehensive filtering, sorting, and search capabilities for student management.
```

### Prompt 8: Admin Dashboard & System Management

```
Create a powerful admin dashboard for system administration:

1. **Admin Dashboard** (`pages/admin/AdminDashboard.tsx`):
   - System overview with key metrics
   - User statistics and trends
   - Activity monitoring
   - System health indicators

2. **User Management** (`pages/admin/UserManagement.tsx`):
   - Create, read, update, delete users
   - Bulk user operations
   - User verification and approval
   - Role management and permissions
   - User activity logs

3. **System Analytics** (`pages/admin/Analytics.tsx`):
   - Interactive charts and graphs
   - Faculty-wise statistics
   - Geographical distribution
   - Employment statistics
   - Graduation trends

4. **Content Management**:
   - Manage faculties and directions
   - Company database management
   - System announcements
   - Configuration settings

5. **Data Management**:
   - Import/export users from Excel/CSV
   - Database backup and restore
   - Data migration tools
   - System maintenance tools

Technical Requirements:
- Implement data tables with sorting, filtering, pagination
- Use charts library (Chart.js or D3.js)
- Handle large datasets efficiently
- Implement real-time updates where needed
- Provide comprehensive search and filtering
- Include data validation and error handling

Make sure to implement proper role-based access control and audit logging.
```

---

## 🔍 Phase 4: Advanced Features

### Prompt 9: Global Search & Filtering System

```
Implement a powerful search system across the entire application:

1. **Global Search Component** (`components/search/GlobalSearch.tsx`):
   - Universal search bar in the header
   - Real-time search suggestions
   - Recent searches history
   - Quick filters and categories

2. **Advanced Search Page** (`pages/search/AdvancedSearch.tsx`):
   - Multi-criteria search forms
   - Search across users, students, teachers, companies
   - Advanced filtering options
   - Search results with pagination
   - Save and share search queries

3. **Search Results Components**:
   - Unified search results display
   - Different result card types for different entities
   - Relevance scoring and sorting
   - Export search results

4. **Filter Components**:
   - Faculty and direction filters
   - Date range filters
   - Custom filter builders
   - Filter persistence in URL

Technical Implementation:
- Use debounced search to reduce API calls
- Implement search result caching
- Handle empty states and error cases
- Provide search analytics and insights
- Use `/api/search/*` endpoints

Include proper TypeScript interfaces and comprehensive error handling.
```

### Prompt 10: Notifications & Communication System

```
Build a comprehensive notification and communication system:

1. **Notification Center** (`components/notifications/NotificationCenter.tsx`):
   - Real-time notification dropdown
   - Notification history and management
   - Mark as read/unread functionality
   - Notification categories and filtering

2. **Notification Management** (`pages/notifications/Notifications.tsx`):
   - List all notifications with pagination
   - Bulk operations (mark all as read, delete)
   - Notification preferences and settings
   - Push notification support (if applicable)

3. **Communication Tools**:
   - Send notifications to users (admin feature)
   - Broadcast announcements
   - Direct messaging between users
   - Email integration

4. **Real-time Features**:
   - WebSocket integration for live notifications
   - Toast notifications for immediate feedback
   - Badge counts on navigation items
   - Sound notifications (optional)

API Integration:
- Use `/api/notifications/*` endpoints
- Implement real-time updates with WebSockets or polling
- Handle notification permissions
- Provide offline notification storage

Include proper state management for notification counts and real-time updates.
```

---

## 🎨 Phase 5: UI/UX & Performance

### Prompt 11: Create Reusable UI Components

```
Build a comprehensive design system with reusable components:

1. **Base Components** (`components/ui/`):
   - Button with variants (primary, secondary, outline, ghost)
   - Input fields with validation states
   - Select dropdowns with search
   - Modal and dialog components
   - Loading states and skeletons
   - Data tables with sorting and pagination

2. **Form Components** (`components/forms/`):
   - FormField wrapper with validation
   - Multi-step form wizard
   - File upload with drag-and-drop
   - Date picker and time picker
   - Rich text editor (if needed)

3. **Layout Components** (`components/layout/`):
   - Responsive navigation sidebar
   - Header with user menu and search
   - Breadcrumb navigation
   - Page layouts with consistent spacing
   - Card layouts for content organization

4. **Data Display Components**:
   - Statistics cards with trend indicators
   - Charts and graphs (using Chart.js or similar)
   - Data tables with advanced features
   - Timeline components
   - Profile cards and avatars

Design Requirements:
- Consistent design tokens (colors, spacing, typography)
- Dark mode support
- Accessibility compliance (ARIA labels, keyboard navigation)
- Mobile-responsive design
- Smooth animations and transitions

Use Tailwind CSS for styling and ensure all components are properly typed with TypeScript.
```

### Prompt 12: Performance Optimization & PWA

```
Implement comprehensive performance optimizations and PWA features:

1. **Code Splitting & Lazy Loading**:
   - Implement route-based code splitting
   - Lazy load heavy components
   - Dynamic imports for large libraries
   - Bundle analysis and optimization

2. **Data Fetching Optimization**:
   - Implement proper caching strategies with TanStack Query
   - Prefetch critical data
   - Optimistic updates for better UX
   - Background sync for offline scenarios

3. **Image and Asset Optimization**:
   - Lazy load images with placeholders
   - Optimize image formats and sizes
   - Implement image compression
   - Use proper caching headers

4. **Progressive Web App Features**:
   - Service worker for caching
   - Offline functionality
   - App manifest for installation
   - Push notifications setup
   - Background sync for data

5. **Performance Monitoring**:
   - Web Vitals monitoring
   - Error boundary implementation
   - Performance analytics
   - Bundle size monitoring

Technical Implementation:
- Use React.memo and useMemo for component optimization
- Implement virtual scrolling for large lists
- Use debouncing for search and API calls
- Minimize re-renders with proper state management
- Implement proper error boundaries

Target Performance Metrics:
- First Contentful Paint < 1.5s
- Largest Contentful Paint < 2.5s
- Time to Interactive < 3s
- Lighthouse Score > 90
```

---

## 🧪 Phase 6: Testing & Quality Assurance

### Prompt 13: Comprehensive Testing Strategy

```
Implement a complete testing suite for the application:

1. **Unit Testing** with Jest and React Testing Library:
   - Test all utility functions
   - Component testing with proper mocking
   - Custom hooks testing
   - Service layer testing
   - Form validation testing

2. **Integration Testing**:
   - API integration tests with MSW (Mock Service Worker)
   - Authentication flow testing
   - Route protection testing
   - Form submission workflows
   - Error handling scenarios

3. **End-to-End Testing** with Playwright or Cypress:
   - Critical user journeys (login, profile update, search)
   - Role-based access testing
   - Cross-browser compatibility
   - Mobile responsiveness testing
   - Performance testing

4. **Accessibility Testing**:
   - Screen reader compatibility
   - Keyboard navigation testing
   - Color contrast validation
   - ARIA attributes verification

5. **Visual Regression Testing**:
   - Component snapshot testing
   - Visual diff testing for UI changes
   - Cross-browser visual testing

Testing Requirements:
- Achieve minimum 80% code coverage
- Test all critical user paths
- Mock all external API calls
- Test error scenarios and edge cases
- Implement proper test data factories

Create comprehensive test utilities and setup proper CI/CD integration for automated testing.
```

### Prompt 14: Error Handling & User Experience

```
Implement comprehensive error handling and user experience improvements:

1. **Error Boundaries**:
   - Global error boundary for unhandled errors
   - Route-specific error boundaries
   - Component-level error boundaries
   - Error reporting and logging

2. **API Error Handling**:
   - Centralized error handling in API client
   - User-friendly error messages
   - Retry mechanisms for failed requests
   - Offline error handling

3. **Form Validation & Error States**:
   - Real-time validation feedback
   - Server-side validation error display
   - Field-level error messages
   - Form submission error handling

4. **Loading States & Feedback**:
   - Skeleton loaders for better perceived performance
   - Progress indicators for long operations
   - Success confirmations with toast notifications
   - Optimistic UI updates

5. **Offline Support**:
   - Detect online/offline status
   - Cache critical data for offline access
   - Queue failed requests for retry
   - Offline user notifications

6. **User Experience Enhancements**:
   - Smooth page transitions
   - Keyboard shortcuts for power users
   - Contextual help and tooltips
   - Undo/redo functionality where applicable

Implementation Requirements:
- Use consistent error message patterns
- Implement proper loading states for all async operations
- Provide clear user feedback for all actions
- Handle edge cases gracefully
- Maintain application state during errors
```

---

## 🚀 Phase 7: Deployment & Production

### Prompt 15: Production Build & Deployment

```
Prepare the application for production deployment:

1. **Build Optimization**:
   - Configure Vite for production builds
   - Implement proper environment variable management
   - Optimize bundle size with tree shaking
   - Configure asset optimization (images, fonts, etc.)

2. **Environment Configuration**:
   - Set up environment-specific configurations
   - Configure API endpoints for different environments
   - Implement feature flags for gradual rollouts
   - Set up proper logging levels

3. **Deployment Setup**:
   - Create Docker configuration for containerization
   - Set up CI/CD pipeline (GitHub Actions or similar)
   - Configure deployment to cloud platforms
   - Implement health checks and monitoring

4. **Security Hardening**:
   - Implement Content Security Policy (CSP)
   - Configure HTTPS and security headers
   - Sanitize user inputs and outputs
   - Implement rate limiting for API calls

5. **Performance Monitoring**:
   - Set up application performance monitoring
   - Implement error tracking and reporting
   - Configure user analytics and usage tracking
   - Monitor Core Web Vitals

6. **Documentation & Maintenance**:
   - Create comprehensive README with setup instructions
   - Document API integration patterns
   - Provide troubleshooting guides
   - Set up automated dependency updates

Production Checklist:
- All environment variables configured
- Security headers implemented
- Performance metrics monitored
- Error tracking configured
- Backup and recovery procedures
- Load testing completed
```

---

## 💡 Development Best Practices & Guidelines

### Code Quality Standards
```typescript
// Example of well-structured component with proper TypeScript
interface UserProfileProps {
  user: User;
  onUpdate: (data: Partial<User>) => Promise<void>;
  isEditing: boolean;
}

export const UserProfile: React.FC<UserProfileProps> = ({
  user,
  onUpdate,
  isEditing
}) => {
  // Component implementation with proper error handling,
  // loading states, and accessibility features
};
```

### API Integration Patterns
```typescript
// Consistent API service pattern
export class UserService {
  static async getUser(id: string): Promise<User> {
    const response = await apiClient.get(`/api/users/${id}`);
    return response.data.data;
  }

  static async updateUser(id: string, data: Partial<User>): Promise<User> {
    const response = await apiClient.put(`/api/users/${id}`, data);
    return response.data.data;
  }
}
```

### State Management Patterns
```typescript
// Zustand store with proper TypeScript typing
interface UserStore {
  users: User[];
  loading: boolean;
  error: string | null;
  
  fetchUsers: () => Promise<void>;
  updateUser: (id: string, data: Partial<User>) => Promise<void>;
  clearError: () => void;
}
```

---

## 🎯 Success Criteria

### Technical Requirements
- ✅ **Performance**: Lighthouse score > 90
- ✅ **Accessibility**: WCAG 2.1 AA compliance
- ✅ **Security**: No XSS or CSRF vulnerabilities
- ✅ **Testing**: > 80% code coverage
- ✅ **Mobile**: Fully responsive design
- ✅ **Browser**: Support for modern browsers (Chrome, Firefox, Safari, Edge)

### Functional Requirements
- ✅ **Authentication**: Complete auth flow with all user types
- ✅ **Role Management**: Proper role-based access control
- ✅ **Data Management**: Full CRUD operations for all entities
- ✅ **Search**: Comprehensive search and filtering
- ✅ **Notifications**: Real-time notification system
- ✅ **Profile Management**: Complete profile and document management
- ✅ **Reporting**: Data export and analytics features

### User Experience Requirements
- ✅ **Intuitive Navigation**: Clear, consistent navigation patterns
- ✅ **Responsive Design**: Works seamlessly on all device sizes
- ✅ **Loading States**: Proper feedback for all async operations
- ✅ **Error Handling**: Clear, actionable error messages
- ✅ **Performance**: Fast, smooth user interactions
- ✅ **Accessibility**: Usable by users with disabilities

---

## 📚 Additional Resources & References

### API Documentation
- **Swagger UI**: `http://127.0.0.1:5000/api/docs/`
- **OpenAPI Spec**: `http://127.0.0.1:5000/apispec_1.json`
- **ReDoc**: `http://127.0.0.1:5000/api/redoc/`

### Key Endpoints Reference
- **Auth**: `/api/auth/login`, `/api/auth/register`, `/api/auth/logout`
- **Profile**: `/api/profile`, `/api/profile/work-experience`, `/api/profile/education-goals`
- **Admin**: `/api/admin/users`, `/api/admin/activity-logs`
- **Search**: `/api/search`, `/api/search/students`
- **Notifications**: `/api/notifications`
- **Dictionaries**: `/api/dictionaries/faculties`, `/api/dictionaries/companies`

### Technology Stack Documentation
- **React**: https://react.dev/
- **TypeScript**: https://www.typescriptlang.org/
- **Vite**: https://vitejs.dev/
- **TanStack Query**: https://tanstack.com/query/
- **Zustand**: https://zustand-demo.pmnd.rs/
- **Tailwind CSS**: https://tailwindcss.com/
- **React Router**: https://reactrouter.com/

---

**Remember**: Each phase should be completed thoroughly before moving to the next. Focus on creating a maintainable, scalable, and user-friendly application that serves the needs of all user roles effectively. Always refer to the backend API documentation for the most current endpoint specifications and data models.