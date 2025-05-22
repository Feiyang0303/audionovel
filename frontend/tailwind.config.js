/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      animation: {
        'gradient-shift': 'gradient-shift 15s ease infinite',
        'gradient-shift-reverse': 'gradient-shift-reverse 20s ease infinite',
        'float-1': 'float-1 8s ease-in-out infinite',
        'float-2': 'float-2 12s ease-in-out infinite',
        'float-3': 'float-3 10s ease-in-out infinite',
        'orb-1': 'orb-1 20s ease-in-out infinite',
        'orb-2': 'orb-2 25s ease-in-out infinite',
        'orb-3': 'orb-3 30s ease-in-out infinite',
      },
      keyframes: {
        'gradient-shift': {
          '0%': { backgroundPosition: '0% 50%' },
          '50%': { backgroundPosition: '100% 50%' },
          '100%': { backgroundPosition: '0% 50%' },
        },
        'gradient-shift-reverse': {
          '0%': { backgroundPosition: '100% 50%' },
          '50%': { backgroundPosition: '0% 50%' },
          '100%': { backgroundPosition: '100% 50%' },
        },
        'float-1': {
          '0%, 100%': { transform: 'translate(0, 0) rotate(0deg)' },
          '25%': { transform: 'translate(100px, -50px) rotate(90deg)' },
          '50%': { transform: 'translate(50px, 100px) rotate(180deg)' },
          '75%': { transform: 'translate(-50px, 50px) rotate(270deg)' },
        },
        'float-2': {
          '0%, 100%': { transform: 'translate(0, 0) rotate(0deg)' },
          '25%': { transform: 'translate(-100px, 50px) rotate(-90deg)' },
          '50%': { transform: 'translate(-50px, -100px) rotate(-180deg)' },
          '75%': { transform: 'translate(50px, -50px) rotate(-270deg)' },
        },
        'float-3': {
          '0%, 100%': { transform: 'translate(0, 0) rotate(0deg)' },
          '25%': { transform: 'translate(50px, 100px) rotate(45deg)' },
          '50%': { transform: 'translate(-100px, 50px) rotate(90deg)' },
          '75%': { transform: 'translate(-50px, -100px) rotate(135deg)' },
        },
        'orb-1': {
          '0%, 100%': { transform: 'translate(0, 0) scale(1)' },
          '50%': { transform: 'translate(50px, 30px) scale(1.2)' },
        },
        'orb-2': {
          '0%, 100%': { transform: 'translate(0, 0) scale(1.1)' },
          '50%': { transform: 'translate(-30px, 50px) scale(0.9)' },
        },
        'orb-3': {
          '0%, 100%': { transform: 'translate(0, 0) scale(0.9)' },
          '50%': { transform: 'translate(30px, -30px) scale(1.1)' },
        },
      },
    },
  },
  plugins: [],
}

