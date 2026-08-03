"""Generates project-level configuration files: app.json, package.json,
tsconfig.json, babel.config.js, and .gitignore.
"""

from __future__ import annotations

import json
import uuid
from typing import Dict, List

from ..enums import StateManagerType
from ..file_writer import FileWriter
from ..models import AppConfig, StateManager


class ConfigFilesGenerator:
    """Generates the project's top-level configuration files."""

    def __init__(
        self,
        config: AppConfig,
        state_managers: List[StateManager],
        writer: FileWriter,
    ) -> None:
        self._config = config
        self._state_managers = state_managers
        self._writer = writer

    # -- config files ---------------------------------------------------
    def generate_app_json(self) -> None:
        config = self._config
        app_json = {
            "expo": {
                "name": config.name,
                "slug": config.slug,
                "version": config.version,
                "orientation": config.orientation,
                "icon": config.icon,
                "splash": config.splash,
                "userInterfaceStyle": "light",
                "assetBundlePatterns": ["**/*"],
                "ios": {
                    "supportsTablet": True,
                    "bundleIdentifier": config.bundle_identifier,
                },
                "android": {
                    "adaptiveIcon": {
                        "foregroundImage": config.icon,
                        "backgroundColor": config.background_color,
                    },
                    "package": config.bundle_identifier,
                },
                "web": {"favicon": config.icon},
                "plugins": ["expo-router"],
                "extra": {
                    "router": {"origin": False},
                    "eas": {"projectId": str(uuid.uuid4())},
                },
            }
        }
        self._writer.write("app.json", json.dumps(app_json, indent=2) + "\n")

    def generate_package_json(self) -> None:
        dependencies: Dict[str, str] = {
            "react": "^18.2.0",
            "react-native": "^0.73.6",
            "expo": "^50.0.0",
            "expo-router": "^3.4.0",
            "expo-constants": "~15.4.5",
            "expo-status-bar": "~1.11.1",
            "@react-navigation/native": "^6.1.9",
            "@react-navigation/bottom-tabs": "^6.5.11",
            "@react-navigation/stack": "^6.3.20",
            "@react-navigation/drawer": "^6.6.6",
            "react-native-screens": "~3.29.0",
            "react-native-safe-area-context": "4.8.2",
            "react-native-gesture-handler": "~2.14.1",
            "react-native-reanimated": "~3.6.2",
        }
        dev_dependencies: Dict[str, str] = {
            "@types/react": "^18.2.45",
            "@babel/preset-env": "^7.23.9",
            "@babel/preset-react": "^7.23.3",
            "@babel/preset-typescript": "^7.23.3",
            "typescript": "^5.3.3",
            "jest": "^29.7.0",
            "jest-expo": "^50.0.1",
            "@testing-library/react-native": "^12.4.3",
            "eslint": "^8.56.0",
            "eslint-config-expo": "^7.0.0",
        }

        for manager in self._state_managers:
            if manager.type is StateManagerType.REDUX:
                dependencies["redux"] = manager.version
                dependencies["react-redux"] = "^9.1.0"
                dependencies["redux-thunk"] = "^3.1.0"
            elif manager.type is StateManagerType.ZUSTAND:
                dependencies["zustand"] = manager.version
            elif manager.type is StateManagerType.RECOIL:
                dependencies["recoil"] = manager.version
            elif manager.type is StateManagerType.CONTEXT:
                pass  # built into React, no dependency needed

        config = self._config
        package_json = {
            "name": config.slug,
            "version": config.version,
            "description": config.description,
            "author": config.author,
            "main": "expo-router/entry",
            "scripts": {
                "start": "expo start",
                "android": "expo start --android",
                "ios": "expo start --ios",
                "web": "expo start --web",
                "test": "jest",
                "lint": "eslint . && tsc --noEmit",
                "typecheck": "tsc --noEmit",
                "build": "eas build --platform all",
            },
            "dependencies": dict(sorted(dependencies.items())),
            "devDependencies": dict(sorted(dev_dependencies.items())),
            "private": True,
        }
        self._writer.write("package.json", json.dumps(package_json, indent=2) + "\n")

    def generate_tsconfig(self) -> None:
        tsconfig = {
            "extends": "expo/tsconfig.base",
            "compilerOptions": {
                "strict": True,
                "baseUrl": ".",
                "paths": {"@/*": ["./src/*"]},
            },
            "include": ["**/*.ts", "**/*.tsx", ".expo/types/**/*.ts", "expo-env.d.ts"],
        }
        self._writer.write("tsconfig.json", json.dumps(tsconfig, indent=2) + "\n")

    def generate_babel_config(self) -> None:
        content = (
            "module.exports = function (api) {\n"
            "  api.cache(true);\n"
            "  return {\n"
            "    presets: ['babel-preset-expo'],\n"
            "    plugins: ['react-native-reanimated/plugin'],\n"
            "  };\n"
            "};\n"
        )
        self._writer.write("babel.config.js", content)

    def generate_gitignore(self) -> None:
        content = "\n".join(
            [
                "node_modules/",
                ".expo/",
                "dist/",
                "web-build/",
                "*.log",
                ".env",
                ".env.local",
                ".DS_Store",
                "*.orig.*",
                "*.p8",
                "*.p12",
                "*.key",
                "*.mobileprovision",
                "*.jks",
                "*.keystore",
            ]
        )
        self._writer.write(".gitignore", content + "\n")
