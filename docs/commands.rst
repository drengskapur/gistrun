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
