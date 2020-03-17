"""Dummy scrapers."""
from __future__ import unicode_literals

import os.path

from file_scraper.base import BaseScraper
from file_scraper.utils import decode_path
from file_scraper.dummy.dummy_model import (
    DummyMeta, DetectedOfficeVersionMeta, DetectedTextVersionMeta,
    DetectedSpssVersionMeta, DetectedPdfaVersionMeta
)


class ScraperNotFound(BaseScraper):
    """Scraper for the case where scraper was not found."""

    def scrape_file(self):
        """No need to scrape anything, just collect."""
        self._errors.append("Proper scraper was not found. "
                            "The file was not analyzed.")
        self.streams.append(DummyMeta())

    @property
    def well_formed(self):
        """
        Academicly, well-formedness is not known and therefore result
        should be None. However, ScraperNotFound should always be unwanted
        output, and therefore we return False.
        """
        return False


class FileExists(BaseScraper):
    """Scraper for the case where file was not found."""

    def scrape_file(self):
        """Check if file exists."""
        if not self.filename:
            self._errors.append("No filename given.")
        elif os.path.isfile(self.filename):
            self._messages.append(
                "File {} was found.".format(decode_path(self.filename))
            )
        else:
            self._errors.append(
                "File {} does not exist.".format(decode_path(self.filename))
            )
        self.streams.append(DummyMeta())

    @property
    def well_formed(self):
        """
        Return False if there are errors, otherwise None.

        This is done as well-formedness of the file is not really known.
        """
        if self._errors:
            return False
        return None


class MimeScraper(BaseScraper):
    """
    Scraper to check if the predefined mimetype and version match with the
    resulted ones.
    """

    _MIME_DICT = {"application/gzip": ["application/warc",
                                       "application/x-internet-archive"]}
    _supported_metadata = [DummyMeta]

    def scrape_file(self):
        """
        No need to scrape anything, just compare already collected metadata.
        """
        self._messages.append("MIME type and file format version check")

        mime = self._params.get("mimetype", "(:unav)")
        ver = self._params.get("version", "(:unav)")
        pre_list = self._MIME_DICT.get(self._predefined_mimetype, [])

        if mime == "(:unav)":
            self._errors.append("File format is not supported.")
        elif mime != self._predefined_mimetype and mime not in pre_list:
            self._errors.append(
                "Predefined mimetype '{}' and resulted mimetype '{}' "
                "mismatch.".format(self._predefined_mimetype, mime))

        if self._predefined_version not in [ver, None]:
            self._errors.append(
                "Predefined version '{}' and resulted version '{}' "
                "mismatch.".format(self._predefined_version, ver))

        self.streams.append(DummyMeta())
        self._check_supported(allow_unav_mime=True,
                              allow_unav_version=True,
                              allow_unap_version=True)


class DetectedBinaryVersionScraper(BaseScraper):
    """
    Use the detected file format version for some file formats.
    Support in metadata scraping and well-formedness checking.
    """

    _supported_metadata = [DetectedOfficeVersionMeta]

    def scrape_file(self):
        """
        Enrich the metadata with the detected file format version for some
        file formats.
        """
        mimetype = self._params.get("detected_mimetype", self._predefined_mimetype)
        version = self._params.get("detected_version", "(:unav)")
        self._messages.append("Using detected file format version.")
        self.iterate_models(mimetype=mimetype, version=version)
        self._check_supported(allow_unav_mime=False, allow_unav_version=True,
                              allow_unap_version=True)


class DetectedMetaVersionScraper(DetectedBinaryVersionScraper):
    """
    Variation of DetectedOfficeVersionScraper for PDF files.
    Support only in metadata scraping.
    """

    _supported_metadata = [DetectedSpssVersionMeta,
                           DetectedTextVersionMeta,
                           DetectedPdfaVersionMeta]

    @classmethod
    def is_supported(cls, mimetype, version=None, check_wellformed=True,
                     params=None):  # pylint: disable=unused-argument
        """
        Support only when no checking of well-formedness is done.

        :mimetype: MIME type of a file
        :version: Version of a file. Defaults to None.
        :check_wellformed: True for scraping with well-formedness check, False
                           for skipping the check. Defaults to True.
        :params: None
        :returns: True if the MIME type and version are supported, False if not
        """
        if check_wellformed:
            return False
        return super(DetectedMetaVersionScraper, cls).is_supported(
            mimetype, version, check_wellformed, params)
