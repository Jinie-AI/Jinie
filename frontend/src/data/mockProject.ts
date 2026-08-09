import type {
    SRSData,
    DesignData,
    PreviewData,
    DeploymentData,
} from "../types/project.types";

export const mockSRS: SRSData = {
    title: "Grocery Delivery App",

    description:
        "A grocery delivery application where users can browse products, place orders, and track deliveries.",

    functionalRequirements: [
        {
            id: "FR-001",
            description: "Users can browse available vegetables and fruits.",
            priority: "High",
        },
        {
            id: "FR-002",
            description: "Users can add products to an order.",
            priority: "Critical",
        },
        {
            id: "FR-003",
            description: "Users can place an order for delivery.",
            priority: "Critical",
        },
        {
            id: "FR-004",
            description: "Users can track their delivery.",
            priority: "High",
        },
    ],

    nonFunctionalRequirements: [
        {
            id: "NFR-001",
            category: "Performance",
            description: "Product listings should load quickly.",
        },
        {
            id: "NFR-002",
            category: "Security",
            description: "User data must be securely handled.",
        },
        {
            id: "NFR-003",
            category: "Accessibility",
            description: "The application should support accessible navigation.",
        },
    ],

    screens: [
        {
            id: "SCR-001",
            name: "Main Feed",
            route: "/main",
        },
        {
            id: "SCR-002",
            name: "Order",
            route: "/order",
        },
        {
            id: "SCR-003",
            name: "Tracking",
            route: "/track",
        },
        {
            id: "SCR-004",
            name: "Order History",
            route: "/history",
        },
    ],
};

export const mockDesign: DesignData = {
    framework: "React Native",
    components: [
        "AppShell",
        "Header",
        "SearchBar",
        "ProductCard",
        "ProductList",
        "OrderSummary",
        "TrackingCard",
        "BottomNavigation",
    ],
    typography: "Inter",
    spacing: "8pt system",
    radius: "12px",
};

export const mockPreview: PreviewData = {
    screens: [
        "Main Feed",
        "Order",
        "Tracking",
        "Order History",
    ],
};

export const mockDeployment: DeploymentData = {
    url: "https://grocery-app.jinie.app",
};