Authentication
==============

GistRun supports accessing private gists by providing a GitHub API token. You can either pass the token using the ``--token`` option or set it as an environment variable (``GH_TOKEN`` or ``GITHUB_TOKEN``).

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

1. Go to your GitHub account settings...
   ... (additional steps to create a GitHub API token)