import type { ScreenConfigData } from "../live_review_panel/HtmlScreenMockup";
import type { RetrievedComponent } from "./RetrievedComponents";

export type Requirement = {
  id: string;
  page: string;
  text: string;
  approved: boolean;
};
export type Design = {
  primary: string;
  secondary?: string;
  accent?: string;
  bodyFont?: string;
  navigation?: string;
  theme: string;
  font: string;
  layout: string;
};
export type Project = {
  api_plan?: {
    model: string;
    summary: string;
    questions: string[];
    unsupported_features: string[];
    screen_configs?: Record<string, ScreenConfigData>;
  } | null;
  id: string;
  name: string;
  prompt: string;
  status: string;
  stage: string;
  error?: string;
  revision: number;
  build_revision: number | null;
  renderer_version?: number;
  design: Design;
  requirements: Requirement[];
  screen_configs?: Record<string, ScreenConfigData>;
  spec: {
    business: string;
    business_label?: string;
    warnings: string[];
    pages: string[];
    products?: Array<{
      id: string;
      name: string;
      price: number;
      category?: string;
      description?: string;
      image_url?: string;
      image_credit?: { name: string; url: string; source_url: string };
      icon?: string;
      badge?: string;
      rating?: number;
    }>;
    screen_configs?: Record<string, ScreenConfigData>;
    rag_components?: RetrievedComponent[];
  };
  models: Record<string, string>;
  model_warnings: string[];
  recommendations: { id: string; score: number | null; source: string }[];
  events: { id: number; stage: string; message: string; time: string }[];
  tests: { id: string; name: string; status: string; kind: string }[];
  traceability: {
    requirement: string;
    page: string;
    files: string[];
    components: string[];
    test: string;
  }[];
  components: {
    id: string;
    name: string;
    source: string;
    used: boolean;
    file: string;
  }[];
  deployment: { url: string; time: string } | null;
  feedback: { id: string; text: string; requirement_id: string }[];
  nfr: { id: string; category?: string; text: string }[];
  rag_components?: RetrievedComponent[];
};
export type Summary = { id: string; name: string; status: string; updated_at?: string };
