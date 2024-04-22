.. _gistrun:

.. warning::
  GistRun executes code from GitHub Gists. While convenient, this poses a security risk as the executed code may be malicious. Use GistRun only with Gists from trusted sources, and review the code before executing it. The authors of GistRun are not responsible for any damage caused by executing untrusted code.

GistRun
=======

GistRun is a command-line tool that allows you to fetch and execute code from GitHub Gists. It provides a convenient way to run code snippets or scripts directly from Gists, without the need to clone or download the entire repository.

.. toctree::
  :maxdepth: 2
  :caption: Contents:

  installation
  usage
  commands
  advanced_usage
  authentication
  integration
  contributing
  license

Indices and Tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Installation
============

GistRun can be installed using pip, the Python package installer. To install the latest stable version, run:

.. code-block:: console

  $ pip install gistrun

Alternatively, you can install GistRun from source by cloning the repository and running the following command:

.. code-block:: console

  $ python setup.py install

Dependencies
------------

GistRun has the following dependencies:

- Python (>=3.6)
- Click (>=7.0)
- Requests (>=2.22.0)

These dependencies will be automatically installed when you install GistRun using pip.

Upgrading
---------

To upgrade GistRun to the latest version, use the following command:

.. code-block:: console

  $ pip install --upgrade gistrun

Verifying the Installation
--------------------------

You can verify that GistRun is installed correctly by running:

.. code-block:: console

  $ gistrun --version

This should print the currently installed version of GistRun.

Usage
=====

The main command to execute code from a GitHub Gist is ``gistrun exec``:

.. code-block:: console

  $ gistrun exec octocat/my-gist

This command will fetch the gist named ``my-gist`` owned by the user ``octocat`` and execute the files it contains using the appropriate commands based on the file extensions.

For more information on available commands and options, see the :doc:`commands` section.

Quick Start
-----------

1. Find a GitHub Gist you want to execute, e.g., ``octocat/my-gist``.
2. Run the following command to execute the gist:

  .. code-block:: console

     $ gistrun exec octocat/my-gist

3. If the gist contains multiple files, you will be prompted to confirm the execution or provide custom commands.
4. The output of the executed files will be displayed in the terminal.

Examples
--------

Here are some examples of how to use the GistRun tool:

.. code-block:: console

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

Commands
========

GistRun provides several commands to interact with GitHub Gists. Each command has its own set of options and arguments.

.. click:: gistrun.gistrun
   :prog: gistrun
   :nested: full

The main commands are:

- ``exec``: Fetch and execute code from a GitHub Gist.
- ``hash``: Generate a hash of the combined contents of a GitHub Gist.
- ``print``: Print the contents of a GitHub Gist.
- ``search``: Search for gists or list gists of a specific user.
- ``version``: Show the version of the GistRun tool.

For detailed information on each command and its options, refer to the respective sections below.

exec
----

The ``exec`` command is used to fetch and execute code from a GitHub Gist. It supports various options to customize the execution behavior.

.. click:: gistrun.gistrun
   :prog: gistrun exec
   :nested: full

hash
----

The ``hash`` command generates a hash of the combined contents of a GitHub Gist. You can specify the hash function to use.

.. click:: gistrun.gistrun
   :prog: gistrun hash
   :nested: full

print
-----

The ``print`` command prints the contents of a GitHub Gist with syntax highlighting.

.. click:: gistrun.gistrun
   :prog: gistrun print
   :nested: full

search
------

The ``search`` command allows you to search for gists or list gists owned by a specific user.

.. click:: gistrun.gistrun
   :prog: gistrun search
   :nested: full

version
-------

The ``version`` command shows the currently installed version of GistRun.

.. click:: gistrun.gistrun
   :prog: gistrun version
   :nested: full

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
  advanced_usage/private_gists

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

Accessing Private Gists
-----------------------

GistRun supports accessing private gists by providing a GitHub API token. You can either pass the token using the ``--token`` option or set it as an environment variable (``GH_TOKEN`` or ``GITHUB_TOKEN``).

When accessing private gists, GistRun automatically includes the provided token in the API requests to GitHub, ensuring that you have the necessary permissions to fetch and execute the gist contents.

Using the `--token` Option
~~~~~~~~~~~~~~~~~~~~~~~~~~

To provide a GitHub API token when executing a command, use the ``--token`` (or ``-t``) option:

.. code-block:: console

  $ gistrun exec octocat/my-private-gist -t YOUR_GITHUB_API_TOKEN

Replace ``YOUR_GITHUB_API_TOKEN`` with your actual GitHub API token.

Using Environment Variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Alternatively, you can set the GitHub API token as an environment variable. GistRun supports the following environment variables:

- ``GH_TOKEN``
- ``GITHUB_TOKEN``

If the token is not provided using the ``--token`` option, GistRun will attempt to retrieve it from these environment variables in the order listed above.

For example, on Unix-based systems, you can set the ``GH_TOKEN`` environment variable like this:

.. code-block:: console

  $ export GH_TOKEN=YOUR_GITHUB_API_TOKEN
  $ gistrun exec octocat/my-private-gist

On Windows, use the ``set`` command:

.. code-block:: console

  > set GH_TOKEN=YOUR_GITHUB_API_TOKEN
  > gistrun exec octocat/my-private-gist

If you don't have a GitHub API token, follow these steps to create one:

1. Go to your GitHub account settings by clicking on your profile picture in the top-right corner of GitHub and selecting "Settings".
2. In the left sidebar, click on "Developer settings".
3. In the left sidebar, click on "Personal access tokens".
4. Click on "Generate new token".
5. Give your token a descriptive name and select the appropriate scopes (e.g., `gist` for accessing gists).
6. Click "Generate token" and copy the generated token.

You can now use this token with GistRun to access your private gists.

Note that GitHub API tokens grant read/write access to your account's data, so treat them like passwords and keep them secure.

Integration
===========

GistRun can be easily integrated with other tools and scripts, allowing you to automate various tasks involving code snippets or scripts hosted on GitHub Gists.

Continuous Integration and Deployment
-------------------------------------

You can use GistRun in your continuous integration and deployment pipelines to fetch and execute test scripts or deployment scripts directly from Gists. This can be particularly useful for sharing and reusing scripts across different projects or teams.

For example, in your CI/CD pipeline, you can run the following command to execute a test script hosted on a GitHub Gist:

.. code-block:: console

  $ gistrun exec octocat/my-test-script

You can also integrate GistRun with popular CI/CD tools like Jenkins, Travis CI, CircleCI, and more.

Scripting and Automation
------------------------

GistRun can be used in combination with other command-line utilities or scripts, enabling you to build more complex workflows and automations around code snippets hosted on GitHub Gists.

For example, you can create a shell script that fetches and executes multiple Gists in a specific order, or you can incorporate GistRun into your existing scripts to dynamically execute code snippets based on certain conditions.

Here's an example shell script that executes multiple Gists:

.. code-block:: bash

  #!/bin/bash

  # Execute a setup script
  gistrun exec octocat/setup-script

  # Execute the main script
  gistrun exec octocat/main-script

  # Execute a cleanup script
  gistrun exec octocat/cleanup-script

By combining GistRun with other scripting languages and tools, you can create powerful and flexible automation solutions tailored to your specific needs.

Contributing
============

Contributions to GistRun are welcome and appreciated! Whether you want to report a bug, suggest a new feature, or submit a pull request, we encourage you to participate in the development process.

Reporting Issues
----------------

If you encounter any issues or bugs while using GistRun, please open a new issue on the `GistRun GitHub repository <https://github.com/your-username/gistrun/issues>`_. When reporting an issue, please provide as much detail as possible, including:

- A clear and descriptive title for the issue
- A detailed description of the problem or bug
- Steps to reproduce the issue
- Any error messages or logs related to the issue
- Your operating system and Python version
- Any relevant code samples or Gists

Suggesting Features
-------------------

If you have an idea for a new feature or enhancement, feel free to open a new issue on the `GistRun GitHub repository <https://github.com/your-username/gistrun/issues>`_ and describe your proposal in detail. We welcome any suggestions that could improve the functionality, usability, or performance of GistRun.

Submitting Pull Requests
------------------------

If you want to contribute code changes or bug fixes to GistRun, you can submit a pull request on the `GistRun GitHub repository <https://github.com/your-username/gistrun>`_. Before submitting a pull request, please make sure to:

1. Fork the GistRun repository and create a new branch for your changes.
2. Follow the coding style and conventions used in the project.
3. Add or update tests for your changes, if applicable.
4. Update the documentation if your changes introduce new features or modify existing behavior.
5. Ensure that all tests pass and your changes don't introduce new bugs or regressions.
6. Provide a clear and descriptive commit message explaining your changes.

Once you've made your changes, submit a pull request against the main branch of the GistRun repository. Your pull request will be reviewed by the maintainers, and feedback or changes may be requested before it can be merged.

Development Environment
-----------------------

To set up a development environment for GistRun, follow these steps:

1. Clone the GistRun repository: ``git clone https://github.com/your-username/gistrun.git``
2. Create a virtual environment: ``python -m venv env``
3. Activate the virtual environment:
  - On Windows: ``env\Scripts\activate``
  - On Unix or macOS: ``source env/bin/activate``
4. Install the development dependencies: ``pip install -r requirements-dev.txt``
5. Install the GistRun package in editable mode: ``pip install -e .``

Now you can make changes to the GistRun codebase, run tests, and build the documentation.

Tests
-----

GistRun includes a suite of tests to ensure the correctness of the codebase. To run the tests, use the following command:

.. code-block:: console

  $ pytest

This command will run all the tests in the ``tests/`` directory.

Building the Documentation
--------------------------

The GistRun documentation is built using Sphinx. To build the documentation locally, follow these steps:

1. Install the documentation dependencies: ``pip install -r docs/requirements.txt``
2. Change to the ``docs/`` directory: ``cd docs/``
3. Build the documentation: ``make html``

The built documentation will be available in the ``docs/_build/html/`` directory.

Code Style
----------

GistRun follows the `PEP 8 <https://www.python.org/dev/peps/pep-0008/>`_ style guide for Python code. We recommend using a tool like `black <https://black.readthedocs.io/en/stable/>`_ or `autopep8 <https://pypi.org/project/autopep8/>`_ to automatically format your code according to PEP 8 before submitting a pull request.

License
-------

By contributing to GistRun, you agree that your contributions will be licensed under the `GPL-3.0-or-Later License <https://spdx.org/licenses/GPL-3.0-or-later.html>`_.

License
=======

GistRun is released under the GNU General Public License v3.0 or later (GPL-3.0-or-later). The full text of the license is available in the `LICENSE <https://github.com/drengskapur/gistrun/blob/main/LICENSE>`_ file.

Summary
-------

The GPL-3.0-or-later license grants you the following rights:

- Freedom to run the program for any purpose.
- Freedom to study how the program works and modify it.
- Freedom to redistribute copies of the program.
- Freedom to improve the program and release your improvements to the public.

You can exercise these rights provided that you comply with the terms and conditions of the license.

Terms and Conditions
--------------------

The key terms and conditions of the GPL-3.0-or-later license include:

- **Source Code Distribution**: If you distribute copies of the software, you must make the source code available under the same license.
- **Modifications and Derived Works**: If you modify the software or create a derived work, you must distribute the modifications or derived work under the same license as the original software.
- **License and Copyright Notice**: You must include the license text and copyright notice in all copies or substantial portions of the software.
- **Disclose Source**: If you convey the software by offering access to copy from a designated place, you must also provide access to the corresponding source code.
- **Non-Discrimination**: You cannot discriminate against any person or group in the distribution or use of the software.

For more details and the complete terms and conditions, please refer to the `GPL-3.0-or-later License <https://spdx.org/licenses/GPL-3.0-or-later.html>`_.
