"""DPX scraper"""

from __future__ import unicode_literals

import six

from file_scraper.base import BaseScraper
from file_scraper.shell import Shell
from file_scraper.dpx.dpx_model import DpxMeta
from file_scraper.utils import encode_path


class DpxScraper(BaseScraper):
    """DPX scraper."""

    _supported_metadata = [DpxMeta]
    _only_wellformed = True

    @property
    def _dpxv(self):
        """Return matching dpxv command current Python version.

        :returns: Path to dpxv command

        """
        if six.PY3:
            return "/usr/bin/dpxv-3"
        return "/usr/bin/dpxv"

    def scrape_file(self):
        """Scrape DPX."""

        shell = Shell([self._dpxv, encode_path(self.filename)])

        if shell.returncode != 0:
            self._errors.append("DPX returned invalid return code: %s\n%s" %
                                (shell.returncode, shell.stderr))

        if shell.stderr:
            self._errors += list(shell.stderr.splitlines())

        if shell.stdout:
            self._messages += list(shell.stdout.splitlines())

        self.streams = list(self.iterate_models(
            well_formed=self.well_formed, messages=self._messages,
            filename=self.filename))

        self._check_supported()
