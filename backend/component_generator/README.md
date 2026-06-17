# Backend Component Generator Module

The Component Generator takes two inputs:
1. Design preferences (colors, typography, layout mode) from the frontend token configuration.
2. The sitemap from the SRS Generator.

It then produces a set of reusable, independently testable UI components (buttons, navbars, cards, fields) styled to match requirements.

## Submodules

### 1. Component Generator Core (`generator.py`)
Applies design token classes and structures widget layouts for each screen component using layout recommendation logic (e.g. Random Forest layout recommender). Stamps each component with its unique Traceability ID.
