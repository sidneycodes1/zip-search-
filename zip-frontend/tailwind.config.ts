import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/features/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        zip: {
          background: '#0A0A0A',
          surface: '#141414',
          border: '#2A2A2A',
          text: '#F5F5F5',
          muted: '#888888',
          accent: '#E8FF00',
          error: '#FF4444',
          success: '#22C55E',
        },
      },
      fontFamily: {
        mono: ['Space Mono', 'IBM Plex Mono', 'monospace'],
        sans: ['Inter', 'Geist', 'sans-serif'],
      },
      borderRadius: {
        DEFAULT: '4px',
        md: '4px',
        lg: '4px',
        xl: '4px',
        '2xl': '4px',
        '3xl': '4px',
      },
    },
  },
  plugins: [],
}
export default config
