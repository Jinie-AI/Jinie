# Mobile store deployment

Jinie Deploy now provides project setup, preflight checks and a background Build & submit job. It snapshots the current generated source, builds signed binaries through EAS, then uploads successful builds. Android targets Play internal testing; iOS targets TestFlight. Store processing, metadata, review and public release remain separate. No store upload has been performed during implementation.

## One-time setup

1. Create the app in your Expo account and relevant store consoles. Use your own package/bundle identifiers.
2. Install the official EAS CLI: `npm install -g eas-cli`.
3. Download the generated ZIP, extract it, run `npm install`, then `eas login` and `eas init` to link your existing Expo project. Configure signing with `eas credentials` and set up EAS Submit store credentials. Complete an initial interactive build if needed. Use the same Expo project and identifiers in Jinie's Deploy form.
4. Set EXPO_TOKEN in the backend environment using an Expo access token. Restart the backend. Never place the token in frontend variables or generated source.
5. Android: configure your Google service account in EAS, or set JINIE_GOOGLE_SERVICE_ACCOUNT_FILE to an absolute backend-only JSON key path outside the generated project. Grant that account the appropriate Play Console app permissions.
6. iOS: configure signing and App Store Connect API credentials in EAS; enter the numeric App Store Connect app ID in Jinie.
7. In Deploy, save your Expo project ID, account/organization, slug and store app identifiers. Confirm credential setup, select destinations, then Build & submit.

The status panel reports queued, building, submitting, submitted or failed. Submitted means upload completed, not public approval. Expo links lead to remote build details. If the backend restarts or times out, inspect Expo before retrying to avoid duplicate remote builds. Build service charges and store membership requirements depend on your accounts.

Jinie is currently a local single-user workspace. Keep this backend on localhost; production hosting requires authentication and per-user credential isolation.

## Preview consistency

Screens and generated apps both use backend/studio/templates/AppView.jsx and ProductCard.jsx. Screens renders those components inside an isolated frame so workspace styles cannot alter them. Validated model candidates remain inspectable artifacts rather than silently replacing an accepted component. Re-accept and rebuild older saved projects to update their generated files. This regenerates source, so download any manually edited project first.

Sources: https://docs.expo.dev/build/automate-submissions/ · https://docs.expo.dev/submit/android/ · https://docs.expo.dev/submit/ios/
