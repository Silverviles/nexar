# Authentication System

## Overview
The authentication system includes:
- Landing page at `/`
- Sign in/Sign up pages at `/signin` and `/signup`
- Protected routes for dashboard and all app features
- Mock authentication with configurable credentials

## Mock User Credentials
```
Email: admin@mail.com
Password: admin123
```

## File Structure
```
frontend/src/
├── lib/
│   └── axios.ts                    # Axios instance with interceptors
├── config/
│   └── mock.ts                     # Mock user configuration
├── contexts/
│   └── AuthContext.tsx             # Auth context and provider
├── components/
│   ├── ProtectedRoute.tsx          # Route protection wrapper
│   └── layout/
│       └── Header.tsx              # Updated with logout functionality
├── pages/
│   ├── Landing.tsx                 # Public landing page
│   └── auth/
│       ├── SignIn.tsx              # Sign in page
│       └── SignUp.tsx              # Sign up page
└── App.tsx                         # Updated with routes and AuthProvider
```

## Features

### Axios Configuration (`lib/axios.ts`)
- Automatic auth token injection in requests
- Response interceptors for error handling
- 401 redirect to sign in
- Configurable base URL via environment variables

### Auth Context (`contexts/AuthContext.tsx`)
Provides:
- `user`: Current user object or null
- `isAuthenticated`: Boolean authentication status
- `isLoading`: Loading state during initialization
- `login(email, password)`: Login function
- `signup(email, password, name)`: Signup function
- `logout()`: Logout function

### Protected Routes
Wrap any route with `<ProtectedRoute>` to require authentication:
```tsx
<Route path="/dashboard" element={
  <ProtectedRoute>
    <Dashboard />
  </ProtectedRoute>
} />
```

## Usage

### Use Auth in Components
```tsx
import { useAuth } from '@/contexts/AuthContext';

function MyComponent() {
  const { user, isAuthenticated, logout } = useAuth();
  
  return (
    <div>
      {isAuthenticated && <p>Welcome, {user.name}!</p>}
      <button onClick={logout}>Logout</button>
    </div>
  );
}
```

### Making Authenticated API Calls
```tsx
import axiosInstance from '@/lib/axios';

// Token is automatically added to headers
const response = await axiosInstance.get('/endpoint');
```

## Flow
1. User visits `/` (Landing page)
2. User clicks "Sign In" or "Sign Up"
3. After authentication, redirected to `/dashboard`
4. All dashboard routes are protected
5. Unauthenticated access redirects to `/signin`
6. User can logout from header dropdown

## Environment Variables
Create `.env` file in frontend directory:
```
VITE_API_BASE_URL=http://localhost:3000/api
```

## Production Considerations
Currently using mock authentication. For production:
1. Replace mock auth in `AuthContext.tsx` with real API calls
2. Update `config/mock.ts` or remove it
3. Implement proper JWT token refresh
4. Add password validation and security features
5. Implement forgot password functionality
