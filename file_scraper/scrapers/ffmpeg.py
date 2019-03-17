"""
This is an ffmpeg wellformed scraper
"""
from file_scraper.base import BaseScraper, Shell


class FFMpeg(BaseScraper):
    """FFMpeg Wellformed scraper
    """

    # Supported mimetypes
    _supported = {'video/mpeg': ['1', '2'], 'video/mp4': [''],
                  'audio/mpeg': ['1', '2'], 'audio/mp4': [''],
                  'video/MP1S': [''], 'video/MP2P': [''],
                  'video/MP2T': ['']}
    _only_wellformed = True  # Only well-formed check

    def scrape_file(self):
        """Scrape DPX.
        """
        shell = Shell(['ffmpeg', '-v', 'error', '-i', self.filename, '-f',
                       'null', '-'])

        if shell.returncode == 0:
            self.messages('The file was scraped successfully.')

        self.errors(shell.stderr)
        self.messages(shell.stdout)
        self._check_supported()
        self._collect_elements()

    # pylint: disable=no-self-use
    def _s_version(sef):
        """Return version
        """
        return None

    # pylint: disable=no-self-use
    def _s_stream_type(self):
        """Return file type
        """
        return None