import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Lock, User, AlertCircle, ArrowRight, Eye, EyeOff, ShieldCheck, Sparkles } from 'lucide-react';
import BrandLogo from '../components/ui/BrandLogo';
import GlassPanel from '../components/ui/GlassPanel';

export default function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      await login(username, password);
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.detail || 'Authentication failed. Please verify credentials.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-midnight-950 ambient-mesh p-4 sm:p-6 textile-grid relative overflow-hidden">
      {/* Background Decorative Ambient Orbs */}
      <div className="absolute top-1/4 -left-20 w-80 h-80 rounded-full bg-emerald-600/10 blur-3xl pointer-events-none" />
      <div className="absolute bottom-1/4 -right-20 w-96 h-96 rounded-full bg-deepTeal-600/15 blur-3xl pointer-events-none" />

      <div className="w-full max-w-md relative z-10">
        <GlassPanel elevated className="p-8 sm:p-10 border-seaglass-300/20 shadow-glass-lg">
          {/* Brand Header */}
          <div className="text-center mb-8">
            <BrandLogo size={52} className="mx-auto mb-4" />
            <h1 className="text-2xl font-extrabold text-frost-50 tracking-tight">
              Textile Intelligence
            </h1>
            <p className="text-xs text-seaglass-200/70 mt-1 font-medium">
              Enterprise Circular Waste Verification Platform
            </p>
          </div>

          {error && (
            <div className="mb-6 p-3.5 bg-rose-500/15 border border-rose-500/30 rounded-xl flex items-start gap-2.5 text-xs text-rose-300">
              <AlertCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-frost-200 mb-1.5 tracking-wide">
                Username or Facility Identifier
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-frost-300/40">
                  <User className="w-4 h-4" />
                </div>
                <input
                  type="text"
                  required
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full pl-10 pr-4 py-2.5 bg-midnight-900/60 border border-white/10 rounded-xl text-sm text-frost-50 placeholder-frost-300/30 focus:outline-none focus:border-emerald-500/60 focus:ring-1 focus:ring-emerald-500/40 transition-all"
                  placeholder="e.g. operator1"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-frost-200 mb-1.5 tracking-wide">
                Secret Key / Password
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-frost-300/40">
                  <Lock className="w-4 h-4" />
                </div>
                <input
                  type={showPassword ? 'text' : 'password'}
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full pl-10 pr-10 py-2.5 bg-midnight-900/60 border border-white/10 rounded-xl text-sm text-frost-50 placeholder-frost-300/30 focus:outline-none focus:border-emerald-500/60 focus:ring-1 focus:ring-emerald-500/40 transition-all font-mono"
                  placeholder="••••••••••••"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 pr-3.5 flex items-center text-frost-300/40 hover:text-frost-100 transition-colors"
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full mt-6 py-3 px-4 bg-gradient-to-r from-emerald-600 to-teal-700 hover:from-emerald-500 hover:to-teal-600 text-frost-50 font-bold text-xs uppercase tracking-wider rounded-xl shadow-glass-md border border-emerald-400/30 flex items-center justify-center gap-2 transition-all disabled:opacity-50"
            >
              {isLoading ? (
                <>
                  <span className="w-3.5 h-3.5 rounded-full border-2 border-white border-t-transparent animate-spin" />
                  <span>Authenticating...</span>
                </>
              ) : (
                <>
                  <span>Sign In to Platform</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          {/* Environmental Assurance Tag */}
          <div className="mt-8 pt-6 border-t border-white/10 flex items-center justify-between text-xs text-frost-300/50">
            <div className="flex items-center gap-1.5">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              <span>RBAC Verified</span>
            </div>
            <p>
              New operator?{' '}
              <Link to="/register" className="font-semibold text-emerald-400 hover:text-emerald-300 underline underline-offset-2">
                Register
              </Link>
            </p>
          </div>
        </GlassPanel>
      </div>
    </div>
  );
}
