"""
Metadata scraper for pdf files, based on Ghostscript.

This scraper does not scrape metadata but instead checks well-formedness of pdf
versions 1.7, A-2a, A-2b, A-2u, A-3a, A-3b and A-3u.
"""
from __future__ import unicode_literals

from file_scraper.base import BaseScraper
from file_scraper.shell import Shell
from file_scraper.ghostscript.ghostscript_model import GhostscriptMeta
from file_scraper.utils import ensure_text, encode_path


class GhostscriptScraper(BaseScraper):
    """Ghostscript pdf scraper."""

    # Supported mimetype and versions
    _supported_metadata = [GhostscriptMeta]
    _only_wellformed = True   # Only well-formed check

    def scrape_file(self):
        """Scrape file."""
        shell = Shell([
            "gs", "-o", "/dev/null", "-sDEVICE=nullpage",
            encode_path(self.filename)])

        if shell.returncode != 0:
            self._errors.append(
                "Ghostscript returned invalid return code: %s\n%s"
                % (shell.returncode, shell.stderr)
                )

        # Ghostscript may print characters which cannot be converted to UTF-8
        stdout_message = ensure_text(shell.stdout_raw, errors='replace')
        stderr_message = ensure_text(shell.stderr_raw, errors='replace')
        self._messages.append(stdout_message)

        # Ghostscript will result 0 if it can repair errors.
        # However, in those cases an error is logged to either _errors or
        # _messages. This case should be handled as well-formed failure.
        if stderr_message:
            self._errors.append(stderr_message)

        # If no errors have been logged, the file is valid.
        else:
            self._messages.append("Well-Formed and valid")

        self.streams = list(self.iterate_models())
        self._check_supported(allow_unav_mime=True, allow_unav_version=True)

    @property
    def well_formed(self):
        """
        Overwrite the normal well-formedness check to also look at the stdout.

        This is needed as ghostscript can log errors to stdout if it has been
        able to repair the file. In these cases, scraper messages contain
        "**** Error" or "**** Warning" (any capitalization is detected), which
        is interpreted as well-formedness failure.

        :returns: True if the file is well-formed, False if it is not.
        """
        for message in self._messages:
            if ("**** error" in message.lower() or
                    "**** warning" in message.lower()):
                return False
        return super(GhostscriptScraper, self).well_formed
