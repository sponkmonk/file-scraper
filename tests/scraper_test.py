"""
Tests for main scraper.

This module tests that:
    - Monkeypatched is_textfile() returns True when scraper returns
      well-formed and False otherwise.
    - checksum() method returns correct checksums both using MD5 and SHA-1
      algorithms.
    - checksum() method raises ValueError when illegal algorithm is given.
    - checksum() method raises IOError when checksum calculation is attempted
      for a file that does not exist.
    - empty text files are not well-formed according to the scraper.
    - non-existent files are not well-formed according to the scraper.
    - giving None instead of a file name to the scraper results in successful
      scraping with a result of not well-formed.
    - file type detection without scraping works and respects the predefined
      file type if provided.
    - Character encoding detection works and respects the predefined file type
      if provided.
"""
from __future__ import unicode_literals

import pytest

from file_scraper.scraper import Scraper


def test_is_textfile():
    """Test that text files (and only text files) are identified as such."""
    textfiles = ["tests/data/text_plain/valid__ascii.txt",
                 "tests/data/text_plain/valid__iso8859.txt",
                 "tests/data/text_plain/valid__utf8_without_bom.txt"]
    binaryfiles = ["tests/data/text_plain/invalid__binary_data.txt",
                   "tests/data/image_png/valid_1.2.png",
                   "tests/data/application_pdf/valid_1.2.pdf"]
    for filename in textfiles:
        scraper = Scraper(filename)
        assert scraper.is_textfile()
    for filename in binaryfiles:
        scraper = Scraper(filename)
        assert scraper.is_textfile() is False


def test_checksum():
    """Test that checksum value of the file is returned."""
    scraper = Scraper("tests/data/text_plain/valid__utf8_without_bom.txt")
    assert scraper.checksum() == "b50b89c3fb5299713b7b272c1797a1e3"
    assert scraper.checksum("SHA-1") == \
        "92103972564bca86230dbfd311eec01f422cead7"
    with pytest.raises(ValueError):
        assert scraper.checksum("foo")
    with pytest.raises(IOError):
        scraper = Scraper("non_exists")
        assert scraper.checksum()


def test_empty_file():
    """Test empty file."""
    scraper = Scraper("test/data/text_plain/invalid__empty.txt")
    scraper.scrape()
    assert not scraper.well_formed


def test_missing_file():
    """Test missing file."""
    scraper = Scraper("missing_file", mimetype="application/pdf")
    scraper.scrape()
    assert not scraper.well_formed
    assert len(scraper.info) == 1 and scraper.info[0]["class"] == "FileExists"

    scraper = Scraper(None, mimetype="application/pdf")
    scraper.scrape()
    assert not scraper.well_formed
    assert len(scraper.info) == 1 and scraper.info[0]["class"] == "FileExists"


@pytest.mark.parametrize(
    ["filename", "params", "expected_results"],
    [
        ("tests/data/image_png/valid_1.2.png", {},
         {"_predefined_mimetype": "image/png", "_predefined_version": "1.0",
          "well_formed": None}),
        ("nonexistent_file", {},
         {"_predefined_mimetype": None, "_predefined_version": None,
          "well_formed": False}),
        ("tests/data/image_png/invalid_1.2_wrong_CRC.png", {},
         {"_predefined_mimetype": "image/png", "_predefined_version": "1.0",
          "well_formed": None}),
        ("tests/data/video_mp4/valid__h264_aac.mp4",
         {"mimetype": "video/mpeg"},
         {"_predefined_mimetype": "video/mpeg", "_predefined_version": None,
          "well_formed": None}),
        ("tests/data/application_pdf/valid_A-1a.pdf",
         {"mimetype": "application/pdf"},
         {"_predefined_mimetype": "application/pdf",
          "_predefined_version": "A-1a", "well_formed": None}),
        ("missing_file",
         {"mimetype": "application/pdf"},
         {"_predefined_mimetype": "application/pdf",
          "_predefined_version": None, "well_formed": False}),
    ]
)
def test_detect_filetype(filename, params, expected_results):
    """
    Test running only the filetype detection.

    This test ensures that the filetype detection fills in mimetype and version
    (if available from detectors) for the file, leaving well_formed and
    streams as None. Info should also contain some entries, but their contents
    are not checked.

    Then it is tested that the same results are also returned if full scraping
    is run before filetype detection.

    :filename: Test file name
    :params: Parameters for Scarper
    :expected_results: Expected results, containing expected values of Scraper
                       attributes
    """
    # Filetype detection should work without scraping
    scraper = Scraper(filename, **params)
    scraper.detect_filetype()
    for field, value in expected_results.items():
        assert getattr(scraper, field) == value
    assert scraper.streams is None
    assert scraper.info

    # Even if scraping has been done previously, detection should erase all
    # streams and other information
    scraper.scrape()
    scraper.detect_filetype()
    for field, value in expected_results.items():
        assert getattr(scraper, field) == value
    assert scraper.streams is None
    assert scraper.info


@pytest.mark.parametrize(
    "charset",
    [None, "UTF-8", "ISO-8859-15"]
)
def test_charset_parameter(charset):
    """
    Test charset parameter.
    In the test we have an UTF-8 file. If given charset is None, it will be
    detected as UTF-8. Otherwise, the parameter value is used.

    :charset: Given character encoding
    """
    scraper = Scraper("tests/data/text_plain/valid__utf8_without_bom.txt",
                      charset=charset)
    scraper.detect_filetype()
    # pylint: disable=protected-access
    assert scraper._params["charset"] in [charset, "UTF-8"]


@pytest.mark.parametrize(
    ("file_path", "expected_grade"),
    [
        # Recommended file format
        (
            "tests/data/text_plain/valid__ascii.txt",
            "fi-dpres-recommended-file-format"
        ),
        # File that does not exist
        (
            "/this/path/does/not/exist",
            "(:unav)"
        ),
        # Empty file
        (
            "tests/data/text_plain/invalid__empty.txt",
            "fi-dpres-unacceptable-file-format"
        ),
        # Format version not accepted according to specification
        (
            "tests/data/application_warc/valid_0.17.warc",
            "fi-dpres-unacceptable-file-format"
        ),
        # Recommended container file format
        (
            "tests/data/video_x-matroska/valid_4_ffv1_flac.mkv",
            "fi-dpres-recommended-file-format"
        ),
        # Acceptable container file format due to containing acceptable audio
        # and video streams
        (
            "tests/data/video_MP2T/valid__mpeg2_mp3.ts",
            "fi-dpres-acceptable-file-format"
        ),
    ]
)
def test_grade(file_path, expected_grade):
    """Test that scraper returns correct digital preservation grade."""
    scraper = Scraper(file_path)

    # File can not be graded before scraping
    assert scraper.grade() == "(:unav)"

    # After scraping the file should have expected grade
    scraper.scrape()
    assert scraper.grade() == expected_grade
