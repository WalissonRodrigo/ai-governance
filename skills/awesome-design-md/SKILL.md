---
name: awesome-design-md
description: Architectural specifications for UI/UX, Design Systems, Design Tokens, and style guides in standardized Markdown (DESIGN.md / STYLEGUIDE.md).
metadata:
  version: "2.1.0"
  audience: developers
---

# Awesome Design MD — Architectural UI & Design System Specs

Operate as a Frontend Architect and Design Systems Specialist. Standardize interface contracts, design tokens, and layout guidelines inside high-density `DESIGN.md` or `STYLEGUIDE.md` files without verbose boilerplate.

## When to Use
- Starting or refactoring web, mobile, or desktop application UIs.
- Defining semantic Design Tokens (colors, typography, spacing, shadows, radii).
- Documenting component interaction matrices and visual consistency rules.
- Reconciling a new product UI against a reference design system.

## Standard `DESIGN.md` Structure

### 1. Design Tokens (Three-Layer Architecture)
Tokens are structured in three layers so primitives stay reusable, semantics carry intent, and components bind both:

1. **Primitive** — raw design values (`px`, `rem`, hex colors): `--space-4: 4px`, `--color-blue-600: #2563eb`.
2. **Semantic** — abstractions giving the UI meaning: `--color-primary`, `--spacing-medium`.
3. **Component** — composites that bind primitives and semantics to a specific component: `--button-primary-bg`.

```markdown
## 1. Design Tokens

### Primitives
- `--space-4`: 4px
- `--radius-sm`: 4px
- `--border-width`: 1px

### Semantic Tokens
| Token | Light Value | Dark Value | Intended Usage |
|---|---|---|---|
| `--color-bg-primary` | `#ffffff` | `#0f172a` | Main page background |
| `--color-bg-surface` | `#f8fafc` | `#1e293b` | Cards, modals, and containers |
| `--color-brand-primary`| `#2563eb` | `#3b82f6` | Primary actions and active links |
| `--color-text-main` | `#0f172a` | `#f8fafc` | High-contrast headers and body |
| `--color-text-muted` | `#64748b` | `#94a3b8` | Subtitles, placeholders, and captions |
| `--color-feedback-err` | `#dc2626` | `#ef4444` | Form errors and critical alerts |

### Component Tokens
- `--button-primary-bg`: var(--color-brand-primary)
- `--card-shadow`: 0 1px 3px rgba(0,0,0,0.1)

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

## Validating a Design System with `preview.html`
Generate a browser preview from the `DESIGN.md` to validate the design system visually before or during implementation:

1. Create a `preview/` directory at the project root.
2. Copy the generated `DESIGN.md` into it as `preview/DESIGN.md`.
3. Render the markdown to HTML with `markdown-it-cli`:
```bash
rtk npx markdown-it-cli -i preview/DESIGN.md -o preview/preview.html --html
```
4. Open `preview/preview.html` in the browser.
5. Optional: emit CSS from the tokens with Style Dictionary and import it into the preview:
```bash
rtk npx style-dictionary build --config style-dictionary.config.js
```
   → produces `preview/tokens.css`, which can be linked from `preview.html`.

For an unimplemented or unfamiliar product, anchor token decisions to a reference design system (e.g., Shopify, Stripe, or Adobe) so palette, type scale, and spacing follow a proven rhythm instead of ad-hoc choices.