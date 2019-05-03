"""Metadata models for files scraped using magic."""
import ctypes

from file_scraper.base import BaseMeta
from file_scraper.defaults import MIMETYPE_DICT
from file_scraper.utils import encode, metadata

try:
    from file_scraper.defaults import MAGIC_LIBRARY

    ctypes.cdll.LoadLibrary(MAGIC_LIBRARY)
except OSError:
    print("%s not found, MS Office detection may not work properly if "
          "file command library is older." % MAGIC_LIBRARY)
try:
    import magic as magic
except ImportError:
    pass


class BaseMagicMeta(BaseMeta):
    """The base class for all metadata models using magic."""
    _starttag = "version "  # Text before file format version in magic result.
    _endtag = None  # Text after file format version in magic result.

    def __init__(self, filename, errors):
        """Imitialize the metadata model."""
        self._filename = filename
        self._errors = errors
        super(BaseMagicMeta, self).__init__()

    @metadata()
    def mimetype(self):
        """Return MIME type."""
        try:
            magic_ = magic.open(magic.MAGIC_MIME_TYPE)
            magic_.load()
            mimetype = magic_.file(encode(self._filename))
            magic_.close()
        except Exception as exception:  # pylint: disable=broad-except
            self._errors.append("Error in analysing file")
            self._errors.append(str(exception))
            return None

        if mimetype in MIMETYPE_DICT:
            mimetype = MIMETYPE_DICT[mimetype]
        return mimetype

    @metadata()
    def version(self):
        try:
            magic_ = magic.open(magic.MAGIC_NONE)
            magic_.load()
            magic_version = magic_.file(
                encode(self._filename)).split(self._starttag)[-1]
            magic_.close()
        except Exception as exception:  # pylint: disable=broad-except
            self._errors.append("Error in analysing file")
            self._errors.append(str(exception))
            return None
        if self._endtag:
            return magic_version.split(self._endtag)[0]
        return magic_version


class BinaryMagicBaseMeta(BaseMagicMeta):
    """Base class for metadata models of binary files."""

    # pylint: disable=no-self-use
    @metadata()
    def stream_type(self):
        """Return file type."""
        return "binary"

    @metadata()
    def version(self):
        """Return version."""
        magic_version = super(BinaryMagicBaseMeta, self).version()
        if magic_version == "data":
            return None
        return magic_version


class TextMagicBaseMeta(BaseMagicMeta):
    """Base class for metadata models of text files."""

    @metadata()
    def version(self):
        """Return version."""
        version = super(TextMagicBaseMeta, self).version()
        if version == "data":
            return None
        return version

    @metadata()
    def charset(self):
        """Return charset."""
        try:
            magic_ = magic.open(magic.MAGIC_MIME_ENCODING)
            magic_.load()
            magic_charset = magic_.file(encode(self._filename))
            magic_.close()
        except Exception as exception:  # pylint: disable=broad-except
            self._errors.append("Error in analyzing file")
            self._errors.append(str(exception))
            return None

        if magic_charset is None or magic_charset.upper() == "BINARY":
            return None
        if magic_charset.upper() == "US-ASCII":
            return "UTF-8"
        if magic_charset.upper() == "ISO-8859-1":
            return "ISO-8859-15"
        if magic_charset.upper() == "UTF-16LE" \
                or magic_charset.upper() == "UTF-16BE":
            return "UTF-16"

        return magic_charset.upper()

    # pylint: disable=no-self-use
    @metadata()
    def stream_type(self):
        """Return file type."""
        return "text"


class TextFileMagicMeta(TextMagicBaseMeta):
    """Metadata models for plaintext and csv files."""

    _supported = {"text/plain": [], "text/csv": []}
    _allow_versions = True  # Allow any version

    @metadata()
    def version(self):
        """Return version."""
        # TODO is this ok, used to return "" or None but text files do not
        #      really have versions do they?
        return "(:unap)"


class XmlFileMagicMeta(TextMagicBaseMeta):
    """Metadata model for xml files."""

    _supported = {"text/xml": []}  # Supported mimetypes
    _starttag = "XML "             # Text before version in magic output
    _endtag = " "                  # Text after version in magic output
    _allow_versions = True         # Allow any version

    @classmethod
    def is_supported(cls, mimetype, version=None,
                     params=None):
        """
        Return True if given MIME type and version are supported.

        This is not a Schematron scraper, skip this in such case.

        :mimetype: Identified mimetype
        :version: Identified version (if needed)
        :check_wellformed: True for the full well-formed check, False for just
                           detection and metadata scraping
        :params: Extra parameters needed for the scraper
        :returns: True if scraper is supported
        """
        if params is None:
            params = {}
        if "schematron" in params:
            return False
        return super(XmlFileMagicMeta, cls).is_supported(mimetype, version,
                                                         params)


class XhtmlFileMagicMeta(TextMagicBaseMeta):
    """Metadata model for xhtml files."""

    # Supported mimetypes
    _supported = {"application/xhtml+xml": []}
    _starttag = "XML "      # Text before version in magic output
    _endtag = " "           # Text after version in magic output
    _allow_versions = True  # Allow any version

    @metadata()
    def mimetype(self):
        """Return MIME type."""
        mime = super(XhtmlFileMagicMeta, self).mimetype()
        if mime == "text/xml":
            return "application/xhtml+xml"
        return mime


class HtmlFileMagicMeta(TextMagicBaseMeta):
    """Metadata model for html files."""

    # Supported mimetypes
    _supported = {"text/html": ["4.01", "5.0"]}

    @metadata()
    def version(self):
        """Return version."""
        return None  # TODO should this be (:unav)? Cons: check_supported fails


class PdfFileMagicMeta(BinaryMagicBaseMeta):
    """Metadata model for PDF files."""

    # Supported mimetype
    _supported = {"application/pdf": ["1.2", "1.3", "1.4", "1.5", "1.6",
                                      "1.7", "A-1a", "A-1b", "A-2a", "A-2b",
                                      "A-2u", "A-3a", "A-3b", "A-3u"]}
    _allow_versions = True  # Allow any version


class OfficeFileMagicMeta(BinaryMagicBaseMeta):
    """Metadata model for office files."""

    # Supported mimetypes and versions
    _supported = {
        "application/vnd.oasis.opendocument.text": [],
        "application/vnd.oasis.opendocument.spreadsheet": [],
        "application/vnd.oasis.opendocument.presentation": [],
        "application/vnd.oasis.opendocument.graphics": [],
        "application/vnd.oasis.opendocument.formula": [],
        "application/msword": [],
        "application/vnd.ms-excel": [],
        "application/vnd.ms-powerpoint": [],
        "application/vnd.openxmlformats-officedocument.wordprocessingml."
        "document": [],
        "application/vnd.openxmlformats-officedocument."
        "spreadsheetml.sheet": [],
        "application/vnd.openxmlformats-officedocument.presentationml."
        "presentation": []}
    _allow_versions = True  # Allow any version

    @metadata()
    def version(self):
        """Return version."""
        return None  # TODO None? Or (:unav)?


class ArcFileMagicMeta(BinaryMagicBaseMeta):
    """Metadata model for Arc files."""

    # Supported mimetype
    _supported = {"application/x-internet-archive": []}
    _allow_versions = True  # Allow any version

    @metadata()
    def mimetype(self):
        """Return mimetype."""
        magic_mimetype = super(ArcFileMagicMeta, self).mimetype()
        if magic_mimetype == "application/x-ia-arc":
            return "application/x-internet-archive"
        return magic_mimetype

    @metadata()
    def version(self):
        """Return version."""
        if self.mimetype() not in self._supported:
            return None
        version = super(ArcFileMagicMeta, self).version()
        if version == "1":
            return "1.0"
        return version


class PngFileMagicMeta(BinaryMagicBaseMeta):
    """Metadata model for PNG files."""

    _supported = {"image/png": []}  # Supported mimetype
    _allow_versions = True  # Allow any version

    @metadata()
    def version(self):
        """Return version."""
        if self.mimetype() not in self._supported:
            return None
        return "1.2"

    @metadata()
    def stream_type(self):
        """Return stream type."""
        return "image"


class JpegFileMagicMeta(BinaryMagicBaseMeta):
    """Metadata model for JPEG files."""

    _supported = {"image/jpeg": []}  # Supported mimetype
    _starttag = "standard "  # Text before version in magic output
    _endtag = ","            # Text after version in magic output
    _allow_versions = True   # Allow any version

    @metadata()
    def stream_type(self):
        """Return stream type."""
        return "image"


class Jp2FileMagicMeta(BinaryMagicBaseMeta):
    """Metadata model for JP2 files."""

    _supported = {"image/jp2": [""]}  # Supported mimetype
    _allow_versions = True  # Allow any version

    @metadata()
    def version(self):
        """Return version."""
        if self.mimetype() not in self._supported:
            return None
        return ""

    @metadata()
    def stream_type(self):
        """Return stream type."""
        return "image"


class TiffFileMagicMeta(BinaryMagicBaseMeta):
    """Metadata model for TIFF files."""

    _supported = {"image/tiff": []}  # Supported mimetype
    _allow_versions = True  # Allow any version

    @metadata()
    def version(self):
        """Return version."""
        if self.mimetype() not in self._supported:
            return None
        return "6.0"

    @metadata()
    def stream_type(self):
        """Return stream type."""
        return "image"
