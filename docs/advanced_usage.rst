
Advanced Usage
==============

GistRun provides several advanced features and options to enhance its functionality and flexibility.

.. toctree::
  :maxdepth: 2

  advanced_usage/execution_mapping
  advanced_usage/execution_timeout
  advanced_usage/dry_run
  advanced_usage/execution_report
  advanced_usage/error_handling

Execution Mapping and File Handling
-----------------------------------

GistRun includes a predefined mapping of file extensions to their respective execution commands. This mapping covers a wide range of programming languages and formats, allowing for easy execution of various file types.

When executing files, GistRun creates temporary files on the system to hold the contents of the gist files. These temporary files are used to execute the commands, and they are automatically removed after the execution is completed.

The execution mapping is implemented in the `execute_mapping` function, which returns a dictionary mapping file extensions to their respective execution commands. This mapping can be easily extended or modified to support additional file types or customized execution commands.

Here's an example of how the execution mapping works:

.. code-block:: python

  def execute_mapping() -> Dict[str, str]:
      mapping = {
          ".py": "python",
          ".js": "node",
          ".rb": "ruby",
          # ... more file extensions and commands
      }
      return mapping

In this example, files with the `.py` extension will be executed using the `python` command, `.js` files will be executed with `node`, and `.rb` files with `ruby`.

When executing a gist, GistRun iterates over the files in the gist, determines the appropriate execution command based on the file extension using the mapping, and executes the file accordingly.

Execution Timeout
-----------------

GistRun allows you to set a timeout for each file execution using the ``--timeout`` option. This timeout is specified in seconds and prevents long-running or infinite loops from causing the tool to hang indefinitely.

The timeout is implemented using the `subprocess` module in Python, which provides a `timeout` parameter for executing external commands. When executing a file, GistRun creates a temporary file with the gist file's content and runs the appropriate command with the specified timeout.

Here's an example of how the timeout is implemented:

.. code-block:: python

  def execute_file(filename: str, file_obj: io.StringIO, command: str, timeout: int, dry_run: bool) -> Tuple[str, float]:
      full_command = f"{command} {filename}"
      if dry_run:
          # Skip execution in dry run mode
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
              # Handle execution errors and timeouts
              execution_time = 0.0
      return full_command, execution_time

In this example, the `execute_file` function creates a temporary file with the gist file's content, executes the provided command with the specified timeout, and returns the full command and execution time. If the timeout is exceeded, a `subprocess.TimeoutExpired` exception is raised, and the execution is terminated.

Dry Run Mode
------------

The ``--dry-run`` option allows you to perform a dry run of the execution without actually running the commands. This can be useful for testing or debugging purposes, as it shows the commands that would be executed without making any changes to the system.

The dry run mode is implemented by skipping the actual execution of the commands and returning a default execution time of 0.0 seconds. When the `--dry-run` option is provided, GistRun prints a message indicating that the execution is being skipped.

Here's an example of how the dry run mode is implemented in the `execute_file` function:

.. code-block:: python

  def execute_file(filename: str, file_obj: io.StringIO, command: str, timeout: int, dry_run: bool) -> Tuple[str, float]:
      full_command = f"{command} {filename}"
      if dry_run:
          click.echo(f"Dry run - Skipping execution of {filename} with {full_command}")
          execution_time = 0.0
      else:
          # Actual execution logic
          ...
      return full_command, execution_time

In this example, if the `dry_run` flag is set to `True`, GistRun prints a message indicating that the execution is being skipped and returns an execution time of 0.0 seconds.

Execution Report
----------------

After executing the files in a gist, you can generate an execution report using the ``--report`` option. The report includes the following information:

- The full command executed for each file
- The execution time for each file
- The total execution time for all files

This report can be useful for tracking and analyzing the execution performance of the gist files.

The execution report is implemented in the `generate_execution_report` function, which takes a list of tuples containing the full command and execution time for each file, and generates a formatted report string.

Here's an example of the `generate_execution_report` function:

.. code-block:: python

  def generate_execution_report(results: List[Tuple[str, float]]) -> str:
      report = "Execution Report:\n"
      total_time = 0.0
      for command, execution_time in results:
          report += f"- Command: {command}\n"
          report += f"  Execution Time: {execution_time:.2f} seconds\n"
          total_time += execution_time
      report += f"\nTotal Execution Time: {total_time:.2f} seconds"
      return report

This function iterates over the list of results, formats each command and execution time, and calculates the total execution time. The resulting report string is then printed to the console or returned for further processing.

Error Handling
--------------

GistRun performs various validations to ensure the correctness of the input and prevent potential errors or misuse. It also handles various exceptions that may occur during the execution, such as network errors, invalid input, or execution failures. Clear error messages are provided to help identify and resolve issues.

Input Validation
~~~~~~~~~~~~~~~~

GistRun includes several input validation functions to ensure that the provided arguments and options are valid and adhere to the expected formats. For example, the `validate_username_gistname_pair` function checks if the provided `username/gistname` pair has the correct format, while the `validate_username` and `validate_gist_name` functions validate the username and gist name individually according to GitHub's naming conventions.

Here's an example of the `validate_username_gistname_pair` function:

.. code-block:: python

  def validate_username_gistname_pair(username_gistname_pair: str) -> Tuple[str, str]:
      if username_gistname_pair.count("/") != 1:
          raise ValueError(f"Invalid format for username_gistname_pair: {username_gistname_pair}. Expected format: 'username/gistname'")

      username, gist_name = username_gistname_pair.split("/", 1)
      if not username or not gist_name:
          raise ValueError("Neither username nor gist name can be empty.")

      return username, gist_name

This function checks if the provided `username_gistname_pair` string contains exactly one forward slash (`/`) separator, and it splits the string into the username and gist name. If the format is invalid or either the username or gist name is empty, a `ValueError` exception is raised with an appropriate error message.

Exception Handling
~~~~~~~~~~~~~~~~~~

GistRun handles various exceptions that may occur during the execution process, such as network errors when fetching gist data, execution failures, or timeouts. These exceptions are caught and handled gracefully, with clear error messages displayed to the user.

Here's an example of how exceptions are handled in the `exec` command:

.. code-block:: python

  @gistrun.command()
  @click.argument("username_gistname_pair")
  # ... options omitted for brevity
  def exec(username_gistname_pair, commands, dry_run, yes, token, timeout, report, hash, hash_func):
      try:
          username, gist_name = validate_username_gistname_pair(username_gistname_pair)
          validate_username(username)
          validate_gist_name(gist_name)

          if not token:
              token = get_github_token_from_env()

          gist_data = fetch_gist(username, gist_name, token)

          if hash:
              compare_hash(gist_data, hash, hash_func)

          # ... execution logic omitted for brevity
      except (requests.exceptions.RequestException, ValueError) as e:
          click.echo(f"Error: {e}")

In this example, the `exec` command wraps its execution logic in a `try` block, and any `requests.exceptions.RequestException` or `ValueError` exceptions raised during the execution are caught and handled by printing an error message to the console.
