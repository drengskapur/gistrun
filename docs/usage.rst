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
