# Backend Deployment Manager Module

The Deployment Manager packages the compiled application and publishes it live to the targeted hosting service.

## Submodules

### 1. Firebase Helper (`firebase_helper.py`)
Prepares assets, configures Firebase hosting parameters, builds web bundles, applies database rules (Firestore), sets up authentication scopes, and executes hosting deployments. Surfaces the public URL upon success.
