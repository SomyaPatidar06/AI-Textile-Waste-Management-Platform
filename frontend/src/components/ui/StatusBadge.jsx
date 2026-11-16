import React from 'react';

/**
 * StatusBadge — Liquid Glass status tag with translucent borders and soft glow.
 */
export default function StatusBadge({ status, type = 'status', className = '', pulse = false }) {
  if (!status) return null;

  const getStyle = () => {
    const s = String(status).toUpperCase();

    // Batch Statuses
    if (s === 'COLLECTED') {
      return 'bg-teal-700/20 text-seaglass-300 border-teal-500/30';
    }
    if (s === 'SORTED') {
      return 'bg-emerald-600/20 text-emerald-300 border-emerald-500/35';
    }
    if (s === 'PROCESSED') {
      return 'bg-blue-600/20 text-blue-300 border-blue-500/35';
    }
    if (s === 'DISPATCHED') {
      return 'bg-purple-600/20 text-purple-300 border-purple-500/35';
    }

    // Circularity Categories
    if (s.includes('EXCELLENT')) {
      return 'bg-emerald-500/25 text-emerald-300 border-emerald-400/40 shadow-[0_0_12px_rgba(54,154,135,0.25)]';
    }
    if (s.includes('HIGH')) {
      return 'bg-teal-600/25 text-seaglass-300 border-teal-400/35';
    }
    if (s.includes('MODERATE')) {
      return 'bg-amber-500/20 text-amber-300 border-amber-500/35';
    }
    if (s.includes('LIMITED') || s.includes('DOWN')) {
      return 'bg-orange-500/20 text-orange-300 border-orange-500/35';
    }
    if (s.includes('DISPOSAL') || s.includes('HAZARDOUS')) {
      return 'bg-rose-500/25 text-rose-300 border-rose-500/40';
    }

    // Role Badges
    if (s === 'ADMIN') {
      return 'bg-indigo-600/20 text-indigo-300 border-indigo-500/35';
    }
    if (s === 'OPERATOR') {
      return 'bg-emerald-600/20 text-emerald-300 border-emerald-500/35';
    }
    if (s === 'SUSTAINABILITY_MANAGER') {
      return 'bg-teal-600/20 text-seaglass-300 border-teal-500/35';
    }
    if (s === 'MANUFACTURER') {
      return 'bg-cyan-600/20 text-cyan-300 border-cyan-500/35';
    }
    if (s === 'RECYCLER') {
      return 'bg-blue-600/20 text-blue-300 border-blue-500/35';
    }

    // Defect Severities
    if (s === 'CRITICAL' || s.includes('CRITICAL')) {
      return 'bg-rose-600/25 text-rose-300 border-rose-500/40';
    }
    if (s === 'MODERATE' || s.includes('MODERATE')) {
      return 'bg-amber-600/20 text-amber-300 border-amber-500/35';
    }
    if (s === 'MINOR' || s.includes('MINOR')) {
      return 'bg-teal-600/20 text-seaglass-300 border-teal-500/30';
    }
    if (s === 'DEFECT FREE' || s === 'CLEAR') {
      return 'bg-emerald-600/20 text-emerald-300 border-emerald-500/35';
    }

    // Default
    return 'bg-white/10 text-frost-200 border-white/15';
  };

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-semibold border backdrop-blur-md ${getStyle()} ${className}`}
    >
      {pulse && (
        <span className="w-1.5 h-1.5 rounded-full bg-current animate-pulse shrink-0" />
      )}
      {status}
    </span>
  );
}
