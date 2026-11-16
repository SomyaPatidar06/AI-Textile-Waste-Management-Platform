import React from 'react';

/**
 * StatCard — Precision KPI metric card for industrial analytics.
 * Combines structured numeric formatting, icon badge, trend pills, and accessible labels.
 */
export default function StatCard({
  title,
  value,
  unit = '',
  subtitle = '',
  icon: Icon,
  trend = null, // e.g. { label: '+12%', positive: true }
  accent = 'emerald', // emerald | teal | seaglass | amber | rose
  className = ''
}) {
  const accentStyles = {
    emerald: {
      iconBg: 'bg-emerald-600/15 text-emerald-400 border-emerald-500/25',
      glow: 'shadow-[0_0_15px_-3px_rgba(54,154,135,0.2)]',
    },
    teal: {
      iconBg: 'bg-deepTeal-700/30 text-seaglass-300 border-deepTeal-500/30',
      glow: 'shadow-[0_0_15px_-3px_rgba(39,98,116,0.2)]',
    },
    seaglass: {
      iconBg: 'bg-seaglass-400/15 text-seaglass-300 border-seaglass-400/25',
      glow: 'shadow-[0_0_15px_-3px_rgba(185,229,223,0.2)]',
    },
    amber: {
      iconBg: 'bg-amber-500/15 text-amber-300 border-amber-500/25',
      glow: 'shadow-[0_0_15px_-3px_rgba(245,158,11,0.2)]',
    },
    rose: {
      iconBg: 'bg-rose-500/15 text-rose-300 border-rose-500/25',
      glow: 'shadow-[0_0_15px_-3px_rgba(244,63,94,0.2)]',
    },
  }[accent] || accentStyles.emerald;

  return (
    <div className={`liquid-glass rounded-2xl p-5 glass-specular liquid-glass-interactive flex flex-col justify-between ${className}`}>
      <div className="flex items-start justify-between gap-3">
        <div>
          <span className="text-[11px] font-semibold uppercase tracking-wider text-frost-300/70 leading-snug block line-clamp-1">
            {title}
          </span>
          <div className="mt-2 flex items-baseline gap-1.5">
            <span className="text-2xl sm:text-3xl font-extrabold tracking-tight text-frost-50 font-mono">
              {value}
            </span>
            {unit && (
              <span className="text-xs font-medium text-seaglass-300/80">
                {unit}
              </span>
            )}
          </div>
        </div>

        {Icon && (
          <div className={`p-2.5 rounded-xl border ${accentStyles.iconBg} ${accentStyles.glow} shrink-0`}>
            <Icon className="w-5 h-5" />
          </div>
        )}
      </div>

      <div className="mt-4 pt-3 border-t border-white/5 flex items-center justify-between text-xs text-frost-200/60">
        <span className="truncate">{subtitle}</span>
        {trend && (
          <span
            className={`inline-flex items-center gap-1 font-semibold text-[11px] px-2 py-0.5 rounded-full border ${
              trend.positive
                ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                : 'bg-rose-500/10 text-rose-400 border-rose-500/20'
            }`}
          >
            {trend.label}
          </span>
        )}
      </div>
    </div>
  );
}
