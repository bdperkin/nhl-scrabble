"""Locust load testing configuration.

Simulates concurrent users accessing the NHL Scrabble web application
to measure performance under load.

Usage:
    # Run with default settings (10 users, 1/s spawn rate, 1 minute)
    locust -f qa/web/tests/performance/locustfile.py \
           --host http://localhost:5000

    # Run with custom settings (50 users, 5/s spawn rate, 5 minutes)
    locust -f qa/web/tests/performance/locustfile.py \
           --host http://localhost:5000 \
           --users 50 \
           --spawn-rate 5 \
           --run-time 5m

    # Run headless with CSV output
    locust -f qa/web/tests/performance/locustfile.py \
           --host http://localhost:5000 \
           --users 100 \
           --spawn-rate 10 \
           --run-time 2m \
           --headless \
           --csv results/load_test

    # Run with web UI on custom port
    locust -f qa/web/tests/performance/locustfile.py \
           --host http://localhost:5000 \
           --web-port 8089
"""

from locust import HttpUser, between, task


class WebsiteUser(HttpUser):
    """Simulates a typical user browsing the NHL Scrabble website.

    This user performs common actions with varying frequencies:
    - Homepage visits (most frequent)
    - Teams page views (frequent)
    - Stats page views (moderate)
    - Divisions page views (moderate)
    - Conferences page views (moderate)
    - Playoffs page views (less frequent)

    Wait time between requests: 1-3 seconds (simulates reading/browsing)
    """

    wait_time = between(1, 3)

    @task(5)
    def load_homepage(self) -> None:
        """Load the homepage.

        Weight: 5 (highest) - Homepage is the most visited page
        """
        self.client.get("/", name="Homepage")

    @task(4)
    def load_teams(self) -> None:
        """Load the teams page.

        Weight: 4 (high) - Teams page is frequently accessed
        """
        self.client.get("/teams", name="Teams Page")

    @task(3)
    def load_stats(self) -> None:
        """Load the stats page.

        Weight: 3 (moderate) - Stats page is moderately accessed
        """
        self.client.get("/stats", name="Stats Page")

    @task(2)
    def load_divisions(self) -> None:
        """Load the divisions page.

        Weight: 2 (moderate) - Divisions page is moderately accessed
        """
        self.client.get("/divisions", name="Divisions Page")

    @task(2)
    def load_conferences(self) -> None:
        """Load the conferences page.

        Weight: 2 (moderate) - Conferences page is moderately accessed
        """
        self.client.get("/conferences", name="Conferences Page")

    @task(1)
    def load_playoffs(self) -> None:
        """Load the playoffs page.

        Weight: 1 (low) - Playoffs page is less frequently accessed
        """
        self.client.get("/playoffs", name="Playoffs Page")

    def on_start(self) -> None:
        """Execute when a simulated user starts.

        Simulates a new user landing on the homepage first.
        """
        self.client.get("/", name="Initial Homepage Visit")


class HeavyUser(HttpUser):
    """Simulates a heavy user who rapidly navigates between pages.

    This user represents power users who:
    - Navigate quickly (0.5-1.5s between requests)
    - Access all pages frequently
    - May represent automated tools or data scrapers

    Use this to test system behavior under aggressive usage patterns.
    """

    wait_time = between(0.5, 1.5)

    @task(3)
    def browse_all_pages(self) -> None:
        """Browse through all major pages in sequence.

        Weight: 3 (moderate) - Simulates thorough browsing
        """
        pages = ["/", "/teams", "/divisions", "/conferences", "/playoffs", "/stats"]
        for page in pages:
            self.client.get(page, name=f"Sequential: {page}")

    @task(2)
    def load_stats_repeatedly(self) -> None:
        """Load stats page repeatedly.

        Weight: 2 (moderate) - Simulates refreshing for updated data
        """
        self.client.get("/stats", name="Stats (Heavy)")

    @task(1)
    def load_teams_repeatedly(self) -> None:
        """Load teams page repeatedly.

        Weight: 1 (low) - Simulates checking team rankings
        """
        self.client.get("/teams", name="Teams (Heavy)")


class CasualUser(HttpUser):
    """Simulates a casual user with longer wait times.

    This user represents typical visitors who:
    - Read content slowly (3-10s between requests)
    - Visit fewer pages per session
    - Mainly view homepage and one or two other pages

    Use this to simulate realistic user behavior.
    """

    wait_time = between(3, 10)

    @task(10)
    def view_homepage(self) -> None:
        """View homepage.

        Weight: 10 (very high) - Most casual users start and stay on homepage
        """
        self.client.get("/", name="Homepage (Casual)")

    @task(2)
    def view_teams(self) -> None:
        """View teams page.

        Weight: 2 (low) - Some casual users check teams
        """
        self.client.get("/teams", name="Teams (Casual)")

    @task(1)
    def view_stats(self) -> None:
        """View stats page.

        Weight: 1 (very low) - Few casual users check detailed stats
        """
        self.client.get("/stats", name="Stats (Casual)")
