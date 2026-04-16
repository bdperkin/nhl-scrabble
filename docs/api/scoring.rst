Scoring Module
==============

Scrabble scoring logic for NHL player names.

The scoring module calculates Scrabble letter values for player names using
standard Scrabble point assignments.

.. automodule:: nhl_scrabble.scoring
   :members:
   :undoc-members:
   :show-inheritance:

Scrabble Scorer
---------------

.. automodule:: nhl_scrabble.scoring.scrabble
   :members:
   :undoc-members:
   :show-inheritance:
   :member-order: bysource

ScrabbleScorer
~~~~~~~~~~~~~~

.. autoclass:: nhl_scrabble.scoring.scrabble.ScrabbleScorer
   :members:
   :undoc-members:
   :show-inheritance:

Calculate Scrabble scores using standard letter values.

**Attributes:**

* ``scrabble_values`` - Dictionary mapping letters to point values

Letter Values
-------------

Standard Scrabble letter point values:

.. list-table::
   :header-rows: 1
   :widths: 10 90

   * - Points
     - Letters
   * - 1
     - A, E, I, O, U, L, N, S, T, R
   * - 2
     - D, G
   * - 3
     - B, C, M, P
   * - 4
     - F, H, V, W, Y
   * - 5
     - K
   * - 8
     - J, X
   * - 10
     - Q, Z

**Constant:**

.. code-block:: python

    SCRABBLE_VALUES = {
        'A': 1, 'E': 1, 'I': 1, 'O': 1, 'U': 1,
        'L': 1, 'N': 1, 'S': 1, 'T': 1, 'R': 1,
        'D': 2, 'G': 2,
        'B': 3, 'C': 3, 'M': 3, 'P': 3,
        'F': 4, 'H': 4, 'V': 4, 'W': 4, 'Y': 4,
        'K': 5,
        'J': 8, 'X': 8,
        'Q': 10, 'Z': 10
    }

Methods
-------

calculate_score
~~~~~~~~~~~~~~~

.. automethod:: nhl_scrabble.scoring.scrabble.ScrabbleScorer.calculate_score

Calculate Scrabble score for arbitrary text.

**Parameters:**

* ``text`` - Input text (case-insensitive, non-letters ignored)

**Returns:**

* Integer score as sum of letter values

**Example:**

.. code-block:: python

    from nhl_scrabble.scoring import ScrabbleScorer

    scorer = ScrabbleScorer()

    # Simple word
    score = scorer.calculate_score("HELLO")
    print(score)  # 8 (H=4, E=1, L=1, L=1, O=1)

    # Player name
    score = scorer.calculate_score("Ovechkin")
    print(score)  # 23 (O=1, V=4, E=1, C=3, H=4, K=5, I=1, N=1)

    # Case insensitive
    assert scorer.calculate_score("OVECHKIN") == scorer.calculate_score("ovechkin")

score_player
~~~~~~~~~~~~

.. automethod:: nhl_scrabble.scoring.scrabble.ScrabbleScorer.score_player

Calculate Scrabble score for a Player object.

**Parameters:**

* ``player`` - Player object with firstName and lastName

**Returns:**

* PlayerScore object with breakdown and total

**Example:**

.. code-block:: python

    from nhl_scrabble.models import Player
    from nhl_scrabble.scoring import ScrabbleScorer

    player = Player(
        id=8478402,
        firstName="Alexander",
        lastName="Ovechkin",
        positionCode="LW"
    )

    scorer = ScrabbleScorer()
    player_score = scorer.score_player(player)

    print(f"First name: {player_score.first_score}")  # 22
    print(f"Last name: {player_score.last_score}")    # 23
    print(f"Total: {player_score.total}")             # 45

Usage Patterns
--------------

**Basic Scoring:**

.. code-block:: python

    from nhl_scrabble.scoring import ScrabbleScorer

    scorer = ScrabbleScorer()

    # Score individual names
    scores = {
        "Crosby": scorer.calculate_score("Crosby"),
        "McDavid": scorer.calculate_score("McDavid"),
        "Matthews": scorer.calculate_score("Matthews"),
    }

    # Find highest scorer
    top_name = max(scores, key=scores.get)
    print(f"{top_name}: {scores[top_name]} points")

**Batch Player Scoring:**

.. code-block:: python

    from nhl_scrabble.scoring import ScrabbleScorer

    scorer = ScrabbleScorer()
    player_scores = [scorer.score_player(p) for p in players]

    # Sort by total score
    player_scores.sort(key=lambda ps: ps.total, reverse=True)

    # Display top 10
    for i, ps in enumerate(player_scores[:10], 1):
        print(f"{i}. {ps.player.firstName} {ps.player.lastName}: {ps.total}")

**Team Aggregation:**

.. code-block:: python

    from nhl_scrabble.scoring import ScrabbleScorer

    scorer = ScrabbleScorer()

    # Score all players on a team
    team_players = rosters["TOR"]
    team_scores = [scorer.score_player(p) for p in team_players]

    # Calculate team total
    team_total = sum(ps.total for ps in team_scores)
    team_avg = team_total / len(team_scores)

    print(f"Toronto Maple Leafs:")
    print(f"  Total: {team_total}")
    print(f"  Average: {team_avg:.1f}")

Special Cases
-------------

**Non-Letter Characters:**

Non-letter characters are ignored:

.. code-block:: python

    scorer = ScrabbleScorer()

    assert scorer.calculate_score("O'Reilly") == scorer.calculate_score("OReilly")
    assert scorer.calculate_score("St. Louis") == scorer.calculate_score("StLouis")
    assert scorer.calculate_score("Suter-2") == scorer.calculate_score("Suter")

**Empty Strings:**

Empty strings score 0:

.. code-block:: python

    assert scorer.calculate_score("") == 0
    assert scorer.calculate_score("   ") == 0
    assert scorer.calculate_score("123") == 0

**International Characters:**

Only ASCII letters A-Z are scored:

.. code-block:: python

    # Accented characters are ignored
    score1 = scorer.calculate_score("Koivu")
    score2 = scorer.calculate_score("Kóívû")  # Accents ignored
    # Scores may differ if letters are different

Related Documentation
---------------------

* :doc:`../explanation/why-scrabble-scoring` - Why Scrabble scoring?
* :doc:`models` - Player and PlayerScore models
* :doc:`processors` - Team aggregation logic
* :doc:`../tutorials/02-understanding-output` - Understanding scores
