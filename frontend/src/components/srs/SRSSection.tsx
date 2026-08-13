import {
    Document,
    Packer,
    Paragraph,
    HeadingLevel,
} from "docx";

interface SRSSectionProps {
    srs: any;
    onApprove: () => void;
}

function getItems(data: any): any[] {
    if (!data) return [];
    if (Array.isArray(data)) return data;
    if (Array.isArray(data.requirements)) return data.requirements;
    if (Array.isArray(data.entities)) return data.entities;
    if (Array.isArray(data.nodes)) return data.nodes;
    if (Array.isArray(data.trees)) return data.trees;
    return [];
}

function displayItem(item: any): string {
    if (typeof item === "string") return item;
    if (!item) return "";

    return (
        item.description ||
        item.requirement ||
        item.name ||
        item.title ||
        item.screen_name ||
        item.entity_name ||
        JSON.stringify(item)
    );
}

function humanize(value: string): string {
    return value.replaceAll("_", " ");
}

export default function SRSSection({
    srs,
    onApprove,
}: SRSSectionProps) {
    const functionalRequirements = getItems(srs?.functional_requirements);
    const nonFunctionalRequirements = getItems(srs?.non_functional_requirements);
    const screens = getItems(srs?.sitemap);
    const entities = getItems(srs?.entities);
    const componentTrees = getItems(srs?.component_trees);

    const downloadSRS = async () => {
        try {
            const children: Paragraph[] = [];

            children.push(
                new Paragraph({
                    text: "Jinie",
                    heading: HeadingLevel.TITLE,
                }),
                new Paragraph({
                    text: "Software Requirements Specification",
                    heading: HeadingLevel.HEADING_1,
                }),
                new Paragraph({
                    text: "Generated automatically by Jinie from the user's project prompt.",
                })
            );

            children.push(
                new Paragraph({
                    text: "1. Functional Requirements",
                    heading: HeadingLevel.HEADING_1,
                }),
                new Paragraph({
                    text: "Features and actions the application should provide.",
                })
            );

            if (functionalRequirements.length > 0) {
                functionalRequirements.forEach((requirement: any, index: number) => {
                    children.push(
                        new Paragraph({
                            text: `FR-${String(index + 1).padStart(2, "0")}: ${displayItem(requirement)}`,
                            bullet: { level: 0 },
                        })
                    );
                });
            } else {
                children.push(
                    new Paragraph({
                        text: "No functional requirements generated.",
                    })
                );
            }

            children.push(
                new Paragraph({
                    text: "2. Non-Functional Requirements",
                    heading: HeadingLevel.HEADING_1,
                }),
                new Paragraph({
                    text: "Quality, performance, security and usability requirements for the application.",
                })
            );

            if (nonFunctionalRequirements.length > 0) {
                nonFunctionalRequirements.forEach((requirement: any, index: number) => {
                    children.push(
                        new Paragraph({
                            text: `NFR-${String(index + 1).padStart(2, "0")}: ${displayItem(requirement)}`,
                            bullet: { level: 0 },
                        })
                    );
                });
            } else {
                children.push(
                    new Paragraph({
                        text: "No non-functional requirements generated.",
                    })
                );
            }

            children.push(
                new Paragraph({
                    text: "3. Application Screens",
                    heading: HeadingLevel.HEADING_1,
                }),
                new Paragraph({
                    text: "Screens identified by Jinie for the application.",
                })
            );

            if (screens.length > 0) {
                screens.forEach((screen: any, index: number) => {
                    const screenName =
                        screen?.screen_name ||
                        screen?.name ||
                        screen?.title ||
                        `Screen ${index + 1}`;

                    const route = screen?.route
                        ? ` | Route: ${screen.route}`
                        : "";

                    const type = screen?.screen_type
                        ? ` | Type: ${screen.screen_type}`
                        : "";

                    children.push(
                        new Paragraph({
                            text: `${String(index + 1).padStart(2, "0")}. ${screenName}${route}${type}`,
                            bullet: { level: 0 },
                        })
                    );
                });
            } else {
                children.push(
                    new Paragraph({
                        text: "No application screens generated.",
                    })
                );
            }

            children.push(
                new Paragraph({
                    text: "4. Data Entities",
                    heading: HeadingLevel.HEADING_1,
                }),
                new Paragraph({
                    text: "Main data objects identified for the application.",
                })
            );

            if (entities.length > 0) {
                entities.forEach((entity: any, index: number) => {
                    const entityName =
                        entity?.name ||
                        entity?.entity_name ||
                        `Entity ${index + 1}`;

                    children.push(
                        new Paragraph({
                            text: entityName,
                            heading: HeadingLevel.HEADING_2,
                        })
                    );

                    if (entity?.description) {
                        children.push(
                            new Paragraph({
                                text: entity.description,
                            })
                        );
                    }

                    if (Array.isArray(entity?.attributes)) {
                        entity.attributes.forEach((attribute: any) => {
                            const attributeName =
                                typeof attribute === "string"
                                    ? attribute
                                    : attribute?.name ||
                                    attribute?.attribute_name ||
                                    JSON.stringify(attribute);

                            children.push(
                                new Paragraph({
                                    text: attributeName,
                                    bullet: { level: 0 },
                                })
                            );
                        });
                    }
                });
            } else {
                children.push(
                    new Paragraph({
                        text: "No data entities generated.",
                    })
                );
            }

            children.push(
                new Paragraph({
                    text: "5. UI Component Structure",
                    heading: HeadingLevel.HEADING_1,
                }),
                new Paragraph({
                    text: "Components Jinie expects to use when creating the application interface.",
                })
            );

            if (componentTrees.length > 0) {
                componentTrees.forEach((tree: any, index: number) => {
                    children.push(
                        new Paragraph({
                            text: `${String(index + 1).padStart(2, "0")}. ${displayItem(tree)}`,
                            bullet: { level: 0 },
                        })
                    );
                });
            } else {
                children.push(
                    new Paragraph({
                        text: "No component structure generated.",
                    })
                );
            }

            if (srs?.tech_stack) {
                children.push(
                    new Paragraph({
                        text: "6. Recommended Technology Stack",
                        heading: HeadingLevel.HEADING_1,
                    }),
                    new Paragraph({
                        text: JSON.stringify(srs.tech_stack, null, 2),
                    })
                );
            }

            const doc = new Document({
                sections: [
                    {
                        properties: {},
                        children,
                    },
                ],
            });

            const blob = await Packer.toBlob(doc);
            const url = window.URL.createObjectURL(blob);
            const link = window.document.createElement("a");

            link.href = url;
            link.download = "Jinie-SRS.docx";

            window.document.body.appendChild(link);
            link.click();
            window.document.body.removeChild(link);

            window.URL.revokeObjectURL(url);
        } catch (error) {
            console.error("SRS download failed:", error);
            alert("Unable to download the SRS document. Please check the browser console.");
        }
    };

    return (
        <div className="section-card srs-panel">
            <div className="srs-panel-header">
                <div>
                    <span className="stage-label">02 · Requirements</span>

                    <h1>Software Requirements</h1>

                    <p>
                        Jinie analyzed your idea and created a complete
                        specification. Review it before moving into design.
                    </p>
                </div>

                <div className="srs-summary">
                    <strong>{functionalRequirements.length}</strong>
                    <span>Functional requirements</span>
                </div>
            </div>

            <div className="srs-block">
                <h2>Functional Requirements</h2>

                <p className="srs-description">
                    Features and actions the application should provide.
                </p>

                {functionalRequirements.length > 0 ? (
                    <div className="srs-list">
                        {functionalRequirements.map((requirement: any, index: number) => (
                            <div className="srs-item" key={requirement?.fr_id || index}>
                                <span className="srs-number">
                                    {String(index + 1).padStart(2, "0")}
                                </span>

                                <div className="srs-item-content">
                                    <div className="srs-item-meta">
                                        <span>
                                            {requirement?.fr_id ||
                                                `FR-${String(index + 1).padStart(2, "0")}`}
                                        </span>

                                        {requirement?.priority && (
                                            <span className="srs-priority">
                                                {requirement.priority}
                                            </span>
                                        )}
                                    </div>

                                    <p>{displayItem(requirement)}</p>

                                    {requirement?.inputs?.length > 0 && (
                                        <div className="srs-tags">
                                            {requirement.inputs.map((input: string) => (
                                                <span key={input}>
                                                    {humanize(input)}
                                                </span>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                ) : (
                    <p className="empty-srs">
                        No functional requirements generated.
                    </p>
                )}
            </div>

            <div className="srs-block">
                <h2>Non-Functional Requirements</h2>

                <p className="srs-description">
                    Quality, performance, security and usability requirements.
                </p>

                {nonFunctionalRequirements.length > 0 ? (
                    <div className="srs-list">
                        {nonFunctionalRequirements.map((requirement: any, index: number) => (
                            <div className="srs-item" key={requirement?.nfr_id || index}>
                                <span className="srs-number">
                                    {String(index + 1).padStart(2, "0")}
                                </span>

                                <div className="srs-item-content">
                                    <div className="srs-item-meta">
                                        <span>
                                            {requirement?.nfr_id ||
                                                `NFR-${String(index + 1).padStart(2, "0")}`}
                                        </span>

                                        {requirement?.category && (
                                            <span className="srs-priority">
                                                {requirement.category}
                                            </span>
                                        )}
                                    </div>

                                    <p>{displayItem(requirement)}</p>
                                </div>
                            </div>
                        ))}
                    </div>
                ) : (
                    <p className="empty-srs">
                        No non-functional requirements generated.
                    </p>
                )}
            </div>

            <div className="srs-block">
                <h2>Application Screens</h2>

                <p className="srs-description">
                    Screens Jinie identified for the application.
                </p>

                {screens.length > 0 ? (
                    <div className="screen-grid">
                        {screens.map((screen: any, index: number) => (
                            <div className="screen-card" key={screen?.screen_id || index}>
                                <span className="screen-number">
                                    {String(index + 1).padStart(2, "0")}
                                </span>

                                <h3>
                                    {screen?.screen_name ||
                                        screen?.name ||
                                        screen?.title ||
                                        `Screen ${index + 1}`}
                                </h3>

                                {screen?.route && (
                                    <span className="screen-route">
                                        {screen.route}
                                    </span>
                                )}

                                {screen?.screen_type && (
                                    <span className="screen-type">
                                        {screen.screen_type}
                                    </span>
                                )}
                            </div>
                        ))}
                    </div>
                ) : (
                    <p className="empty-srs">
                        No application screens generated.
                    </p>
                )}
            </div>

            <div className="srs-block">
                <h2>Data Entities</h2>

                <p className="srs-description">
                    Main data objects identified for the application.
                </p>

                {entities.length > 0 ? (
                    <div className="entity-grid">
                        {entities.map((entity: any, index: number) => (
                            <div className="entity-card" key={entity?.entity_id || index}>
                                <h3>
                                    {entity?.name ||
                                        entity?.entity_name ||
                                        `Entity ${index + 1}`}
                                </h3>

                                {entity?.description && (
                                    <p>{entity.description}</p>
                                )}

                                {Array.isArray(entity?.attributes) && (
                                    <div className="entity-attributes">
                                        {entity.attributes.map(
                                            (attribute: any, attributeIndex: number) => (
                                                <span key={attributeIndex}>
                                                    {typeof attribute === "string"
                                                        ? attribute
                                                        : attribute?.name ||
                                                        attribute?.attribute_name ||
                                                        JSON.stringify(attribute)}
                                                </span>
                                            )
                                        )}
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                ) : (
                    <p className="empty-srs">
                        No data entities generated.
                    </p>
                )}
            </div>

            <div className="srs-block">
                <h2>UI Component Structure</h2>

                <p className="srs-description">
                    Components Jinie expects to use when building the interface.
                </p>

                {componentTrees.length > 0 ? (
                    <div className="srs-list">
                        {componentTrees.map((tree: any, index: number) => (
                            <div className="srs-item" key={tree?.screen_id || index}>
                                <span className="srs-number">
                                    {String(index + 1).padStart(2, "0")}
                                </span>

                                <div className="srs-item-content">
                                    <div className="srs-item-meta">
                                        <span>Screen structure</span>
                                    </div>

                                    <p>
                                        {tree?.screen_name ||
                                            displayItem(tree)}
                                    </p>
                                </div>
                            </div>
                        ))}
                    </div>
                ) : (
                    <p className="empty-srs">
                        No component structure generated.
                    </p>
                )}
            </div>

            {srs?.tech_stack && (
                <div className="srs-block">
                    <h2>Recommended Technology Stack</h2>

                    <p className="srs-description">
                        Technologies recommended by Jinie for this application.
                    </p>

                    <div className="tech-stack-card">
                        <pre>{JSON.stringify(srs.tech_stack, null, 2)}</pre>
                    </div>
                </div>
            )}

            <div className="srs-actions">
                <div className="srs-actions-copy">
                    <strong>Ready to continue?</strong>
                    <span>
                        Approve these requirements to start designing your app.
                    </span>
                </div>

                <div className="srs-actions-buttons">
                    <button
                        className="secondary-button"
                        onClick={downloadSRS}
                        type="button"
                    >
                        Download SRS
                    </button>

                    <button
                        className="primary-button"
                        onClick={onApprove}
                        type="button"
                    >
                        Approve Requirements <span>→</span>
                    </button>
                </div>
            </div>
        </div>
    );
}