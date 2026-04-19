/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        // Nivo design system:
        // 90% neutral (ink/paper/stone/cloud), 5-10% forest accent.
        nivo: {
          ink: '#000000',
          paper: '#FFFFFF',
          stone: '#4A4A4A',
          'stone-soft': '#6B6B6B',
          mist: '#9A9A9A',
          cloud: '#E5E5E5',
          'cloud-soft': '#F3F3F3',
          forest: '#1A3C34',
          'forest-soft': '#254F46',
          line: '#D4D4D4',
        },
      },
      boxShadow: {
        // card: primary content container
        // subtle: low-elevation separators / quiet panels
        // forest: reserved for accent CTA emphasis
        card: '0 1px 2px rgba(0, 0, 0, 0.04), 0 8px 32px rgba(0, 0, 0, 0.06)',
        subtle: '0 1px 0 rgba(0, 0, 0, 0.04)',
        forest: '0 8px 24px rgba(26, 60, 52, 0.18)',
      },
      backgroundImage: {
        // Editorial grids used as mathematical / cryptographic texture.
        'nivo-grid':
          'linear-gradient(rgba(0, 0, 0, 0.04) 1px, transparent 1px), linear-gradient(90deg, rgba(0, 0, 0, 0.04) 1px, transparent 1px)',
        'nivo-grid-fine':
          'linear-gradient(rgba(0, 0, 0, 0.025) 1px, transparent 1px), linear-gradient(90deg, rgba(0, 0, 0, 0.025) 1px, transparent 1px)',
      },
      backgroundSize: {
        grid: '64px 64px',
        'grid-fine': '32px 32px',
      },
      fontFamily: {
        // Display = premium/editorial headlines
        // Sans = body/UI
        // Mono = technical labels, timestamps, badges
        display: [
          '"Neue Haas Grotesk Display Pro"',
          '"Neue Haas Grotesk"',
          '"Inter Display"',
          'Inter',
          'ui-sans-serif',
          'system-ui',
          'sans-serif',
        ],
        sans: [
          'Inter',
          '"Inter Display"',
          'ui-sans-serif',
          'system-ui',
          '-apple-system',
          'BlinkMacSystemFont',
          'sans-serif',
        ],
        mono: ['"JetBrains Mono"', '"SF Mono"', 'Menlo', 'Consolas', 'monospace'],
      },
      letterSpacing: {
        // Tight tracking helps preserve the Apple/Cobre/Notion-inspired rhythm.
        tightest: '-0.035em',
        'tighter-1': '-0.025em',
      },
    },
  },
  plugins: [],
};
