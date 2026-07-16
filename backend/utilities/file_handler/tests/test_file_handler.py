import pytest
from file_handler import FileHandler

@pytest.fixture
def handler(tmp_path):
    return FileHandler(base_path=str(tmp_path))

def test_write_and_read_file(handler):
    assert handler.write_file("app/index.tsx", "export default function App() {}")
    assert handler.read_file("app/index.tsx") == "export default function App() {}"

def test_write_no_overwrite_returns_false(handler):
    handler.write_file("a.txt", "v1")
    result = handler.write_file("a.txt", "v2", overwrite=False)
    assert result is False
    assert handler.read_file("a.txt") == "v1"

def test_file_exists_and_delete(handler):
    handler.write_file("temp.txt", "data")
    assert handler.file_exists("temp.txt")
    handler.delete_file("temp.txt")
    assert not handler.file_exists("temp.txt")

def test_create_project_scaffold(handler):
    structure = {
        "App.tsx": "export default App;",
        "components": {
            "Header.tsx": "export const Header = () => null;"
        }
    }
    assert handler.create_project_scaffold("my_app", structure)
    assert handler.file_exists("my_app/App.tsx")
    assert handler.file_exists("my_app/components/Header.tsx")

def test_read_missing_file_raises(handler):
    with pytest.raises(FileNotFoundError):
        handler.read_file("nope.txt")