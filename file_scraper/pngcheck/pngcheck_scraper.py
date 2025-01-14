"""Module for pngcheck scraper."""
from __future__ import unicode_literals

from file_scraper.base import BaseScraper
from file_scraper.shell import Shell
from file_scraper.pngcheck.pngcheck_model import PngcheckMeta
from file_scraper.utils import encode_path


class PngcheckScraper(BaseScraper):
    """
    Pngcheck scraper.

    .. seealso:: http://www.libpng.org/pub/png/apps/pngcheck.html
    """

    _supported_metadata = [PngcheckMeta]
    _only_wellformed = True              # Only well-formed check

    def scrape_file(self):
        """Scrape file."""
        shell = Shell(["pngcheck", encode_path(self.filename)])

        if shell.returncode != 0:
            self._errors.append("Pngcheck returned invalid return code: %s\n%s"
                                % (shell.returncode, shell.stderr))

        self._messages.append(shell.stdout)

        # This scraper does not know anything about the MIME type, so checking
        # is not useful. Just add metadata models.
        self.streams = list(self.iterate_models())

        self._check_supported(allow_unav_mime=True, allow_unav_version=True)
