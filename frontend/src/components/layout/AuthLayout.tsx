import React from 'react';
import { Link } from 'react-router-dom';
import { Atom } from 'lucide-react';

interface AuthLayoutProps {
  children: React.ReactNode;
  title: string;
  description: string;
}

const AuthLayout: React.FC<AuthLayoutProps> = ({ children, title, description }) => {
  return (
    <div className="min-h-screen flex">
      {/* Left Side - Branding & Image */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 relative overflow-hidden">
        {/* Background Image */}
        <div className="absolute inset-0">
          <img 
            src="/auth/quantum_bg.jpg" 
            alt="Quantum Background" 
            className="w-full h-full object-cover opacity-40"
          />
        </div>
        
        {/* Overlay gradients */}
        <div className="absolute inset-0 bg-gradient-to-br from-slate-900/80 via-slate-800/70 to-slate-900/90" />
        <div className="absolute inset-0 bg-gradient-to-t from-slate-900 via-transparent to-transparent" />
        
        {/* Quantum glow effects */}
        <div className="absolute top-20 left-20 w-72 h-72 bg-primary/20 rounded-full blur-[100px] animate-pulse" />
        <div className="absolute bottom-20 right-20 w-96 h-96 bg-quantum/10 rounded-full blur-[120px] animate-pulse delay-1000" />
        
        {/* Content */}
        <div className="relative z-10 flex flex-col justify-between p-12 text-white">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-3 group">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary/20 backdrop-blur-sm border border-primary/30 glow-quantum group-hover:scale-110 transition-transform">
              <Atom className="h-7 w-7 text-quantum" />
            </div>
            <div>
              <h1 className="font-mono text-2xl font-bold">Nexar</h1>
              <p className="text-sm text-slate-400">Intelligent Quantum-Classical Workload Orchestration Platform</p>
            </div>
          </Link>

          {/* Center Content */}
          <div className="space-y-6">
            <div className="space-y-4">
              <div className="inline-block px-4 py-2 rounded-full bg-primary/10 border border-primary/20 text-sm font-medium">
                AI-Powered Intelligence
              </div>
              <h2 className="text-5xl font-bold leading-tight">
                Optimize Your Code
                <br />
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-quantum">
                  Execution
                </span>
              </h2>
              <p className="text-lg text-slate-300 max-w-md">
                Make intelligent decisions with our advanced AI engine. Analyze, decide, and execute with confidence.
              </p>
            </div>

            {/* Feature Pills */}
            <div className="flex flex-wrap gap-3">
              {['Real-time Analytics', 'Cost Optimization', 'ML Models', 'Hardware Abstraction'].map((feature) => (
                <div 
                  key={feature}
                  className="px-4 py-2 rounded-lg bg-white/5 backdrop-blur-sm border border-white/10 text-xs"
                >
                  {feature}
                </div>
              ))}
            </div>
          </div>

          {/* Footer */}
          <div className="text-sm text-slate-400">
            <p>&copy; 2025 Nexar. All rights reserved.</p>
          </div>
        </div>
      </div>

      {/* Right Side - Form */}
      <div className="flex-1 flex items-center justify-center p-8 bg-background">
        <div className="w-full max-w-md space-y-8">
          {/* Mobile Logo */}
          <div className="lg:hidden text-center">
            <Link to="/" className="inline-flex items-center gap-3 group">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 glow-quantum">
                <Atom className="h-6 w-6 text-quantum" />
              </div>
              <div className="text-left">
                <h1 className="font-mono text-xl font-bold">Nexar</h1>
                <p className="text-xs text-muted-foreground">Intelligent Quantum-Classical Workload Orchestration Platform</p>
              </div>
            </Link>
          </div>

          {/* Header */}
          <div className="text-center lg:text-left space-y-2">
            <h1 className="text-3xl font-bold tracking-tight">{title}</h1>
            <p className="text-muted-foreground">{description}</p>
          </div>

          {/* Form Content */}
          <div>{children}</div>

          {/* Back to home link for mobile */}
          <div className="lg:hidden text-center">
            <Link to="/" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
              ← Back to home
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AuthLayout;
