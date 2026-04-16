Reference
=========

Information-oriented technical specifications and API documentation.

Complete reference documentation for NHL Scrabble's command-line interface,
configuration options, and build tools.

.. toctree::
   :maxdepth: 2
   :caption: Command-Line Interface

   cli
   cli-generated

.. toctree::
   :maxdepth: 2
   :caption: Configuration

   configuration
   environment-variables

.. toctree::
   :maxdepth: 2
   :caption: Build Tools

   makefile

.. toctree::
   :maxdepth: 2
   :caption: API Documentation

   api/index

Quick Reference
---------------

**Command-Line Interface**
   :doc:`cli`
      Complete CLI reference with all commands, options, and arguments

   :doc:`cli-generated`
      Auto-generated CLI documentation from Click decorators

**Configuration**
   :doc:`configuration`
      All configuration options and their effects

   :doc:`environment-variables`
      Environment variables for customizing behavior

**Build Tools**
   :doc:`makefile`
      Makefile targets for development, testing, and deployment (55 targets)

**API Documentation**
   :doc:`api/index`
      Auto-generated API reference from Python docstrings

Reference Documentation
-----------------------

Reference materials are **information-oriented** and follow the Diátaxis framework:

* **Factual** - Accurate technical specifications
* **Complete** - Comprehensive coverage of all options
* **Structured** - Organized for easy lookup
* **Authoritative** - The definitive source of truth

How to Use This Reference
--------------------------

**Looking up a specific option?**
   Use the search function or navigate to the relevant section

**Want complete command syntax?**
   See :doc:`cli` for all commands and options

**Need to configure behavior?**
   Check :doc:`environment-variables` for available settings

**Understanding the API?**
   Browse :doc:`api/index` for module documentation

**Using the Makefile?**
   See :doc:`makefile` for all 55 targets with descriptions

Related Documentation
---------------------

* :doc:`../tutorials/index` - Learn NHL Scrabble with step-by-step lessons
* :doc:`../how-to/index` - Solve specific problems with practical guides
* :doc:`../explanation/index` - Understand design and architecture
* :doc:`../development/index` - Contribute to the project

About Auto-Generated Documentation
-----------------------------------

Some reference pages are auto-generated:

* :doc:`cli-generated` - Generated from Click decorators
* :doc:`api/index` - Generated from Python docstrings with Sphinx autodoc

These pages are automatically updated when code changes, ensuring
documentation stays in sync with implementation.
