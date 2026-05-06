const nivoColor = (token) => `rgb(var(--nivo-${token}) / <alpha-value>)`;

/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ['selector', ':root[data-theme="dark"]'],
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        // Nivo design system:
        // 90% neutral (ink/paper/stone/cloud), 5-10% forest accent.
        nivo: {
          ink: nivoColor('ink'),
          paper: nivoColor('paper'),
          stone: nivoColor('stone'),
          'stone-soft': nivoColor('stone-soft'),
          mist: nivoColor('mist'),
          cloud: nivoColor('cloud'),
          'cloud-soft': nivoColor('cloud-soft'),
          forest: nivoColor('forest'),
          'forest-soft': nivoColor('forest-soft'),
          line: nivoColor('line'),
        },
      },
      boxShadow: {
        card:
          '0 1px 2px rgb(var(--nivo-shadow) / 0.06), 0 8px 32px rgb(var(--nivo-shadow) / 0.12)',
        subtle: '0 1px 0 rgb(var(--nivo-shadow) / 0.06)',
        forest: '0 8px 24px rgb(var(--nivo-forest) / 0.22)',
      },
      backgroundImage: {
        'nivo-grid':
          'linear-gradient(rgb(var(--nivo-grid-line) / 0.04) 1px, transparent 1px), linear-gradient(90deg, rgb(var(--nivo-grid-line) / 0.04) 1px, transparent 1px)',
        'nivo-grid-fine':
          'linear-gradient(rgb(var(--nivo-grid-line) / 0.025) 1px, transparent 1px), linear-gradient(90deg, rgb(var(--nivo-grid-line) / 0.025) 1px, transparent 1px)',
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
