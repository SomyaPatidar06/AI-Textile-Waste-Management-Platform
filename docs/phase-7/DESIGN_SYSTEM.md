# Phase 7 Design System Specification — Liquid Glass Industrial Intelligence

**Project:** AI Textile Waste Management Platform  
**Target Architecture:** React 18, Vite 5.4, Tailwind CSS 3.4  
**Design Standard:** Modern Liquid Glass & Precision Industrial Analytics  
**Version:** v2.1.0  
**Status:** **ACTIVE DESIGN SYSTEM**

---

## 1. Design Philosophy

The Liquid Glass design system transforms the AI Textile Waste Intelligence Platform from a generic template into a sophisticated, distinctive industrial intelligence workstation. The aesthetic evokes optical clarity, circular sustainability, and technological depth.

Key visual attributes:
- **Optical Depth:** Semi-transparent frosted glass layers with multi-scale blur, separating background ambient mesh from high-priority foreground data.
- **Specular Highlights:** Subtle 1px translucent top gradients simulating light reflecting across glass borders.
- **Textile Lattice Texture:** Ultra-subtle geometric grid backgrounds referencing interwoven warp and weft yarns.
- **Zero Decorative Noise:** Elimination of emojis, excessive neon glowing borders, and ungrounded decorative charts in favor of clean tabular typography, standard Lucide iconography, and purposeful visualizations.

---

## 2. Color Palette & Semantic Tokens

```
+-----------------------------------------------------------------------------------+
| BASE SURFACES                                                                     |
|   Midnight Graphite 950 : #040D12   (Deep base canvas background)                 |
|   Midnight Graphite 900 : #081721   (Primary container backdrop)                  |
|   Midnight Graphite 850 : #0D1F2B   (Liquid glass elevated surface)               |
|                                                                                   |
| BRAND ACCENTS & OPTICAL TEAL                                                      |
|   Deep Teal 800         : #173943   (Navigation headers & primary borders)        |
|   Emerald Accent        : #369A87   (Primary interactive action & AI confidence)  |
|   Sea Glass 300         : #B9E5DF   (Secondary labels, highlights & borders)      |
|   Frost White 100       : #EEF5F3   (Primary typography & active headers)         |
+-----------------------------------------------------------------------------------+
```

### Color Token Mapping

| Token Name | Hex Code | Opacity / Tailwind Class | Primary Usage |
| :--- | :---: | :---: | :--- |
| `midnight-950` | `#040D12` | `bg-midnight-950` | Primary application canvas |
| `midnight-900` | `#081721` | `bg-midnight-900/60` | Input fields, table rows |
| `deepTeal-800` | `#173943` | `bg-deepTeal-800` | Table headers, stat icons |
| `emerald-600` | `#369A87` | `bg-emerald-600` | Primary CTA buttons, circularity badges |
| `seaglass-300` | `#B9E5DF` | `text-seaglass-300` | Subtitles, secondary indicators |
| `frost-100` | `#EEF5F3` | `text-frost-100` | Headings, primary numeric values |
| `border-glass` | `rgba(185, 229, 223, 0.12)` | `border-white/10` | Universal translucent surface borders |

---

## 3. Glass Surface Architecture

### CSS Implementation
```css
/* Standard Liquid Glass */
.liquid-glass {
  background: rgba(13, 31, 43, 0.68);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid rgba(185, 229, 223, 0.12);
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
  position: relative;
}

/* Elevated Liquid Glass (Modals, Overlays, Active Cards) */
.liquid-glass-elevated {
  background: rgba(18, 42, 58, 0.78);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(185, 229, 223, 0.18);
  box-shadow: 0 16px 40px -8px rgba(0, 0, 0, 0.5);
  position: relative;
}

/* Top Specular Edge Highlight */
.glass-specular::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent 0%, rgba(185, 229, 223, 0.3) 50%, transparent 100%);
  pointer-events: none;
}
```

### Usability & Contrast Safeguard
- Dense data tables and text bodies are rendered with **high contrast and zero cell transparency** (`bg-midnight-900/40` on `text-frost-100`) to guarantee WCAG AA text legibility.
- Glass effects are strictly reserved for structural cards, sidebars, modal overlays, and status badges.

---

## 4. Typography Hierarchy

| Level | Size / Weight | Line Height | Tracking | Usage |
| :--- | :--- | :--- | :--- | :--- |
| **Display Heading** | 24px (1.5rem) / 800 | 1.2 | `-0.025em` | Page Titles, Hero Certifications |
| **Section Heading** | 18px (1.125rem) / 700 | 1.3 | `-0.02em` | Studio Panels, Dashboard Groups |
| **Card Header** | 14px (0.875rem) / 700 | 1.4 | `-0.01em` | Modal titles, Card titles |
| **Label / Category** | 11px (0.6875rem) / 600 | 1.4 | `+0.05em` | Monospace uppercase tags |
| **Body Text** | 13px (0.8125rem) / 400 | 1.5 | `normal` | Explanations, table descriptions |
| **Numeric KPI** | 28px - 32px / 800 | 1.0 | `-0.03em` | Monospace tabular figures (`tabular-nums`) |

---

## 5. Reusable Component Catalog

The design system introduces 10 reusable UI primitives in `frontend/src/components/ui/`:

1. **`BrandLogo.jsx`:** Scalable SVG vector depicting interwoven warp and weft yarn strands forming an infinite circular loop.
2. **`GlassPanel.jsx`:** Universal container with `liquid-glass`, translucent borders, and specular highlight.
3. **`GlassCard.jsx`:** Interactive card with smooth hover elevation and border sheen.
4. **`StatCard.jsx`:** High-precision KPI card with title, large formatted metric, trend pill, and accent icon badge.
5. **`StatusBadge.jsx`:** Unified badge supporting 4 batch lifecycle statuses, 5 circularity categories, 4 roles, and 3 defect severities.
6. **`DataTable.jsx`:** Opaque-cell tabular component with sticky glass header, hover highlight, and pagination controls.
7. **`GlassModal.jsx`:** Accessible dialog overlay with backdrop blur, smooth animation, focus trap, and ESC close.
8. **`FormField.jsx`:** Accessible input, select, and textarea fields with focus glow and error states.
9. **`LoadingSkeleton.jsx`:** Shimmer pulse loading placeholders.
10. **`EmptyState.jsx`:** Clean graphic placeholder for zero-result states.

---

## 6. Motion & Accessibility

- **Subtle Transitions:** Micro-interactions utilize `cubic-bezier(0.16, 1, 0.3, 1)` with durations between $150\text{ ms}$ and $250\text{ ms}$.
- **Reduced Motion Support:** All animations and transitions automatically collapse to instantaneous states when `@media (prefers-reduced-motion: reduce)` is active.
- **Keyboard Focus:** Every interactive control features a visible, high-contrast emerald focus ring (`outline: 2px solid #369A87; outline-offset: 2px;`).
