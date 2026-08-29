---
name: awesome-design-md
description: Architectural specifications for UI/UX, Design Systems, Design Tokens, and style guides in standardized Markdown (DESIGN.md / STYLEGUIDE.md).
metadata:
  version: "2.0.0"
  audience: developers
---

# Awesome Design MD — Architectural UI & Design System Specs

Operate as a Frontend Architect and Design Systems Specialist. Standardize interface contracts, design tokens, and layout guidelines inside high-density `DESIGN.md` or `STYLEGUIDE.md` files without verbose boilerplate.

## When to Use
- Starting or refactoring web, mobile, or desktop application UIs.
- Defining semantic Design Tokens (colors, typography, spacing, shadows, radii).
- Documenting component interaction matrices and visual consistency rules.

## Standard `DESIGN.md` Structure

### 1. Foundation Tokens
```markdown
## 1. Design Tokens

### Color Palette (Semantic Tokens)
| Token | Light Value | Dark Value | Intended Usage |
|---|---|---|---|
| `--color-bg-primary` | `#ffffff` | `#0f172a` | Main page background |
| `--color-bg-surface` | `#f8fafc` | `#1e293b` | Cards, modals, and containers |
| `--color-brand-primary`| `#2563eb` | `#3b82f6` | Primary actions and active links |
| `--color-text-main` | `#0f172a` | `#f8fafc` | High-contrast headers and body |
| `--color-text-muted` | `#64748b` | `#94a3b8` | Subtitles, placeholders, and captions |
| `--color-feedback-err` | `#dc2626` | `#ef4444` | Form errors and critical alerts |

### Typography Scale
| Level | Size / Line-Height | Weight | Applied Elements |
|---|---|---|---|
| Display | 2.25rem (36px) / 1.2 | Bold (700) | Hero headers |
| H1 | 1.5rem (24px) / 1.3 | SemiBold (600) | Page titles |
| H2 | 1.25rem (20px) / 1.4 | Medium (500) | Section and card headers |
| Body | 0.875rem (14px) / 1.5 | Regular (400) | Main content and inputs |
| Caption | 0.75rem (12px) / 1.4 | Regular (400) | Metadata and helper text |

### Spacing & Layout
- **Base Grid:** 8pt (`4px, 8px, 12px, 16px, 24px, 32px, 48px, 64px`)
- **Border Radii:** `sm: 4px`, `md: 8px`, `lg: 12px`, `full: 9999px`
- **Breakpoints:** `sm: 640px`, `md: 768px`, `lg: 1024px`, `xl: 1280px`
```

### 2. Component Blueprint Matrix
For every interactive UI component, explicitly define strict states:
- `Default`, `Hover`, `Active`, `Focus-Visible` (outline 2px), `Disabled`, `Loading`, `Empty`, `Error`.

### 3. Accessibility Guidelines (A11y)
- Minimum text contrast ratio: **4.5:1** (WCAG AA).
- Complete keyboard navigation support (`Tab`, `Shift+Tab`, `Enter`, `Space`, `Escape`).
- Semantic ARIA attributes (`aria-expanded`, `aria-label`, `aria-live`) where dynamicity exists.

## Token Economy
- Use dense Markdown tables instead of long descriptive paragraphs.
- Reuse token references instead of repeating raw hex values in code generation.