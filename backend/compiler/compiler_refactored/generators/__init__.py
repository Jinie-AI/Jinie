"""Code-generation modules for the compiler package.

Each module in this package owns generation of one category of output file
(config files, navigation, components, state management, etc.), following
the single-responsibility principle. `engine.CompilerEngine.compile()` wires
these generators together into the full compilation pipeline.
"""
