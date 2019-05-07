"""Metadata models for Warcs and Arcs."""
from file_scraper.utils import metadata, ensure_str
from file_scraper.base import BaseMeta


# pylint: disable=too-few-public-methods
class BaseWarctoolsMeta(BaseMeta):
    """Base metadata class for Warcs and Arcs."""

    # pylint: disable=no-self-use
    @metadata()
    def stream_type(self):
        """Return file type."""
        return "binary"


class GzipWarctoolsMeta(BaseWarctoolsMeta):
    """Metadata model for compressed Warcs and Arcs."""

    _supported = {"application/gzip": []}  # Supported mimetype
    _allow_versions = True  # Allow any version

    def __init__(self, metadata_model):
        """
        Initialize the metadata model

        :metadata_model: Either WarcWarctoolsMeta or ArcWarctoolsMeta object
                         representing the extracted warc or arc.
        """
        self._metadata_model = metadata_model

    @metadata()
    def mimetype(self):
        """Return MIME type."""
        return self._metadata_model[0].mimetype()

    @metadata()
    def version(self):
        """Return the version."""
        return self._metadata_model[0].version()


class WarcWarctoolsMeta(BaseWarctoolsMeta):
    """Metadata models for Warcs"""

    # Supported mimetype and versions
    _supported = {"application/warc": []}
    _allow_versions = True  # Allow any version

    def __init__(self, line):
        """
        Initialize the metadata model.

        :line: The first line of the warc archive.
        """
        self._line = line
        super(WarcWarctoolsMeta, self).__init__()

    @metadata()
    def mimetype(self):
        """Return MIME type."""
        return "application/warc"

    @metadata()
    def version(self):
        """Return the version."""
        if len(self._line.split(b"WARC/", 1)) > 1:
            return ensure_str(
                self._line.split(b"WARC/", 1)[1].split(b" ")[0].strip())
        return "(:unav)"


class ArcWarctoolsMeta(BaseWarctoolsMeta):
    """Metadata model for Arcs."""

    # Supported mimetype and varsions
    _supported = {"application/x-internet-archive": []}
    _allow_versions = True  # Allow any version

    @metadata()
    def mimetype(self):
        """Return MIME type."""
        return "application/x-internet-archive"