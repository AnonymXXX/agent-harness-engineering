---
version: alpha
name: Project Design System
description: Visual identity and implementation guidance for this project.
colors:
  primary: "#111827"
  secondary: "#6B7280"
  background: "#FFFFFF"
  surface: "#F9FAFB"
  border: "#E5E7EB"
  accent: "#2563EB"
  danger: "#DC2626"
typography:
  heading-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: 700
    lineHeight: 1.2
  heading-md:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: 650
    lineHeight: 1.25
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: 400
    lineHeight: 1.5
  label-sm:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: 500
    lineHeight: 1.4
spacing:
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 32px
rounded:
  sm: 4px
  md: 8px
  lg: 12px
components:
  button-primary:
    backgroundColor: "{colors.accent}"
    textColor: "#FFFFFF"
    rounded: "{rounded.md}"
    padding: 12px
  button-danger:
    backgroundColor: "{colors.danger}"
    textColor: "#FFFFFF"
    rounded: "{rounded.md}"
    padding: 12px
  card:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.primary}"
    rounded: "{rounded.md}"
    padding: 16px
  divider:
    backgroundColor: "{colors.border}"
    height: 1px
---

## Overview

This file is a starting template, not the final project design system.
Before using it for a real project, inspect the existing pages, components,
style files, theme configuration, and product context. Replace the placeholder
tokens and prose with the project's actual visual language.

Describe the product's visual character, target users, density, and tone using
specific references. Avoid vague-only adjectives such as "modern", "clean", or
"premium" unless they are tied to concrete interface behavior.

## Colors

Replace the default colors with values found in the existing UI or the intended
brand direction.

- **Primary** is for main text, headings, and high-emphasis interface elements.
- **Secondary** is for captions, metadata, disabled text, and quiet borders.
- **Background** is the page foundation.
- **Surface** is for panels, cards, tables, and elevated content areas.
- **Border** is for dividers, outlines, and low-emphasis structure.
- **Accent** is for primary actions, focus states, and selected states.
- **Danger** is reserved for destructive actions and error states.

## Typography

Replace font families and sizes with the project's real typography. If the app
already has a component library or theme scale, mirror that scale rather than
inventing a new one.

Use headings for hierarchy, body text for readable content, and labels for
forms, metadata, toolbar controls, and dense operational surfaces.

## Layout

Describe the project's spacing rhythm, page width, grid behavior, mobile
breakpoints, and information density.

Prefer the existing layout model. For dashboards and admin tools, prioritize
scanability, repeat actions, and stable dimensions over decorative composition.

## Elevation & Depth

Describe how hierarchy is conveyed: borders, tonal surfaces, shadows, overlays,
or flat layers. Keep this aligned with the existing component system.

## Shapes

Describe radius, control shapes, card shape, modal shape, and any special
geometry. Do not introduce large or playful rounding unless it already belongs
to the product.

## Components

Describe expected behavior and styling for buttons, inputs, selects, tables,
cards, modals, tabs, navigation, empty states, and loading states.

Prefer existing reusable components and local patterns. If a component pattern
conflicts with this file, keep the established component behavior and update the
DESIGN.md draft to document the actual rule.

## Do's and Don'ts

- **Do** derive the final DESIGN.md from the project's existing UI and theme.
- **Do** keep the final file specific enough that another agent can follow it.
- **Do** preserve existing component conventions unless explicitly redesigning.
- **Do** document intentional constraints, not every possible bad design.
- **Don't** copy this template unchanged into a project as the final design system.
- **Don't** introduce a new visual language unless explicitly requested.
- **Don't** use decorative gradients, oversized hero sections, or unrelated illustration styles unless the product requires them.
