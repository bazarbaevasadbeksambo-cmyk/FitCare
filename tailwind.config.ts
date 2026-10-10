import type { Config } from 'tailwindcss';
import { colors, radius, fontStack } from './src/config/tokens';

export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors,
      borderRadius: radius,
      fontFamily: { sans: fontStack },
      fontSize: {
        title: ['28px', { lineHeight: '34px', fontWeight: '700' }],
        subtitle: ['20px', { lineHeight: '26px', fontWeight: '700' }],
        body: ['16px', { lineHeight: '22px' }],
        caption: ['13px', { lineHeight: '18px' }],
        button: ['17px', { lineHeight: '22px', fontWeight: '700' }],
      },
      spacing: { screen: '20px' },
      keyframes: {
        breathe: { '0%,100%': { transform: 'scale(1)' }, '50%': { transform: 'scale(1.015)' } },
        bounce1: { '0%,100%': { transform: 'scale(1)' }, '50%': { transform: 'scale(1.05)' } },
        pop: { '0%': { transform: 'scale(0.6)', opacity: '0' }, '70%': { transform: 'scale(1.05)', opacity: '1' }, '100%': { transform: 'scale(1)' } },
        slideIn: { '0%': { transform: 'translateX(var(--slide-from, 40px))', opacity: '0' }, '100%': { transform: 'translateX(0)', opacity: '1' } },
        fadeIn: { '0%': { opacity: '0' }, '100%': { opacity: '1' } },
        confetti: { to: { transform: 'translateY(110vh) rotate(720deg)' } },
        flameUp: { '0%': { transform: 'scale(0.3) translateY(30px)', opacity: '0' }, '60%': { transform: 'scale(1.2) translateY(-6px)', opacity: '1' }, '100%': { transform: 'scale(1)' } },
        flicker: { '0%,100%': { transform: 'scale(1) rotate(-2deg)' }, '50%': { transform: 'scale(1.08) rotate(2deg)' } },
        shake: { '0%,100%': { transform: 'translateX(0)' }, '20%,60%': { transform: 'translateX(-6px)' }, '40%,80%': { transform: 'translateX(6px)' } },
        shimmer: { '0%': { backgroundPosition: '-200px 0' }, '100%': { backgroundPosition: '200px 0' } },
      },
      animation: {
        breathe: 'breathe 3s ease-in-out infinite',
        bounce1: 'bounce1 250ms ease-out',
        pop: 'pop 220ms ease-out both',
        slideIn: 'slideIn 200ms ease-out both',
        fadeIn: 'fadeIn 200ms ease-out both',
        shimmer: 'shimmer 1.2s linear infinite',
        enter: 'fadeIn 150ms ease-out both, bounce1 250ms ease-out',
        confetti: 'confetti 2s linear forwards',
        flameUp: 'flameUp 600ms cubic-bezier(.2,1.4,.4,1) both',
        flicker: 'flicker 900ms ease-in-out infinite',
        'enter-shake': 'fadeIn 150ms ease-out both, shake 400ms ease-in-out',
      },
    },
  },
  plugins: [],
} satisfies Config;
