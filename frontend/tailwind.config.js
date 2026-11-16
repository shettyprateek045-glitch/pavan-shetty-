/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#F8FAFC', // Slate-50: crisp, clean white-tinted canvas
        surface: '#FFFFFF',
        card: '#FFFFFF',
        sidebar: '#FFFFFF',
        border: {
          DEFAULT: '#E2E8F0', // Slate-200: subtle blue-gray border
          subtle: '#F1F5F9',  // Slate-100
          strong: '#CBD5E1',  // Slate-300
          focus: '#3B82F6',   // Blue-500
        },
        primary: {
          DEFAULT: '#0F172A', // Slate-900: deep readable navy-black
          muted: '#334155',   // Slate-700
          navy: '#1E293B',    // Slate-800
        },
        secondary: {
          DEFAULT: '#475569', // Slate-600: balanced secondary text
          light: '#64748B',   // Slate-500
          muted: '#94A3B8',   // Slate-400
        },
        accent: {
          DEFAULT: '#2563EB', // Blue-600: Polished royal blue
          hover: '#1D4ED8',   // Blue-700
          active: '#1E40AF',  // Blue-800
          light: '#EFF6FF',   // Blue-50
          muted: '#DBEAFE',   // Blue-100
          border: '#BFDBFE',  // Blue-200
          navy: '#1E3A8A',    // Blue-900: deep restrained navy
        },
        navy: {
          950: '#0A0F1D',
          900: '#0F172A',
          800: '#1E293B',
          700: '#334155',
          600: '#475569',
          100: '#E2E8F0',
          50: '#F8FAFC',
        },
        success: {
          DEFAULT: '#059669', // Emerald-600
          light: '#ECFDF5',   // Emerald-50
          border: '#A7F3D0',  // Emerald-200
        },
        warning: {
          DEFAULT: '#D97706', // Amber-600
          light: '#FFFBEB',   // Amber-50
          border: '#FDE68A',  // Amber-200
        },
        danger: {
          DEFAULT: '#DC2626', // Red-600
          light: '#FEF2F2',   // Red-50
          border: '#FECACA',  // Red-200
        },
      },
      fontFamily: {
        sans: [
          'Inter',
          '-apple-system',
          'BlinkMacSystemFont',
          '"Segoe UI"',
          'Roboto',
          'sans-serif'
        ],
        mono: [
          'JetBrains Mono',
          'ui-monospace',
          'SFMono-Regular',
          'Menlo',
          'monospace'
        ]
      },
      borderRadius: {
        'xs': '4px',
        'sm': '6px',
        'DEFAULT': '8px',
        'md': '8px',
        'lg': '10px',
        'xl': '12px',
        '2xl': '16px',
      },
      boxShadow: {
        'subtle': '0 1px 2px 0 rgba(15, 23, 42, 0.05)',
        'elevated': '0 4px 6px -1px rgba(15, 23, 42, 0.06), 0 2px 4px -2px rgba(15, 23, 42, 0.04)',
        'card': '0 1px 3px 0 rgba(15, 23, 42, 0.04), 0 1px 2px -1px rgba(15, 23, 42, 0.03)',
        'dropdown': '0 10px 15px -3px rgba(15, 23, 42, 0.08), 0 4px 6px -4px rgba(15, 23, 42, 0.04)',
        'drawer': '-4px 0 24px -2px rgba(15, 23, 42, 0.08)',
        'glow-blue': '0 0 15px -2px rgba(37, 99, 235, 0.15)',
      }
    },
  },
  plugins: [],
}
