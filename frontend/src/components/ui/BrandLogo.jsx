import React from 'react';

/**
 * BrandLogo — Geometric optical textile weave icon.
 * Depicts interwoven yarn strands in a circular loop, symbolizing circular textile intelligence.
 */
export default function BrandLogo({ size = 36, className = '' }) {
  return (
    <div
      className={`relative flex items-center justify-center shrink-0 rounded-xl bg-gradient-to-br from-deepTeal-800 to-midnight-900 border border-emerald-500/30 shadow-glass-sm ${className}`}
      style={{ width: size, height: size }}
      aria-label="Textile Waste Intelligence Platform logo"
    >
      <svg
        width={size * 0.65}
        height={size * 0.65}
        viewBox="0 0 24 24"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="text-emerald-400 drop-shadow-[0_0_8px_rgba(54,154,135,0.4)]"
      >
        {/* Warp and weft circular interwoven lattice */}
        <path
          d="M4 12C4 7.58172 7.58172 4 12 4C14.5 4 16.7 5.1 18.2 6.9"
          stroke="currentColor"
          strokeWidth="2.2"
          strokeLinecap="round"
        />
        <path
          d="M20 12C20 16.4183 16.4183 20 12 20C9.5 20 7.3 18.9 5.8 17.1"
          stroke="#B9E5DF"
          strokeWidth="2.2"
          strokeLinecap="round"
        />
        {/* Weave intersection crossbar */}
        <path
          d="M9 9L15 15M15 9L9 15"
          stroke="#369A87"
          strokeWidth="2"
          strokeLinecap="round"
        />
      </svg>
    </div>
  );
}
