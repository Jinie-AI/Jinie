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

    if (Array.isArray(data)) {
        return data;
    }

    if (Array.isArray(data.requirements)) {
        return data.requirements;
    }

    if (Array.isArray(data.entities)) {
        return data.entities;
    }

    if (Array.isArray(data.nodes)) {
        return data.nodes;
    }

    if (Array.isArray(data.trees)) {
        return data.trees;
    }

    return [];
}

function displayItem(item: any): string {
    if (typeof item === "string") {
        return item;
    }

    if (!item) {
        return "";
    }

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

export default function SRSSection({
    srs,
    onApprove,
}: SRSSectionProps) {

    const functionalRequirements = getItems(
        srs?.functional_requirements
    );

    const nonFunctionalRequirements = getItems(
        srs?.non_functional_requirements
    );

    const screens = getItems(
        srs?.sitemap
    );

    const entities = getItems(
        srs?.entities
    );

    const componentTrees = getItems(
        srs?.component_trees
    );


    // ==========================================
    // DOWNLOAD SRS AS WORD DOCUMENT
    // ==========================================

    const downloadSRS = async () => {

        try {

            const children: Paragraph[] = [];


            // ------------------------------------------
            // TITLE
            // ------------------------------------------

            children.push(
                new Paragraph({
                    text: "Jinie",
                    heading: HeadingLevel.TITLE,
                })
            );

            children.push(
                new Paragraph({
                    text: "Software Requirements Specification",
                    heading: HeadingLevel.HEADING_1,
                })
            );

            children.push(
                new Paragraph({
                    text: "Generated automatically by Jinie from the user's project prompt.",
                })
            );


            // ------------------------------------------
            // FUNCTIONAL REQUIREMENTS
            // ------------------------------------------

            children.push(
                new Paragraph({
                    text: "1. Functional Requirements",
                    heading: HeadingLevel.HEADING_1,
                })
            );

            children.push(
                new Paragraph({
                    text: "Features and actions the application should provide.",
                })
            );


            if (functionalRequirements.length > 0) {

                functionalRequirements.forEach(
                    (requirement: any, index: number) => {

                        children.push(
                            new Paragraph({
                                text:
                                    `FR-${String(index + 1).padStart(2, "0")}: ` +
                                    displayItem(requirement),
                                bullet: {
                                    level: 0,
                                },
                            })
                        );

                    }
                );

            } else {

                children.push(
                    new Paragraph({
                        text: "No functional requirements generated.",
                    })
                );

            }


            // ------------------------------------------
            // NON-FUNCTIONAL REQUIREMENTS
            // ------------------------------------------

            children.push(
                new Paragraph({
                    text: "2. Non-Functional Requirements",
                    heading: HeadingLevel.HEADING_1,
                })
            );

            children.push(
                new Paragraph({
                    text:
                        "Quality, performance, security and usability " +
                        "requirements for the application.",
                })
            );


            if (nonFunctionalRequirements.length > 0) {

                nonFunctionalRequirements.forEach(
                    (requirement: any, index: number) => {

                        children.push(
                            new Paragraph({
                                text:
                                    `NFR-${String(index + 1).padStart(2, "0")}: ` +
                                    displayItem(requirement),
                                bullet: {
                                    level: 0,
                                },
                            })
                        );

                    }
                );

            } else {

                children.push(
                    new Paragraph({
                        text:
                            "No non-functional requirements generated.",
                    })
                );

            }


            // ------------------------------------------
            // APPLICATION SCREENS
            // ------------------------------------------

            children.push(
                new Paragraph({
                    text: "3. Application Screens",
                    heading: HeadingLevel.HEADING_1,
                })
            );

            children.push(
                new Paragraph({
                    text:
                        "Screens identified by Jinie for the application.",
                })
            );


            if (screens.length > 0) {

                screens.forEach(
                    (screen: any, index: number) => {

                        const screenName =
                            screen?.screen_name ||
                            screen?.name ||
                            screen?.title ||
                            `Screen ${index + 1}`;

                        const route =
                            screen?.route
                                ? ` | Route: ${screen.route}`
                                : "";

                        const type =
                            screen?.screen_type
                                ? ` | Type: ${screen.screen_type}`
                                : "";

                        children.push(
                            new Paragraph({
                                text:
                                    `${String(index + 1).padStart(2, "0")}. ` +
                                    `${screenName}${route}${type}`,
                                bullet: {
                                    level: 0,
                                },
                            })
                        );

                    }
                );

            } else {

                children.push(
                    new Paragraph({
                        text: "No application screens generated.",
                    })
                );

            }


            // ------------------------------------------
            // DATA ENTITIES
            // ------------------------------------------

            children.push(
                new Paragraph({
                    text: "4. Data Entities",
                    heading: HeadingLevel.HEADING_1,
                })
            );

            children.push(
                new Paragraph({
                    text:
                        "Main data objects identified for the application.",
                })
            );


            if (entities.length > 0) {

                entities.forEach(
                    (entity: any, index: number) => {

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


                        if (
                            Array.isArray(entity?.attributes) &&
                            entity.attributes.length > 0
                        ) {

                            children.push(
                                new Paragraph({
                                    text: "Attributes:",
                                })
                            );


                            entity.attributes.forEach(
                                (attribute: any) => {

                                    const attributeName =
                                        typeof attribute === "string"
                                            ? attribute
                                            : attribute?.name ||
                                            attribute?.attribute_name ||
                                            JSON.stringify(attribute);

                                    children.push(
                                        new Paragraph({
                                            text: attributeName,
                                            bullet: {
                                                level: 0,
                                            },
                                        })
                                    );

                                }
                            );

                        }

                    }
                );

            } else {

                children.push(
                    new Paragraph({
                        text: "No data entities generated.",
                    })
                );

            }


            // ------------------------------------------
            // UI COMPONENT STRUCTURE
            // ------------------------------------------

            children.push(
                new Paragraph({
                    text: "5. UI Component Structure",
                    heading: HeadingLevel.HEADING_1,
                })
            );

            children.push(
                new Paragraph({
                    text:
                        "Components Jinie expects to use when creating " +
                        "the application interface.",
                })
            );


            if (componentTrees.length > 0) {

                componentTrees.forEach(
                    (tree: any, index: number) => {

                        children.push(
                            new Paragraph({
                                text:
                                    `${String(index + 1).padStart(2, "0")}. ` +
                                    displayItem(tree),
                                bullet: {
                                    level: 0,
                                },
                            })
                        );

                    }
                );

            } else {

                children.push(
                    new Paragraph({
                        text:
                            "No component structure generated.",
                    })
                );

            }


            // ------------------------------------------
            // TECHNOLOGY STACK
            // ------------------------------------------

            if (srs?.tech_stack) {

                children.push(
                    new Paragraph({
                        text: "6. Recommended Technology Stack",
                        heading: HeadingLevel.HEADING_1,
                    })
                );

                children.push(
                    new Paragraph({
                        text:
                            "Technologies recommended by Jinie for " +
                            "this application.",
                    })
                );


                const techStackText =
                    typeof srs.tech_stack === "string"
                        ? srs.tech_stack
                        : JSON.stringify(
                            srs.tech_stack,
                            null,
                            2
                        );


                children.push(
                    new Paragraph({
                        text: techStackText,
                    })
                );

            }


            // ------------------------------------------
            // CREATE WORD DOCUMENT
            // ------------------------------------------

            // IMPORTANT:
            // We use "doc" instead of "document".
            // This prevents conflict with window.document.

            const doc = new Document({

                sections: [
                    {
                        properties: {},

                        children: children,
                    },
                ],

            });


            // ------------------------------------------
            // CREATE DOCX BLOB
            // ------------------------------------------

            const blob = await Packer.toBlob(doc);


            // ------------------------------------------
            // DOWNLOAD FILE
            // ------------------------------------------

            const url =
                window.URL.createObjectURL(blob);


            const link =
                window.document.createElement("a");


            link.href = url;

            link.download =
                "Jinie-SRS.docx";


            window.document.body.appendChild(link);


            link.click();


            window.document.body.removeChild(link);


            window.URL.revokeObjectURL(url);


            console.log(
                "SRS Word document downloaded successfully."
            );

        } catch (error) {

            console.error(
                "SRS download failed:",
                error
            );

            alert(
                "Unable to download the SRS document. " +
                "Please check the browser console."
            );

        }

    };


    // ==========================================
    // UI
    // ==========================================

    return (

        <div className="section-card">

            <span className="stage-label">
                02
            </span>


            <h1>
                Software Requirements
            </h1>


            <p>
                Jinie analyzed your idea and generated a complete
                software requirements specification. Review the
                requirements before moving to the design stage.
            </p>


            {/* FUNCTIONAL REQUIREMENTS */}

            <div className="srs-block">

                <h2>
                    Functional Requirements
                </h2>


                <p className="srs-description">
                    Features and actions the application should provide.
                </p>


                {functionalRequirements.length > 0 ? (

                    <div className="srs-list">

                        {functionalRequirements.map(
                            (
                                requirement: any,
                                index: number
                            ) => (

                                <div
                                    className="srs-item"
                                    key={index}
                                >

                                    <span className="srs-number">
                                        FR-
                                        {String(index + 1).padStart(
                                            2,
                                            "0"
                                        )}
                                    </span>


                                    <span>
                                        {displayItem(requirement)}
                                    </span>

                                </div>

                            )
                        )}

                    </div>

                ) : (

                    <p className="empty-srs">
                        No functional requirements generated.
                    </p>

                )}

            </div>


            {/* NON FUNCTIONAL REQUIREMENTS */}

            <div className="srs-block">

                <h2>
                    Non-Functional Requirements
                </h2>


                <p className="srs-description">
                    Quality, performance, security and usability
                    requirements for the application.
                </p>


                {nonFunctionalRequirements.length > 0 ? (

                    <div className="srs-list">

                        {nonFunctionalRequirements.map(
                            (
                                requirement: any,
                                index: number
                            ) => (

                                <div
                                    className="srs-item"
                                    key={index}
                                >

                                    <span className="srs-number">
                                        NFR-
                                        {String(index + 1).padStart(
                                            2,
                                            "0"
                                        )}
                                    </span>


                                    <span>
                                        {displayItem(requirement)}
                                    </span>

                                </div>

                            )
                        )}

                    </div>

                ) : (

                    <p className="empty-srs">
                        No non-functional requirements generated.
                    </p>

                )}

            </div>


            {/* APPLICATION SCREENS */}

            <div className="srs-block">

                <h2>
                    Application Screens
                </h2>


                <p className="srs-description">
                    Screens Jinie identified for the application.
                </p>


                {screens.length > 0 ? (

                    <div className="screen-grid">

                        {screens.map(
                            (
                                screen: any,
                                index: number
                            ) => (

                                <div
                                    className="screen-card"
                                    key={index}
                                >

                                    <span className="screen-number">
                                        {String(index + 1).padStart(
                                            2,
                                            "0"
                                        )}
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

                            )
                        )}

                    </div>

                ) : (

                    <p className="empty-srs">
                        No application screens generated.
                    </p>

                )}

            </div>


            {/* ENTITIES */}

            <div className="srs-block">

                <h2>
                    Data Entities
                </h2>


                <p className="srs-description">
                    Main data objects identified for the application.
                </p>


                {entities.length > 0 ? (

                    <div className="entity-grid">

                        {entities.map(
                            (
                                entity: any,
                                index: number
                            ) => (

                                <div
                                    className="entity-card"
                                    key={index}
                                >

                                    <h3>

                                        {entity?.name ||
                                            entity?.entity_name ||
                                            `Entity ${index + 1}`}

                                    </h3>


                                    {entity?.description && (

                                        <p>
                                            {entity.description}
                                        </p>

                                    )}


                                    {entity?.attributes && (

                                        <div className="entity-attributes">

                                            {entity.attributes.map(
                                                (
                                                    attribute: any,
                                                    attributeIndex: number
                                                ) => (

                                                    <span
                                                        key={
                                                            attributeIndex
                                                        }
                                                    >

                                                        {typeof attribute ===
                                                            "string"
                                                            ? attribute
                                                            : attribute?.name ||
                                                            attribute?.attribute_name ||
                                                            JSON.stringify(
                                                                attribute
                                                            )}

                                                    </span>

                                                )
                                            )}

                                        </div>

                                    )}

                                </div>

                            )
                        )}

                    </div>

                ) : (

                    <p className="empty-srs">
                        No data entities generated.
                    </p>

                )}

            </div>


            {/* COMPONENT TREES */}

            <div className="srs-block">

                <h2>
                    UI Component Structure
                </h2>


                <p className="srs-description">
                    Components Jinie expects to use when creating
                    the application interface.
                </p>


                {componentTrees.length > 0 ? (

                    <div className="srs-list">

                        {componentTrees.map(
                            (
                                tree: any,
                                index: number
                            ) => (

                                <div
                                    className="srs-item"
                                    key={index}
                                >

                                    <span className="srs-number">
                                        {String(index + 1).padStart(
                                            2,
                                            "0"
                                        )}
                                    </span>


                                    <span>
                                        {displayItem(tree)}
                                    </span>

                                </div>

                            )
                        )}

                    </div>

                ) : (

                    <p className="empty-srs">
                        No component structure generated.
                    </p>

                )}

            </div>


            {/* TECH STACK */}

            {srs?.tech_stack && (

                <div className="srs-block">

                    <h2>
                        Recommended Technology Stack
                    </h2>


                    <p className="srs-description">
                        Technologies recommended by Jinie for this
                        application.
                    </p>


                    <div className="tech-stack-card">

                        <pre>
                            {JSON.stringify(
                                srs.tech_stack,
                                null,
                                2
                            )}
                        </pre>

                    </div>

                </div>

            )}


            {/* ACTIONS */}

            <div className="srs-actions">

                {/* DOWNLOAD WORD */}

                <button
                    className="secondary-button"
                    onClick={downloadSRS}
                    type="button"
                >
                    📄 Download SRS
                </button>


                {/* APPROVE */}

                <button
                    className="primary-button"
                    onClick={onApprove}
                    type="button"
                >
                    Approve Requirements
                    <span>→</span>
                </button>

            </div>

        </div>

    );
}