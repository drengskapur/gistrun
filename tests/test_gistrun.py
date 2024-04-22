import io
import json
import os
import subprocess
from unittest.mock import Mock, patch

import pytest
import requests
from click.testing import CliRunner

from gistrun.__about__ import __version__
from gistrun.cli import *


def create_mock_gist(description, files):
    mock_gist = Mock()
    mock_gist.description = description
    mock_gist.files = files
    return mock_gist


def create_mock_file(filename, content):
    mock_file = Mock()
    mock_file.filename = filename
    mock_file.content = content
    return mock_file


with open("tests/data.json", "r") as f:
    gist_data = json.load(f)

# DIFFERENT FILE TYPES
python_file = create_mock_file("script.py", "print('Hello, World!')")
javascript_file = create_mock_file("script.js", "console.log('Hello, World!');")
shell_file = create_mock_file("script.sh", "#!/bin/bash\necho 'Hello, World!'")
markdown_file = create_mock_file("README.md", "# Hello, World!")
text_file = create_mock_file("file.txt", "Hello, World!")
csv_file = create_mock_file("data.csv", "Name,Age\nJohn,25\nJane,30")
json_file = create_mock_file("data.json", '{"name": "John", "age": 25}')
xml_file = create_mock_file("data.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<data>\n  <name>John</name>\n  <age>25</age>\n</data>')
html_file = create_mock_file("index.html", "<!DOCTYPE html>\n<html>\n<head>\n  <title>Hello, World!</title>\n</head>\n<body>\n  <h1>Hello, World!</h1>\n</body>\n</html>")
css_file = create_mock_file("styles.css", "body {\n  background-color: #f0f0f0;\n  color: #333;\n}")

# MULTIPLE FILES
multiple_files_gist = create_mock_gist("Multiple Files Gist", [python_file, javascript_file, shell_file])

# DIFFERENT SIZES
small_gist = create_mock_gist("Small Gist", [create_mock_file("small.txt", "Hello")])
medium_gist = create_mock_gist("Medium Gist", [create_mock_file("medium.txt", "Hello, World!\n" * 100)])
large_gist = create_mock_gist("Large Gist", [create_mock_file("large.txt", "Hello, World!\n" * 1000)])

# DIFFERENT DESCRIPTIONS
descriptive_gist = create_mock_gist("Descriptive Gist", [python_file])
special_chars_gist = create_mock_gist("Gist with Special Characters !@#$%^&*()", [python_file])
emoji_gist = create_mock_gist("Gist with Emoji 😄🚀", [python_file])
long_description_gist = create_mock_gist("Gist with a Very Long Description " * 10, [python_file])
empty_description_gist = create_mock_gist("", [python_file])

# DIFFERENT LEVELS OF COMPLEXITY
simple_gist = create_mock_gist("Simple Gist", [python_file])
complex_gist = create_mock_gist("Complex Gist", [python_file, javascript_file, shell_file, markdown_file, text_file, csv_file, json_file, xml_file, html_file, css_file])

# EDGE CASES
empty_file_gist = create_mock_gist("Gist with Empty File", [create_mock_file("empty.txt", "")])
whitespace_file_gist = create_mock_gist("Gist with Whitespace File", [create_mock_file("whitespace.txt", "   \n\t   \n")])
non_ascii_file_gist = create_mock_gist("Gist with Non-ASCII File", [create_mock_file("non_ascii.txt", "Héllô, Wôrld!")])
special_chars_filename_gist = create_mock_gist("Gist with Special Characters in Filename", [create_mock_file("file!@#$%^&*().txt", "Hello, World!")])


@pytest.fixture
def runner():
    return CliRunner()


@patch("gistrun.cli.fetch_gist")
@patch("gistrun.cli.get_files")
@patch("gistrun.cli.execute_files")
def test_exec_command_with_different_file_types(mock_execute_files, mock_get_files, mock_fetch_gist, runner):
    mock_fetch_gist.return_value = multiple_files_gist
    mock_get_files.return_value = [
        ("script.py", python_file),
        ("script.js", javascript_file),
        ("script.sh", shell_file),
    ]
    result = runner.invoke(gistrun, ["exec", "octocat/multiple-files-gist", "-y"])
    mock_execute_files.assert_called_once()
    assert result.exit_code == 0


@patch("gistrun.cli.fetch_gist")
@patch("gistrun.cli.get_files")
@patch("gistrun.cli.execute_files")
def test_exec_command_with_different_gist_sizes(mock_execute_files, mock_get_files, mock_fetch_gist, runner):
    mock_fetch_gist.side_effect = [small_gist, medium_gist, large_gist]
    mock_get_files.side_effect = [
        [("small.txt", small_gist.files[0])],
        [("medium.txt", medium_gist.files[0])],
        [("large.txt", large_gist.files[0])],
    ]
    result = runner.invoke(gistrun, ["exec", "octocat/small-gist", "-y"])
    assert result.exit_code == 0
    result = runner.invoke(gistrun, ["exec", "octocat/medium-gist", "-y"])
    assert result.exit_code == 0
    result = runner.invoke(gistrun, ["exec", "octocat/large-gist", "-y"])
    assert result.exit_code == 0


@patch("gistrun.cli.fetch_gist")
@patch("gistrun.cli.get_files")
@patch("gistrun.cli.execute_files")
def test_exec_command_with_different_descriptions(mock_execute_files, mock_get_files, mock_fetch_gist, runner):
    mock_fetch_gist.side_effect = [descriptive_gist, special_chars_gist, emoji_gist, long_description_gist, empty_description_gist]
    mock_get_files.side_effect = [
        [("script.py", descriptive_gist.files[0])],
        [("script.py", special_chars_gist.files[0])],
        [("script.py", emoji_gist.files[0])],
        [("script.py", long_description_gist.files[0])],
        [("script.py", empty_description_gist.files[0])],
    ]
    result = runner.invoke(gistrun, ["exec", "octocat/descriptive-gist", "-y"])
    assert result.exit_code == 0
    result = runner.invoke(gistrun, ["exec", "octocat/special-chars-gist", "-y"])
    assert result.exit_code == 0
    result = runner.invoke(gistrun, ["exec", "octocat/emoji-gist", "-y"])
    assert result.exit_code == 0
    result = runner.invoke(gistrun, ["exec", "octocat/long-description-gist", "-y"])
    assert result.exit_code == 0
    result = runner.invoke(gistrun, ["exec", "octocat/empty-description-gist", "-y"])
    assert result.exit_code == 0


@patch("gistrun.cli.fetch_gist")
@patch("gistrun.cli.get_files")
@patch("gistrun.cli.execute_files")
def test_exec_command_with_different_complexity(mock_execute_files, mock_get_files, mock_fetch_gist, runner):
    mock_fetch_gist.side_effect = [simple_gist, complex_gist]
    mock_get_files.side_effect = [
        [("script.py", simple_gist.files[0])],
        [
            ("script.py", complex_gist.files[0]),
            ("script.js", complex_gist.files[1]),
            ("script.sh", complex_gist.files[2]),
            ("README.md", complex_gist.files[3]),
            ("file.txt", complex_gist.files[4]),
            ("data.csv", complex_gist.files[5]),
            ("data.json", complex_gist.files[6]),
            ("data.xml", complex_gist.files[7]),
            ("index.html", complex_gist.files[8]),
            ("styles.css", complex_gist.files[9]),
        ],
    ]
    result = runner.invoke(gistrun, ["exec", "octocat/simple-gist", "-y"])
    assert result.exit_code == 0
    result = runner.invoke(gistrun, ["exec", "octocat/complex-gist", "-y"])
    assert result.exit_code == 0


@patch("gistrun.cli.fetch_gist")
@patch("gistrun.cli.get_files")
@patch("gistrun.cli.execute_files")
def test_exec_command_with_edge_cases(mock_execute_files, mock_get_files, mock_fetch_gist, runner):
    mock_fetch_gist.side_effect = [empty_file_gist, whitespace_file_gist, non_ascii_file_gist, special_chars_filename_gist]
    mock_get_files.side_effect = [
        [("empty.txt", empty_file_gist.files[0])],
        [("whitespace.txt", whitespace_file_gist.files[0])],
        [("non_ascii.txt", non_ascii_file_gist.files[0])],
        [("file!@#$%^&*().txt", special_chars_filename_gist.files[0])],
    ]
    result = runner.invoke(gistrun, ["exec", "octocat/empty-file-gist", "-y"])
    assert result.exit_code == 0
    result = runner.invoke(gistrun, ["exec", "octocat/whitespace-file-gist", "-y"])
    assert result.exit_code == 0
    result = runner.invoke(gistrun, ["exec", "octocat/non-ascii-file-gist", "-y"])
    assert result.exit_code == 0
    result = runner.invoke(gistrun, ["exec", "octocat/special-chars-filename-gist", "-y"])
    assert result.exit_code == 0


# Test the exec command
@patch("gistrun.cli.fetch_gist")
@patch("gistrun.cli.get_files")
@patch("gistrun.cli.click.confirm")
@patch("gistrun.cli.execute_files")
def test_exec_command_confirmed(mock_execute_files, mock_confirm, mock_get_files, mock_fetch_gist, runner: CliRunner):
    mock_confirm.return_value = True
    mock_fetch_gist.return_value = {"id": "gist_id", "description": "my-gist", "files": {}}
    mock_get_files.return_value = [("file1.py", io.StringIO("print('Hello, World!')")), ("file2.js", io.StringIO("console.log('Hello, World!')"))]

    result = runner.invoke(gistrun, ["exec", "octocat/my-gist"])

    mock_confirm.assert_called_once()
    mock_execute_files.assert_called_once()
    assert "The following commands will be executed:" in result.output


@patch("gistrun.cli.fetch_gist")
@patch("gistrun.cli.get_files")
@patch("gistrun.cli.click.confirm")
@patch("gistrun.cli.execute_files")
def test_exec_command_skipped(mock_execute_files, mock_confirm, mock_get_files, mock_fetch_gist, runner: CliRunner):
    mock_confirm.return_value = False
    mock_fetch_gist.return_value = {"id": "gist_id", "description": "my-gist", "files": {}}
    mock_get_files.return_value = [("file1.py", io.StringIO("print('Hello, World!')")), ("file2.js", io.StringIO("console.log('Hello, World!')"))]

    result = runner.invoke(gistrun, ["exec", "octocat/my-gist"])

    mock_confirm.assert_called_once()
    mock_execute_files.assert_not_called()
    assert "The following commands will be executed:" in result.output
    assert "Aborted" in result.output


@patch("gistrun.cli.fetch_gist")
@patch("gistrun.cli.get_files")
@patch("gistrun.cli.click.confirm")
@patch("gistrun.cli.execute_files")
def test_exec_command_dry_run(mock_execute_files, mock_confirm, mock_get_files, mock_fetch_gist, runner: CliRunner):
    mock_fetch_gist.return_value = {"id": "gist_id", "description": "my-gist", "files": {}}
    mock_get_files.return_value = [("file1.py", io.StringIO("print('Hello, World!')")), ("file2.js", io.StringIO("console.log('Hello, World!')"))]

    result = runner.invoke(gistrun, ["exec", "octocat/my-gist", "--dry-run"])

    mock_confirm.assert_not_called()
    mock_execute_files.assert_not_called()
    assert "Dry run - Skipping execution" in result.output


@patch("gistrun.cli.fetch_gist")
@patch("gistrun.cli.get_files")
@patch("gistrun.cli.click.confirm")
@patch("gistrun.cli.execute_files")
def test_exec_command_no_prompt(mock_execute_files, mock_confirm, mock_get_files, mock_fetch_gist, runner: CliRunner):
    mock_fetch_gist.return_value = {"id": "gist_id", "description": "my-gist", "files": {}}
    mock_get_files.return_value = [("file1.py", io.StringIO("print('Hello, World!')")), ("file2.js", io.StringIO("console.log('Hello, World!')"))]

    result = runner.invoke(gistrun, ["exec", "octocat/my-gist", "-y"])

    mock_confirm.assert_not_called()
    mock_execute_files.assert_called_once()
    assert "The following commands will be executed:" not in result.output


@patch("gistrun.cli.fetch_gist")
@patch("gistrun.cli.get_files")
def test_exec_command_no_executable_files(mock_get_files, mock_fetch_gist, runner: CliRunner):
    mock_fetch_gist.return_value = {"id": "gist_id", "description": "my-gist", "files": {}}
    mock_get_files.return_value = []

    result = runner.invoke(gistrun, ["exec", "octocat/my-gist"])

    assert "Gist 'my-gist' doesn't contain any executable files." in result.output


# Validation tests
def test_validate_username_gistname_pair_empty():
    with pytest.raises(ValueError):
        validate_username_gistname_pair("")


def test_validate_username_gistname_pair_invalid():
    with pytest.raises(ValueError):
        validate_username_gistname_pair("invalid-format")
    with pytest.raises(ValueError):
        validate_username_gistname_pair("/")


def test_validate_username_empty():
    with pytest.raises(ValueError):
        validate_username("")


def test_validate_username_too_long():
    with pytest.raises(ValueError):
        validate_username("a" * 40)


def test_validate_username_invalid():
    with pytest.raises(ValueError):
        validate_username("invalid-username!")


def test_validate_gist_name_empty():
    with pytest.raises(ValueError):
        validate_gist_name("")


def test_validate_gist_name_invalid_characters():
    with pytest.raises(ValueError):
        validate_gist_name("invalid!@#")


def test_validate_username_gistname_pair_valid():
    assert validate_username_gistname_pair("octocat/my-gist") == ("octocat", "my-gist")


def test_validate_username_valid():
    validate_username("octocat")
    validate_username("valid_username123")


def test_validate_gist_name_valid():
    validate_gist_name("my-gist")
    validate_gist_name("valid_gist_name123")


# GitHub API tests
@patch("requests.get")
def test_search_gists_success(mock_get):
    mock_response = Mock()
    mock_response.json.return_value = [{"id": "gist_id", "description": "my-gist"}]
    mock_get.return_value = mock_response
    token = os.getenv("GITHUB_TOKEN")
    gists = search_gists("search_query", token)
    assert len(gists) == 1
    assert gists[0]["id"] == "gist_id"
    assert gists[0]["description"] == "my-gist"


@patch("requests.get")
def test_search_gists_failure(mock_get):
    mock_get.side_effect = requests.exceptions.RequestException("Request failed")
    token = os.getenv("GITHUB_TOKEN")
    with pytest.raises(requests.exceptions.RequestException):
        search_gists("search_query", token)


@patch("requests.get")
def test_list_user_gists_success(mock_get):
    mock_response = Mock()
    mock_response.json.return_value = [{"id": "gist_id", "description": "user-gist"}]
    mock_get.return_value = mock_response
    token = os.getenv("GITHUB_TOKEN")
    gists = list_user_gists("octocat", token)
    assert len(gists) == 1
    assert gists[0]["id"] == "gist_id"
    assert gists[0]["description"] == "user-gist"


@patch("requests.get")
def test_list_user_gists_failure(mock_get):
    mock_get.side_effect = requests.exceptions.RequestException("Request failed")
    with pytest.raises(requests.exceptions.RequestException):
        list_user_gists("octocat", "token")


@patch("requests.get")
def test_fetch_gists_empty_response(mock_get):
    mock_response = Mock()
    mock_response.json.return_value = []
    mock_get.return_value = mock_response
    token = os.getenv("GITHUB_TOKEN")
    gists = fetch_gists("octocat", 1, token)
    assert len(gists) == 0


@patch("requests.get")
def test_fetch_gists_success(mock_get):
    mock_response = Mock()
    mock_response.json.return_value = [{"id": "gist_id", "description": "my-gist"}]
    mock_get.return_value = mock_response
    token = os.getenv("GITHUB_TOKEN")
    gists = fetch_gists("octocat", 1, token)
    assert len(gists) == 1
    assert gists[0]["id"] == "gist_id"
    assert gists[0]["description"] == "my-gist"


@patch("requests.get")
def test_fetch_gists_pagination(mock_get):
    mock_response = Mock()
    mock_response.json.side_effect = [
        [{"id": "gist_id1", "description": "gist1"}],
        [{"id": "gist_id2", "description": "gist2"}],
        [],
    ]
    mock_get.return_value = mock_response
    token = os.getenv("GITHUB_TOKEN")
    gists = fetch_gist("octocat", "gist1", token)
    assert gists["id"] == "gist_id1"
    assert gists["description"] == "gist1"


@patch("requests.get")
def test_fetch_gist_not_found(mock_get):
    mock_get.side_effect = [
        Mock(json=lambda: [{"id": "gist_id1", "description": "gist1"}]),
        Mock(json=lambda: []),
    ]
    token = os.getenv("GITHUB_TOKEN")
    with pytest.raises(ValueError):
        fetch_gist("octocat", "gist2", token)


@patch("requests.get")
def test_fetch_gist_not_found_http_error(mock_get):
    mock_get.side_effect = requests.exceptions.HTTPError("403 Client Error")
    token = os.getenv("GITHUB_TOKEN")
    with pytest.raises(requests.exceptions.HTTPError):
        fetch_gists("octocat", 1, token)


# Gist processing tests
def test_get_files_empty():
    gist_data = {"files": {}}
    files = get_files(gist_data)
    assert len(files) == 0


def test_get_files_multiple():
    gist_data = {
        "files": {
            "file1.txt": {"raw_url": "https://gist.githubusercontent.com/file1.txt", "content": "File 1 content"},
            "file2.txt": {"raw_url": "https://gist.githubusercontent.com/file2.txt", "content": "File 2 content"},
            "file3.txt": {"raw_url": "https://gist.githubusercontent.com/file3.txt", "content": "File 3 content"},
        }
    }
    files = get_files(gist_data)
    assert len(files) == 3


def test_get_files():
    gist_data = {
        "files": {
            "file1.txt": {"raw_url": "https://gist.githubusercontent.com/file1.txt"},
            "file2.txt": {"raw_url": "https://gist.githubusercontent.com/file2.txt"},
        }
    }

    with patch("requests.get") as mock_get:
        mock_response_1 = Mock()
        mock_response_1.text = "File 1 content"
        mock_response_2 = Mock()
        mock_response_2.text = "File 2 content"
        mock_get.side_effect = [mock_response_1, mock_response_2]

        files = get_files(gist_data)
        assert len(files) == 2
        assert files[0][0] == "file1.txt"
        assert files[0][1].getvalue() == "File 1 content"
        assert files[1][0] == "file2.txt"
        assert files[1][1].getvalue() == "File 2 content"


def test_execute_mapping_case_insensitive():
    mapping = execute_mapping()
    assert mapping[".PY"] == "python"
    assert mapping[".Js"] == "node"
    assert mapping[".sH"] == "bash"


def test_execute_mapping_missing_extension():
    mapping = execute_mapping()
    assert ".nomapping" not in mapping


def test_execute_mapping():
    mapping = execute_mapping()
    assert mapping[".py"] == "python"
    assert mapping[".js"] == "node"
    assert mapping[".sh"] == "bash"


# Execution tests
def test_execute_file_dry_run():
    filename = "script.py"
    code = "print('Hello, World!')"
    command = "python"
    timeout = 60
    execute_file(filename, code, command, timeout, dry_run=True)


@patch("subprocess.run")
def test_execute_file_success(mock_run):
    mock_run.return_value = subprocess.CompletedProcess(args=["python", "file_to_test.py"], returncode=0)

    filename = "file_to_test.py"
    file_obj = io.StringIO("print('Hello, World!')")
    command = "python"
    timeout = 60
    execute_file(filename, file_obj, command, timeout, dry_run=False)


@patch("subprocess.run")
def test_execute_file_failure(mock_run):
    mock_run.side_effect = subprocess.CalledProcessError(1, "python script.py")
    filename = "script.py"
    file_obj = io.StringIO("invalid code")
    command = "python"
    timeout = 60
    execute_file(filename, file_obj, command, timeout, dry_run=False)


@patch("subprocess.run")
def test_execute_files_mixed_commands(mock_run):
    mock_run.return_value = subprocess.CompletedProcess(args=["python", "file.py"], returncode=0)
    files = [("file1.py", io.StringIO("print('file1')")), ("file2.js", io.StringIO("console.log('file2')"))]
    commands = ["python", "node"]
    timeout = 60
    dry_run = False
    execute_files(files, commands, timeout, dry_run)


@patch("subprocess.run")
def test_execute_files(mock_run):
    mock_run.return_value = subprocess.CompletedProcess(args=["python", "file_to_test.py"], returncode=0)

    files = [("file1.py", io.StringIO("print('file1')")), ("file2.py", io.StringIO("print('file2')"))]
    commands = ["python", "python"]
    timeout = 60
    dry_run = False
    execute_files(files, commands, timeout, dry_run)


def test_execute_files_skip_file():
    files = [("script1.py", io.StringIO("")), ("script2.py", io.StringIO(""))]
    commands = ["python", "skip"]
    timeout = 60
    dry_run = False
    execute_files(files, commands, timeout, dry_run)


def test_validate_commands_empty():
    files = [("script1.py", ""), ("script2.py", "")]
    commands = []
    validated_commands = validate_commands(commands, files)
    assert validated_commands == ["skip", "skip"]


def test_validate_commands_match():
    files = [("script1.py", ""), ("script2.py", "")]
    commands = ["python", "node"]
    validated_commands = validate_commands(commands, files)
    assert validated_commands == commands


@patch("click.confirm")
@patch("subprocess.run")
def test_validate_commands_mismatch(mock_run, mock_confirm):
    mock_confirm.return_value = False
    files = [("script1.py", ""), ("script2.py", "")]
    commands = ["python"]
    with pytest.raises(ValueError):
        validate_commands(commands, files)


# Reporting tests
def test_generate_execution_report_no_results():
    results = []
    report = generate_execution_report(results)
    expected_report = "Execution Report:\n\nTotal Execution Time: 0.00 seconds"
    assert report == expected_report


def test_generate_execution_report_empty():
    results = []
    report = generate_execution_report(results)
    expected_report = "Execution Report:\n\nTotal Execution Time: 0.00 seconds"
    assert report == expected_report


def test_generate_execution_report():
    results = [
        ("python script1.py", 1.23),
        ("node script2.js", 0.45),
        ("Skipped script3.txt", 0.0),
    ]
    report = generate_execution_report(results)
    expected_report = "Execution Report:\n" "- Command: python script1.py\n" "  Execution Time: 1.23 seconds\n" "- Command: node script2.js\n" "  Execution Time: 0.45 seconds\n" "- Command: Skipped script3.txt\n" "  Execution Time: 0.00 seconds\n" "\n" "Total Execution Time: 1.68 seconds"
    assert report == expected_report


# Output tests
@patch("click.echo")
def test_print_gist_no_files(mock_echo):
    gist = {
        "id": "gist_id",
        "description": "description",
        "files": {},
    }
    print_gist(gist)


@patch("click.echo")
def test_print_gist_empty(mock_echo):
    gist = {"id": "gist_id", "description": "description", "files": {}}
    print_gist(gist)


@patch("click.echo")
def test_print_gist(mock_echo):
    gist = {
        "id": "gist_id",
        "description": "description",
        "files": {
            "file1": {"raw_url": "https://gist.githubusercontent.com/file1", "content": "content1"},
            "file2": {"raw_url": "https://gist.githubusercontent.com/file2", "content": "content2"},
        },
    }
    with patch("requests.get") as mock_get:
        mock_response_1 = Mock()
        mock_response_1.text = "content1"
        mock_response_2 = Mock()
        mock_response_2.text = "content2"
        mock_get.side_effect = [mock_response_1, mock_response_2]
        print_gist(gist)
        mock_echo.assert_any_call("File: file1")
        mock_echo.assert_any_call("content1")
        mock_echo.assert_any_call("File: file2")
        mock_echo.assert_any_call("content2")


# Hashing tests
def test_hash_gist_empty_files():
    gist_data = {"files": {}}
    gist_hash = hash_gist(gist_data)
    expected_hash = hashlib.sha256(b"").hexdigest()
    assert gist_hash == expected_hash


def test_hash_gist_empty():
    gist_data = {"files": {}}
    gist_hash = hash_gist(gist_data)
    expected_hash = hashlib.sha256(b"").hexdigest()
    assert gist_hash == expected_hash


def test_hash_gist():
    gist_data = {
        "files": {
            "file1.py": {"raw_url": "https://gist.githubusercontent.com/file1.py", "content": "print('Hello, World!')"},
            "file2.txt": {"raw_url": "https://gist.githubusercontent.com/file2.txt", "content": "This is a text file."},
        }
    }
    with patch("requests.get") as mock_get:
        mock_response_1 = Mock()
        mock_response_1.text = "print('Hello, World!')"
        mock_response_2 = Mock()
        mock_response_2.text = "This is a text file."
        mock_get.side_effect = [mock_response_1, mock_response_2]

        gist_hash = hash_gist(gist_data)
        combined_content = "print('Hello, World!')This is a text file."
        expected_hash = hashlib.sha256(combined_content.encode("utf-8")).hexdigest()
        assert gist_hash == expected_hash


# GitHub token tests
def test_get_github_token_from_env_not_set():
    if "GH_TOKEN" in os.environ:
        del os.environ["GH_TOKEN"]
    if "GITHUB_TOKEN" in os.environ:
        del os.environ["GITHUB_TOKEN"]
    token = get_github_token_from_env()
    assert token == ""


def test_get_github_token_from_env():
    os.environ["GH_TOKEN"] = "test_token"
    token = get_github_token_from_env()
    assert token == "test_token"
    del os.environ["GH_TOKEN"]


def test_get_github_token_from_env_multiple():
    os.environ["GH_TOKEN"] = "test_token1"
    os.environ["GITHUB_TOKEN"] = "test_token2"
    token = get_github_token_from_env()
    assert token == "test_token1"
    del os.environ["GH_TOKEN"]
    del os.environ["GITHUB_TOKEN"]


# Search command tests
@patch("gistrun.cli.search_gists")
def test_search_command_search_query(mock_search_gists, runner: CliRunner):
    mock_search_gists.return_value = [{"id": "gist_id", "description": "my-gist"}]
    result = runner.invoke(gistrun, ["search", "--search", "query"])
    mock_search_gists.assert_called_once_with("query", None)
    assert "Gist ID: gist_id, Description: my-gist" in result.output


@patch("gistrun.cli.list_user_gists")
def test_search_command_list_user(mock_list_user_gists, runner: CliRunner):
    mock_list_user_gists.return_value = [{"id": "gist_id", "description": "user-gist"}]
    result = runner.invoke(gistrun, ["search", "--list", "octocat"])
    mock_list_user_gists.assert_called_once_with("octocat", None)
    assert "Gist ID: gist_id, Description: user-gist" in result.output


@patch("gistrun.cli.search_gists")
def test_search_gists_function(mock_search_gists, runner: CliRunner):
    mock_search_gists.return_value = [{"id": "gist_id", "description": "my-gist"}]
    result = runner.invoke(gistrun, ["search", "--search", "query"])
    mock_search_gists.assert_called_once_with("query", None)
    assert "Gist ID: gist_id, Description: my-gist" in result.output


# Hash command tests
@patch("gistrun.cli.fetch_gist")
def test_hash_command(mock_fetch_gist, runner: CliRunner):
    mock_fetch_gist.return_value = {
        "id": "gist_id",
        "description": "my-gist",
        "files": {
            "file1.txt": {"raw_url": "https://gist.githubusercontent.com/file1.txt", "content": "File 1 content"},
            "file2.txt": {"raw_url": "https://gist.githubusercontent.com/file2.txt", "content": "File 2 content"},
        },
    }
    with patch("requests.get") as mock_get:
        mock_response_1 = Mock()
        mock_response_1.text = "File 1 content"
        mock_response_2 = Mock()
        mock_response_2.text = "File 2 content"
        mock_get.side_effect = [mock_response_1, mock_response_2]
        result = runner.invoke(gistrun, ["hash", "octocat/my-gist"])
        combined_content = "File 1 contentFile 2 content"
        expected_hash = hashlib.sha256(combined_content.encode("utf-8")).hexdigest()
        assert f"Hash of the combined gist contents (sha256): {expected_hash}" in result.output


@patch("gistrun.cli.fetch_gist")
def test_hash_command_invalid_gist(mock_fetch_gist, runner: CliRunner):
    mock_fetch_gist.side_effect = ValueError("Gist not found")
    result = runner.invoke(gistrun, ["hash", "octocat/invalid-gist"])
    assert "Error: Gist not found" in result.output


# Print command tests
@patch("gistrun.cli.fetch_gist")
@patch("gistrun.cli.print_gist")
def test_print_command(mock_print_gist, mock_fetch_gist, runner: CliRunner):
    mock_fetch_gist.return_value = {
        "id": "gist_id",
        "description": "my-gist",
        "files": {
            "file1.txt": {"raw_url": "https://gist.githubusercontent.com/file1.txt", "content": "File 1 content"},
            "file2.txt": {"raw_url": "https://gist.githubusercontent.com/file2.txt", "content": "File 2 content"},
        },
    }
    result = runner.invoke(gistrun, ["print", "octocat/my-gist"])
    mock_print_gist.assert_called_once_with(mock_fetch_gist.return_value)


@patch("gistrun.cli.fetch_gist")
def test_print_command_invalid_gist(mock_fetch_gist, runner: CliRunner):
    mock_fetch_gist.side_effect = ValueError("Gist not found")
    result = runner.invoke(gistrun, ["print", "octocat/invalid-gist"])
    assert "Error: Gist not found" in result.output


# Version command test
def test_version_command(runner: CliRunner):
    result = runner.invoke(gistrun, ["version"])
    assert f"gistrun {__version__}" in result.output


@patch("gistrun.cli.search_gists")
def test_search_gists_function(mock_search_gists, runner: CliRunner):
    mock_search_gists.return_value = [{"id": "gist_id", "description": "my-gist"}]
    result = runner.invoke(gistrun, ["search", "--search", "query"])
    mock_search_gists.assert_called_once_with("query", None)
    assert "Gist ID: gist_id, Description: my-gist" in result.output


# Test the hash function directly
@patch("gistrun.cli.fetch_gist")
def test_hash_function(mock_fetch_gist, runner: CliRunner):
    mock_fetch_gist.return_value = {
        "id": "gist_id",
        "description": "my-gist",
        "files": {
            "file1.txt": {"raw_url": "https://gist.githubusercontent.com/file1.txt", "content": "File 1 content"},
            "file2.txt": {"raw_url": "https://gist.githubusercontent.com/file2.txt", "content": "File 2 content"},
        },
    }
    with patch("requests.get") as mock_get:
        mock_response_1 = Mock()
        mock_response_1.text = "File 1 content"
        mock_response_2 = Mock()
        mock_response_2.text = "File 2 content"
        mock_get.side_effect = [mock_response_1, mock_response_2]
        result = runner.invoke(gistrun, ["hash", "octocat/my-gist"])
        combined_content = "File 1 contentFile 2 content"
        expected_hash = hashlib.sha256(combined_content.encode("utf-8")).hexdigest()
        assert f"Hash of the combined gist contents (sha256): {expected_hash}" in result.output


def test_hash_gist_all_hash_functions():
    gist_data = {
        "files": {
            "hello.py": {"raw_url": "https://gist.githubusercontent.com/hello.py"},
        }
    }
    file_content = "Hello, World!"
    file_obj = io.StringIO(file_content)
    hash_functions = ["md5", "sha1", "sha224", "sha256", "sha384", "sha512", "blake2b", "blake2s"]
    for hash_func in hash_functions:
        with patch("gistrun.cli.get_files") as mock_get_files:
            mock_get_files.return_value = [("hello.py", file_obj)]
            gist_hash = hash_gist(gist_data, hash_func)
            file_obj.seek(0)  # Reset the file object's position
            expected_hash = hashlib.new(hash_func, file_obj.read().encode("utf-8")).hexdigest()
            assert gist_hash == expected_hash


def test_fetch_gist_from_gist_data():
    gist_id = "648da9ea18b4853dc0c842b3b806d97e"
    gist = next((gist for gist in gist_data if gist["id"] == gist_id), None)
    assert gist is not None
    assert gist["description"] == "hello.py"
    assert gist["public"] is True


def test_get_files_from_gist_data():
    gist_id = "648da9ea18b4853dc0c842b3b806d97e"
    gist = next((gist for gist in gist_data if gist["id"] == gist_id), None)
    files = get_files(gist)
    assert len(files) == 1
    assert files[0][0] == "hello.py"
    assert files[0][1].getvalue() == 'print("Hello, World!")'


def test_hash_gist_from_gist_data():
    gist_id = "648da9ea18b4853dc0c842b3b806d97e"
    gist = next((gist for gist in gist_data if gist["id"] == gist_id), None)
    gist_hash = hash_gist(gist)
    expected_hash = hashlib.sha256('print("Hello, World!")'.encode("utf-8")).hexdigest()
    assert gist_hash == expected_hash


def test_search_gists_from_gist_data():
    query = "python"
    matching_gists = [gist for gist in gist_data if query.lower() in gist["description"].lower()]
    assert len(matching_gists) > 0


def test_list_user_gists_from_gist_data():
    username = "jonathanagustin"
    user_gists = [gist for gist in gist_data if gist["owner"]["login"] == username]
    assert len(user_gists) == len(gist_data)


def test_validate_username_gistname_pair_from_gist_data():
    gist = gist_data[0]
    username = gist["owner"]["login"]
    gist_name = gist["description"]
    assert validate_username_gistname_pair(f"{username}/{gist_name}") == (username, gist_name)


def test_print_gist_from_gist_data(capsys):
    gist = gist_data[0]
    print_gist(gist)
    captured = capsys.readouterr()
    assert "File: hello.py" in captured.out
    assert 'print("Hello, World!")' in captured.out


def test_validate_commands_valid():
    files = [("script1.py", ""), ("script2.py", "")]
    commands = ["python", "node"]
    validated_commands = validate_commands(commands, files)
    assert validated_commands == commands


def test_validate_commands_mismatch_confirm_yes(monkeypatch):
    monkeypatch.setattr("click.confirm", lambda _: True)
    files = [("script1.py", ""), ("script2.py", "")]
    commands = ["python"]
    validated_commands = validate_commands(commands, files)
    assert validated_commands == ["python", "skip"]


def test_validate_commands_mismatch_confirm_no(monkeypatch):
    monkeypatch.setattr("click.confirm", lambda _: False)
    files = [("script1.py", ""), ("script2.py", "")]
    commands = ["python"]
    with pytest.raises(ValueError):
        validate_commands(commands, files)


def test_compare_hash_match():
    file_content = "Hello, World!\n"
    gist_data = {"files": {"file.txt": {"raw_url": "https://gist.githubusercontent.com/file.txt", "content": file_content}}}
    expected_hash = hashlib.sha256(file_content.encode("utf-8")).hexdigest()
    with patch("gistrun.cli.get_files", return_value=[("file.txt", io.StringIO(file_content))]):
        compare_hash(gist_data, expected_hash, "sha256")


def test_compare_hash_mismatch():
    gist_data = {"files": {"file.txt": {"raw_url": "https://gist.githubusercontent.com/file.txt", "content": "Hello, World!"}}}
    expected_hash = hashlib.sha256("Different content".encode("utf-8")).hexdigest()
    with pytest.raises(ValueError):
        compare_hash(gist_data, expected_hash, "sha256")


@pytest.mark.parametrize("hash_func", ["md5", "sha1", "sha256"])
@patch("gistrun.cli.fetch_gist")
@patch("gistrun.cli.get_files")
@patch("gistrun.cli.compare_hash")
@patch("gistrun.cli.execute_files")
def test_exec_command_with_hash(mock_execute_files, mock_compare_hash, mock_get_files, mock_fetch_gist, hash_func, runner):
    mock_fetch_gist.return_value = {
        "id": "gist_id",
        "description": "my-gist",
        "files": {
            "file1.py": {"raw_url": "https://gist.githubusercontent.com/file1.py", "content": "print('Hello, World!')"},
        },
    }
    mock_get_files.return_value = [("file1.py", io.StringIO("print('Hello, World!')"))]
    expected_hash = hashlib.new(hash_func, "print('Hello, World!')".encode("utf-8")).hexdigest()
    result = runner.invoke(gistrun, ["exec", "octocat/my-gist", "--hash", expected_hash, "--hash-func", hash_func, "-y"])
    mock_compare_hash.assert_called_once_with(mock_fetch_gist.return_value, expected_hash, hash_func)
    mock_execute_files.assert_called_once()
    assert result.exit_code == 0


@patch("gistrun.cli.search_gists")
def test_search_command_no_results(mock_search_gists, runner):
    mock_search_gists.return_value = []
    result = runner.invoke(gistrun, ["search", "--search", "query"])
    assert "No gists found matching the search query." in result.output


@patch("gistrun.cli.fetch_gist")
@patch("gistrun.cli.print_gist")
def test_print_command_multiple_files(mock_print_gist, mock_fetch_gist, runner):
    mock_fetch_gist.return_value = {
        "id": "gist_id",
        "description": "my-gist",
        "files": {
            "file1.txt": {"raw_url": "https://gist.githubusercontent.com/file1.txt", "content": "File 1 content"},
            "file2.txt": {"raw_url": "https://gist.githubusercontent.com/file2.txt", "content": "File 2 content"},
        },
    }
    result = runner.invoke(gistrun, ["print", "octocat/my-gist"])
    mock_print_gist.assert_called_once_with(mock_fetch_gist.return_value)
    assert result.exit_code == 0
