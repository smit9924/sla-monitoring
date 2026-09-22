/**
 * Fixed-order categorical palette for multi-service charts (per-service line
 * colors). Order is the CVD-safety mechanism, not cosmetic -- assign by
 * index and never re-cycle/re-sort once assigned, so a given service keeps
 * the same color across re-renders.
 */
export const CHART_CATEGORICAL_PALETTE = [
  '#2a78d6', // blue
  '#eb6834', // orange
  '#1baf7a', // aqua
  '#eda100', // yellow
  '#e87ba4', // magenta
  '#008300', // green
  '#4a3aa7', // violet
  '#e34948', // red
] as const;
