import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { TooltipProvider } from '@/components/ui/tooltip'
import { Toaster } from '@/components/ui/sonner'
import { AuthProvider } from '@/contexts/AuthContext'
import { ThemeProvider } from '@/contexts/ThemeContext'
import ProtectedRoute from '@/components/ProtectedRoute'
import Landing from './pages/Landing'
import About from './pages/About'
import UseCases from './pages/UseCases'
import Pricing from './pages/Pricing'
import ApiDocs from './pages/ApiDocs'
import Contact from './pages/Contact'
import SignIn from './pages/auth/SignIn'
import SignUp from './pages/auth/SignUp'
import VerifyEmail from './pages/auth/VerifyEmail'
import VerifyEmailNotice from './pages/auth/VerifyEmailNotice'
import GoogleCallback from './pages/auth/GoogleCallback'
import Index from './pages/Index'
import CodeAnalysis from './pages/CodeAnalysis'
import DecisionEngine from './pages/decision-engine/DecisionEngine'
import DecisionResults from './pages/decision-engine/DecisionResults'
import HardwareStatus from './pages/HardwareStatus'
import ExecutionHistory from './pages/ExecutionHistory'
import MLModels from './pages/MLModels'
import CostManagement from './pages/CostManagement'
import Settings from './pages/Settings'
import AICodeConverter from './pages/AICodeConverter'
import CodeConversionResults from './pages/CodeConversionResults'
import NotFound from './pages/NotFound'
import QuantumASTPatternAnalyzer from './pages/QuantumASTPatternAnalyzer'
import Pipeline from './pages/Pipeline'

const queryClient = new QueryClient()

const App = () => (
  <ThemeProvider>
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <Toaster />
        <BrowserRouter>
          <AuthProvider>
            <Routes>
            {/* Public routes */}
            <Route path="/" element={<Landing />} />
            <Route path="/signin" element={<SignIn />} />
            <Route path="/signup" element={<SignUp />} />
            <Route path="/verify-email" element={<VerifyEmail />} />
            <Route path="/verify-email-notice" element={<VerifyEmailNotice />} />
            <Route path="/auth/google/callback" element={<GoogleCallback />} />
            <Route path="/about" element={<About />} />
            <Route path="/use-cases" element={<UseCases />} />
            <Route path="/pricing" element={<Pricing />} />
            <Route path="/docs" element={<ApiDocs />} />
            <Route path="/contact" element={<Contact />} />

            {/* Protected routes */}
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <Index />
                </ProtectedRoute>
              }
            />
            <Route
              path="/pipeline"
              element={
                <ProtectedRoute>
                  <Pipeline />
                </ProtectedRoute>
              }
            />
            <Route
              path="/analysis"
              element={
                <ProtectedRoute>
                  <CodeAnalysis />
                </ProtectedRoute>
              }
            />
            <Route
              path="/decision-engine"
              element={
                <ProtectedRoute>
                  <DecisionEngine />
                </ProtectedRoute>
              }
            />
            <Route
              path="/decision-results"
              element={
                <ProtectedRoute>
                  <DecisionResults />
                </ProtectedRoute>
              }
            />
            <Route
              path="/results"
              element={
                <ProtectedRoute>
                  <DecisionResults />
                </ProtectedRoute>
              }
            />
            <Route
              path="/hardware"
              element={
                <ProtectedRoute>
                  <HardwareStatus />
                </ProtectedRoute>
              }
            />
            <Route
              path="/history"
              element={
                <ProtectedRoute>
                  <ExecutionHistory />
                </ProtectedRoute>
              }
            />
            <Route
              path="/models"
              element={
                <ProtectedRoute>
                  <MLModels />
                </ProtectedRoute>
              }
            />
            <Route
              path="/costs"
              element={
                <ProtectedRoute>
                  <CostManagement />
                </ProtectedRoute>
              }
            />
            <Route
              path="/settings"
              element={
                <ProtectedRoute>
                  <Settings />
                </ProtectedRoute>
              }
            />
            <Route
              path="/ai-converter"
              element={
                <ProtectedRoute>
                  <AICodeConverter />
                </ProtectedRoute>
              }
            />
            <Route
              path="/conversion-results"
              element={
                <ProtectedRoute>
                  <CodeConversionResults />
                </ProtectedRoute>
              }
            />
            <Route
              path="/ast-pattern-analyzer"
              element={
                <ProtectedRoute>
                  <QuantumASTPatternAnalyzer />
                </ProtectedRoute>
              }
            />

            <Route path="*" element={<NotFound />} />
            </Routes>
          </AuthProvider>
        </BrowserRouter>
      </TooltipProvider>
    </QueryClientProvider>
  </ThemeProvider>
)

export default App
