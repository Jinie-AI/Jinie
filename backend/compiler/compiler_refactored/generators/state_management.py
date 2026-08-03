"""Generates state-management scaffolding files for whichever state
management solutions (Redux, Zustand, Context, Recoil) are configured.
"""

from __future__ import annotations

from typing import List

from ..enums import StateManagerType
from ..file_writer import FileWriter
from ..models import StateManager


class StateManagementGenerator:
    """Generates state-management library scaffolding files."""

    def __init__(self, state_managers: List[StateManager], writer: FileWriter) -> None:
        self._state_managers = state_managers
        self._writer = writer

    # -- state management ---------------------------------------------------
    def generate_state_management(self) -> None:
        for manager in self._state_managers:
            if manager.type is StateManagerType.REDUX:
                self._generate_redux_files()
            elif manager.type is StateManagerType.ZUSTAND:
                self._generate_zustand_files()
            elif manager.type is StateManagerType.CONTEXT:
                self._generate_context_files()
            elif manager.type is StateManagerType.RECOIL:
                self._generate_recoil_files()

    def _generate_redux_files(self) -> None:
        self._writer.write(
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
        self._writer.write(
            "src/state/actions/index.ts",
            """export const ACTIONS = {
  // Action types will be added here
} as const;
""",
        )
        self._writer.write(
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
        self._writer.write(
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
        self._writer.write(
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
        self._writer.write(
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
