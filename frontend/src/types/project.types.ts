export type WorkflowStage =
    | "idle"
    | "srs"
    | "design"
    | "preview"
    | "deployment";

export interface FunctionalRequirement {
    id: string;
    description: string;
    priority: string;
}

export interface NonFunctionalRequirement {
    id: string;
    category: string;
    description: string;
}

export interface Screen {
    id: string;
    name: string;
    route: string;
}

export interface SRSData {
    title: string;
    description: string;
    functionalRequirements: FunctionalRequirement[];
    nonFunctionalRequirements: NonFunctionalRequirement[];
    screens: Screen[];
}

export interface DesignData {
    framework: string;
    components: string[];
    typography: string;
    spacing: string;
    radius: string;
}

export interface PreviewData {
    screens: string[];
}

export interface DeploymentData {
    url: string;
}