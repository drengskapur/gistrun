
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
