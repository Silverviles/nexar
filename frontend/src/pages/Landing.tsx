import React from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { ArrowRight, Zap, Shield, BarChart, Atom, Sparkles, Cpu, Lock, TrendingUp } from 'lucide-react';

const Landing: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-950 text-white overflow-hidden">
      {/* Background minimalist pattern */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-blue-500/10 rounded-full blur-3xl" />
        <div className="absolute top-1/3 -left-20 w-60 h-60 bg-purple-500/10 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 right-1/4 w-40 h-40 bg-cyan-500/10 rounded-full blur-3xl" />
      </div>

      {/* Content */}
      <div className="relative z-10">
        {/* Navigation */}
        <nav className="container mx-auto px-6 py-6">
          <div className="flex justify-between items-center">
            <Link to="/" className="flex items-center gap-3 group">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-600 group-hover:bg-blue-500 transition-colors">
                <Atom className="h-6 w-6 text-white" />
              </div>
              <div className="text-2xl font-bold font-sans text-white">Nexar</div>
            </Link>
            <div className="flex items-center gap-4">
              <Link to="/features" className="text-gray-300 hover:text-white font-medium">
                Features
              </Link>
              <Link to="/pricing" className="text-gray-300 hover:text-white font-medium">
                Pricing
              </Link>
              <Link to="/signin">
                <Button variant="ghost" className="text-gray-300 hover:text-white hover:bg-white/10">Sign In</Button>
              </Link>
              <Link to="/signup">
                <Button className="bg-blue-600 hover:bg-blue-500 text-white">Get Started</Button>
              </Link>
            </div>
          </div>
        </nav>

        {/* Hero Section */}
        <section className="relative container mx-auto px-6 py-20 md:py-32">
          {/* Background Image */}
          <div className="absolute inset-0 -mx-6 overflow-hidden">
            <img 
              src="/auth/quantum_bg.jpg" 
              alt="Quantum Background" 
              className="w-full h-full object-cover opacity-60"
            />
            <div className="absolute inset-0 bg-gradient-to-b from-gray-950/80 via-gray-950/70 to-gray-950/90" />
          </div>
          
          <div className="relative z-10 max-w-4xl mx-auto text-center">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-blue-500/10 border border-blue-500/20 text-sm font-medium text-blue-300 mb-8">
              <Sparkles className="h-4 w-4" />
              AI-Powered Intelligence Platform
            </div>
            
            <h1 className="text-5xl md:text-7xl font-bold text-white mb-6 tracking-tight">
              The Future of Hybrid Computing{' '}
              <span className="relative">
                <span className="relative z-10 bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">Today</span>
                <div className="absolute bottom-2 left-0 right-0 h-3 bg-blue-500/30 blur-lg -z-10" />
              </span>
            </h1>
            
            <p className="text-xl text-gray-300 mb-10 max-w-2xl mx-auto leading-relaxed">
            Intelligent workload routing between quantum and classical systems. Predict performance, optimize costs, and maximize efficiency with ML-driven decisions.
            </p>
            
            <div className="flex flex-col sm:flex-row justify-center gap-4">
              <Link to="/signup">
                <Button size="lg" className="text-lg px-8 bg-blue-600 hover:bg-blue-500 text-white h-14">
                  Sign Up for Free
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Button>
              </Link>
            </div>
            
            {/* Trust indicators */}
            <div className="mt-16 pt-8 border-t border-gray-800">
              <p className="text-sm text-gray-400 mb-6">Trusted by innovative teams worldwide</p>
              <div className="flex flex-wrap justify-center items-center gap-8 opacity-60">
                <div className="text-lg font-semibold text-gray-500">TechCorp</div>
                <div className="text-lg font-semibold text-gray-500">Innovate Inc</div>
                <div className="text-lg font-semibold text-gray-500">Future Labs</div>
                <div className="text-lg font-semibold text-gray-500">Quantum AI</div>
              </div>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section className="container mx-auto px-6 py-20">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              Engineered for Excellence
            </h2>
            <p className="text-gray-300 max-w-2xl mx-auto">
              Built with cutting-edge technology to deliver unparalleled performance
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            <div className="bg-gray-900/50 backdrop-blur-sm border border-gray-800 p-8 rounded-2xl hover:border-gray-700 transition-colors">
              <div className="w-12 h-12 rounded-xl bg-blue-500/10 flex items-center justify-center mb-6">
                <Cpu className="h-6 w-6 text-blue-400" />
              </div>
              <h3 className="text-xl font-semibold mb-3 text-white">Real-time Processing</h3>
              <p className="text-gray-400">
                Analyze and process data in real-time with our low-latency architecture.
              </p>
              <div className="mt-6 pt-6 border-t border-gray-800">
                <span className="text-sm font-medium text-blue-400">Learn more →</span>
              </div>
            </div>

            <div className="bg-gray-900/50 backdrop-blur-sm border border-gray-800 p-8 rounded-2xl hover:border-gray-700 transition-colors">
              <div className="w-12 h-12 rounded-xl bg-green-500/10 flex items-center justify-center mb-6">
                <Lock className="h-6 w-6 text-green-400" />
              </div>
              <h3 className="text-xl font-semibold mb-3 text-white">Enterprise Security</h3>
              <p className="text-gray-400">
                End-to-end encryption and compliance with industry security standards.
              </p>
              <div className="mt-6 pt-6 border-t border-gray-800">
                <span className="text-sm font-medium text-green-400">Learn more →</span>
              </div>
            </div>

            <div className="bg-gray-900/50 backdrop-blur-sm border border-gray-800 p-8 rounded-2xl hover:border-gray-700 transition-colors">
              <div className="w-12 h-12 rounded-xl bg-purple-500/10 flex items-center justify-center mb-6">
                <TrendingUp className="h-6 w-6 text-purple-400" />
              </div>
              <h3 className="text-xl font-semibold mb-3 text-white">Predictive Analytics</h3>
              <p className="text-gray-400">
                Advanced ML models that forecast trends and optimize decision-making.
              </p>
              <div className="mt-6 pt-6 border-t border-gray-800">
                <span className="text-sm font-medium text-purple-400">Learn more →</span>
              </div>
            </div>
          </div>
        </section>

        {/* Stats Section */}
        <section className="bg-gray-900/30 backdrop-blur-sm py-20">
          <div className="container mx-auto px-6">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
              <div className="text-center">
                <div className="text-4xl font-bold text-white mb-2">99.9%</div>
                <div className="text-gray-400">Uptime</div>
              </div>
              <div className="text-center">
                <div className="text-4xl font-bold text-white mb-2">10K+</div>
                <div className="text-gray-400">Decisions Processed</div>
              </div>
              <div className="text-center">
                <div className="text-4xl font-bold text-white mb-2">50ms</div>
                <div className="text-gray-400">Average Response Time</div>
              </div>
              <div className="text-center">
                <div className="text-4xl font-bold text-white mb-2">24/7</div>
                <div className="text-gray-400">Support</div>
              </div>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="container mx-auto px-6 py-20">
          <div className="bg-gradient-to-br from-blue-600 to-cyan-600 text-white rounded-3xl p-12 text-center max-w-4xl mx-auto">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Start your AI journey today
            </h2>
            <p className="text-blue-50 mb-8 max-w-2xl mx-auto">
              Join forward-thinking companies that are transforming their operations with AI.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link to="/signup">
                <Button size="lg" className="text-lg px-8 bg-white text-blue-600 hover:bg-blue-50 h-14">
                  Get Started Free
                </Button>
              </Link>
              <Link to="/contact">
                <Button size="lg" variant="outline" className="text-lg px-8 border-white text-white hover:bg-white/10 h-14">
                  Contact Sales
                </Button>
              </Link>
            </div>
            <p className="text-sm text-blue-100 mt-6">No credit card required • 14-day free trial</p>
          </div>
        </section>

        {/* Footer */}
        <footer className="container mx-auto px-6 py-12 border-t border-gray-800">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="flex items-center gap-3 mb-6 md:mb-0">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-600">
                <Atom className="h-4 w-4 text-white" />
              </div>
              <div className="text-xl font-bold text-white">Nexar</div>
            </div>
            
            <div className="flex gap-8 mb-6 md:mb-0">
              <Link to="/privacy" className="text-gray-400 hover:text-white">
                Privacy
              </Link>
              <Link to="/terms" className="text-gray-400 hover:text-white">
                Terms
              </Link>
              <Link to="/contact" className="text-gray-400 hover:text-white">
                Contact
              </Link>
            </div>
            
            <div className="text-gray-500 text-sm">
              &copy; {new Date().getFullYear()} Nexar. All rights reserved.
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
};

export default Landing;