/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        midnight: {
          950: '#040d12',
          900: '#081721',
          850: '#0d1f2b',
          800: '#122a3a',
          700: '#1b3b4f',
          600: '#254d65',
        },
        deepTeal: {
          950: '#0c1d22',
          900: '#112a32',
          800: '#173943',
          700: '#1f4a56',
          600: '#285f6e',
          500: '#347b8e',
        },
        emerald: {
          900: '#1a473e',
          800: '#235e52',
          700: '#2d7969',
          600: '#369A87',
          500: '#46b29e',
          400: '#63c5b3',
          300: '#8dd9cb',
        },
        seaglass: {
          50: '#f6fcfa',
          100: '#edf8f5',
          200: '#d7f0ea',
          300: '#B9E5DF',
          400: '#96d6cc',
          500: '#6fbfb3',
        },
        frost: {
          50: '#FAFCFB',
          100: '#EEF5F3',
          200: '#DEEAE7',
          300: '#C9DCD7',
        },
        brand: {
          50: '#EEF5F3',
          100: '#B9E5DF',
          500: '#369A87',
          600: '#2d7969',
          700: '#173943',
          900: '#081721',
        }
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['JetBrains Mono', 'ui-monospace', 'SFMono-Regular', 'Menlo', 'Monaco', 'Consolas', 'monospace'],
      },
      boxShadow: {
        'glass-sm': '0 2px 8px 0 rgba(0, 0, 0, 0.25), inset 0 1px 0 0 rgba(255, 255, 255, 0.08)',
        'glass-md': '0 8px 24px -4px rgba(0, 0, 0, 0.35), inset 0 1px 0 0 rgba(255, 255, 255, 0.12)',
        'glass-lg': '0 16px 40px -8px rgba(0, 0, 0, 0.45), inset 0 1px 0 0 rgba(255, 255, 255, 0.16)',
        'glass-glow': '0 0 25px -4px rgba(54, 154, 135, 0.3), inset 0 1px 0 0 rgba(185, 229, 223, 0.25)',
      },
      backgroundImage: {
        'liquid-mesh': 'radial-gradient(at 0% 0%, rgba(23, 57, 67, 0.45) 0px, transparent 55%), radial-gradient(at 100% 100%, rgba(54, 154, 135, 0.2) 0px, transparent 50%), radial-gradient(at 50% 50%, rgba(8, 23, 33, 0.6) 0px, transparent 100%)',
      }
    },
  },
  plugins: [],
}
