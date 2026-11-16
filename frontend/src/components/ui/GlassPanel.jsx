import React from 'react';

/**
 * GlassPanel — Foundational Liquid Glass surface container.
 * Features frosted backdrop blur, translucent borders, soft shadow, and optional specular top highlight.
 */
export default function GlassPanel({
  children,
  className = '',
  elevated = false,
  specular = true,
  onClick = null,
  interactive = false,
  ...props
}) {
  const baseClasses = elevated ? 'liquid-glass-elevated' : 'liquid-glass';
  const specularClass = specular ? 'glass-specular' : '';
  const interactiveClass = interactive ? 'liquid-glass-interactive cursor-pointer' : '';

  return (
    <div
      onClick={onClick}
      className={`rounded-2xl ${baseClasses} ${specularClass} ${interactiveClass} ${className}`}
      {...props}
    >
      {children}
    </div>
  );
}
