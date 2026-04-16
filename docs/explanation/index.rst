Explanation
===========

Understanding-oriented documentation about NHL Scrabble's design and architecture.

These explanations provide context, background, and design rationale. They help you
understand *why* things work the way they do.

.. toctree::
   :maxdepth: 2
   :caption: Design & Architecture

   why-scrabble-scoring
   architecture
   nhl-api-strategy
   testing-philosophy

Topics Covered
--------------

**Why Scrabble Scoring?**
   :doc:`why-scrabble-scoring`
      The concept behind using Scrabble letter values to rank NHL players.
      Explores the whimsical nature of the project and its educational value.

**Architecture Overview**
   :doc:`architecture`
      System design and component organization. How the package is structured
      and why specific architectural decisions were made.

**NHL API Strategy**
   :doc:`nhl-api-strategy`
      Integration approach with the NHL API. Rate limiting, error handling,
      retry logic, and data flow design.

**Testing Philosophy**
   :doc:`testing-philosophy`
      Testing strategy and quality assurance approach. Unit vs integration tests,
      coverage goals, and test automation.

About Explanations
------------------

Unlike tutorials (which teach) or how-to guides (which solve problems), explanations
focus on **understanding**:

* **Context** - Historical background and motivation
* **Design** - Why things are structured this way
* **Trade-offs** - Decisions made and alternatives considered
* **Concepts** - Core ideas and principles

These explanations follow the Diátaxis framework:

* **Understanding-oriented** - Deepen your knowledge
* **Conceptual** - Focus on ideas and connections
* **Background** - Provide context and rationale
* **Informative** - Explain without instructing

When to Read Explanations
--------------------------

* **After tutorials** - You've used the package and want to understand it better
* **During development** - You're adding features and need architectural context
* **For decision-making** - You need to understand trade-offs and design choices
* **Out of curiosity** - You want to know the "why" behind the "what"

Related Documentation
---------------------

* :doc:`../tutorials/index` - Learn by doing with step-by-step lessons
* :doc:`../how-to/index` - Solve specific problems with practical guides
* :doc:`../reference/index` - Look up technical specifications
* :doc:`../development/index` - Contribute to the project
