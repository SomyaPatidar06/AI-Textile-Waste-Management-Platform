import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import api from '../api';
import { User, Mail, Lock, Shield, AlertCircle, CheckCircle2, ArrowRight, Eye, EyeOff } from 'lucide-react';
import BrandLogo from '../components/ui/BrandLogo';
import GlassPanel from '../components/ui/GlassPanel';

export default function Register() {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [role, setRole] = useState('OPERATOR');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setIsLoading(true);

    try {
      await api.post('/auth/register', {
        username,
        email,
        password,
        role,
      });
      setSuccess('Operational account provisioned successfully. Redirecting to login...');
      setTimeout(() => navigate('/login'), 1500);
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed. Please check inputs.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-midnight-950 ambient-mesh p-4 sm:p-6 textile-grid relative overflow-hidden">
      {/* Background Decorative Ambient Orbs */}
      <div className="absolute top-1/4 -right-20 w-80 h-80 rounded-full bg-emerald-600/10 blur-3xl pointer-events-none" />
      <div className="absolute bottom-1/4 -left-20 w-96 h-96 rounded-full bg-deepTeal-600/15 blur-3xl pointer-events-none" />

      <div className="w-full max-w-md relative z-10">
        <GlassPanel elevated className="p-8 sm:p-10 border-seaglass-300/20 shadow-glass-lg">
          {/* Brand Header */}
          <div className="text-center mb-6">
            <BrandLogo size={48} className="mx-auto mb-3" />
            <h1 className="text-2xl font-extrabold text-frost-50 tracking-tight">
              Create Account
            </h1>
            <p className="text-xs text-seaglass-200/70 mt-1 font-medium">
              Join the Circular Textile Verification Network
            </p>
          </div>

          {error && (
            <div className="mb-5 p-3.5 bg-rose-500/15 border border-rose-500/30 rounded-xl flex items-start gap-2.5 text-xs text-rose-300">
              <AlertCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          {success && (
            <div className="mb-5 p-3.5 bg-emerald-500/15 border border-emerald-500/30 rounded-xl flex items-start gap-2.5 text-xs text-emerald-300">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
              <span>{success}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-3.5">
            <div>
              <label className="block text-xs font-semibold text-frost-200 mb-1 tracking-wide">
                Operator Username
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
                  className="w-full pl-10 pr-4 py-2 bg-midnight-900/60 border border-white/10 rounded-xl text-sm text-frost-50 placeholder-frost-300/30 focus:outline-none focus:border-emerald-500/60 focus:ring-1 focus:ring-emerald-500/40"
                  placeholder="e.g. operator_smith"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-frost-200 mb-1 tracking-wide">
                Enterprise Email
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-frost-300/40">
                  <Mail className="w-4 h-4" />
                </div>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 bg-midnight-900/60 border border-white/10 rounded-xl text-sm text-frost-50 placeholder-frost-300/30 focus:outline-none focus:border-emerald-500/60 focus:ring-1 focus:ring-emerald-500/40"
                  placeholder="name@facility.com"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-frost-200 mb-1 tracking-wide">
                Password (Min. 8 characters)
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-frost-300/40">
                  <Lock className="w-4 h-4" />
                </div>
                <input
                  type={showPassword ? 'text' : 'password'}
                  required
                  minLength={8}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full pl-10 pr-10 py-2 bg-midnight-900/60 border border-white/10 rounded-xl text-sm text-frost-50 placeholder-frost-300/30 focus:outline-none focus:border-emerald-500/60 focus:ring-1 focus:ring-emerald-500/40 font-mono"
                  placeholder="••••••••••••"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 pr-3.5 flex items-center text-frost-300/40 hover:text-frost-100 transition-colors"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-frost-200 mb-1 tracking-wide">
                Requested Operational Role
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-frost-300/40">
                  <Shield className="w-4 h-4" />
                </div>
                <select
                  value={role}
                  onChange={(e) => setRole(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 bg-midnight-900/60 border border-white/10 rounded-xl text-sm text-frost-50 focus:outline-none focus:border-emerald-500/60 focus:ring-1 focus:ring-emerald-500/40"
                >
                  <option value="OPERATOR" className="bg-midnight-900">Plant Operator (Sorting & Scanning)</option>
                  <option value="MANUFACTURER" className="bg-midnight-900">Textile Manufacturer (Scrap Producer)</option>
                  <option value="SUSTAINABILITY_MANAGER" className="bg-midnight-900">Sustainability Manager (Auditor)</option>
                  <option value="RECYCLER" className="bg-midnight-900">Circular Recycler (Secondary Fiber Processor)</option>
                  <option value="VIEWER" className="bg-midnight-900">Auditor / Viewer (Read Only)</option>
                </select>
              </div>
              <p className="text-[10px] text-frost-300/40 mt-1 italic">
                Administrator roles are granted exclusively by existing Admins via RBAC controls.
              </p>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full mt-4 py-2.5 px-4 bg-gradient-to-r from-emerald-600 to-teal-700 hover:from-emerald-500 hover:to-teal-600 text-frost-50 font-bold text-xs uppercase tracking-wider rounded-xl shadow-glass-md border border-emerald-400/30 flex items-center justify-center gap-2 transition-all disabled:opacity-50"
            >
              {isLoading ? 'Creating Account...' : 'Complete Registration'}
              {!isLoading && <ArrowRight className="w-4 h-4" />}
            </button>
          </form>

          <div className="mt-6 pt-4 border-t border-white/10 text-center">
            <p className="text-xs text-frost-300/60">
              Already registered?{' '}
              <Link to="/login" className="font-semibold text-emerald-400 hover:text-emerald-300 underline underline-offset-2">
                Sign in
              </Link>
            </p>
          </div>
        </GlassPanel>
      </div>
    </div>
  );
}
