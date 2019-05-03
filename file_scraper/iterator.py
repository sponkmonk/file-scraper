"""Scraper iterator."""
# flake8: noqa
# pylint:disable=unused-import

# old imports stored temporarily
#from file_scraper.base import BaseScraper
#from file_scraper.jhove_base import JHove
#from file_scraper.magic_base import BinaryMagic, TextMagic
#from file_scraper.mediainfo_base import Mediainfo
#from file_scraper.pil_base import Pil
#from file_scraper.scrapers.jhove import GifJHove, HtmlJHove, JpegJHove, \
#    PdfJHove, TiffJHove, Utf8JHove, WavJHove
#from file_scraper.scrapers.xmllint import Xmllint
#from file_scraper.scrapers.lxml_encoding import XmlEncoding
#from file_scraper.scrapers.warctools import GzipWarctools, WarcWarctools, \
#    ArcWarctools
#from file_scraper.scrapers.ghostscript import GhostScript
#from file_scraper.scrapers.pngcheck import Pngcheck
#from file_scraper.scrapers.csv_scraper import Csv
#from file_scraper.scrapers.mediainfo import MpegMediainfo, WavMediainfo
#from file_scraper.scrapers.ffmpeg import FFMpegWellformed
#from file_scraper.scrapers.office import Office
#from file_scraper.scrapers.magic import TextFileMagic, XmlFileMagic, \
#    HtmlFileMagic, PdfFileMagic, OfficeFileMagic, PngFileMagic, \
#    JpegFileMagic, Jp2FileMagic, TiffFileMagic, XhtmlFileMagic, \
#    ArcFileMagic
#from file_scraper.scrapers.wand import TiffWand, ImageWand
#from file_scraper.scrapers.pil import ImagePil, JpegPil, TiffPil
#from file_scraper.scrapers.pspp import Pspp
#from file_scraper.scrapers.verapdf import VeraPdf
#from file_scraper.scrapers.dpx import Dpx
#from file_scraper.scrapers.vnu import Vnu
#from file_scraper.scrapers.dummy import ScraperNotFound

from file_scraper.detectors import FidoDetector, MagicDetector
from file_scraper.csv.csv_scraper import CsvScraper
from file_scraper.dummy.dummy_scraper import ScraperNotFound
from file_scraper.ffmpeg.ffmpeg_scraper import FFMpegScraper
from file_scraper.jhove.jhove_scraper import (JHoveGifScraper, JHoveHtmlScraper,
                                              JHoveJpegScraper, JHoveTiffScraper,
                                              JHovePdfScraper, JHoveWavScraper)
from file_scraper.lxml.lxml_scraper import LxmlScraper
from file_scraper.mediainfo.mediainfo_scraper import MediainfoScraper
from file_scraper.magic_scraper.magic_scraper import MagicScraper
from file_scraper.office.office_scraper import OfficeScraper
from file_scraper.pil.pil_scraper import PilScraper
from file_scraper.pngcheck.pngcheck_scraper import PngcheckScraper
from file_scraper.pspp.pspp_scraper import PsppScraper
from file_scraper.schematron.schematron_scraper import SchematronScraper
from file_scraper.textfile.textfile_scraper import TextfileScraper
from file_scraper.verapdf.verapdf_scraper import VerapdfScraper
from file_scraper.vnu.vnu_scraper import VnuScraper
from file_scraper.wand.wand_scraper import WandScraper
from file_scraper.ghostscript.ghostscript_scraper import GhostscriptScraper
from file_scraper.xmllint.xmllint_scraper import XmllintScraper
from file_scraper.warctools.warctools_scraper import (GzipWarctoolsScraper,
                                                      WarcWarctoolsScraper,
                                                      ArcWarctoolsScraper)

def iter_detectors():
    """
    Iterate detectors.

    We want to keep the detectors in ordered list.
    :returns: detector class
    """
    for cls in [FidoDetector, MagicDetector]:
        yield cls


def iter_scrapers(mimetype, version, check_wellformed=True, params=None):
    """
    Iterate scrapers.

    :mimetype: Identified mimetype of the file
    :version: Identified file format version
    :check_wellformed: True for the full well-formed check, False for just
                       identification and metadata scraping
    :params: Extra parameters needed for the scraper
    :returns: scraper class
    """
    scraper_found = False

    scrapers = [WandScraper, GhostscriptScraper, JHoveGifScraper,
                JHoveHtmlScraper, JHoveJpegScraper, JHoveTiffScraper,
                JHovePdfScraper, JHoveWavScraper, CsvScraper, FFMpegScraper,
                LxmlScraper, MediainfoScraper, OfficeScraper, PilScraper,
                PngcheckScraper, PsppScraper, SchematronScraper, TextfileScraper,
                VerapdfScraper, VnuScraper, XmllintScraper, GzipWarctoolsScraper,
                WarcWarctoolsScraper, ArcWarctoolsScraper, MagicScraper]

    for scraper in scrapers:
        if scraper.is_supported(mimetype, version, check_wellformed, params):
            scraper_found = True
            yield scraper

    if not scraper_found:
        yield ScraperNotFound

    # TODO This old iterator can be reinstated when all scrapers are compatible
    #      with the new design.
#    # pylint: disable=no-member
#    if params is None:
#        params = {}
#    found_scraper = False
#
#    scraper_superclasses = [BaseScraper, BinaryMagic, TextMagic, JHove,
#                            Mediainfo, Pil, Wand]
#    for superclass in scraper_superclasses:
#        for cls in superclass.__subclasses__():
#            if cls.is_supported(mimetype, version, check_wellformed, params):
#                found_scraper = True
#                yield cls
#
#    if not found_scraper:
#        yield ScraperNotFound
