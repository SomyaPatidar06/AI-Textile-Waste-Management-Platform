import React, { useEffect, useRef } from 'react';
import { X } from 'lucide-react';

/**
 * GlassModal — Accessible dialog overlay with Liquid Glass backdrop blur and subtle specular highlights.
 */
export default function GlassModal({
  isOpen,
  onClose,
  title,
  subtitle = '',
  children,
  maxWidth = 'max-w-xl',
  className = ''
}) {
  const modalRef = useRef(null);

  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    if (isOpen) {
      document.body.style.overflow = 'hidden';
      window.addEventListener('keydown', handleKeyDown);
    }
    return () => {
      document.body.style.overflow = 'unset';
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 overflow-y-auto bg-midnight-950/75 backdrop-blur-md animate-fadeIn"
      role="dialog"
      aria-modal="true"
      aria-labelledby="glass-modal-title"
    >
      <div
        className="fixed inset-0 transition-opacity"
        onClick={onClose}
        aria-hidden="true"
      />

      <div
        ref={modalRef}
        className={`relative w-full ${maxWidth} liquid-glass-elevated glass-specular rounded-2xl shadow-glass-lg border border-seaglass-300/20 z-10 my-8 overflow-hidden transform transition-all ${className}`}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-start justify-between p-5 sm:p-6 border-b border-white/10">
          <div>
            <h3 id="glass-modal-title" className="text-lg font-bold text-frost-50 tracking-tight">
              {title}
            </h3>
            {subtitle && (
              <p className="text-xs text-seaglass-200/70 mt-1">
                {subtitle}
              </p>
            )}
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-frost-300/60 hover:text-frost-50 rounded-lg hover:bg-white/10 transition-colors"
            aria-label="Close dialog"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Body */}
        <div className="p-5 sm:p-6 max-h-[calc(85vh-120px)] overflow-y-auto custom-scrollbar">
          {children}
        </div>
      </div>
    </div>
  );
}
