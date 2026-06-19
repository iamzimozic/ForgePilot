from pathlib import Path

def test_html_structure():
    html_content = Path("index.html").read_text()

    assert "<title>Snake Game</title>" in html_content
    assert "<link rel=\"stylesheet\" href=\"style.css\">" in html_content
    assert "<canvas id=\"gameCanvas\" width=\"400\" height=\"400\"></canvas>" in html_content
    assert "<div id=\"score\">Score: 0</div>" in html_content
    assert "<button id=\"startButton\">Start Game</button>" in html_content
    assert "<script src=\"script.js\"></script>" in html_content

def test_css_file_exists():
    assert Path("style.css").exists()
    assert Path("style.css").read_text() # Check if it's not empty

def test_js_file_exists():
    assert Path("script.js").exists()
    assert Path("script.js").read_text() # Check if it's not empty
