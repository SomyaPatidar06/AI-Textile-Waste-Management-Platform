import React from 'react';

/**
 * LoadingSkeleton — Shimmer skeleton indicators for cards, text, and metrics.
 */
export function SkeletonCard({ className = '' }) {
  return (
    <div className={`liquid-glass rounded-2xl p-5 border border-white/5 animate-pulse ${className}`}>
      <div className="flex justify-between items-start">
        <div className="space-y-2.5 w-2/3">
          <div className="h-3 bg-white/10 rounded w-1/2" />
          <div className="h-7 bg-white/15 rounded w-3/4" />
        </div>
        <div className="w-10 h-10 rounded-xl bg-white/10" />
      </div>
      <div className="mt-4 pt-3 border-t border-white/5">
        <div className="h-3 bg-white/10 rounded w-1/3" />
      </div>
    </div>
  );
}

export function SkeletonLine({ width = 'w-full', height = 'h-4', className = '' }) {
  return (
    <div className={`${width} ${height} bg-white/10 rounded animate-pulse ${className}`} />
  );
}
