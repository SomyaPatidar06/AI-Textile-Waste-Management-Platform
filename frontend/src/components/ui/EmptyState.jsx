import React from 'react';

/**
 * EmptyState — Refined empty graphic state for data collections.
 */
export default function EmptyState({
  icon: Icon,
  title,
  description,
  actionText = '',
  onAction = null,
  className = ''
}) {
  return (
    <div className={`p-8 sm:p-12 text-center rounded-2xl liquid-glass border border-white/10 ${className}`}>
      {Icon && (
        <div className="w-12 h-12 rounded-2xl bg-deepTeal-800/40 border border-emerald-500/20 text-seaglass-300 flex items-center justify-center mx-auto mb-4 shadow-[0_0_15px_-4px_rgba(54,154,135,0.3)]">
          <Icon className="w-6 h-6" />
        </div>
      )}
      <h4 className="text-base font-bold text-frost-50">{title}</h4>
      {description && (
        <p className="text-xs text-frost-300/60 max-w-sm mx-auto mt-1.5 leading-relaxed">
          {description}
        </p>
      )}
      {actionText && onAction && (
        <button
          onClick={onAction}
          className="mt-5 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-frost-50 text-xs font-semibold rounded-xl shadow-glass-sm border border-emerald-400/30 transition-all"
        >
          {actionText}
        </button>
      )}
    </div>
  );
}
