"""Compiler Engine Module (compiler.py)

Wires up page navigation, integrates state managers, injects static data, and
generates the entry points (App.tsx, package.json, app.json, navigation
routes) of a React Native (with Expo) project.

This module serves as the final compilation step that takes:
  - Generated components (from Module 5)
  - Functional requirements / sitemap (from Module 4)
and compiles them into a single coherent React Native application project.
"""

from __future__ import annotations

import json
import logging
import re
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


# --------------------------------------------------------------------------- #
# Exceptions
# --------------------------------------------------------------------------- #
class CompilerError(Exception):
    """Base exception for all compiler-related failures."""


class ValidationError(CompilerError):
    """Raised when input configuration is invalid."""


class CompilationError(CompilerError):
    """Raised when the compilation process fails."""


# --------------------------------------------------------------------------- #
# Enums / dataclasses
# --------------------------------------------------------------------------- #
class NavigationType(str, Enum):
    """Supported navigation types in the app."""

    STACK = "stack"
    TAB = "tab"
    DRAWER = "drawer"
    BOTTOM_TAB = "bottom_tab"


class StateManagerType(str, Enum):
    """Supported state management solutions."""

    REDUX = "redux"
    ZUSTAND = "zustand"
    CONTEXT = "context"
    RECOIL = "recoil"


_VALID_NAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")
_SLUG_SANITIZE_RE = re.compile(r"[^a-z0-9-]+")
_NAME_SPLIT_RE = re.compile(r"[^0-9A-Za-z]+")


@dataclass
class NavRoute:
    """Represents a single navigation route."""

    name: str
    component: str  # screen filename, e.g. "HomeScreen.tsx"
    title: Optional[str] = None
    icon: Optional[str] = None
    initial_route: bool = False
    screen_options: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.name or not _VALID_NAME_RE.match(self.name):
            raise ValidationError(
                f"Route name {self.name!r} must start with a letter and contain "
                "only letters, digits, or underscores."
            )
        if not self.component:
            raise ValidationError(f"Route {self.name!r} is missing a component filename.")
        if not self.component.endswith((".tsx", ".ts")):
            raise ValidationError(
                f"Route {self.name!r} component {self.component!r} must end in .tsx or .ts"
            )


@dataclass
class StateManager:
    """Represents a state management solution."""

    name: str
    type: StateManagerType
    stores: List[str] = field(default_factory=list)
    version: str = "latest"

    def __post_init__(self) -> None:
        if isinstance(self.type, str):
            try:
                self.type = StateManagerType(self.type)
            except ValueError as exc:
                valid = ", ".join(t.value for t in StateManagerType)
                raise ValidationError(
                    f"Unknown state manager type {self.type!r}. Valid options: {valid}"
                ) from exc


@dataclass
class AppConfig:
    """Main application configuration."""

    name: str
    display_name: str
    version: str = "1.0.0"
    description: str = ""
    author: str = ""
    slug: str = ""
    icon: str = "./assets/icon.png"
    splash: Dict[str, str] = field(
        default_factory=lambda: {
            "image": "./assets/splash.png",
            "resizeMode": "contain",
            "backgroundColor": "#ffffff",
        }
    )
    orientation: str = "portrait"
    primary_color: str = "#007AFF"
    background_color: str = "#ffffff"
    bundle_id_prefix: str = "com.jinie"

    def __post_init__(self) -> None:
        if not self.name:
            raise ValidationError("AppConfig.name is required.")
        if not self.slug:
            self.slug = slugify(self.name)
        else:
            self.slug = slugify(self.slug)
        if not self.slug:
            raise ValidationError(f"Could not derive a valid slug from name {self.name!r}.")

    @property
    def bundle_identifier(self) -> str:
        package_segment = self.slug.replace("-", "")
        return f"{self.bundle_id_prefix}.{package_segment}"


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def slugify(value: str) -> str:
    """Convert a string into a URL/package-safe slug (lowercase, hyphenated)."""
    value = value.strip().lower().replace("_", "-").replace(" ", "-")
    value = _SLUG_SANITIZE_RE.sub("-", value)
    value = re.sub(r"-{2,}", "-", value).strip("-")
    return value


def to_pascal_case(filename: str) -> str:
    """Derive a PascalCase component identifier from a filename or string.

    Preserves existing internal casing (so 'HomeScreen.tsx' -> 'HomeScreen',
    not 'Homescreen' as `str.title()` would produce), while still handling
    snake_case / kebab-case / space-separated input.
    """
    stem = Path(filename).stem
    parts = [p for p in _NAME_SPLIT_RE.split(stem) if p]
    if not parts:
        return "Component"
    return "".join(p[0].upper() + p[1:] for p in parts)


def to_screen_component_name(filename: str) -> str:
    """Derive the exported screen function name, ensuring a single 'Screen'
    suffix rather than duplicating it (e.g. 'HomeScreen.tsx' -> 'HomeScreen',
    not 'HomeScreenScreen'; 'Home.tsx' -> 'HomeScreen').
    """
    name = to_pascal_case(filename)
    return name if name.endswith("Screen") else f"{name}Screen"


def _safe_relative_path(base: Path, *parts: str) -> Path:
    """Join path parts under `base`, rejecting any attempt to escape it."""
    candidate = base.joinpath(*parts).resolve()
    base_resolved = base.resolve()
    if base_resolved not in candidate.parents and candidate != base_resolved:
        raise ValidationError(f"Path {candidate} escapes output directory {base_resolved}.")
    return candidate


# --------------------------------------------------------------------------- #
# Compiler Engine
# --------------------------------------------------------------------------- #
class CompilerEngine:
    """Orchestrates the compilation of React Native components into a
    complete, executable Expo project.
    """

    def __init__(self, output_dir: str, config: Optional[AppConfig] = None) -> None:
        self.output_dir = Path(output_dir)
        self.config = config or AppConfig(
            name="JinieApp", display_name="Jinie Application", slug="jinie-app"
        )
        self.routes: List[NavRoute] = []
        self.state_managers: List[StateManager] = []
        self.components: Dict[str, Dict[str, Any]] = {}
        self.static_data: Dict[str, Any] = {}
        self.navigation_structure: Dict[str, Any] = {"type": NavigationType.STACK.value}

    # -- registration API ---------------------------------------------------
    def add_route(self, route: NavRoute) -> None:
        if any(r.name == route.name for r in self.routes):
            raise ValidationError(f"Duplicate route name: {route.name!r}")
        self.routes.append(route)

    def add_state_manager(self, manager: StateManager) -> None:
        self.state_managers.append(manager)

    def add_component(self, name: str, content: Dict[str, Any]) -> None:
        if not _VALID_NAME_RE.match(name):
            raise ValidationError(f"Invalid component name: {name!r}")
        self.components[name] = content

    def add_static_data(self, key: str, data: Any) -> None:
        try:
            json.dumps(data)
        except (TypeError, ValueError) as exc:
            raise ValidationError(f"Static data for key {key!r} is not JSON-serializable.") from exc
        self.static_data[key] = data

    def set_navigation_structure(self, structure: Dict[str, Any]) -> None:
        nav_type = structure.get("type", NavigationType.STACK.value)
        try:
            NavigationType(nav_type)
        except ValueError as exc:
            valid = ", ".join(t.value for t in NavigationType)
            raise ValidationError(
                f"Unknown navigation type {nav_type!r}. Valid options: {valid}"
            ) from exc
        self.navigation_structure = structure

    # -- compilation ----------------------------------------------------
    def compile(self) -> bool:
        """Execute the full compilation process.

        Returns:
            True if compilation succeeded.

        Raises:
            CompilationError: if any generation step fails. The partially
                generated output directory is left in place for inspection.
        """
        if not self.routes:
            raise ValidationError("Cannot compile an app with zero routes.")

        steps = [
            ("directory structure", self._create_directory_structure),
            ("app.json", self._generate_app_json),
            ("package.json", self._generate_package_json),
            ("tsconfig.json", self._generate_tsconfig),
            ("babel.config.js", self._generate_babel_config),
            ("App.tsx", self._generate_app_tsx),
            ("navigation", self._generate_navigation_structure),
            ("components", self._generate_components),
            ("state management", self._generate_state_management),
            ("static data", self._generate_static_data),
            ("utilities", self._generate_utilities),
            ("env files", self._generate_env_files),
            ("gitignore", self._generate_gitignore),
        ]

        for step_name, step_fn in steps:
            try:
                step_fn()
            except CompilerError:
                raise
            except Exception as exc:  # noqa: BLE001 - surfaced as CompilationError
                raise CompilationError(f"Failed while generating {step_name}: {exc}") from exc

        logger.info("Compilation successful. Project generated at: %s", self.output_dir)
        return True

    def _write_file(self, relative_path: str, content: str) -> None:
        path = _safe_relative_path(self.output_dir, relative_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    # -- directory scaffolding ----------------------------------------------
    def _create_directory_structure(self) -> None:
        directories = [
            "src",
            "src/navigation",
            "src/screens",
            "src/components",
            "src/state",
            "src/state/actions",
            "src/state/reducers",
            "src/state/selectors",
            "src/services",
            "src/utils",
            "src/constants",
            "src/types",
            "src/hooks",
            "assets",
            "assets/images",
            "assets/fonts",
            "assets/icons",
        ]
        for directory in directories:
            _safe_relative_path(self.output_dir, directory).mkdir(parents=True, exist_ok=True)

    # -- config files ---------------------------------------------------
    def _generate_app_json(self) -> None:
        app_json = {
            "expo": {
                "name": self.config.name,
                "slug": self.config.slug,
                "version": self.config.version,
                "orientation": self.config.orientation,
                "icon": self.config.icon,
                "splash": self.config.splash,
                "userInterfaceStyle": "light",
                "assetBundlePatterns": ["**/*"],
                "ios": {
                    "supportsTablet": True,
                    "bundleIdentifier": self.config.bundle_identifier,
                },
                "android": {
                    "adaptiveIcon": {
                        "foregroundImage": self.config.icon,
                        "backgroundColor": self.config.background_color,
                    },
                    "package": self.config.bundle_identifier,
                },
                "web": {"favicon": self.config.icon},
                "plugins": ["expo-router"],
                "extra": {
                    "router": {"origin": False},
                    "eas": {"projectId": str(uuid.uuid4())},
                },
            }
        }
        self._write_file("app.json", json.dumps(app_json, indent=2) + "\n")

    def _generate_package_json(self) -> None:
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

        for manager in self.state_managers:
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

        package_json = {
            "name": self.config.slug,
            "version": self.config.version,
            "description": self.config.description,
            "author": self.config.author,
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
        self._write_file("package.json", json.dumps(package_json, indent=2) + "\n")

    def _generate_tsconfig(self) -> None:
        tsconfig = {
            "extends": "expo/tsconfig.base",
            "compilerOptions": {
                "strict": True,
                "baseUrl": ".",
                "paths": {"@/*": ["./src/*"]},
            },
            "include": ["**/*.ts", "**/*.tsx", ".expo/types/**/*.ts", "expo-env.d.ts"],
        }
        self._write_file("tsconfig.json", json.dumps(tsconfig, indent=2) + "\n")

    def _generate_babel_config(self) -> None:
        content = (
            "module.exports = function (api) {\n"
            "  api.cache(true);\n"
            "  return {\n"
            "    presets: ['babel-preset-expo'],\n"
            "    plugins: ['react-native-reanimated/plugin'],\n"
            "  };\n"
            "};\n"
        )
        self._write_file("babel.config.js", content)

    def _generate_gitignore(self) -> None:
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
        self._write_file(".gitignore", content + "\n")

    # -- App entry point --------------------------------------------------
    def _generate_app_tsx(self) -> None:
        imports = self._generate_state_providers_import()
        open_tags = self._generate_state_providers_wrapper()
        close_tags = self._generate_state_providers_close()

        content = f"""import React from 'react';
import {{ GestureHandlerRootView }} from 'react-native-gesture-handler';
import {{ NavigationContainer }} from '@react-navigation/native';
import {{ SafeAreaProvider }} from 'react-native-safe-area-context';
import {{ StatusBar }} from 'expo-status-bar';
import RootNavigator from './src/navigation/RootNavigator';
{imports}

export default function App() {{
  return (
    <GestureHandlerRootView style={{{{ flex: 1 }}}}>
      <SafeAreaProvider>
{open_tags}
        <NavigationContainer>
          <RootNavigator />
        </NavigationContainer>
{close_tags}
        <StatusBar style="auto" />
      </SafeAreaProvider>
    </GestureHandlerRootView>
  );
}}
"""
        self._write_file("App.tsx", content)

    def _generate_state_providers_import(self) -> str:
        imports = []
        for manager in self.state_managers:
            if manager.type is StateManagerType.REDUX:
                imports.append("import { Provider } from 'react-redux';")
                imports.append("import store from './src/state/store';")
            elif manager.type is StateManagerType.RECOIL:
                imports.append("import { RecoilRoot } from 'recoil';")
            elif manager.type is StateManagerType.CONTEXT:
                imports.append("import { AppContextProvider } from './src/state/AppContext';")
            # zustand needs no provider/import here
        return "\n".join(imports)

    def _generate_state_providers_wrapper(self) -> str:
        tags = []
        for manager in self.state_managers:
            if manager.type is StateManagerType.REDUX:
                tags.append("<Provider store={store}>")
            elif manager.type is StateManagerType.RECOIL:
                tags.append("<RecoilRoot>")
            elif manager.type is StateManagerType.CONTEXT:
                tags.append("<AppContextProvider>")
        return "\n".join(f"        {t}" for t in tags)

    def _generate_state_providers_close(self) -> str:
        tags = []
        for manager in reversed(self.state_managers):
            if manager.type is StateManagerType.REDUX:
                tags.append("</Provider>")
            elif manager.type is StateManagerType.RECOIL:
                tags.append("</RecoilRoot>")
            elif manager.type is StateManagerType.CONTEXT:
                tags.append("</AppContextProvider>")
        return "\n".join(f"        {t}" for t in tags)

    # -- navigation -------------------------------------------------------
    def _generate_navigation_structure(self) -> None:
        self._generate_root_navigator()
        self._generate_screen_files()
        self._generate_navigation_types()

    def _navigator_kind(self) -> NavigationType:
        return NavigationType(self.navigation_structure.get("type", NavigationType.STACK.value))

    def _generate_root_navigator(self) -> None:
        nav_kind = self._navigator_kind()
        initial_route = self.navigation_structure.get("initialRoute") or next(
            (r.name for r in self.routes if r.initial_route), self.routes[0].name
        )

        navigator_var, factory_import, factory_call, screen_tag = {
            NavigationType.STACK: (
                "Navigator",
                "import { createStackNavigator } from '@react-navigation/stack';",
                "createStackNavigator<RootStackParamList>()",
                "Navigator.Screen",
            ),
            NavigationType.TAB: (
                "Navigator",
                "import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';",
                "createBottomTabNavigator<RootStackParamList>()",
                "Navigator.Screen",
            ),
            NavigationType.BOTTOM_TAB: (
                "Navigator",
                "import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';",
                "createBottomTabNavigator<RootStackParamList>()",
                "Navigator.Screen",
            ),
            NavigationType.DRAWER: (
                "Navigator",
                "import { createDrawerNavigator } from '@react-navigation/drawer';",
                "createDrawerNavigator<RootStackParamList>()",
                "Navigator.Screen",
            ),
        }[nav_kind]

        screen_imports = self._generate_navigation_imports()
        screen_entries = self._generate_navigation_screens(screen_tag)

        content = f"""import React from 'react';
{factory_import}
import {{ RootStackParamList }} from '../types/navigation';
{screen_imports}

const {navigator_var} = {factory_call};

export default function RootNavigator() {{
  return (
    <{navigator_var}.Navigator
      initialRouteName="{initial_route}"
      screenOptions={{{{ headerShown: false }}}}
    >
{screen_entries}
    </{navigator_var}.Navigator>
  );
}}
"""
        self._write_file("src/navigation/RootNavigator.tsx", content)

    def _generate_navigation_imports(self) -> str:
        lines = []
        for route in self.routes:
            component_name = to_screen_component_name(route.component)
            module_name = Path(route.component).stem
            lines.append(f"import {component_name} from '../screens/{module_name}';")
        return "\n".join(lines)

    def _generate_navigation_screens(self, screen_tag: str) -> str:
        screens = []
        for route in self.routes:
            component_name = to_screen_component_name(route.component)
            options = json.dumps(route.screen_options) if route.screen_options else "{}"
            screens.append(
                f'      <{screen_tag}\n'
                f'        name="{route.name}"\n'
                f"        component={{{component_name}}}\n"
                f"        options={{{options}}}\n"
                f"      />"
            )
        return "\n".join(screens)

    def _generate_screen_files(self) -> None:
        for route in self.routes:
            component_name = to_screen_component_name(route.component)
            module_name = Path(route.component).stem
            title = (route.title or route.name).replace("'", "\\'")
            body = self._generate_screen_body(route)

            content = f"""import React from 'react';
import {{ View, Text, StyleSheet }} from 'react-native';
import {{ SafeAreaView }} from 'react-native-safe-area-context';

export default function {component_name}() {{
  return (
    <SafeAreaView style={{styles.container}}>
      <View style={{styles.content}}>
        <Text style={{styles.title}}>{title}</Text>
        {body}
      </View>
    </SafeAreaView>
  );
}}

const styles = StyleSheet.create({{
  container: {{
    flex: 1,
    backgroundColor: '{self.config.background_color}',
  }},
  content: {{
    flex: 1,
    padding: 16,
    justifyContent: 'center',
  }},
  title: {{
    fontSize: 24,
    fontWeight: '600',
    marginBottom: 16,
    color: '#000',
  }},
}});
"""
            self._write_file(f"src/screens/{module_name}.tsx", content)

    def _generate_screen_body(self, route: NavRoute) -> str:
        if route.name in self.components:
            return f"<{route.name} />"
        return "<Text>Screen content goes here</Text>"

    def _generate_navigation_types(self) -> None:
        route_entries = "\n".join(f"  {route.name}: undefined;" for route in self.routes)
        content = f"""export type RootStackParamList = {{
{route_entries}
}};

export type AppContextType = {{
  theme: string;
  setTheme: (theme: string) => void;
}};
"""
        self._write_file("src/types/navigation.ts", content)

    # -- components -------------------------------------------------------
    def _generate_components(self) -> None:
        for component_name, component_data in self.components.items():
            props_block = self._generate_component_props(component_data)
            body = self._generate_component_body(component_data)
            content = f"""import React from 'react';
import {{ View, Text, StyleSheet }} from 'react-native';

interface {component_name}Props {{
{props_block}
}}

export function {component_name}(props: {component_name}Props) {{
  return (
    <View style={{styles.container}}>
      {body}
    </View>
  );
}}

const styles = StyleSheet.create({{
  container: {{
    flex: 1,
    padding: 16,
  }},
}});
"""
            self._write_file(f"src/components/{component_name}.tsx", content)

    def _generate_component_props(self, component_data: Dict[str, Any]) -> str:
        props = component_data.get("props", {})
        if not props:
            return "  // No props"
        return "\n".join(f"  {name}: {prop_type};" for name, prop_type in props.items())

    def _generate_component_body(self, component_data: Dict[str, Any]) -> str:
        content = component_data.get("content", "")
        if content:
            escaped = str(content).replace("{", "{'{'}").replace("}", "{'}'}")
            return f"<Text>{escaped}</Text>"
        return "<Text>Component placeholder</Text>"

    # -- state management ---------------------------------------------------
    def _generate_state_management(self) -> None:
        for manager in self.state_managers:
            if manager.type is StateManagerType.REDUX:
                self._generate_redux_files()
            elif manager.type is StateManagerType.ZUSTAND:
                self._generate_zustand_files()
            elif manager.type is StateManagerType.CONTEXT:
                self._generate_context_files()
            elif manager.type is StateManagerType.RECOIL:
                self._generate_recoil_files()

    def _generate_redux_files(self) -> None:
        self._write_file(
            "src/state/store.ts",
            """import { configureStore } from '@reduxjs/toolkit';
import rootReducer from './reducers';

const store = configureStore({
  reducer: rootReducer,
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

export default store;
""",
        )
        self._write_file(
            "src/state/actions/index.ts",
            """export const ACTIONS = {
  // Action types will be added here
} as const;
""",
        )
        self._write_file(
            "src/state/reducers/index.ts",
            """export interface AppState {
  // Shape of application state goes here
}

const initialState: AppState = {};

export default function rootReducer(state: AppState = initialState, action: { type: string }): AppState {
  switch (action.type) {
    default:
      return state;
  }
}
""",
        )

    def _generate_zustand_files(self) -> None:
        self._write_file(
            "src/state/store.ts",
            """import { create } from 'zustand';

interface AppStore {
  // State properties go here
  // Actions go here
}

export const useAppStore = create<AppStore>((set) => ({
  // Store implementation goes here
}));
""",
        )

    def _generate_context_files(self) -> None:
        self._write_file(
            "src/state/AppContext.tsx",
            """import React, { createContext, useContext, useState, ReactNode } from 'react';

interface AppContextType {
  theme: string;
  setTheme: (theme: string) => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export function AppContextProvider({ children }: { children: ReactNode }) {
  const [theme, setTheme] = useState<string>('light');

  return (
    <AppContext.Provider value={{ theme, setTheme }}>
      {children}
    </AppContext.Provider>
  );
}

export function useAppContext(): AppContextType {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useAppContext must be used within an AppContextProvider');
  }
  return context;
}
""",
        )

    def _generate_recoil_files(self) -> None:
        self._write_file(
            "src/state/atoms.ts",
            """import { atom } from 'recoil';

export const themeAtom = atom<string>({
  key: 'themeAtom',
  default: 'light',
});

export const userAtom = atom<unknown | null>({
  key: 'userAtom',
  default: null,
});
""",
        )

    # -- static data / constants ---------------------------------------------
    def _generate_static_data(self) -> None:
        self._write_file(
            "src/constants/colors.ts",
            """export const Colors = {
  primary: '#007AFF',
  secondary: '#5AC8FA',
  success: '#34C759',
  warning: '#FF9500',
  error: '#FF3B30',
  white: '#FFFFFF',
  black: '#000000',
  gray: '#8E8E93',
  lightGray: '#F2F2F7',
} as const;
""",
        )
        self._write_file(
            "src/constants/spacing.ts",
            """export const Spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  xxl: 48,
} as const;
""",
        )
        self._write_file(
            "src/constants/typography.ts",
            """export const Typography = {
  h1: { fontSize: 32, fontWeight: '700', lineHeight: 38 },
  h2: { fontSize: 24, fontWeight: '600', lineHeight: 30 },
  body: { fontSize: 16, fontWeight: '400', lineHeight: 24 },
  caption: { fontSize: 12, fontWeight: '400', lineHeight: 16 },
} as const;
""",
        )
        if self.static_data:
            data_content = "export const DATA = " + json.dumps(self.static_data, indent=2) + " as const;\n"
            self._write_file("src/constants/data.ts", data_content)

    # -- utilities ------------------------------------------------------
    def _generate_utilities(self) -> None:
        self._write_file(
            "src/utils/validation.ts",
            r"""export function isEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

export function isPhoneNumber(phone: string): boolean {
  const phoneRegex = /^[\d\s\-+()]{10,}$/;
  return phoneRegex.test(phone);
}

export function isEmpty(value: unknown): boolean {
  if (value === undefined || value === null || value === '') return true;
  if (Array.isArray(value)) return value.length === 0;
  if (typeof value === 'object') return Object.keys(value as object).length === 0;
  return false;
}
""",
        )
        self._write_file(
            "src/utils/format.ts",
            """export function formatDate(date: Date, _format: string = 'MM/DD/YYYY'): string {
  const options: Intl.DateTimeFormatOptions = {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  };
  return new Intl.DateTimeFormat('en-US', options).format(date);
}

export function formatCurrency(amount: number, currency: string = 'USD'): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
  }).format(amount);
}

export function truncateString(str: string, length: number): string {
  if (str.length <= length) return str;
  return str.substring(0, Math.max(0, length - 3)) + '...';
}
""",
        )
        self._write_file(
            "src/utils/api.ts",
            """import Constants from 'expo-constants';

const API_BASE_URL =
  process.env.EXPO_PUBLIC_API_URL ?? (Constants.expoConfig?.extra?.apiUrl as string | undefined) ?? 'http://localhost:3000';

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

export async function apiCall<T = unknown>(
  endpoint: string,
  method: string = 'GET',
  data?: unknown,
  headers?: Record<string, string>,
): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...headers,
    },
    body: data !== undefined ? JSON.stringify(data) : undefined,
  });

  if (!response.ok) {
    throw new ApiError(`HTTP ${response.status}: ${response.statusText}`, response.status);
  }

  return (await response.json()) as T;
}
""",
        )

    # -- environment files ----------------------------------------------
    def _generate_env_files(self) -> None:
        self._write_file(
            ".env.development",
            "# Development environment\n"
            "EXPO_PUBLIC_API_URL=http://localhost:3000\n"
            "EXPO_PUBLIC_APP_ENV=development\n",
        )
        self._write_file(
            ".env.production",
            "# Production environment - fill in real values before deploying\n"
            "EXPO_PUBLIC_API_URL=https://api.production.example.com\n"
            "EXPO_PUBLIC_APP_ENV=production\n",
        )
        self._write_file(
            ".env.example",
            "# Copy this file to .env.development / .env.production and fill in values\n"
            "EXPO_PUBLIC_API_URL=http://localhost:3000\n"
            "EXPO_PUBLIC_APP_ENV=development\n",
        )

    # -- reporting ------------------------------------------------------
    def generate_report(self) -> Dict[str, Any]:
        """Generate a JSON-serializable compilation report."""
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "appName": self.config.name,
            "version": self.config.version,
            "outputDirectory": str(self.output_dir),
            "routes": len(self.routes),
            "components": len(self.components),
            "stateManagers": [
                {**asdict(m), "type": m.type.value} for m in self.state_managers
            ],
            "navigationStructure": self.navigation_structure,
            "status": "completed",
        }


# --------------------------------------------------------------------------- #
# Builder
# --------------------------------------------------------------------------- #
class CompilerBuilder:
    """Fluent builder for configuring and running a CompilerEngine."""

    def __init__(self, output_dir: str) -> None:
        self.compiler = CompilerEngine(output_dir)

    def set_config(self, config: AppConfig) -> "CompilerBuilder":
        self.compiler.config = config
        return self

    def add_route(
        self, name: str, component: str, title: Optional[str] = None, initial: bool = False
    ) -> "CompilerBuilder":
        self.compiler.add_route(
            NavRoute(name=name, component=component, title=title or name, initial_route=initial)
        )
        return self

    def add_state_manager(
        self, name: str, manager_type: str, version: str = "latest"
    ) -> "CompilerBuilder":
        self.compiler.add_state_manager(StateManager(name=name, type=manager_type, version=version))
        return self

    def add_component(self, name: str, content: Dict[str, Any]) -> "CompilerBuilder":
        self.compiler.add_component(name, content)
        return self

    def add_static_data(self, key: str, data: Any) -> "CompilerBuilder":
        self.compiler.add_static_data(key, data)
        return self

    def set_navigation_structure(self, structure: Dict[str, Any]) -> "CompilerBuilder":
        self.compiler.set_navigation_structure(structure)
        return self

    def build(self) -> CompilerEngine:
        return self.compiler

    def compile(self) -> bool:
        return self.compiler.compile()


# --------------------------------------------------------------------------- #
# Example usage / CLI entry point
# --------------------------------------------------------------------------- #
def _main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    output_path = "./generated_app"
    config = AppConfig(
        name="MyApp",
        display_name="My Application",
        slug="my-app",
        version="1.0.0",
        description="Auto-generated React Native app",
        author="Jinie",
    )

    try:
        builder = (
            CompilerBuilder(output_path)
            .set_config(config)
            .add_route("Home", "HomeScreen.tsx", "Home", initial=True)
            .add_route("Profile", "ProfileScreen.tsx", "Profile")
            .add_route("Settings", "SettingsScreen.tsx", "Settings")
            .add_state_manager("Redux Store", "redux", "^4.2.1")
            .add_component("Button", {"props": {"label": "string", "onPress": "() => void"}})
            .add_component("Card", {"props": {"title": "string", "content": "string"}})
            .add_static_data("apiUrl", "https://api.example.com")
            .set_navigation_structure({"type": "stack", "initialRoute": "Home"})
        )
        builder.compile()
    except CompilerError as exc:
        logger.error("Compilation failed: %s", exc)
        return 1

    logger.info("React Native app successfully generated!")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
