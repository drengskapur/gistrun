.. _gistrun:

GistRun - Put Your Gists to Work
===============================

Have a bunch of code snippets scripts gathering dust? 

GistRun is a command-line tool that lets you fetch and run that code directly from your Gists. GistRun saves you from having to clone or download entire repos just to access a few lines of code. No more tedious copy-pasting either—just run your Gists with a simple command. Turn those idle Gists into executable code with GistRun. Whether you're exploring programming concepts, testing algorithms, or sharing samples, this tool lets you actually use those snippets as runnable scripts. GistRun streamlines your workflow by bridging the gap between coding and research. Put your dormant Gists to work, increase productivity, and keep your coding efforts closely tied to your research—all with one utility. Make those forgotten snippets useful again with GistRun.

.. warning::
   GistRun executes code from GitHub Gists. While convenient, this poses a security risk as the executed code may be malicious. Use GistRun only with Gists from trusted sources, and review the code before executing it. The authors of GistRun are not responsible for any damage caused by executing untrusted code.

Use Cases
---------

GistRun can be particularly useful in the following scenarios:

- **Reusing code snippets:** Instead of rewriting the same code snippets for common tasks (e.g., utility functions, data processing scripts, etc.), you can store them in GitHub Gists and easily fetch and execute them using GistRun.
- **Sharing scripts:** GistRun allows you to share scripts or code snippets with others by hosting them on GitHub Gists. Others can then execute your code using GistRun without needing to clone or download your entire repository.
- **Automating workflows:** You can integrate GistRun into your automation scripts or continuous integration/deployment pipelines to fetch and execute scripts or tests directly from Gists, streamlining your workflows.
- **Learning and experimenting:** GistRun provides a convenient way to execute code snippets from GitHub Gists, making it easier to learn from examples or experiment with new ideas without cluttering your local environment.

By leveraging GistRun, you can save time, avoid reinventing the wheel, and promote code reuse and collaboration within your team or community.

Installation
------------

To install GistRun, run:

.. code-block:: console

   $ pip install gistrun

Usage
-----

The main command to execute code from a GitHub Gist is ``gistrun exec``:

.. code-block:: console

   $ gistrun exec octocat/my-gist

This command will fetch the gist named `my-gist` owned by the user `octocat` and execute the files it contains using the appropriate commands based on the file extensions.
