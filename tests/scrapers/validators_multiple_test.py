"""
Tests office-file scraping with combination of Office-scraper and
File-scraper.

This module tests that:
    - For a well-formed odt file, all scrapers supporting
      application/vnd.oasis.opendocument.text version 1.1 report it as
      well-formed or None.
    - For a corrupted odt file, at least one scraper supporting
      application/vnd.oasis.opendocument.text reports it as not well-formed.
    - When a valid odt file is scraped with scrapers selected using wrong MIME
      type (application/msword) at least one of them reports it as not well-
      formed.
"""
from __future__ import unicode_literals

import os
import pytest
from file_scraper.iterator import iter_scrapers

BASEPATH = "tests/data"


# Test valid file
@pytest.mark.parametrize(
    ['filename', 'mimetype'],
    [
        ("valid_1.1.odt", "application/vnd.oasis.opendocument.text"),
    ]
)
def test_scrape_valid_file(filename, mimetype):
    """
    Test scraping for a well-formed odt file.

    :filename: Test file name
    :mimetype: File MIME type
    """
    for class_ in iter_scrapers(mimetype, None):
        scraper = class_(
            filename=os.path.join(BASEPATH, mimetype.replace('/', '_'),
                                  filename),
            mimetype=mimetype)
        scraper.scrape_file()
        assert scraper.well_formed in [True, None]


# Test invalid files
@pytest.mark.parametrize(
    ['filename', 'mimetype'],
    [
        # Corrupted file - caught by Office scraper
        ("ODF_Text_Document_corrupted.odt",
         "application/vnd.oasis.opendocument.text"),
        # Wrong MIME - caught by File scraper
        ("valid_1.1.odt", "application/msword"),
    ]
)
def test_scrape_invalid_file(filename, mimetype):
    """
    Test scraping for invalid files.

    :filename: Test file name
    :mimetype: File MIME type
    """
    scraper_results = []
    for class_ in iter_scrapers(mimetype, None):
        scraper = class_(
            filename=os.path.join(
                BASEPATH, "application_vnd.oasis.opendocument.text", filename),
            mimetype=mimetype)
        scraper_results.append(scraper.well_formed)

    assert not all(scraper_results)
    assert scraper_results
