"""
A command-line tool for fetching and executing code from GitHub Gists.
"""

import hashlib
import io
import os
import re
import subprocess
import tempfile
import time
from typing import Any, Dict, List, Tuple

import click
import requests

from gistrun.__about__ import __version__

GITHUB_API_BASE_URL: str = "https://api.github.com"
GIST_FETCH_LIMIT: int = 100
REQUEST_TIMEOUT: int = 60 * 5
GITHUB_TOKEN_ENV_VARS: List[str] = ["GH_TOKEN", "GITHUB_TOKEN"]


def get_files(gist_data: Dict[str, Any]) -> List[Tuple[str, io.StringIO]]:
    """
    Extracts files from the provided Gist data.

    :param gist_data: The data of the Gist.
    :type gist_data: Dict[str, Any]
    :return: A list of tuples with filename and in-memory file-like object.
    :rtype: List[Tuple[str, io.StringIO]]
    """
    files = []
    for filename, file_data in gist_data.get("files", {}).items():
        raw_url = file_data["raw_url"]
        content = requests.get(raw_url, timeout=REQUEST_TIMEOUT).text
        file_obj = io.StringIO(content)
        files.append((filename, file_obj))
    return files


def get_github_token_from_env() -> str:
    """
    Retrieves the GitHub API token from the environment variables.

    :return: The GitHub API token if found, otherwise an empty string.
    :rtype: str
    """
    for env_var in GITHUB_TOKEN_ENV_VARS:
        token = os.getenv(env_var)
        if token:
            return token
    return ""


def validate_username_gistname_pair(username_gistname_pair: str) -> Tuple[str, str]:
    """
    Validate the format of the username and gist name pair.

    :param username_gistname_pair: The combined username and gist name.
    :type username_gistname_pair: str
    :return: Tuple containing validated username and gist name.
    :rtype: Tuple[str, str]
    :raises ValueError: If the input format is incorrect or doesn't match the expected pattern.
    """
    if username_gistname_pair.count("/") != 1:
        raise ValueError(f"Invalid format for username_gistname_pair: {username_gistname_pair}. Expected format: 'username/gistname'")

    username, gist_name = username_gistname_pair.split("/", 1)
    if not username or not gist_name:
        raise ValueError("Neither username nor gist name can be empty.")

    return username, gist_name


def validate_username(username: str):
    """
    Validate the format of the GitHub username.

    :param username: The GitHub username.
    :type username: str
    :raises ValueError: If the username format is invalid or too long.
    """
    username_pattern = re.compile(r"^[a-zA-Z0-9]([a-zA-Z0-9-_]{0,38}[a-zA-Z0-9])?$")
    if not username_pattern.match(username):
        raise ValueError(f"Invalid GitHub username format: {username}")
    if len(username) > 39:
        raise ValueError(f"GitHub username too long (maximum 39 characters): {username}")


def validate_gist_name(gist_name: str):
    """
    Validate the format of the gist name.

    :param gist_name: The name of the gist.
    :type gist_name: str
    :raises ValueError: If the gist name format is invalid.
    """
    gist_name_pattern = re.compile(r"^[a-zA-Z0-9-_\.]+$")
    if not gist_name_pattern.match(gist_name):
        raise ValueError(f"Invalid gist name format: {gist_name}")


def search_gists(query: str, token: str = None) -> List[Dict[str, Any]]:
    """
    Search for gists based on the provided query.

    :param query: The search query.
    :type query: str
    :param token: The GitHub API token for authentication (optional).
    :type token: str
    :return: A list of gist data matching the search query.
    :rtype: List[Dict[str, Any]]
    :raises requests.exceptions.RequestException: If there's an error while making the API request.
    """
    endpoint_url: str = f"{GITHUB_API_BASE_URL}/gists/public"
    query_params: Dict[str, Any] = {"q": query, "per_page": GIST_FETCH_LIMIT}
    headers = {"Authorization": f"token {token}"} if token else None
    response: requests.Response = requests.get(endpoint_url, params=query_params, headers=headers, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    return response.json()


def list_user_gists(username: str, token: str = None) -> List[Dict[str, Any]]:
    """
    List all gists of a given user.

    :param username: The GitHub username.
    :type username: str
    :param token: The GitHub API token for authentication (optional).
    :type token: str
    :return: A list of gist data for the user.
    :rtype: List[Dict[str, Any]]
    :raises requests.exceptions.RequestException: If there's an error while making the API request.
    """
    endpoint_url: str = f"{GITHUB_API_BASE_URL}/users/{username}/gists"
    query_params: Dict[str, Any] = {"per_page": GIST_FETCH_LIMIT}
    headers = {"Authorization": f"token {token}"} if token else None
    response: requests.Response = requests.get(endpoint_url, params=query_params, headers=headers, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    return response.json()


def fetch_gists(username: str, page: int, token: str = None) -> List[Dict[str, Any]]:
    """
    Fetch gists for a given username and page number.

    :param username: The GitHub username.
    :type username: str
    :param page: The page number of gists to fetch.
    :type page: int
    :param token: The GitHub API token for authentication (optional).
    :type token: str
    :return: A list of gist data.
    :rtype: List[Dict[str, Any]]
    :raises requests.exceptions.RequestException: If there's an error while making the API request.
    """
    endpoint_url: str = f"{GITHUB_API_BASE_URL}/users/{username}/gists"
    query_params: Dict[str, Any] = {"per_page": GIST_FETCH_LIMIT, "page": page}
    headers = {"Authorization": f"token {token}"} if token else None
    response: requests.Response = requests.get(endpoint_url, params=query_params, headers=headers, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    return response.json()


def fetch_gist(username: str, gist_name: str, token: str = None) -> Dict[str, Any]:
    """
    Fetch a specific gist by name from a user's gists.

    :param username: The GitHub username.
    :type username: str
    :param gist_name: The description name of the gist to fetch.
    :type gist_name: str
    :param token: The GitHub API token for authentication (optional).
    :type token: str
    :return: The gist data if found.
    :rtype: Dict[str, Any]
    :raises ValueError: If the gist is not found.
    """
    page: int = 1
    while True:
        gists: List[Dict[str, Any]] = list_user_gists(username, token)
        if not gists:
            break

        for gist in gists:
            if gist["description"] == gist_name:
                return gist

        page += 1

    raise ValueError(f"Gist not found: {username}/{gist_name}")


def get_files(gist_data: Dict[str, Any]) -> List[Tuple[str, io.StringIO]]:
    """
    Extracts files from the provided Gist data.

    :param gist_data: The data of the Gist.
    :type gist_data: Dict[str, Any]
    :return: A list of tuples with filename and in-memory file-like object.
    :rtype: List[Tuple[str, io.StringIO]]
    """
    files = []
    for filename, file_data in gist_data.get("files", {}).items():
        raw_url = file_data["raw_url"]
        content = requests.get(raw_url, timeout=REQUEST_TIMEOUT).text
        file_obj = io.StringIO(content)
        files.append((filename, file_obj))
    return files


def execute_mapping() -> Dict[str, str]:
    """
    Returns a dictionary mapping file extensions to their respective execution commands.

    :return: A dictionary of file extension to execution command.
    :rtype: Dict[str, str]
    """

    mapping = {
        ".asm": "nasm",
        ".awk": "awk -f",
        ".bat": "cmd /c",
        ".c": "gcc",
        ".clj": "clojure",
        ".cpp": "g++",
        ".cs": "dotnet script",
        ".css": "skip",
        ".dart": "dart",
        ".erl": "escript",
        ".fsx": "dotnet fsi",
        ".go": "go run",
        ".groovy": "groovy",
        ".h": "skip",
        ".hpp": "skip",
        ".hs": "runhaskell",
        ".html": "skip",
        ".java": "javac",
        ".js": "node",
        ".json": "skip",
        ".jsx": "node",
        ".kt": "kotlin",
        ".less": "skip",
        ".lua": "lua",
        ".m": "octave",
        ".md": "skip",
        ".ml": "ocaml",
        ".nim": "nim compile --run",
        ".p": "prolog",
        ".pas": "fpc",
        ".php": "php",
        ".pl": "perl",
        ".ps1": "powershell -File",
        ".py": "python",
        ".pyc": "python",
        ".pyx": "cython",
        ".r": "Rscript",
        ".rb": "ruby",
        ".rs": "rustc",
        ".rst": "skip",
        ".sass": "skip",
        ".scala": "scala",
        ".scss": "skip",
        ".sh": "bash",
        ".sml": "sml",
        ".sql": "skip",
        ".swift": "swift",
        ".tcl": "tclsh",
        ".tex": "skip",
        ".ts": "ts-node",
        ".tsx": "ts-node",
        ".txt": "skip",
        ".vb": "vbnc",
        ".vbs": "cscript //Nologo",
        ".vue": "skip",
        ".xml": "skip",
        ".yaml": "skip",
        ".yml": "skip",
    }

    lowercase_mapping = {ext.lower(): cmd for ext, cmd in mapping.items()}

    class CaseInsensitiveDict(dict):
        def __missing__(self, key):
            return self.get(key.lower(), "")

    return CaseInsensitiveDict(lowercase_mapping)


def hash_gist(gist_data: Dict[str, Any], hash_func: str = "sha256", encoding: str = "utf-8") -> str:
    """
    Generate a hash of the combined contents of the gist files.

    :param gist_data: The data of the Gist.
    :type gist_data: Dict[str, Any]
    :param hash_func: The hash function to use (default: "sha256").
    :type hash_func: str
    :param encoding: The encoding to use for the file contents (default: "utf-8").
    :type encoding: str
    :return: The hash of the combined gist contents.
    :rtype: str
    """
    files = get_files(gist_data)
    combined_content = "".join(file_obj.getvalue() for _, file_obj in files)
    hash_obj = hashlib.new(hash_func)
    hash_obj.update(combined_content.encode(encoding))
    return hash_obj.hexdigest()


def compare_hash(gist_data: Dict[str, Any], expected_hash: str, hash_func: str) -> None:
    actual_hash = hash_gist(gist_data, hash_func)
    if actual_hash != expected_hash:
        raise ValueError(f"Hash mismatch. Expected: {expected_hash}, Actual: {actual_hash}")


def print_gist(gist_data: Dict[str, Any]) -> None:
    """
    Print the contents of the gist files.
    :param gist_data: The data of the Gist.
    :type gist_data: Dict[str, Any]
    """
    files = get_files(gist_data)
    for filename, file_obj in files:
        click.echo(f"File: {filename}")
        click.echo(file_obj.getvalue())
        click.echo()


def execute_file(filename: str, file_obj: io.StringIO, command: str, timeout: int, dry_run: bool) -> Tuple[str, float]:
    """
    Executes a file using the provided command.
    :param filename: Name of the file to execute.
    :type filename: str
    :param file_obj: In-memory file-like object containing the file content.
    :type file_obj: io.StringIO
    :param command: Command to execute the file.
    :type command: str
    :param timeout: Timeout for the execution in seconds.
    :type timeout: int
    :param dry_run: Whether to perform a dry run without executing the command.
    :type dry_run: bool
    :return: A tuple containing the full command string and the execution time in seconds.
    :rtype: Tuple[str, float]
    """
    full_command = f"{command} {filename}"
    if dry_run:
        click.echo(f"Dry run - Skipping execution of {filename} with {full_command}")
        execution_time = 0.0
    else:
        try:
            start_time = time.time()
            with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
                temp_file.write(file_obj.getvalue())
                temp_filename = temp_file.name
            subprocess.run(f"{command} {temp_filename}", check=True, shell=True, timeout=timeout)
            os.remove(temp_filename)
            execution_time = time.time() - start_time
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            click.echo(f"Error executing {filename}: {e}")
            execution_time = 0.0
    return full_command, execution_time


def execute_files(files: List[Tuple[str, io.StringIO]], commands: List[str], timeout: int, dry_run: bool) -> List[Tuple[str, float]]:
    """
    Execute files using the provided commands.

    :param files: List of tuples containing filename and in-memory file-like object.
    :type files: List[Tuple[str, io.StringIO]]
    :param commands: List of commands to execute the files.
    :type commands: List[str]
    :param timeout: Timeout for each file execution in seconds.
    :type timeout: int
    :param dry_run: Whether to perform a dry run without executing the commands.
    :type dry_run: bool
    :return: List of tuples containing full command strings and execution times.
    :rtype: List[Tuple[str, float]]
    """
    results = []
    for (filename, file_obj), command in zip(files, commands):
        if command.lower() == "skip":
            click.echo(f"Skipping {filename}...")
            results.append((f"Skipped {filename}", 0.0))
        else:
            full_command, execution_time = execute_file(filename, file_obj, command, timeout, dry_run)
            results.append((full_command, execution_time))
    return results


def validate_commands(commands: List[str], files: List[Tuple[str, str]]) -> List[str]:
    """
    Validate the commands against the number of files.

    :param commands: List of commands to execute the files.
    :type commands: List[str]
    :param files: List of tuples containing filename and code.
    :type files: List[Tuple[str, str]]
    :return: List of validated commands.
    :rtype: List[str]
    :raises ValueError: If the number of commands doesn't match the number of files.
    """
    num_files = len(files)
    num_commands = len(commands)

    if num_commands == 0:
        click.echo("No commands provided to execute files.")
        return ["skip"] * num_files
    elif num_commands != num_files:
        click.echo(f"Number of run commands ({num_commands}) does not match the number of files ({num_files}).")
        if not click.confirm("Do you want to proceed with the available commands?"):
            raise ValueError("Aborted due to command mismatch.")
        commands = commands[:num_files] + ["skip"] * (num_files - num_commands)
    return commands


def generate_execution_report(results: List[Tuple[str, float]]) -> str:
    """
    Generate a report of the execution results.

    :param results: List of tuples containing full command strings and execution times.
    :type results: List[Tuple[str, float]]
    :return: The generated execution report.
    :rtype: str
    """
    report = "Execution Report:\n"
    total_time = 0.0
    for command, execution_time in results:
        report += f"- Command: {command}\n"
        report += f"  Execution Time: {execution_time:.2f} seconds\n"
        total_time += execution_time
    report += f"\nTotal Execution Time: {total_time:.2f} seconds"
    return report


@click.group()
@click.version_option(__version__, "--version", help="Show the version and exit.")
def gistrun():
    """
    gistrun: A command-line tool for fetching and executing code from GitHub Gists.

    Usage:

        gistrun [OPTIONS] COMMAND [ARGS]...

    Options:

        --version   Show the version and exit.

        --help      Show this message and exit.

    Commands:

        exec        Fetch and execute code from a GitHub Gist.

        hash        Generate a hash of the combined contents of a GitHub Gist.

        print       Print the contents of a GitHub Gist.

        run         Fetch and execute code from a GitHub Gist.

        search      Search for gists or list gists of a specific user.

    Run 'gistrun COMMAND --help' for more information on a specific command.

    GitHub Authentication:

        The gistrun tool supports accessing private gists by providing a GitHub API token. You can either pass the token using the '--token' option or set it as an environment variable.

        The following environment variables are supported:

            - GH_TOKEN

            - GITHUB_TOKEN

        If the token is not provided, gistrun will attempt to retrieve it from the environment variables in the order listed above.

    Examples:

        $ gistrun exec octocat/my-gist

            Fetch and execute the code from the gist 'my-gist' owned by 'octocat'.

        $ gistrun exec octocat/my-gist -x "python" -x "skip" -x "node"

            Fetch and execute the code from 'my-gist', using the specified commands for each file in order.

        $ gistrun exec octocat/my-gist --dry-run

            Perform a dry run of executing the code from 'my-gist' without actually running the commands.

        $ gistrun exec octocat/my-gist -y

            Fetch and execute the code from 'my-gist' without prompting for confirmation.

        $ gistrun exec octocat/my-private-gist -t YOUR_GITHUB_API_TOKEN

            Fetch and execute the code from the private gist 'my-private-gist' using the provided GitHub API token.

        $ gistrun exec octocat/my-gist --timeout 120

            Fetch and execute the code from 'my-gist' with a timeout of 120 seconds for each file execution.

        $ gistrun exec octocat/my-gist --report

            Fetch and execute the code from 'my-gist' and generate an execution report.

        $ gistrun hash octocat/my-gist

            Generate a hash of the combined contents of the gist 'my-gist'.

        $ gistrun hash octocat/my-gist --token YOUR_GITHUB_API_TOKEN

            Generate a hash of the combined contents of 'my-gist' using the provided GitHub API token.

        $ gistrun print octocat/my-gist

            Print the contents of the gist 'my-gist'.

        $ gistrun print octocat/my-private-gist --token YOUR_GITHUB_API_TOKEN

            Print the contents of the private gist 'my-private-gist' using the provided GitHub API token.

        $ gistrun search --search "python script"

            Search for gists containing the query "python script".

        $ gistrun search --list octocat

            List all gists owned by the user 'octocat'.

        $ gistrun search --list octocat --token YOUR_GITHUB_API_TOKEN

            List all gists owned by 'octocat' using the provided GitHub API token.
    """
    pass


@gistrun.command()
@click.argument("username_gistname_pair")
@click.option("--run", "-x", "commands", multiple=True, help="Commands to execute the files in order. Can be specified multiple times. Use 'skip' to skip a file.")
@click.option("--dry-run", is_flag=True, help="Perform a dry run without executing the commands.")
@click.option("--yes", "-y", is_flag=True, help="Confirm execution of commands.")
@click.option("--token", "-t", help="GitHub API token for accessing private gists.")
@click.option("--timeout", type=int, default=60, help="Timeout for each file execution in seconds (default: 60).")
@click.option("--report", is_flag=True, help="Generate an execution report.")
@click.option("--hash", "-H", help="Expected hash of the combined gist contents.")
@click.option("--hash-func", "-f", default="sha256", help="The hash function to use for comparing the hash (default: 'sha256').")
def exec(username_gistname_pair, commands, dry_run, yes, token, timeout, report, hash, hash_func):
    """
    Fetch and execute code from a GitHub Gist.

    Arguments:

      USERNAME/GIST_NAME  The GitHub username and gist name in the format 'username/gistname'.

    Options:

      -x, --run TEXT         Commands to execute the files in order. Can be specified multiple times. Use 'skip' to skip a file.

      --dry-run              Perform a dry run without executing the commands.

      -y, --yes              Confirm execution of commands.

      -t, --token TEXT       GitHub API token for accessing private gists.

      --timeout INTEGER      Timeout for each file execution in seconds (default: 60).

      --report               Generate an execution report.

      -H, --hash TEXT        Expected hash of the combined gist contents.

      -f, --hash-func TEXT   The hash function to use for comparing the hash (default: 'sha256').

      -h, --help             Show this message and exit.

    Examples:

      $ gistrun exec octocat/my-gist

        Fetch and execute the code from the gist 'my-gist' owned by 'octocat'.

      $ gistrun exec octocat/my-gist -x "python" -x "skip" -x "node"

        Fetch and execute the code from 'my-gist', using the specified commands for each file in order.

      $ gistrun exec octocat/my-gist --dry-run

        Perform a dry run of executing the code from 'my-gist' without actually running the commands.

      $ gistrun exec octocat/my-gist -y

        Fetch and execute the code from 'my-gist' without prompting for confirmation.

      $ gistrun exec octocat/my-private-gist -t YOUR_GITHUB_API_TOKEN

        Fetch and execute the code from the private gist 'my-private-gist' using the provided GitHub API token.

      $ gistrun exec octocat/my-gist --timeout 120

        Fetch and execute the code from 'my-gist' with a timeout of 120 seconds for each file execution.

      $ gistrun exec octocat/my-gist --report

        Fetch and execute the code from 'my-gist' and generate an execution report.

      $ gistrun exec octocat/my-gist -H EXPECTED_HASH

        Fetch and execute the code from 'my-gist' and compare the combined gist contents with the expected hash.
    """
    try:
        username, gist_name = validate_username_gistname_pair(username_gistname_pair)
        validate_username(username)
        validate_gist_name(gist_name)

        if not token:
            token = get_github_token_from_env()

        gist_data = fetch_gist(username, gist_name, token)

        if hash:
            compare_hash(gist_data, hash, hash_func)

        files = get_files(gist_data)

        if not commands:
            commands = [execute_mapping().get(os.path.splitext(filename)[1], "skip") for filename, _ in files]
        commands = validate_commands(commands, files)

        if files:
            if not dry_run and not yes:
                click.echo()
                click.echo("The following commands will be executed:")
                for filename, _ in files:
                    command = commands[files.index((filename, _))]
                    click.echo()
                    click.echo(f"  {command} {filename}")
                click.echo()

                if not click.confirm("Are you sure you want to proceed?", abort=True):
                    click.echo("Aborted")
                    return

            if dry_run:
                click.echo("Dry run - Skipping execution.")
            else:
                results = execute_files(files, commands, timeout, dry_run)
                if report:
                    report_content = generate_execution_report(results)
                    click.echo(report_content)
        else:
            click.echo(f"Gist '{gist_name}' doesn't contain any executable files.")
    except (requests.exceptions.RequestException, ValueError) as e:
        click.echo(f"Error: {e}")


@click.command()
@click.argument("username_gistname_pair")
@click.option("--token", "-t", help="GitHub API token for accessing private gists.")
@click.option("--hash-func", "-f", default="sha256", help="The hash function to use for generating the hash (default: 'sha256').")
def hash(username_gistname_pair, token, hash_func):
    """
    Generate a hash of the combined contents of a GitHub Gist.

    Arguments:

      USERNAME/GIST_NAME  The GitHub username and gist name in the format 'username/gistname'.

    Options:

      -t, --token TEXT      GitHub API token for accessing private gists.

      -f, --hash-func TEXT  The hash function to use for generating the hash (default: 'sha256').

      -h, --help            Show this message and exit.

    Examples:

      $ gistrun hash octocat/my-gist

        Generate a hash of the combined contents of the gist 'my-gist'.

      $ gistrun hash octocat/my-gist --token YOUR_GITHUB_API_TOKEN

        Generate a hash of the combined contents of 'my-gist' using the provided GitHub API token.

      $ gistrun hash octocat/my-gist --hash-func md5

        Generate an MD5 hash of the combined contents of 'my-gist'.
    """
    try:
        username, gist_name = validate_username_gistname_pair(username_gistname_pair)
        validate_username(username)
        validate_gist_name(gist_name)

        if not token:
            token = get_github_token_from_env()

        gist_data = fetch_gist(username, gist_name, token)
        gist_hash = hash_gist(gist_data, hash_func)
        click.echo(f"Hash of the combined gist contents ({hash_func}): {gist_hash}")

    except (requests.exceptions.RequestException, ValueError) as e:
        click.echo(f"Error: {e}")


@click.command()
@click.argument("username_gistname_pair")
@click.option("--token", "-t", help="GitHub API token for accessing private gists.")
def print(username_gistname_pair, token):
    """
    Print the contents of a GitHub Gist with syntax highlighting.

    Arguments:

      USERNAME/GIST_NAME  The GitHub username and gist name in the format 'username/gistname'.

    Options:

      -t, --token TEXT    GitHub API token for accessing private gists.

      -h, --help          Show this message and exit.

    Examples:

      $ gistrun print octocat/my-gist

        Print the contents of the gist 'my-gist' with syntax highlighting.

      $ gistrun print octocat/my-private-gist --token YOUR_GITHUB_API_TOKEN Print the contents of the private gist 'my-private-gist' using the  provided GitHub API token.

    """
    try:
        username, gist_name = validate_username_gistname_pair(username_gistname_pair)
        validate_username(username)
        validate_gist_name(gist_name)

        if not token:
            token = get_github_token_from_env()

        gist_data = fetch_gist(username, gist_name, token)
        print_gist(gist_data)

    except (requests.exceptions.RequestException, ValueError) as e:
        click.echo(f"Error: {e}")


@click.command()
@click.option("--search", "-s", help="Search for gists based on the provided query.")
@click.option("--list", "-l", "list_username", help="List all gists of the specified user.")
@click.option("--token", "-t", help="GitHub API token for accessing private gists.")
def search(search, list_username, token):
    """
    Search for gists or list gists of a specific user.

    Options:

      -s, --search TEXT   Search for gists based on the provided query.

      -l, --list TEXT     List all gists of the specified user.

      -t, --token TEXT    GitHub API token for accessing private gists.

      -h, --help          Show this message and exit.

    Examples:

      $ gistrun search --search "python script"

        Search for gists containing the query "python script".

      $ gistrun search --list octocat

        List all gists owned by the user 'octocat'.

      $ gistrun search --list octocat --token YOUR_GITHUB_API_TOKEN

        List all gists owned by 'octocat' using the provided GitHub API token.
    """
    try:
        if not token:
            token = get_github_token_from_env()
        if not token:
            token = None
        if search:
            gists = search_gists(search, token)
            if gists:
                for gist in gists:
                    click.echo(f"Gist ID: {gist['id']}, Description: {gist['description']}")
            else:
                click.echo("No gists found matching the search query.")
        elif list_username:
            validate_username(list_username)
            gists = list_user_gists(list_username, token)
            if gists:
                for gist in gists:
                    click.echo(f"Gist ID: {gist['id']}, Description: {gist['description']}")
            else:
                click.echo(f"No gists found for user: {list_username}")
        else:
            click.echo("Please provide a search query or username.")
    except (requests.exceptions.RequestException, ValueError) as e:
        click.echo(f"Error: {e}")


@gistrun.command()
def version():
    """
    Show the version of the gistrun tool.
    """
    click.echo(f"gistrun {__version__}")


gistrun.add_command(exec)
gistrun.add_command(hash)
gistrun.add_command(print)
gistrun.add_command(search)
gistrun.add_command(version)

if __name__ == "__main__":
    gistrun()
