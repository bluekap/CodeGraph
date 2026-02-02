/**
 * Light and dark mode for CodeGraph UI and graph
 */
export type ThemeId = 'light' | 'dark';

export interface GraphTheme {
  getComplexityColor: (complexity: number) => string;
  linkStroke: string;
  arrowFill: string;
  nodeStroke: string;
  highlightStroke: string;
  labelColor: string;
  graphBg: string;
  graphBorder: string;
  tooltipBg: string;
  tooltipText: string;
}

function lerp(a: number, b: number, t: number) {
  return Math.round(a + (b - a) * t);
}
// Blue scale: low complexity = light blue → high = deep blue
function complexityToColor(complexity: number, low: [number, number, number], mid: [number, number, number], high: [number, number, number]): string {
  const t = Math.min(1, Math.max(0, complexity / 20));
  const [r, g, b] = t < 0.5
    ? [lerp(low[0], mid[0], t * 2), lerp(low[1], mid[1], t * 2), lerp(low[2], mid[2], t * 2)]
    : [lerp(mid[0], high[0], (t - 0.5) * 2), lerp(mid[1], high[1], (t - 0.5) * 2), lerp(mid[2], high[2], (t - 0.5) * 2)];
  return `rgb(${r},${g},${b})`;
}

export const graphThemes: Record<ThemeId, GraphTheme> = {
  light: {
    getComplexityColor: (c) => complexityToColor(c, [147, 197, 253], [96, 165, 250], [29, 78, 216]),
    linkStroke: '#60a5fa',
    arrowFill: '#2563eb',
    nodeStroke: '#eff6ff',
    highlightStroke: '#1d4ed8',
    labelColor: '#1e3a8a',
    graphBg: '#eff6ff',
    graphBorder: '#bfdbfe',
    tooltipBg: 'rgba(30, 58, 138, 0.95)',
    tooltipText: '#f0f9ff',
  },
  dark: {
    getComplexityColor: (c) => complexityToColor(c, [96, 165, 250], [59, 130, 246], [30, 64, 175]),
    linkStroke: '#475569',
    arrowFill: '#60a5fa',
    nodeStroke: '#334155',
    highlightStroke: '#93c5fd',
    labelColor: '#e2e8f0',
    graphBg: '#0f172a',
    graphBorder: '#1e293b',
    tooltipBg: 'rgba(15, 23, 42, 0.98)',
    tooltipText: '#e2e8f0',
  },
};
