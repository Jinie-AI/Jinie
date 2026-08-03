"""Generates the app's entry point: App.tsx, wired up with whichever state
management providers are configured.
"""

from __future__ import annotations

from typing import List

from ..enums import StateManagerType
from ..file_writer import FileWriter
from ..models import StateManager


class AppEntryGenerator:
    """Generates App.tsx and its state-provider wiring."""

    def __init__(self, state_managers: List[StateManager], writer: FileWriter) -> None:
        self._state_managers = state_managers
        self._writer = writer

    # -- App entry point --------------------------------------------------
    def generate_app_tsx(self) -> None:
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
        self._writer.write("App.tsx", content)

    def _generate_state_providers_import(self) -> str:
        imports = []
        for manager in self._state_managers:
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
        for manager in self._state_managers:
            if manager.type is StateManagerType.REDUX:
                tags.append("<Provider store={store}>")
            elif manager.type is StateManagerType.RECOIL:
                tags.append("<RecoilRoot>")
            elif manager.type is StateManagerType.CONTEXT:
                tags.append("<AppContextProvider>")
        return "\n".join(f"        {t}" for t in tags)

    def _generate_state_providers_close(self) -> str:
        tags = []
        for manager in reversed(self._state_managers):
            if manager.type is StateManagerType.REDUX:
                tags.append("</Provider>")
            elif manager.type is StateManagerType.RECOIL:
                tags.append("</RecoilRoot>")
            elif manager.type is StateManagerType.CONTEXT:
                tags.append("</AppContextProvider>")
        return "\n".join(f"        {t}" for t in tags)
