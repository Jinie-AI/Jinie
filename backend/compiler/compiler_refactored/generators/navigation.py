"""Generates navigation wiring: RootNavigator.tsx, per-route screen files,
and the navigation TypeScript types.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from ..enums import NavigationType
from ..file_writer import FileWriter
from ..helpers import to_screen_component_name
from ..models import AppConfig, NavRoute


class NavigationGenerator:
    """Generates the navigation structure of the app (navigator, screens,
    and navigation types).
    """

    def __init__(
        self,
        routes: List[NavRoute],
        components: Dict[str, Dict[str, Any]],
        navigation_structure: Dict[str, Any],
        config: AppConfig,
        writer: FileWriter,
    ) -> None:
        self._routes = routes
        self._components = components
        self._navigation_structure = navigation_structure
        self._config = config
        self._writer = writer

    # -- navigation -------------------------------------------------------
    def generate_navigation_structure(self) -> None:
        self._generate_root_navigator()
        self._generate_screen_files()
        self._generate_navigation_types()

    def _navigator_kind(self) -> NavigationType:
        return NavigationType(self._navigation_structure.get("type", NavigationType.STACK.value))

    def _generate_root_navigator(self) -> None:
        nav_kind = self._navigator_kind()
        initial_route = self._navigation_structure.get("initialRoute") or next(
            (r.name for r in self._routes if r.initial_route), self._routes[0].name
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
        self._writer.write("src/navigation/RootNavigator.tsx", content)

    def _generate_navigation_imports(self) -> str:
        lines = []
        for route in self._routes:
            component_name = to_screen_component_name(route.component)
            module_name = Path(route.component).stem
            lines.append(f"import {component_name} from '../screens/{module_name}';")
        return "\n".join(lines)

    def _generate_navigation_screens(self, screen_tag: str) -> str:
        screens = []
        for route in self._routes:
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
        for route in self._routes:
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
    backgroundColor: '{self._config.background_color}',
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
            self._writer.write(f"src/screens/{module_name}.tsx", content)

    def _generate_screen_body(self, route: NavRoute) -> str:
        if route.name in self._components:
            return f"<{route.name} />"
        return "<Text>Screen content goes here</Text>"

    def _generate_navigation_types(self) -> None:
        route_entries = "\n".join(f"  {route.name}: undefined;" for route in self._routes)
        content = f"""export type RootStackParamList = {{
{route_entries}
}};

export type AppContextType = {{
  theme: string;
  setTheme: (theme: string) => void;
}};
"""
        self._writer.write("src/types/navigation.ts", content)
