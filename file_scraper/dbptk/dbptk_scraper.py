"""A SIARD scraper module using DBPTK-developer.

This scraper does not scrape metadata but instead checks well-formedness
of SIARD files.
"""
from __future__ import unicode_literals

from file_scraper.base import BaseScraper
from file_scraper.shell import Shell
from file_scraper.dbptk.dbptk_model import DbptkMeta


class DbptkScraper(BaseScraper):
    """DBPTK scraper. Supports only SIARD files."""

    _supported_metadata = [DbptkMeta]
    _only_wellformed = True  # Only well-formed check

    def scrape_file(self):
        """Scrape file using dbptk."""
        shell = Shell([
            "dbptk",
            "validate",
            "-if",
            self.filename])

        report = shell.stdout

        # Read and parse validation report
        if all(("Validation process finished the SIARD is valid." in report,
                "Number of errors [0]" in report)):
            self._messages.append(report)
        else:
            self._errors.append("Validator returned error.")
            self._errors.append(report)
            self._errors.append(shell.stderr)

        self.streams = list(self.iterate_models())
        self._check_supported(allow_unav_version=True)
