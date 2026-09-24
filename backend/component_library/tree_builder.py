class ComponentNode:
    def __init__(self, name: str, props: dict = None, category: str = ""):
        self.name = name
        self.props = props or {}
        self.category = category
        self.children = []

    def add_child(self, node: "ComponentNode"):
        self.children.append(node)
        return node

    def to_dict(self):
        return {
            "component": self.name,
            "category": self.category,
            "props": self.props,
            "children": [child.to_dict() for child in self.children]
        }

def build_screen_tree_from_rag(retrieved_components):
    root = ComponentNode("View", {"style": {"flex": 1, "padding": 16, "justifyContent": "center"}}, category="Layout")
    container = root.add_child(ComponentNode("Card", {"elevation": 2}, category="Surface"))

    for comp in retrieved_components:
        name = comp.get("name")
        category = comp.get("category")
        
        default_props = {}
        if name == "TextInput":
            default_props = {"placeholder": "Enter value", "mode": "outlined"}
        elif name == "Button":
            default_props = {"mode": "contained"}

        container.add_child(ComponentNode(name, default_props, category=category))

    return root.to_dict()

if __name__ == "__main__":
    from backend.srs_rag_bridge import get_rag_components
    from backend.component_library.tree_builder import build_component_tree

    # Fetch real components using your bridge
    retrieved_data = get_rag_components("TouchableRipple button interaction")
    
    # Pass them into the tree builder
    tree_output = build_component_tree(retrieved_data)
    print("Generated Tree Structure:", tree_output)
    