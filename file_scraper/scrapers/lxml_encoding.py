"""class for XML and HTML5 header encoding check with lxml. """
try:
    from lxml import etree
except ImportError:
    pass

from file_scraper.base import BaseScraper


class XmlEncoding(BaseScraper):
    """
    Scrape character encoding from XML/HTML header.
    """

    # We use JHOVE for HTML4 and XHTML files.
    _supported = {'text/xml': ['1.0'], 'text/html': ['5.0']}
    _only_wellformed = True  # Only well-formed check

    def __init__(self, filename, mimetype, validation=True, params=None):
        """Initialize scraper.
        :filename: File path
        :mimetype: Predicted mimetype of the file
        :validation: True for the full validation, False for just
                     identification and metadata scraping
        :params: Extra parameters: delimiter and separator
        """
        self._charset = None
        super(XmlEncoding, self).__init__(filename, mimetype,
                                          validation, params)

    @classmethod
    def is_supported(cls, mimetype, version=None,
                     validation=True, params=None):
        """This is not a Schematron scraper, we skip this in such case.
        :mimetype: Identified mimetype
        :version: Identified version (if needed)
        :validation: True for the full validation, False for just
                     identification and metadata scraping
        :params: Extra parameters needed for the scraper
        :returns: True if scraper is supported
        """
        if params is None:
            params = {}
        if 'schematron' in params:
            return False
        return super(XmlEncoding, cls).is_supported(mimetype, version,
                                                    validation, params)

    def scrape_file(self):
        """Scrape file.
        """
        parser = etree.XMLParser(dtd_validation=False, no_network=True,
                                 recover=True)
        fd = open(self.filename)
        tree = etree.parse(fd, parser)
        self._charset = tree.docinfo.encoding
        self.messages('Encoding metadata found.')
        self._check_supported()
        self._collect_elements()

    def _s_charset(self):
        """Return charset
        """
        return self._charset

    # pylint: disable=no-self-use
    def _s_stream_type(self):
        """Return file type
        """
        return 'text'