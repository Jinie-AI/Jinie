"""Generates React component .tsx files from registered component data."""

from __future__ import annotations

from typing import Any, Dict

from ..file_writer import FileWriter


class ComponentsGenerator:
    """Generates the project's React component files."""

    def __init__(self, components: Dict[str, Dict[str, Any]], writer: FileWriter) -> None:
        self._components = components
        self._writer = writer

    # -- components -------------------------------------------------------
    def generate_components(self) -> None:
        for component_name, component_data in self._components.items():
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
            self._writer.write(f"src/components/{component_name}.tsx", content)

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
