Jinie — AI-Driven UI to Flutter Application Generation

> **Department** **of** **Computer** **Sciences** **Air** **University**
> **Islamabad** **(AU)**
>
> Project Proposal
>
> **Jinie**
>
> **AI-Driven** **UI** **to** **Flutter** **Application** **Generation**
>
> _By_
>
> Chaudry Ali Sher – 232418 Ansa Anwaar – 232382 Kaneez Zehra – 232403
>
> **Supervisor** Dr. Bilal Ahmad
>
> **Co-Supervisor** Sir Asim Ali Fayyaz
>
> Page 1
>
> Jinie — AI-Driven UI to Flutter Application Generation
>
> **Supervisor** **Meeting** **Log**

||
||
||
||
||

> Page 2

Jinie — AI-Driven UI to Flutter Application Generation

**Table** **of** **Contents**

Introduction

Related System Analysis Problem Statement Proposed Solution Objectives

Scope

System Limitations Backend Modules

> Module 1 Utilities Module 2 Engine
>
> Module 3 Traceability Manager Module 4 SRS Generator Module 5
> Component Generator Module 6 Compiler
>
> Module 7 Tester Module 8 Logger

Module 9 Deployment Manager Frontend Modules

> Module 10 Input Interface
>
> Module 11 Design Preferences Panel Module 12 Progress and Status Panel
> Module 13 SRS Viewer and Editor Module 14 Live Review Panel

Module 15 Code Explorer Data Gathering Approach

AI Models Summary Tools and Technologies

Project Stakeholders and Roles Module-Based Work Division Gantt Chart

> Page 3
>
> Jinie — AI-Driven UI to Flutter Application Generation
>
> **Introduction**
>
> Modern mobile application development requires both UI design and
> programming expertise. Designers create visual layouts using design
> tools, and developers must then manually convert those layouts into
> functional code. This process is time-consuming, prone to
> inconsistency, and demands significant repetitive effort in
> translating interface elements into structured widget hierarchies.
>
> Jinie addresses this challenge by proposing an AI-assisted system that
> bridges software development and visual design by automatically
> transforming user-defined UI layouts into fully functional Flutter
> applications. The novelty of the system lies in its three trained AI
> models: a fine-tuned DistilBERT model that extracts structured
> requirements from natural language descriptions, a Random Forest
> layout recommendation model trained on a curated dataset of e-commerce
> UI patterns, and a fine-tuned CodeT5-small model that generates React
> Native and Flutter component code from structured layout descriptions.
>
> Unlike existing tools that depend on external API calls or rule-based
> engines, Jinie trains its own machine learning models on self-curated
> datasets. This approach ensures academic rigor, full control over
> model behavior, and a genuinely intelligent pipeline that connects
> visual design with functional mobile application engineering.
>
> **Related** **System** **Analysis**

||
||
||
||
||
||

> Page 4

Jinie — AI-Driven UI to Flutter Application Generation

**Problem** **Statement**

Mobile application development demands the transformation of visual
interface designs into structured, functional code. Currently, designers
use tools such as Figma to create UI layouts, while developers must
manually convert those layouts into Flutter widget trees. This process
is time-consuming, repetitive, and frequently introduces inconsistencies
in spacing, alignment, and component hierarchy.

Existing platforms either focus on design alone (Figma), generate
complex non-optimized code within closed ecosystems (FlutterFlow), or
assist with coding only when externally prompted (GitHub Copilot,
ChatGPT). None of these solutions provide an end-to-end pipeline that
understands user intent in natural language, recommends appropriate UI
layouts intelligently, and generates clean Flutter code using
self-trained models.

**Proposed** **Solution**

Jinie proposes an AI-assisted application generation system built on
three self-trained machine learning models. The system follows a
structured pipeline spanning backend processing and frontend
interaction:

> • Input Interface: The user describes their application in plain
> English or Urdu, optionally uploading reference files or selecting a
> template. All inputs are combined into a unified prompt object.
>
> • Engine & NLP Processing: A fine-tuned DistilBERT model extracts
> structured requirements including pages needed, features, business
> type, and style preferences.
>
> • SRS Generation: The system produces a full Software Requirements
> Specification covering functional requirements, non-functional
> requirements, a sitemap, and technology stack recommendations.
>
> • Component Generation: AI-generated UI components are assembled based
> on user design preferences and the generated sitemap.
>
> • Compilation: Components and requirements are wired together into a
> complete, runnable Flutter project.
>
> • Testing and Validation: Use-case scenarios are run against the
> compiled app to verify all requirements are satisfied.
>
> • Deployment: The tested app is packaged and deployed to Firebase,
> with the live URL returned to the user in the deploy dashboard.

**Objectives**

> • To develop a fine-tuned DistilBERT model capable of extracting
> structured application requirements from natural language descriptions
> in English and Urdu.
>
> • To build and curate a dataset of 300–500 labeled e-commerce UI
> layouts and train a Random Forest layout recommendation model on this
> dataset.
>
> Page 5

Jinie — AI-Driven UI to Flutter Application Generation

> • To construct a component-to-code dataset of 100–200 pairs and
> fine-tune a CodeT5-small model for Flutter widget code generation.
>
> • To create a backend engine that maintains project state, reframes
> user input, and drives the generation pipeline end to end.
>
> • To implement a Traceability Manager that assigns unique IDs to every
> artifact so all outputs are traceable to their originating
> requirements.
>
> • To generate a complete, executable Flutter project including widget
> trees, Dart files, and project scaffolding through an automated
> compiler module.
>
> • To provide a live in-browser preview of the generated application
> before export and deployment.
>
> • To deploy the generated app to Firebase with a single click through
> an integrated Deployment Manager module.
>
> • To reduce manual coding effort and accelerate mobile application
> development for non-technical users.

**Scope**

> • Web-based interface covering the full pipeline from prompt input to
> deployed app, accessible without any local tooling.
>
> • Domain: e-commerce mobile applications targeting small businesses in
> Pakistan (clothing, food, electronics, accessories, services).
>
> • NLP-based requirement extraction supporting both English and
> Urdu-English code-switching input.
>
> • AI layout recommendation for up to 8 page types: home, product
> listing, product detail, cart, checkout, contact, about, search.
>
> • Automated SRS generation including functional requirements,
> non-functional requirements, sitemap, and technology stack
> identification.
>
> • Automated Flutter/Dart code generation from finalized layout JSON
> using a fine-tuned CodeT5-small model.
>
> • Generation of a complete Flutter project folder with main.dart,
> screen files, component files, pubspec.yaml, and Firebase
> configuration.
>
> • In-browser application preview using an embedded Flutter/Expo
> simulator.
>
> • One-click deployment to Firebase Hosting via an integrated
> Deployment Manager.
>
> • System supports mobile applications only; web and desktop targets
> are out of scope.

**System** **Limitations**

> • The NLP intake model is trained on e-commerce descriptions only.
> Non-commerce application types (e.g., social media, gaming) are not
> supported.
>
> • The layout recommendation model covers only the predefined component
> library. Highly custom UI elements beyond the 20–30 curated components
> are not supported.
>
> Page 6

flowchart TD

    A["1. Prompt"]
    B["2. Requirements (SRS)"]
    C["3. Design"]
    D["4. Design Review"]
    E["5. Implementation"]
    F["6. Testing & Preview"]
    G["7. Deployment"]

    A --> B --> C --> D --> E --> F --> G

> • The CodeT5-small model is fine-tuned on a dataset of 100–200
> component pairs. Generated code may require minor manual adjustments
> for complex or deeply nested components.
>
> • The system handles basic application structure only. Animations,
> custom transitions, and complex state logic are out of scope.
>
> • Processing time may increase for applications with more than 8
> screens due to sequential code generation per component.
>
> • The system targets Flutter mobile applications only; web and desktop
> outputs are not generated.
>
> • All three trained models require initial training time on Google
> Colab before deployment. Model retraining is not available to end
> users.

**Project** **Flow:**

> Page 7

Jinie — AI-Driven UI to Flutter Application Generation

**Backend** **Modules**

The backend is the intelligence and processing layer of Jinie. It
receives raw user intent and drives it through a nine-module pipeline
that produces a tested, deployed Flutter application. Every artifact the
backend produces carries a unique traceable ID so nothing is ever lost
or unaccountable.

**<u>PLANNING:</u>**

**MODULE** **01** **:** **UTILITIES:**

Utilities is the shared service floor that all other modules build on.
It is a collection of independently callable tools file I/O, code
editing, format conversion, style enforcement, environment setup, and
quality checking. No other module implements any of these capabilities
itself; they always import from Utilities. This means the entire system
has one consistent, tested implementation for every low-level operation.

**Submodule:** **File** **Handler**

The File Handler is responsible for every read, write, move, copy, and
delete operation on files in the workspace. Whenever any module needs to
save a generated file or load an existing one, it calls the File Handler
rather than touching the filesystem directly. This creates a single,
predictable path for all file operations across the whole pipeline,
making it easy to audit, log, and replay any file-level action.

**Submodule:** **Code** **Editor**

The Code Editor handles programmatic changes to source files. It can
insert new lines, delete blocks, replace tokens, and apply formatting
rules all without opening a visual editor. The Compiler and Reformatter
both call this submodule whenever they need to write or modify generated
code. Because all edits go through one interface, the system can
maintain a clean diff history of every change made to the codebase.

**Submodule:** **.md** **Converter**

The MD Converter translates between Markdown and other formats such as
HTML or plain text. The SRS Generator uses this submodule whenever it
needs to export requirements documents in a human-readable format for
the user or for downstream tools. It also handles conversion in the
other direction parsing Markdown-formatted user input into structured
data the engine can work with.

**Submodule:** **Reformatter**

The Reformatter takes any piece of generated code and applies a
consistent style to it correct indentation, line length limits, naming
conventions, and whitespace rules. It runs on every file before it moves
downstream, so the final codebase always looks like it was written by
one person following one style guide. This is especially important for
generated Flutter/Dart code where readability affects maintainability.

**Submodule:** **Environment** **Setup** **Manager**

Before any code can run, the environment must be ready. This submodule
installs the correct package versions, creates configuration files, sets
environment variables, and scaffolds the folder structure for the chosen
technology stack. It fires once at project start and again whenever the
stack identifier recommends a change. It works hand-in-hand with the
Project Scaffolding output to ensure the generated project is
immediately runnable.

> Page 8

Jinie — AI-Driven UI to Flutter Application Generation

**Submodule:** **V&V** **(Verification** **and** **Validation)**

Verification checks that an artifact was built correctly according to
its specification. Validation checks that the artifact actually does
what the user originally asked for. Every output from the Utilities
layer passes through V&V before it is handed to any other module, acting
as a quality gate on every internal transaction. Failed checks are
reported back to the Engine with a structured error object so the
pipeline can self-correct.

**MODULE** **02:** **ENGINE:**

The Engine is the intelligence center of the backend. It is the only
module that truly understands what the user is trying to build. All
other modules are workers that execute well-defined tasks the Engine is
the manager that decides what task to run next, maintains the project's
memory, and checks whether results match what the user actually wanted.

**Submodule:** **Engine** **Reframer**

When a user sends a message that is vague, contradictory, or changes
something they approved earlier, the Engine Reframer steps in. It
rewrites the input into a clean, unambiguous problem statement that the
rest of the pipeline can act on without confusion. It fires at the start
of every new user turn and produces a canonical problem statement that
is stored in Current State and passed to the SRS Generator.

**Submodule:** **Customer** **Feedback**

This submodule listens for corrections, approvals, ratings, and comments
from the user at any point during the pipeline. It receives that
feedback and routes it back to whichever upstream module produced the
artifact being criticized, so the engine knows exactly where to restart
the generation process. This tight feedback loop is what allows Jinie to
refine its output iteratively without requiring the user to restart from
scratch.

**Submodule:** **Current** **State**

The Current State submodule maintains a live, up-to-date snapshot of
every artifact the pipeline has produced so far the requirements, the
sitemap, the design preferences, the components, the test results, and
the build status. Every other module reads from Current State to
understand where the project stands right now and writes to it when they
produce something new. It is the single source of truth for all
in-progress work.

**MODULE** **03:** **TRACEABILITY** **MANAGER:**

The Traceability Manager ensures that every piece of output every
requirement, every component, every test, every response can be traced
forward to what it created and backward to what created it. This is how
the system avoids orphaned artifacts and how the user or the evaluation
committee can always answer the question: why does this exist and what
does it affect?

**Submodule:** **ID** **Assigner** **(Traceability** **Matrix)**

Every time the pipeline produces anything, the ID Assigner stamps it
with a unique, hierarchical identifier. That ID encodes where in the
pipeline the item came from and which requirement it was built to
satisfy. The Traceability Matrix is the live table that records all of
these relationships. If something breaks or changes, the matrix can be
queried to find every artifact that is affected downstream, enabling
precise targeted regeneration instead of a full rebuild.

> Page 9

Jinie — AI-Driven UI to Flutter Application Generation

**MODULE** **04:** **SRS** **GENERATOR:**

The SRS Generator turns the Engine's clean problem statement into a
formal Software Requirements Specification the complete written contract
for what the app must do. Every other generation module downstream reads
from this document. The SRS Generator has five dedicated submodules
because the quality of what it produces determines the quality of
everything that follows.

**Submodule:** **Requirement** **Generator**

This submodule reads the Engine's problem statement and breaks it into
individual, numbered, atomic requirements. Each requirement describes
exactly one thing the system must do or must not do, in plain language
that both the user and the code generator can understand. Requirements
are tagged with traceability IDs the moment they are created.

**Submodule:** **Sitemap** **Generator**

The Sitemap Generator produces a hierarchical map of every screen,
route, and view the finished app must contain. It describes the
navigation structure which pages exist, what they are called, and how a
user moves between them. The Component Generator and Compiler both use
this map as their primary structural blueprint when assembling the
application.

**Submodule:** **Functional** **Requirement** **Generator**

Functional requirements describe what the system actively does every
user action, every system response, and every data flow. This submodule
enumerates all of those behaviors in a structured list, each one tagged
with the ID of the parent requirement it belongs to. The Tester module
later uses this list to derive its use-case scenarios.

**Submodule:** **Non-Functional** **Requirement** **Generator**

Non-functional requirements describe how well the system does things how
fast pages must load, how many users it must handle simultaneously, what
security standards it must meet, and what accessibility level it must
reach. This submodule produces that quality specification alongside the
functional one. Non-functional requirements are passed to the Deployment
Manager and the Technology Stack Identifier.

**Submodule:** **Technology** **and** **Stack** **Identifier**

Once all requirements are written, this submodule reads both the
functional and non-functional requirements and recommends the technology
stack that best satisfies them. For Jinie it confirms the frontend
framework, backend runtime, database, authentication provider, and
hosting platform. Those choices are passed to the Environment Setup
Manager and the Compiler so the generated project is built on exactly
the right stack from the start.

**<u>DESIGN</u>:**

**MODULE** **05:** **COMPONENT** **GENERATOR:**

The Component Generator takes two inputs the user's design preferences
(colors, typography, layout mode) from the frontend and the sitemap from
the SRS Generator and turns them into a set of reusable, independently
testable UI components. Each component is a self-contained building
block: a button, a navigation bar, a form, a product card, a checkout
section. They are

> Page 10

Jinie — AI-Driven UI to Flutter Application Generation

built to the user's exact visual style and named to match the sitemap
node that required them. Every component is stamped with a traceability
ID linking it back to its originating sitemap node.

**<u>IMPLEMENTATION:</u>** **MODULE** **06:** **COMPILER:**

The Compiler takes the components from Module 5, the functional
requirements from Module 4, and the sitemap, and wires them together
into a working application. It assembles page files, connects routes,
plugs in state management, and links data calls. The output is a
complete Flutter codebase where every functional requirement is
addressed by at least one code path. The Reformatter runs over the whole
output before it is handed to the Tester, ensuring the final code is
clean and consistently styled.

**<u>TESTING:</u>**

**MODULE** **07:** **TESTER:**

The Tester takes the compiled application and runs it against the
use-case scenarios derived from the functional requirements. For each
use case it checks whether the app behaves as specified, records a pass
or fail result against the relevant requirement ID, and writes a full
test report. If any requirement has no passing test case, the Tester
flags it back to the Engine with a structured error object so the gap is
closed before deployment is allowed to proceed. No build ships without a
green test report.

**MODULE** **08:** **LOGGER:**

The Logger records a timestamped event for every significant action
anywhere in the pipeline a module starting, a file being written, a test
passing, a user submitting feedback. Its most critical feature is the
login and app break check: before the Deployment Manager is allowed to
run, the Logger verifies that the app can boot successfully and that the
authentication flow works end to end. If either check fails, deployment
is blocked and the failure event is surfaced to the user in the frontend
status panel with a plain-language description of what went wrong.

**<u>DEPLOYMENT:</u>**

**MODULE** **09:** **DEPLOYMENT** **MANAGER:**

The Deployment Manager is the final step in the backend pipeline. It
takes the compiled, tested application, packages it for the target
hosting environment, and pushes it live. It also configures any cloud
services the app depends on databases, authentication, and storage
rules.

**Submodule:** **Firebase** **Helper**

The Firebase Helper handles all Firebase-specific deployment steps. It
builds the hosting bundle, uploads it to Firebase Hosting, applies
Firestore security rules, configures Firebase Authentication providers,
and executes the final deploy command. It watches the deployment for

> Page 11

Jinie — AI-Driven UI to Flutter Application Generation

errors and reports back to the Logger with a success or failure event,
which in turn triggers the frontend Deploy Dashboard to display either
the live URL or a detailed error message.

**Frontend** **Modules**

The frontend is everything the user sees and touches. While the backend
runs its pipeline, the frontend keeps the user informed, collects their
preferences, shows them the output in real time, and gives them controls
to adjust or deploy. It is designed so that a non-technical user can go
from an idea to a live app without ever opening a terminal or a code
editor.

**MODULE** **10:** **INPUT** **INTERFACE:**

The Input Interface is the very first screen. Its job is to capture the
user's product idea in whatever form feels most natural to them. Some
users want to type a detailed description; others want to upload a
sketch or a PDF; others want to speak their idea out loud. The Input
Interface accepts all of these modes and combines them into a single
structured prompt object that is sent to the Engine.

**Submodule:** **Prompt** **Input** **Box**

A large, free-form text area where the user types or pastes their app
idea. It accepts plain language, bullet lists, or detailed
specifications. The Engine Reframer handles cleanup and disambiguation,
so the user does not need to follow any particular format.

**Submodule:** **File** **Uploader**

Allows the user to attach reference documents, screenshots, wireframes,
or existing codebases. Uploaded files are passed to the File Handler and
made available to the Engine as additional context when generating
requirements.

**MODULE** **11:** **DESIGN** **PREFRENCES** **PANEL:**

Before a single component is generated, the user tells the system what
they want the app to look and feel like. The Design Preferences Panel
collects those choices and serializes them into a design token object a
structured file of color values, font names, spacing rules, and theme
settings that is passed directly to the Component Generator.

**Submodule:** **Color** **Palette**

A color picker and preset swatch library where the user selects or
defines the primary, secondary, and accent colors for their app. Choices
are immediately reflected in a live mini-preview so the user can see the
combination before committing.

**Submodule:** **Typography**

A font selector where the user chooses heading and body typefaces from a
curated set of web-safe options. The selection is passed to the
Component Generator as part of the design token object and applied
consistently across all generated screens.

**Submodule:** **Layout** **Mode**

> Page 12

Jinie — AI-Driven UI to Flutter Application Generation

A toggle between common layout patterns such as left-nav, top-nav, or
sidebar, which influences how the Sitemap Generator structures the page
hierarchy and how the Component Generator arranges navigation elements.

**Submodule:** **Dark** **/** **Light** **Toggle**

Lets the user specify whether the app should launch in dark mode, light
mode, or system-default. This choice is baked into the generated CSS and
Flutter theme configuration from the start, rather than being an
afterthought.

**MODULE** **12:** **PROGRESS** **AND** **STATUS** **PANEL:**

Once the user submits their idea and preferences, the backend starts its
pipeline and the Progress Panel takes over the screen. Its job is to
make the wait feel transparent and in control rather than like a black
box. Every stage the backend completes fires an event to this panel so
the user always knows exactly what is happening and how far along the
generation is.

**Submodule:** **Stage** **Tracker**

A visual stepper showing which pipeline stage is currently running,
requirements, sitemap, components, compilation, testing and which stages
are complete or still pending. Each stage node is clickable to show its
output artifact in a side panel.

**Submodule:** **Live** **Log** **Stream**

A scrolling text panel that streams real-time log messages from the
Logger module, giving technical users a detailed view of exactly what
the backend is doing at any given moment. Errors appear highlighted in
red.

**Submodule:** **Error** **Alerts**

If any backend module reports an error or V&V failure, a prominent
inline alert appears here with a plain-language explanation of what went
wrong and what the user can do about it. Alerts link directly to the
affected requirement or file.

**Submodule:** **Cancel** **/** **Retry**

Buttons that let the user stop the current pipeline run cleanly, or
restart a failed stage without having to re-enter their original input.
The Engine maintains enough state in Current State to resume from any
stage checkpoint.

**MODULE** **13:** **SRS** **VIEWER** **AND** **EDITOR:**

Once the SRS Generator finishes, the frontend presents the full
requirements document to the user before any code is written. This is
the checkpoint where the user confirms the system understood them
correctly. If something is wrong here, it is far cheaper to fix than
after the Compiler has built hundreds of files around a bad requirement.

**Submodule:** **Requirement** **List** **View**

Displays all generated requirements in a numbered, hierarchical list
grouped by functional area, making it easy to scan and spot problems.
Each requirement shows its traceability ID and links to the sitemap
nodes it affects.

> Page 13

Jinie — AI-Driven UI to Flutter Application Generation

**Submodule:** **Inline** **Editor**

Lets the user click on any requirement and edit its text directly in the
browser. Changes are automatically synced back to the Engine's Current
State, which then re-runs only the downstream modules affected by that
change.

**Submodule:** **Approval** **Toggle**

A per-requirement checkbox that the user must check before the pipeline
is allowed to proceed past the SRS stage. No component is generated for
a requirement that has not been explicitly approved, preventing wasted
build time on misunderstood features.

**Submodule:** **ID** **Badge** **Display**

Shows the unique traceability ID next to each requirement so the user
can see how the system has tagged and tracked every decision. Clicking a
badge opens the Traceability Matrix view showing all artifacts linked to
that requirement.

**MODULE** **14:** **LIVE** **REVIEW** **PANEL:**

The Live Preview Panel renders the actual output of the Compiler inside
the browser so the user can see and interact with their app before it is
deployed anywhere. It is the most important panel in the frontend
because it turns an abstract pipeline process into a concrete, clickable
product.

**Submodule:** **Component** **Preview**

Shows individual generated components in isolation so the user can
inspect each building block the navigation bar, the login form, the
product card without the noise of the full page around it. Useful for
catching visual issues at the component level before reviewing the full
assembled app.

**Submodule:** **Full** **App** **Preview**

Renders the entire compiled app in a sandboxed iframe so the user can
click through the real navigation and test the real interactions exactly
as they will work in production. The preview connects to mock data so
all screens populate correctly.

**Submodule:** **Device** **Toggle**

Switches the preview between desktop, tablet, and mobile viewport sizes
so the user can verify the layout is responsive before approving the
build. This maps directly to the Flutter responsive breakpoints baked
into the generated code.

**Submodule:** **Feedback** **Capture**

An inline annotation tool that lets the user highlight any element in
the preview and leave a note. Those notes are routed to the Customer
Feedback submodule in the Engine, which triggers a targeted regeneration
of only the affected component rather than a full rebuild.

**MODULE** **15:** **CODE** **EXPLORER:**

The Code Explorer exposes the raw generated source code in a readable,
navigable interface without requiring the user to open a terminal or a
local IDE. It is also how a developer would download the project to
continue working on it locally after the initial generation.

**Submodule:** **File** **Tree** **View**

> Page 14

Jinie — AI-Driven UI to Flutter Application Generation

A collapsible directory browser showing every file the Compiler
produced, organized by folder exactly as they will appear in the
deployed project. Clicking any file opens it in the Syntax Editor.

**Submodule:** **Syntax** **Editor**

A read/write code editor with Flutter/Dart syntax highlighting that
opens any file from the tree view. Edits made here are sent to the Code
Editor submodule in Utilities and written back into the compiled output,
maintaining the traceability link between the file and its originating
requirement.

**Submodule:** **Download** **ZIP**

A single button that packages the entire generated codebase into a ZIP
archive and triggers a browser download, giving the user a full offline
copy of their project. The archive is structured to open and run
immediately in Android Studio or VS Code.

**Submodule:** **Traceability** **Link**

Next to every file in the tree, a small badge shows which requirement ID
that file was created to satisfy. Clicking it opens the corresponding
requirement in the SRS Viewer, completing the two-way trace between code
and specification.

Once deployment succeeds, this field shows the public URL of the
deployed app as a clickable link. It also displays the deployment
timestamp and the traceability ID of the build that was shipped, so the
deployed artifact is fully traceable back to the original requirements
session.

> Page 15
>
> Jinie — AI-Driven UI to Flutter Application Generation
>
> **Data** **Gathering** **Approach**
>
> All three datasets used in this project are built by the project team.
> No external API or pre-existing dataset is used as a primary data
> source. The following approach is taken for each dataset:
>
> **Dataset** **1** **—** **NLP** **Requirement** **Intake**
> **(DistilBERT)**
>
> 500–800 short business descriptions are written manually by the team,
> covering 10–15 e-commerce business categories common in Pakistan
> (clothing, food, electronics, accessories, furniture, beauty,
> bookshops, mobile repair, jewellery, digital services). Each
> description is written in English, Urdu-English code-switching, and
> formal English to ensure model robustness.
>
> Each entry is manually labeled with: business_type, pages required
> (multi-label), features required (multi-label), and style preference.
> Data augmentation through paraphrasing is applied to expand the
> dataset. The final dataset is split 80/10/10 for training, validation,
> and testing.
>
> **Dataset** **2** **—** **UI** **Layout** **Recommendation**
> **(Random** **Forest)**
>
> 300–500 e-commerce screen layout records are curated from publicly
> available Figma Community templates and Dribbble design portfolios.
> For each layout, the team records: business type suitability, page
> type, components present, layout style, and assigns a unique template
> ID.
>
> Each record is a row of tabular features suitable for scikit-learn
> training. The dataset is split 80/10/10 for training, validation, and
> testing. Cross-validation is used for hyperparameter tuning.
>
> **Dataset** **3** **—** **Component-to-Code** **Generation**
> **(CodeT5-small)**
>
> 100–200 component-to-code pairs are built manually. Each entry
> consists of a plain English description of a UI component and its
> corresponding Flutter/Dart widget code. The team builds pairs for
> 15–20 core e-commerce components (product card, navbar, hero banner,
> cart item, category chip, checkout button, search bar, image gallery,
> discount badge, and others), with 5– 10 description variations per
> component to improve generalization.
>
> This dataset is the most critical for the academic contribution of the
> project. Its construction methodology, curation process, and coverage
> statistics are documented in the project report.
>
> **AI** **Models** **Summary**

||
||
||
||

> Page 16
>
> Jinie — AI-Driven UI to Flutter Application Generation

||
||
||
||
||

> **Tools** **and** **Technologies**

||
||
||
||
||
||
||
||
||
||
||
||
||
||

> **Project** **Stakeholders** **and** **Roles**

||
||
||
||
||
||

> Page 17
>
> Jinie — AI-Driven UI to Flutter Application Generation

||
||
||
||
||
||
||

> **Module-Based** **Work** **Division**

||
||
||
||
||
||

> **Gantt** **Chart**

||
||
||
||
||
||
||
||
||
||
||
||

> Page 18
>
> Jinie — AI-Driven UI to Flutter Application Generation

||
||
||
||
||
||
||
||
||
||

> **References**
>
> Google. (2024). Flutter Documentation. Available at:
> https://docs.flutter.dev (Used for Flutter architecture, widget tree
> structure, and state management.)
>
> Sanh, V., Debut, L., Chaumond, J., & Wolf, T. (2019). DistilBERT, a
> distilled version of BERT: smaller, faster, cheaper and lighter.
> arXiv:1910.01108. (Used as the base model for NLP requirement
> extraction.)
>
> Wang, Y., Wang, W., Joty, S., & Hoi, S. C. H. (2021). CodeT5:
> Identifier-aware Unified Pre-trained Encoder-Decoder Models for Code
> Understanding and Generation. EMNLP 2021. (Used as the base model for
> Flutter code generation.)
>
> Breiman, L. (2001). Random Forests. Machine Learning, 45(1), 5–32.
> (Theoretical foundation for the layout recommendation model.)
>
> Gamma, E., Helm, R., Johnson, R., & Vlissides, J. (1994). Design
> Patterns: Elements of Reusable Object-Oriented Software.
> Addison-Wesley.
>
> Sommerville, I. (2016). Software Engineering (10th ed.). Pearson.
> (Used for system design, modular architecture, and project scaffolding
> concepts.)
>
> Fowler, M. (2002). Patterns of Enterprise Application Architecture.
> Addison-Wesley. (Referenced for layered architecture and structured
> system organization.)
>
> Wolf, T., et al. (2020). HuggingFace's Transformers: State-of-the-art
> Natural Language Processing. EMNLP 2020 (Systems Demonstrations).
> (Framework used for fine-tuning DistilBERT and CodeT5-small.)
>
> Page 19
