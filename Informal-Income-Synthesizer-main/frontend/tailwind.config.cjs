/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  theme: {
    extend: {
      colors: {
        canvas: '#000000',
        surface: '#0A0A0A',
        card: '#121212',
        'card-hover': '#181818',
        'border-subtle': '#222222',
        'border-focus': '#333333',
        'border-strong': '#444444',
        accent: {
          DEFAULT: '#FFFFFF',
          hover: '#E5E5E5',
          muted: 'rgba(255, 255, 255, 0.1)',
        },
        'accent-dark': '#000000',
        positive: '#FFFFFF',
        caution: '#D4D4D8',
        negative: '#71717A',
        text: {
          primary: '#FFFFFF',
          secondary: '#A1A1AA',
          muted: '#71717A',
        }
      },
      fontFamily: {
        sans: ['Outfit', 'Plus Jakarta Sans', 'Inter', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'Space Grotesk', 'monospace'],
      },
      borderRadius: {
        '2xl': '16px',
        '3xl': '24px',
        pill: '9999px',
      },
      boxShadow: {
        'white-glow': '0 0 25px rgba(255, 255, 255, 0.15)',
        'card-subtle': '0 4px 24px rgba(0, 0, 0, 0.6)',
      }
    },
  },
  plugins: [],
};
