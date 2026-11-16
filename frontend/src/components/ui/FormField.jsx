import React from 'react';

/**
 * FormField — Accessible input field wrapped in Liquid Glass aesthetics with focus glow.
 */
export default function FormField({
  label,
  id,
  type = 'text',
  value,
  onChange,
  placeholder = '',
  required = false,
  error = '',
  helperText = '',
  icon: Icon = null,
  options = [], // for select type
  rows = 3, // for textarea type
  className = '',
  disabled = false,
  ...props
}) {
  const inputBaseStyle = `w-full px-3.5 py-2.5 rounded-xl bg-midnight-900/60 border ${
    error
      ? 'border-rose-500/60 focus:border-rose-400 focus:ring-1 focus:ring-rose-500/40'
      : 'border-white/10 hover:border-seaglass-300/30 focus:border-emerald-500/60 focus:ring-1 focus:ring-emerald-500/40'
  } text-sm text-frost-50 placeholder-frost-300/30 backdrop-blur-md transition-all focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed`;

  return (
    <div className={`space-y-1.5 ${className}`}>
      {label && (
        <label htmlFor={id} className="block text-xs font-semibold text-frost-200/90 tracking-wide">
          {label} {required && <span className="text-emerald-400">*</span>}
        </label>
      )}

      <div className="relative">
        {Icon && (
          <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-frost-300/50">
            <Icon className="w-4 h-4" />
          </div>
        )}

        {type === 'select' ? (
          <select
            id={id}
            value={value}
            onChange={onChange}
            required={required}
            disabled={disabled}
            className={`${inputBaseStyle} ${Icon ? 'pl-10' : ''}`}
            {...props}
          >
            {options.map((opt) => (
              <option key={opt.value} value={opt.value} className="bg-midnight-900 text-frost-100">
                {opt.label}
              </option>
            ))}
          </select>
        ) : type === 'textarea' ? (
          <textarea
            id={id}
            value={value}
            onChange={onChange}
            placeholder={placeholder}
            required={required}
            disabled={disabled}
            rows={rows}
            className={`${inputBaseStyle} ${Icon ? 'pl-10' : ''}`}
            {...props}
          />
        ) : (
          <input
            id={id}
            type={type}
            value={value}
            onChange={onChange}
            placeholder={placeholder}
            required={required}
            disabled={disabled}
            className={`${inputBaseStyle} ${Icon ? 'pl-10' : ''}`}
            {...props}
          />
        )}
      </div>

      {error ? (
        <p className="text-[11px] text-rose-400 mt-1 font-medium">{error}</p>
      ) : helperText ? (
        <p className="text-[11px] text-frost-300/50 mt-1">{helperText}</p>
      ) : null}
    </div>
  );
}
