import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  ScanLine,
  Boxes,
  FileBarChart,
  LogOut,
  X,
  Sparkles
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import BrandLogo from './ui/BrandLogo';
import StatusBadge from './ui/StatusBadge';

export default function Sidebar({ isOpen = true, onClose = null }) {
  const { user, role, logout } = useAuth();

  const navItems = [
    {
      name: 'Executive Dashboard',
      path: '/',
      icon: LayoutDashboard,
      badge: null
    },
    {
      name: 'AI Inspection Studio',
      path: '/upload',
      icon: ScanLine,
      badge: 'ResNet-18'
    },
    {
      name: 'Textile Inventory',
      path: '/inventory',
      icon: Boxes,
      badge: null
    },
    {
      name: 'Sustainability & ESG',
      path: '/reports',
      icon: FileBarChart,
      badge: null
    },
  ];

  return (
    <>
      {/* Mobile Backdrop Overlay */}
      {isOpen && onClose && (
        <div
          className="fixed inset-0 z-40 bg-midnight-950/80 backdrop-blur-sm lg:hidden"
          onClick={onClose}
          aria-hidden="true"
        />
      )}

      <aside
        className={`fixed lg:static top-0 bottom-0 left-0 z-50 w-72 shrink-0 liquid-glass border-r border-white/10 flex flex-col h-screen select-none transition-transform duration-300 ease-in-out ${
          isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0 pointer-events-none lg:pointer-events-auto'
        }`}
      >
        {/* Brand Header */}
        <div className="p-5 border-b border-white/10 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <BrandLogo size={38} />
            <div>
              <div className="flex items-center gap-1.5">
                <span className="font-extrabold text-frost-50 tracking-tight text-sm">
                  Textile Waste AI
                </span>
                <span className="text-[10px] px-1.5 py-0.2 rounded font-mono font-bold bg-emerald-500/15 text-emerald-400 border border-emerald-500/20">
                  v2.1
                </span>
              </div>
              <p className="text-[11px] text-seaglass-300/70 font-medium tracking-wide">
                Circular Intelligence
              </p>
            </div>
          </div>

          {onClose && (
            <button
              onClick={onClose}
              className="lg:hidden p-1.5 rounded-lg text-frost-300/60 hover:text-frost-50 hover:bg-white/10"
              aria-label="Close navigation"
            >
              <X className="w-5 h-5" />
            </button>
          )}
        </div>

        {/* Navigation Menu */}
        <nav className="flex-1 p-4 space-y-1.5 overflow-y-auto custom-scrollbar">
          <div className="px-3 pb-2 text-[10px] font-bold uppercase tracking-wider text-frost-300/40">
            Workspaces
          </div>

          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              onClick={onClose}
              className={({ isActive }) =>
                `flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-semibold tracking-wide transition-all ${
                  isActive
                    ? 'bg-gradient-to-r from-emerald-600/25 to-teal-700/25 text-seaglass-100 border border-emerald-500/40 shadow-[0_0_15px_-4px_rgba(54,154,135,0.3)]'
                    : 'text-frost-200/70 hover:text-frost-50 hover:bg-white/5 hover:border hover:border-white/5'
                }`
              }
            >
              <div className="flex items-center gap-3">
                <item.icon className="w-4 h-4 shrink-0 text-emerald-400" />
                <span>{item.name}</span>
              </div>
              {item.badge && (
                <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                  {item.badge}
                </span>
              )}
            </NavLink>
          ))}

          <div className="pt-6 px-3 pb-2 text-[10px] font-bold uppercase tracking-wider text-frost-300/40">
            Operational Governance
          </div>

          <div className="p-3.5 rounded-xl bg-midnight-900/50 border border-white/5 space-y-2">
            <div className="flex items-center gap-2 text-xs font-semibold text-seaglass-200">
              <Sparkles className="w-3.5 h-3.5 text-emerald-400" />
              <span>Option B Standard</span>
            </div>
            <p className="text-[11px] text-frost-300/60 leading-relaxed">
              Optical RGB outputs are visual characterizations. High-purity yarn blends route to automated manual sorting.
            </p>
          </div>
        </nav>

        {/* User Profile & Session Controls */}
        <div className="p-4 border-t border-white/10 bg-midnight-950/40">
          <div className="flex items-center justify-between mb-3">
            <div className="truncate mr-2">
              <p className="text-xs font-bold text-frost-50 truncate">
                {user?.username || 'Operator'}
              </p>
              <p className="text-[11px] text-seaglass-300/60 truncate font-mono">
                {user?.email || 'facility@textile.ai'}
              </p>
            </div>
            <StatusBadge status={role} />
          </div>

          <button
            onClick={logout}
            className="w-full flex items-center justify-center gap-2 px-3 py-2 text-xs font-semibold text-rose-300/80 hover:text-rose-200 bg-rose-500/10 hover:bg-rose-500/20 border border-rose-500/20 rounded-xl transition-all"
          >
            <LogOut className="w-3.5 h-3.5" /> End Session
          </button>
        </div>
      </aside>
    </>
  );
}
