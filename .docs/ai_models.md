# AI Models & Data Gathering Specifications

This document outlines the machine learning models utilized by **Jinie**, their data compilation methods, and validation profiles.

---

## 🤖 AI Models Summary

| Model Identifier | Core Responsibility | Architecture & Base | Dataset Size | Data Partitioning |
| :--- | :--- | :--- | :--- | :--- |
| **NLP Intake Recommender** | Extracts page requirements, styling choices, features, and target business domains from natural language prompts. | Fine-tuned `DistilBERT` | 500–800 descriptions | 80% Train / 10% Val / 10% Test |
| **Layout Recommender** | Selects and structures component configurations matching the target business domains. | `Random Forest` | 300–500 layout logs | 80% Train / 10% Val / 10% Test |
| **Component Code Generator** | Outputs structured React Native component code matching visual token patterns. | Fine-tuned `CodeT5-small` | 100–200 curated component-code pairs | Custom curation |

---

## 📊 Data Gathering & Curation Approach

### 1. NLP Intake Model (DistilBERT)
* **Dataset Composition**: 500–800 business descriptions written manually by the team, covering 10–15 e-commerce categories common in Pakistan (clothing, food, electronics, accessories, furniture, beauty, bookshops, mobile repair, jewellery, digital services).
* **Language Support**: Includes formal English, formal Urdu, and mixed code-switching (Roman Urdu/English) to handle colloquial local input.
* **Labeling Layout**: Tagged with: `business_type`, `pages_required` (multi-label), `features_required` (multi-label), and `style_preference`.
* **Augmentation**: Paraphrasing variations are applied to scale the diversity of the inputs.

### 2. UI Layout Recommender (Random Forest)
* **Dataset Composition**: 300–500 e-commerce screen layout logs extracted from Figma Community templates and Dribbble design portfolios.
* **Tabular Features**: Suited for `scikit-learn` training. Features include business type, page type, components present, and layout style, mapping to a unique template ID.
* **Tuning**: K-Fold cross-validation is used to optimize hyperparameter ranges.

### 3. Component Code Generator (CodeT5-small)
* **Dataset Composition**: 100–200 manual pairs consisting of a natural language description of a UI component and its corresponding React Native (with Expo) TSX component code block.
* **Core Components Covered**: 15–20 e-commerce components (product card, hero banner, cart item, category chip, checkout buttons, search bar, discount badges, and image galleries).
* **Variability**: 5–10 phrasing descriptions are mapped to each component to improve training generalization limits.

---

## 📚 References

- **React Native & Expo Documentation**: [reactnative.dev](https://reactnative.dev) & [docs.expo.dev](https://docs.expo.dev) (Used for component trees, state management, and Expo configuration files).
- **DistilBERT Base**: Sanh, V. et al. (2019). *DistilBERT, a distilled version of BERT: smaller, faster, cheaper and lighter*. arXiv:1910.01108.
- **CodeT5 Base**: Wang, Y. et al. (2021). *CodeT5: Identifier-aware Unified Pre-trained Encoder-Decoder Models for Code Understanding and Generation*. EMNLP 2021.
- **Random Forest Foundations**: Breiman, L. (2001). *Random Forests*. Machine Learning, 45(1), 5–32.
- **Software Engineering Conventions**: Sommerville, I. (2016). *Software Engineering (10th ed.)*. Pearson.
