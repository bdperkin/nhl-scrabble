NHL API Module
==============

NHL API client with retry logic and rate limiting.

The API module provides an async HTTP client for fetching roster data from the
official NHL API with built-in error handling, retries, and rate limiting.

.. automodule:: nhl_scrabble.api
   :members:
   :undoc-members:
   :show-inheritance:

NHL Client
----------

.. automodule:: nhl_scrabble.api.nhl_client
   :members:
   :undoc-members:
   :show-inheritance:
   :member-order: bysource

NHLClient
~~~~~~~~~

.. autoclass:: nhl_scrabble.api.nhl_client.NHLClient
   :members:
   :undoc-members:
   :show-inheritance:

Async HTTP client for NHL API with context manager support.

**Features:**

* Async/await support with aiohttp
* Automatic retry with exponential backoff
* Rate limiting with configurable delay
* Timeout handling
* Session management via context manager
* Comprehensive error handling

**Configuration:**

Environment variables for customization:

* ``NHL_SCRABBLE_API_TIMEOUT`` - Request timeout in seconds (default: 10)
* ``NHL_SCRABBLE_API_RETRIES`` - Number of retry attempts (default: 3)
* ``NHL_SCRABBLE_RATE_LIMIT_DELAY`` - Delay between requests in seconds (default: 0.3)

**Usage:**

.. code-block:: python

    from nhl_scrabble.api import NHLClient
    import asyncio

    async def fetch_data():
        async with NHLClient() as client:
            # Fetch all teams
            teams = await client.fetch_all_teams()

            # Fetch roster for specific team
            roster = await client.fetch_team_roster("TOR")

            # Fetch all rosters (with rate limiting)
            all_rosters = await client.fetch_all_rosters()

        return teams, all_rosters

    # Run async code
    teams, rosters = asyncio.run(fetch_data())

Methods
-------

fetch_all_teams
~~~~~~~~~~~~~~~

.. automethod:: nhl_scrabble.api.nhl_client.NHLClient.fetch_all_teams

Fetch metadata for all NHL teams including division and conference.

**Returns:**

* List of Team objects with:
  * Team ID, abbreviation, full name
  * Division and conference assignments
  * Logo URL

**Endpoint:**

``GET https://api-web.nhle.com/v1/standings/now``

**Example:**

.. code-block:: python

    async with NHLClient() as client:
        teams = await client.fetch_all_teams()

    for team in teams:
        print(f"{team.name} ({team.abbrev}) - {team.division}, {team.conference}")

fetch_team_roster
~~~~~~~~~~~~~~~~~

.. automethod:: nhl_scrabble.api.nhl_client.NHLClient.fetch_team_roster

Fetch current roster for a specific team.

**Parameters:**

* ``team_abbrev`` - Team abbreviation (e.g., 'TOR', 'MTL', 'NYR')

**Returns:**

* List of Player objects for the team's current roster

**Endpoint:**

``GET https://api-web.nhle.com/v1/roster/{team_abbrev}/current``

**Example:**

.. code-block:: python

    async with NHLClient() as client:
        roster = await client.fetch_team_roster("TOR")

    print(f"Toronto Maple Leafs roster: {len(roster)} players")
    for player in roster[:5]:
        print(f"  {player.firstName} {player.lastName}")

fetch_all_rosters
~~~~~~~~~~~~~~~~~

.. automethod:: nhl_scrabble.api.nhl_client.NHLClient.fetch_all_rosters

Fetch rosters for all NHL teams with rate limiting.

**Returns:**

* Dictionary mapping team abbreviations to lists of Player objects

**Example:**

.. code-block:: python

    async with NHLClient() as client:
        all_rosters = await client.fetch_all_rosters()

    total_players = sum(len(roster) for roster in all_rosters.values())
    print(f"Total players across NHL: {total_players}")

Error Handling
--------------

The client handles various error conditions:

**Network Errors:**

* Connection timeouts → Automatic retry with exponential backoff
* Network unavailable → Raises with descriptive error message
* DNS failures → Raises with connection details

**HTTP Errors:**

* 404 Not Found → Logs warning, returns empty list
* 429 Too Many Requests → Respects retry-after header
* 500+ Server Errors → Retries with backoff

**Example Error Handling:**

.. code-block:: python

    from nhl_scrabble.api import NHLClient
    import aiohttp
    import asyncio

    async def safe_fetch():
        try:
            async with NHLClient() as client:
                teams = await client.fetch_all_teams()
        except aiohttp.ClientError as e:
            print(f"Network error: {e}")
            teams = []
        except asyncio.TimeoutError:
            print("Request timed out")
            teams = []

        return teams

Rate Limiting
-------------

The client implements rate limiting to be respectful to the NHL API:

* Default delay: 0.3 seconds between roster fetches
* Configurable via ``NHL_SCRABBLE_RATE_LIMIT_DELAY``
* Applied in ``fetch_all_rosters()`` method
* Uses ``asyncio.sleep()`` for non-blocking delays

**Custom Rate Limit:**

.. code-block:: python

    import os
    os.environ['NHL_SCRABBLE_RATE_LIMIT_DELAY'] = '0.5'  # 500ms delay

    async with NHLClient() as client:
        rosters = await client.fetch_all_rosters()  # Uses 500ms delay

Retry Logic
-----------

Automatic retry with exponential backoff:

* **Retries:** Configurable (default: 3)
* **Backoff:** Exponential (1s, 2s, 4s)
* **Conditions:** Network errors, timeouts, 5xx errors
* **No Retry:** 4xx errors (client errors)

**Custom Retry Configuration:**

.. code-block:: python

    import os
    os.environ['NHL_SCRABBLE_API_RETRIES'] = '5'  # 5 retry attempts

    async with NHLClient() as client:
        teams = await client.fetch_all_teams()  # Up to 5 retries

Related Documentation
---------------------

* :doc:`../explanation/nhl-api-strategy` - API integration strategy
* :doc:`../how-to/configure-api-settings` - Configuration guide
* :doc:`../how-to/debug-api-issues` - Troubleshooting
* :doc:`models` - Data models for API responses
