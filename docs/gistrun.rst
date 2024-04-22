.. _gistrun:

gistrun
=======

gistrun is a command-line tool that allows you to fetch and execute code from GitHub Gists. It provides a convenient way to run code snippets or scripts directly from Gists, without the need to clone or download the entire repository.

Installation
------------

You can install the latest version of gistrun using pip:

.. code-block:: console

   $ pip install gistrun

If you prefer, you can also install gistrun from source by cloning the repository and running the following command:

.. code-block:: console

   $ python setup.py install

Usage
-----

The gistrun tool provides several commands to interact with GitHub Gists. The general usage is as follows:

.. code-block:: console

   $ gistrun [OPTIONS] COMMAND [ARGS]...

Options
~~~~~~~

.. option:: --version

   Show the version of the gistrun tool and exit.

.. option:: --help

   Show the help message and exit.

Commands
~~~~~~~~

.. click:: gistrun.gistrun
    :prog: gistrun
    :nested: full

GitHub Authentication
---------------------

gistrun supports accessing private gists by providing a GitHub API token. You can either pass the token using the ``--token`` option or set it as an environment variable.

The following environment variables are supported:

- ``GH_TOKEN``
- ``GITHUB_TOKEN``

If the token is not provided, gistrun will attempt to retrieve it from the environment variables in the order listed above.

Examples
--------

Here are some examples of how to use the gistrun tool:

.. code-block:: console

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

Executing a Gist
~~~~~~~~~~~~~~~~

To fetch and execute the code from a GitHub Gist, use the ``exec`` command:

.. code-block:: console

   $ gistrun exec octocat/my-gist

This command will fetch the gist named ``my-gist`` owned by the user ``octocat`` and execute the files it contains using the appropriate commands based on the file extensions.

You can specify custom commands for executing the files using the ``--run`` (or ``-x``) option:

.. code-block:: console

   $ gistrun exec octocat/my-gist -x "python" -x "skip" -x "node"

In this example, the first file will be executed with the ``python`` command, the second file will be skipped, and the third file will be executed with the ``node`` command.

Other useful options for the ``exec`` command include:

- ``--dry-run``: Perform a dry run without executing the commands.
- ``--yes`` (or ``-y``): Confirm execution of commands without prompting.
- ``--token`` (or ``-t``): Provide a GitHub API token for accessing private gists.
- ``--timeout``: Set a timeout for each file execution in seconds.
- ``--report``: Generate an execution report after running the commands.
- ``--hash`` (or ``-H``): Specify an expected hash of the combined gist contents for verification.
- ``--hash-func`` (or ``-f``): Specify the hash function to use for generating or comparing the hash.

Generating a Hash
~~~~~~~~~~~~~~~~~

You can generate a hash of the combined contents of a GitHub Gist using the ``hash`` command:

.. code-block:: console

   $ gistrun hash octocat/my-gist

By default, the SHA-256 hash function is used, but you can specify a different hash function using the ``--hash-func`` (or ``-f``) option:

.. code-block:: console

   $ gistrun hash octocat/my-gist --hash-func md5

Printing Gist Contents
~~~~~~~~~~~~~~~~~~~~~~

To print the contents of a GitHub Gist with syntax highlighting, use the ``print`` command:

.. code-block:: console

   $ gistrun print octocat/my-gist

Searching and Listing Gists
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``search`` command allows you to search for gists or list gists owned by a specific user.

To search for gists based on a query:

.. code-block:: console

   $ gistrun search --search "python script"

To list all gists owned by a user:

.. code-block:: console

   $ gistrun search --list octocat

You can provide a GitHub API token using the ``--token`` (or ``-t``) option if you need to access private gists.

Advanced Usage
--------------

Validation and Error Handling
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

gistrun performs various validations to ensure the correctness of the input and prevent potential errors or misuse. Here are some examples of the validations performed:

- **Username and Gist Name Validation**: The tool validates the format of the provided username and gist name pair, ensuring that it follows the expected pattern of ``username/gistname``. It also checks that neither the username nor the gist name is empty.

- **Username Format Validation**: The username is validated against a regular expression pattern to ensure it follows GitHub's username format rules.

- **Gist Name Format Validation**: The gist name is also validated against a regular expression pattern to ensure it follows the allowed format.

- **Command Validation**: When executing files, gistrun validates the provided commands against the number of files in the gist. If the number of commands doesn't match the number of files, it prompts the user to confirm whether to proceed with the available commands or abort.

- **Hash Verification**: When executing a gist, you can optionally provide an expected hash of the combined gist contents. gistrun will compare the actual hash with the expected hash and raise an error if they don't match.

- **Error Handling**: gistrun handles various exceptions that may occur during the execution, such as network errors, invalid input, or execution failures. It provides clear error messages to help identify and resolve issues.

Execution Mapping and File Handling
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

gistrun includes a predefined mapping of file extensions to their respective execution commands. This mapping covers a wide range of programming languages and formats, allowing for easy execution of various file types.

When executing files, gistrun creates temporary files on the system to hold the contents of the gist files. These temporary files are used to execute the commands, and they are automatically removed after the execution is completed.

Execution Timeout
~~~~~~~~~~~~~~~~~

gistrun allows you to set a timeout for each file execution using the ``--timeout`` option. This timeout is specified in seconds and prevents long-running or infinite loops from causing the tool to hang indefinitely.

Dry Run Mode
~~~~~~~~~~~~

The ``--dry-run`` option allows you to perform a dry run of the execution without actually running the commands. This can be useful for testing or debugging purposes, as it shows the commands that would be executed without making any changes to the system.

Execution Report
~~~~~~~~~~~~~~~~

After executing the files in a gist, you can generate an execution report using the ``--report`` option. The report includes the following information:

- The full command executed for each file
- The execution time for each file
- The total execution time for all files

This report can be useful for tracking and analyzing the execution performance of the gist files.

GitHub Authentication and Private Gists
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

gistrun supports accessing private gists by providing a GitHub API token. You can either pass the token using the ``--token`` option or set it as an environment variable (``GH_TOKEN`` or ``GITHUB_TOKEN``).

When accessing private gists, gistrun automatically includes the provided token in the API requests to GitHub, ensuring that you have the necessary permissions to fetch and execute the gist contents.

Integration with Other Tools
----------------------------

gistrun can be easily integrated with other tools and scripts, allowing you to automate various tasks involving code snippets or scripts hosted on GitHub Gists.

For example, you can use gistrun in your continuous integration and deployment pipelines to fetch and execute test scripts or deployment scripts directly from Gists. This can be particularly useful for sharing and reusing scripts across different projects or teams.

Additionally, gistrun can be used in combination with other command-line utilities or scripts, enabling you to build more complex workflows and automations around code snippets hosted on GitHub Gists.

Contributing
------------

If you encounter any issues or have suggestions for improvements, please feel free to open an issue or submit a pull request on the gistrun repository on GitHub.

Contributions to the project are welcome and appreciated. Please follow the contribution guidelines outlined in the repository's README file.

License
-------

gistrun is released under the MIT License. See the LICENSE file for more details.
