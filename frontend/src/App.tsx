import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "@/contexts/AuthContext";
import ProtectedRoute from "@/components/ProtectedRoute";
import Landing from "./pages/Landing";
import SignIn from "./pages/auth/SignIn";
import SignUp from "./pages/auth/SignUp";
import Index from "./pages/Index";
import CodeAnalysis from "./pages/CodeAnalysis";
import DecisionEngine from "./pages/decision-engine/DecisionEngine";
import DecisionResults from "./pages/decision-engine/DecisionResults";
import HardwareStatus from "./pages/HardwareStatus";
import ExecutionHistory from "./pages/ExecutionHistory";
import MLModels from "./pages/MLModels";
import CostManagement from "./pages/CostManagement";
import Settings from "./pages/Settings";
import AICodeConverter from "./pages/AICodeConverter";
import CodeConversionResults from "./pages/CodeConversionResults";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <AuthProvider>
          <Routes>
            {/* Public routes */}
            <Route path="/" element={<Landing />} />
            <Route path="/signin" element={<SignIn />} />
            <Route path="/signup" element={<SignUp />} />
            
            {/* Protected routes */}
            <Route path="/dashboard" element={
              <ProtectedRoute>
                <Index />
              </ProtectedRoute>
            } />
            <Route path="/analysis" element={
              <ProtectedRoute>
                <CodeAnalysis />
              </ProtectedRoute>
            } />
            <Route path="/decision-engine" element={
              <ProtectedRoute>
                <DecisionEngine />
              </ProtectedRoute>
            } />
            <Route path="/decision-results" element={
              <ProtectedRoute>
                <DecisionResults />
              </ProtectedRoute>
            } />
            <Route path="/results" element={
              <ProtectedRoute>
                <DecisionResults />
              </ProtectedRoute>
            } />
            <Route path="/hardware" element={
              <ProtectedRoute>
                <HardwareStatus />
              </ProtectedRoute>
            } />
            <Route path="/history" element={
              <ProtectedRoute>
                <ExecutionHistory />
              </ProtectedRoute>
            } />
            <Route path="/models" element={
              <ProtectedRoute>
                <MLModels />
              </ProtectedRoute>
            } />
            <Route path="/costs" element={
              <ProtectedRoute>
                <CostManagement />
              </ProtectedRoute>
            } />
            <Route path="/settings" element={
              <ProtectedRoute>
                <Settings />
              </ProtectedRoute>
            } />
            <Route path="/ai-converter" element={
              <ProtectedRoute>
                <AICodeConverter />
              </ProtectedRoute>
            } />
            <Route path="/conversion-results" element={
              <ProtectedRoute>
                <CodeConversionResults />
              </ProtectedRoute>
            } />
            
            <Route path="*" element={<NotFound />} />
          </Routes>
        </AuthProvider>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
