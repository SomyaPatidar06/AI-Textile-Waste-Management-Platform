import React from 'react';

/**
 * GlassCard — Polished card component with optical glass depth, padding presets, and hover states.
 */
export default function GlassCard({
  children,
  className = '',
  padding = 'p-5',
  interactive = true,
  elevated = false,
  ...props
}) {
  return (
    <div
      className={`rounded-2xl liquid-glass ${
        elevated ? 'liquid-glass-elevated' : ''
      } ${
        interactive ? 'liquid-glass-interactive' : ''
      } glass-specular ${padding} ${className}`}
      {...props}
    >
      {children}
    </div>
  );
}
