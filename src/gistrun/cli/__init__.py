import click
import os
import requests
import yaml
from urllib.parse import urlparse
import hashlib
import subprocess
import tempfile
import time
import platform
from werkzeug.utils import secure_filename, uri_to_iri, iri_to_uri

from gistrun.__about__ import __version__

GISTRUN_CONFIG_ENV_VAR = "GISTRUN_CONFIG"
CONFIG_HOME_PATH = os.path.join(os.path.expanduser("~"), ".gistrun", ".gistrun-config.yaml")
DEFAULT_EXECUTE_COMMAND = "bash"

INSTALL_COMMANDS: Dict[str, str] = {
    "win32": "winget install --id GitHub.cli",
    "darwin": "brew install gh",
    "linux": "sudo apt install gh",
}


def is_gh_installed() -> bool:
    """Check if the 'gh' command-line tool is installed."""
    try:
        subprocess.run(
            ["gh", "--version"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return True
    except FileNotFoundError:
        return False


def install_gh() -> None:
    """Install the 'gh' command-line tool."""
    os_name = platform.system().lower()
    if os_name not in INSTALL_COMMANDS:
        click.echo(
            f"Unsupported operating system: {os_name}. Please install 'gh' manually."
        )
        click.echo("Installation instructions: https://cli.github.com/manual/installation")
        sys.exit(1)

    install_cmd = INSTALL_COMMANDS[os_name]
    click.echo(f"Installing 'gh' command-line tool using: {install_cmd}")
    try:
        subprocess.run(install_cmd, check=True, shell=True)
        click.echo("'gh' command-line tool installed successfully.")
    except subprocess.CalledProcessError:
        click.echo(
            f"Failed to install 'gh' command-line tool using: {install_cmd}"
        )
        click.echo(
            "Please install it manually by following the instructions at: https://cli.github.com/manual/installation"
        )
        sys.exit(1)


def find_config_file(start_dir=None):
    """
    Search for a .gistrun-config.yaml (or .yml) file recursively upwards.

    Args:
        start_dir (str, optional): The directory to start the search from.
                                      Defaults to the current working directory.

    Returns:
        str or None: The path to the config file if found, otherwise None.
    """
    if start_dir is None:
        start_dir = os.getcwd()

    current_dir = start_dir
    while True:
        for filename in [".gistrun-config.yaml", ".gistrun-config.yml"]:
            config_path = os.path.join(current_dir, filename)
            if os.path.exists(config_path):
                return config_path

        parent_dir = os.path.dirname(current_dir)
        if parent_dir == current_dir:  # Reached the root
            break
        current_dir = parent_dir

    return None  # Not found


def is_url(value):
    """
    Check if a value is a URL.

    Args:
        value (str): The value to check.

    Returns:
        bool: True if the value is a URL, False otherwise.
    """
    try:
        result = urlparse(value)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def validate_config(config):
    """
    Validates the structure of the gistrun configuration.

    Args:
        config (dict): The configuration dictionary.

    Returns:
        bool: True if valid, False otherwise.
    """
    if not isinstance(config, dict):
        click.echo("WARNING: Configuration is not a dictionary.")
        return False

    if "bindings" not in config:
        click.echo("WARNING: Configuration missing 'bindings' key.")
        return False

    if not isinstance(config["bindings"], list):
        click.echo("WARNING: 'bindings' key should be a list.")
        return False

    for binding in config["bindings"]:
        if not isinstance(binding, dict):
            click.echo("WARNING: Each binding should be a dictionary.")
            return False

        if not all(key in binding for key in ("name", "url")):
            click.echo(
                "WARNING: Each binding must have 'name' and 'url' keys."
            )
            return False

    return True


def get_config(config_file=None):
    """
    Load and validate the gistrun configuration.

    Loads in this order:
        1. Specified config file (if provided)
        2. Value from GISTRUN_CONFIG environment variable
        3. Recursively search upwards from current directory
        4. .gistrun/gistrun-config.yaml (or .yml) in user's home directory

    Args:
        config_file (str, optional): Path to the config file (overrides other methods).

    Returns:
        dict: The loaded configuration dictionary.
    """

    if config_file:
        try:
            return load_config(config_file)
        except FileNotFoundError:
            pass

    # Check environment variable
    config_file_from_env = os.getenv(GISTRUN_CONFIG_ENV_VAR)
    if config_file_from_env:
        try:
            return load_config(config_file_from_env)
        except FileNotFoundError:
            pass

    # Check other locations if not found in environment or argument
    config_file = find_config_file()
    if config_file:
        try:
            return load_config(config_file)
        except FileNotFoundError:
            pass

    # Fallback to home directory if no config file is found
    try:
        return load_config(os.path.join(CONFIG_HOME_PATH))
    except FileNotFoundError:
        pass

    return {"bindings": []}  # Return empty config if no file is found


def load_config(config_path):
    """
    Load the configuration from the specified path.

    Args:
        config_path (str): The path to the configuration file.

    Returns:
        dict: The loaded configuration dictionary.

    Raises:
        FileNotFoundError: If the configuration file is not found.
        yaml.YAMLError: If there's an error parsing the YAML file.
        ValueError: If the configuration file is invalid.
    """
    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"Invalid YAML in configuration file: {e}")

    if not validate_config(config):
        raise ValueError("Configuration file failed validation.")

    # Set default execute commands based on file extensions (if provided)
    extension_mapping = config.get("extensions", {})
    for binding in config["bindings"]:
        if "files" in binding:
            for file_config in binding["files"]:
                if "execute" not in file_config:
                    file_name = file_config.get("name")
                    _, ext = os.path.splitext(file_name)
                    file_config["execute"] = extension_mapping.get(ext)

    return config


def get_gist_url(username: str, gist_id: str) -> str:
    """
    Construct the URL to fetch the raw content of a gist.

    Args:
        username (str): The GitHub username.
        gist_id (str): The Gist ID.

    Returns:
        str: The URL to fetch the raw content of the gist.
    """
    return f"https://gist.githubusercontent.com/{username}/{gist_id}/raw"


def get_gist_content(gist_url: str, token: str = None) -> str:
    """
    Fetch the raw content of a gist.

    Args:
        gist_url (str): The URL to fetch the raw content.
        token (str, optional): The GitHub API token for authentication.

    Returns:
        str: The raw content of the gist.

    Raises:
        requests.exceptions.RequestException: If there's an error fetching the gist content.
        FileNotFoundError: If the gist is not found (HTTP 404).
    """
    headers = {}
    if token:
        headers["Authorization"] = f"token {token}"
    try:
        response = requests.get(gist_url, headers=headers, timeout=60)
        response.raise_for_status()  # This will raise an error for 404 (Not Found)
        return response.text
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            raise FileNotFoundError(f"Gist not found at: {gist_url}")
        else:
            raise requests.exceptions.RequestException(
                f"Error fetching gist content: {e}"
            )
    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(f"Error fetching gist content: {e}")


def execute_script(content: str, execute_command: str, timeout: int, dry_run: bool):
    """
    Execute the provided script content using the specified command.

    Args:
        content (str): The content of the script to execute.
        execute_command (str): The command to use to execute the script.
        timeout (int): The timeout for execution in seconds.
        dry_run (bool): If True, only print the command, don't execute.
    """
    if dry_run:
        click.echo(f"Dry run: {execute_command} (content omitted)")
        return

    with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
        temp_file.write(content)
        temp_filename = temp_file.name

    try:
        start_time = time.time()
        subprocess.run(
            f"{execute_command} {temp_filename}",
            check=True,
            shell=True,
            timeout=timeout,
        )
        end_time = time.time()
        click.echo(
            f"Script executed successfully in {end_time - start_time:.2f} seconds."
        )
    except subprocess.CalledProcessError as e:
        click.echo(f"Error executing script: {e}")
    except subprocess.TimeoutExpired:
        click.echo(f"Execution timed out after {timeout} seconds.")
    finally:
        os.remove(temp_filename)


@click.group()
def gistrun():
    """A command-line tool for fetching and executing code from GitHub Gists."""
    # Check if 'gh' is installed
    if not is_gh_installed():
        click.echo("The 'gh' command-line tool is not installed.")
        if click.confirm("Do you want to install it now?"):
            install_gh()
        else:
            click.echo(
                "Please install 'gh' manually. See instructions: https://cli.github.com/manual/installation"
            )
            sys.exit(1)


@gistrun.group()
def config():
    """Manage gistrun configuration bindings."""
    pass


@config.command()
@click.argument("value")
@click.option(
    "--config-file",
    "-c",
    help="Path to the local configuration file (optional)",
)
def set(value, config_file=None):
    """
    Set the default gist user or specify a URL to a remote configuration file.

    If no configuration file exists, a default one will be created in
    your home directory at: ~/.gistrun/.gistrun-config.yaml

    VALUE can be either:
      - <username>:           Sets the default GitHub gist user.
      - <config-url>:         Sets the URL to a remote .gistrun-config.yaml file.
    """
    if config_file is None:
        config_file = CONFIG_HOME_PATH  # Default config file path

    if "/" not in value and not is_url(value):  # Assume username
        config = {"gist_user": value, "bindings": []}

        with open(config_file, "w") as f:
            yaml.dump(config, f)
        click.echo(f"Default gist user set to: {value}")

    elif is_url(value):  # Assume URL to remote config
        try:
            response = requests.get(value)
            response.raise_for_status()
            config = yaml.safe_load(response.text)

            # Validate the structure of config
            if not validate_config(config):
                raise ValueError("Invalid configuration from URL.")

            with open(config_file, "w") as f:
                yaml.dump(config, f)
            click.echo(f"Configuration loaded from URL: {value}")

        except requests.exceptions.RequestException as e:
            click.echo(f"Error fetching remote configuration: {e}")
        except yaml.YAMLError as e:
            click.echo(f"Invalid YAML in remote configuration: {e}")
        except ValueError as e:
            click.echo(f"Error: {e}")
    else:
        click.echo(
            "Invalid input. Please provide a valid gist username or a URL."
        )

    # Validate after setting
    if validate_config(config):
        click.echo("Configuration is valid.")
    else:
        click.echo(
            "Configuration has validation errors. Please review the warnings."
        )


@config.command()
@click.argument("name")
@click.argument("url")
@click.option(
    "--execute",
    "-e",
    help="Specify the command to execute the binding (optional)",
)
@click.option("--config-file", "-c", help="Path to the configuration file (optional)")
def add(name, url, execute, config_file=None):
    """
    Add a binding to the configuration file.

    NAME:  The name or alias for the script or folder.
    URL:   The URL to the gist raw file or folder.
    """
    config = get_config(config_file)

    new_binding = {"name": name, "url": url}
    if execute:
        new_binding["execute"] = execute

    config["bindings"].append(new_binding)

    if config_file is None:
        config_file = find_config_file()
        if config_file is None:
            config_file = CONFIG_HOME_PATH

    with open(config_file, "w") as f:
        yaml.dump(config, f)
    click.echo(f"Binding '{name}' added to configuration: {config_file}")


@config.command()
@click.argument("name")
@click.option("--config-file", "-c", help="Path to the configuration file (optional)")
def remove(name, config_file=None):
    """
    Remove a binding from the configuration file.

    NAME: The name or alias of the script or folder to remove.
    """
    config = get_config(config_file)

    config["bindings"] = [b for b in config["bindings"] if b["name"] != name]

    if config_file is None:
        config_file = find_config_file()
        if config_file is None:
            config_file = CONFIG_HOME_PATH

    with open(config_file, "w") as f:
        yaml.dump(config, f)
    click.echo(f"Binding '{name}' removed from configuration: {config_file}")


@config.command()
@click.option("--config-file", "-c", help="Path to the configuration file (optional)")
def list(config_file=None):
    """List all bindings in the configuration file."""
    config = get_config(config_file)

    if config["bindings"]:
        click.echo("Bindings:")
        for binding in config["bindings"]:
            click.echo(
                f"  - {binding['name']}: {iri_to_uri(binding['url'])}"
            )  # Use iri_to_uri for display
            if "execute" in binding:
                click.echo(f"    Execute: {binding['execute']}")
    else:
        click.echo("No bindings found in the configuration.")


@config.command()
@click.argument("source", required=False)
@click.option(
    "--config-file",
    "-c",
    help="Path to the local configuration file (optional)",
)
def validate(source, config_file=None):
    """
    Validate a gistrun configuration file.

    SOURCE (optional):
      - <config-url>:       URL to a remote .gistrun-config.yaml file.
      - <config-file-path>: Path to a local .gistrun-config.yaml file.

    If SOURCE is not provided, the currently active configuration will be validated.
    """
    if source:
        # Validate remote or local file based on source
        if is_url(source):  # Assume URL
            try:
                response = requests.get(source)
                response.raise_for_status()
                config = yaml.safe_load(response.text)
            except requests.exceptions.RequestException as e:
                click.echo(f"Error fetching remote configuration: {e}")
                return
            except yaml.YAMLError as e:
                click.echo(f"Invalid YAML in remote configuration: {e}")
                return
        else:  # Assume file path
            try:
                with open(source, "r") as f:
                    config = yaml.safe_load(f)
            except FileNotFoundError:
                click.echo(f"Configuration file not found: {source}")
                return
            except yaml.YAMLError as e:
                click.echo(f"Invalid YAML in configuration file: {e}")
                return
    else:
        # Validate the currently set configuration
        config = get_config(config_file)

    if validate_config(config):
        click.echo("Configuration is valid.")
    else:
        click.echo(
            "Configuration has validation errors. Please review the warnings."
        )


@gistrun.command()
@click.argument("name")  # Can be "alias/script" or "script"
@click.option("--dry-run", is_flag=True, help="Perform a dry run.")
@click.option("--token", "-t", help="GitHub API token.")
@click.option("--timeout", type=int, default=60, help="Timeout in seconds.")
@click.option("--config-file", "-c", help="Path to the config file (optional)")
def exec(name, dry_run, token, timeout, config_file=None):
    """
    Execute a script from a Gist.

    NAME:  The name or alias of the script, or "alias/script" for scripts in folders.
    """
    config = get_config(config_file)

    gist_user = config.get("gist_user")
    if not gist_user:
        click.echo(
            "Error: Default gist user not set. "
            "Please run 'gistrun config set <username>' to configure."
        )
        return

    bindings = config.get("bindings", [])

    if "/" in name:  # "alias/script" format
        alias, script_name = name.split("/", 1)
        binding = next((b for b in bindings if b["name"] == alias), None)
        if binding:
            base_url = binding["url"]
            script_url = f"{base_url}{script_name}"

            # Check for file-specific execute command
            file_config = next(
                (
                    f
                    for f in binding.get("files", [])
                    if f["name"] == script_name or (
                        "*" in f["name"] and script_name.endswith(f["name"].replace("*", ""))
                    )
                ),
                None,
            )
            execute_command = file_config.get("execute") if file_config else None
        else:
            click.echo(f"Error: Alias not found: {alias}")
            return
    else:  # Just "script"
        binding = next((b for b in bindings if b["name"] == name), None)
        if binding is None:
            # You need to fetch the gist id for the default gist user
            gist_id =  # ... (implementation to fetch gist ID for the user) ...
            script_url = get_gist_url(gist_user, gist_id) + "/" + name
            execute_command = None
        else:
            script_url = binding["url"]
            execute_command = binding.get("execute")

    if execute_command is None:
        _, extension = os.path.splitext(script_url)
        execute_command = config.get("extensions", {}).get(
            extension, DEFAULT_EXECUTE_COMMAND
        )

        if execute_command is None:
            click.echo(
                f"Error: No execute command specified for '{name}' and file extension '{extension}' is not configured. "
                "Please add an 'execute' key to the binding in your config file or configure a default command for the extension."
            )
            return

    try:
        content = get_gist_content(script_url, token)
        execute_script(content, execute_command, timeout, dry_run)
    except FileNotFoundError as e:
        click.echo(f"Error: {e}")
    except requests.exceptions.RequestException as e:
        click.echo(f"Error: {e}")


@gistrun.command()
@click.argument("username_gist_id")
@click.option("--token", "-t", help="GitHub API token.")
@click.option(
    "--hash-func",
    "-f",
    default="sha256",
    help="The hash function to use (default: sha256)",
)
@click.option("--config-file", "-c", help="Path to the config file (optional)")
def hash_gist(username_gist_id, token, hash_func, config_file=None):
    """Generate a hash of a GitHub Gist."""
    try:
        username, gist_id = username_gist_id.split("/", 1)
        gist_url = get_gist_url(username, gist_id)
        content = get_gist_content(gist_url, token)

        hash_obj = hashlib.new(hash_func)
        hash_obj.update(content.encode())
        gist_hash = hash_obj.hexdigest()

        click.echo(f"Hash ({hash_func}) of Gist '{gist_url}': {gist_hash}")

    except ValueError as e:
        click.echo(f"Error: {e}")
    except requests.exceptions.RequestException as e:
        click.echo(f"Error fetching Gist content: {e}")


@gistrun.command()
@click.argument("username_gist_id")
@click.option("--token", "-t", help="GitHub API token.")
@click.option("--config-file", "-c", help="Path to the config file (optional)")
def print_gist(username_gist_id, token, config_file=None):
    """Print the contents of a GitHub Gist."""
    try:
        username, gist_id = username_gist_id.split("/", 1)
        gist_url = get_gist_url(username, gist_id)
        content = get_gist_content(gist_url, token)

        click.echo(content)

    except ValueError as e:
        click.echo(f"Error: {e}")
    except requests.exceptions.RequestException as e:
        click.echo(f"Error fetching Gist content: {e}")


@gistrun.command()
@click.argument("source")  # Can be a file path or a URL
@click.option(
    "--hash-func",
    "-f",
    default="sha256",
    help="The hash function to use (default: sha256)",
)
def hash(source, hash_func):
    """
    Generate a hash of a file or content from a URL.

    SOURCE can be either:
      - <file-path>:  Path to a local file.
      - <url>:         URL to fetch content from.
    """
    if is_url(source):
        try:
            source = uri_to_iri(source)  # Convert URI to IRI
            response = requests.get(source)
            response.raise_for_status()
            content = response.content
        except requests.exceptions.RequestException as e:
            click.echo(f"Error fetching content from URL: {e}")
            return
    else:
        try:
            with open(source, "rb") as f:
                content = f.read()
        except FileNotFoundError:
            click.echo(f"File not found: {source}")
            return

    hash_obj = hashlib.new(hash_func)
    hash_obj.update(content)
    file_hash = hash_obj.hexdigest()

    click.echo(f"Hash ({hash_func}) of '{source}': {file_hash}")


@gistrun.command()
def version():
    """Show the version of the gistrun tool."""
    click.echo(f"gistrun {__version__}")


if __name__ == "__main__":
    gistrun()
