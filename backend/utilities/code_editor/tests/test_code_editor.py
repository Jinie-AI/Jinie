from code_editor import CodeEditor

def test_insert_at_line():
    editor = CodeEditor("line1\nline3")
    editor.insert_at_line(2, "line2")
    assert editor.get_content() == "line1\nline2\nline3"

def test_replace_block():
    editor = CodeEditor("a\nb\nc\nd")
    editor.replace_block(2, 3, "X\nY")
    assert editor.get_content() == "a\nX\nY\nd"

def test_insert_component_prevents_duplicates():
    editor = CodeEditor("")
    assert editor.insert_component("Header", "const Header = () => null;")
    # second attempt should be rejected
    assert editor.insert_component("Header", "const Header = () => null;") is False

def test_validate_python_syntax_valid():
    editor = CodeEditor("def foo():\n    return 1")
    is_valid, error = editor.validate_syntax("python")
    assert is_valid and error is None

def test_validate_python_syntax_invalid():
    editor = CodeEditor("def foo(:\n    return 1")
    is_valid, error = editor.validate_syntax("python")
    assert not is_valid
    assert "SyntaxError" in error

def test_validate_tsx_bracket_balance():
    editor = CodeEditor("function App() { return <View>{items.map(i => <Item/>)}</View> }")
    is_valid, _ = editor.validate_syntax("tsx")
    assert is_valid

def test_validate_tsx_unbalanced():
    editor = CodeEditor("function App() { return <View>")
    is_valid, error = editor.validate_syntax("tsx")
    assert not is_valid