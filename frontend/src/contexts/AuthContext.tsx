import React, { createContext, useContext, useState, useEffect } from 'react';
import { mockConfig } from '@/config/mock';

interface User {
  email: string;
  name: string;
  role: string;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string, name: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Check if user is already logged in on mount
  useEffect(() => {
    const storedUser = localStorage.getItem('user');
    const token = localStorage.getItem('authToken');
    
    if (storedUser && token) {
      setUser(JSON.parse(storedUser));
    }
    setIsLoading(false);
  }, []);

  const login = async (email: string, password: string) => {
    // Mock authentication - in production, this would be an API call
    if (email === mockConfig.mockUser.email && password === mockConfig.mockUser.password) {
      const userData = {
        email: mockConfig.mockUser.email,
        name: mockConfig.mockUser.name,
        role: mockConfig.mockUser.role,
      };
      
      // Generate mock token
      const mockToken = btoa(`${email}:${Date.now()}`);
      
      localStorage.setItem('authToken', mockToken);
      localStorage.setItem('user', JSON.stringify(userData));
      setUser(userData);
    } else {
      throw new Error('Invalid email or password');
    }
  };

  const signup = async (email: string, password: string, name: string) => {
    // Mock signup - in production, this would be an API call
    // For now, just accept any signup and log them in
    const userData = {
      email,
      name,
      role: 'user',
    };
    
    const mockToken = btoa(`${email}:${Date.now()}`);
    
    localStorage.setItem('authToken', mockToken);
    localStorage.setItem('user', JSON.stringify(userData));
    setUser(userData);
  };

  const logout = () => {
    localStorage.removeItem('authToken');
    localStorage.removeItem('user');
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        signup,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
