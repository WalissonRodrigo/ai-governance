---
name: ui-ux-pro-max
description: Production-grade UI/UX engineering engine. Enforces WCAG 2.2 AA accessibility, cohesive Design Systems, exhaustive component state modeling, and performance-optimized micro-interactions.
metadata:
  version: "2.0.0"
  audience: developers
---

# UI/UX Pro Max — High-Performance Design & Frontend Architecture

Operate as a Lead Product Designer and Senior Frontend Architect. Design and implement UI components that are visually distinct, fully accessible, and structurally bulletproof on the first iteration.

## 1. Visual Hierarchy & Spatial Grid
- **The 60-30-10 Rule**: 60% dominant neutral background, 30% structural/card layer, 10% high-contrast brand/action accent.
- **8pt Fluid Grid**: Strictly use 4px/8px multiples for margins, paddings, and layout gaps (`4, 8, 12, 16, 24, 32, 48, 64px`).
- **Typography Rhythm**: Clear typographic hierarchy (H1 -> H2 -> Body -> Caption) with line-height ratios between `1.3` (headings) and `1.5-1.6` (body).

---

## 2. Exhaustive Component State Matrix
Every interactive component (buttons, inputs, select menus, dialogs, cards) MUST implement 8 distinct states:

| State | Visual Requirement | Accessibility Contract |
|---|---|---|
| **Default** | Base styling with sharp baseline contrast | Standard semantic markup (`<button>`, `<input>`) |
| **Hover** | Subtle lift (`translateY(-1px)`) or background tint shift | Not triggered on touch devices |
| **Active / Pressed** | Tactile feedback (`scale(0.98)` or inset shadow) | Immediate responsive transition |
| **Focus-Visible** | High-contrast 2px solid outline with `outline-offset: 2px` | Mandatory for keyboard navigation (`:focus-visible`) |
| **Disabled** | 50% opacity, distinct mute color, no hover elevation | `disabled`, `aria-disabled="true"`, `pointer-events: none` |
| **Loading** | Skeleton shimmer or inline SVG spinner | `aria-busy="true"`, retains component dimensions |
| **Empty** | Meaningful empty state graphic + clear CTA message | Clear landmark role (`role="region"`) |
| **Error** | Semantic red boundary/text with persistent alert badge | `aria-invalid="true"`, `aria-describedby="err-id"` |

---

## 3. Accessibility & Compliance (WCAG 2.2 AA)
- **Contrast Thresholds**: Minimum **4.5:1** for regular text; **3:1** for large text (>=18pt or 14pt bold) and interactive UI borders.
- **Keyboard Traversal**: Full navigation support via `Tab`, `Shift+Tab`, `Enter`, `Space`, and `Escape` for dismissal.
- **Dynamic Semantics**: Explicit ARIA states (`aria-expanded`, `aria-controls`, `aria-live="polite"`, `role="dialog"`).

---

## 4. Modern CSS & Interaction Directives
- **Zero Hardcoded Magic Numbers**: Rely on semantic CSS custom properties or Tailwind design tokens.
- **Micro-Interactions**: Use modern cubic-bezier easing (`cubic-bezier(0.16, 1, 0.3, 1)`) with durations between `150ms` and `250ms`.
- **Hardware Acceleration**: Confine animations to `transform` and `opacity` to avoid layout reflows.