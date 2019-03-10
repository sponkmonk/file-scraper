"""Test the dpres_scraper.scrapers.pngcheck module"""
import pytest
from tests.scrapers.common import parse_results
from dpres_scraper.scrapers.pngcheck import Pngcheck


SUPPORT_MIME = 'image/png'


@pytest.mark.parametrize(
    ['filename', 'result_dict', 'validation'],
    [
        ('valid_1.2.png', {
            'purpose': 'Test valid file.',
            'stdout_part': 'OK',
            'stderr_part': ''}, True),
        ('invalid_1.2.png', {
            'purpose': 'Test corrupted file.',
            'stdout_part': '',
            'stderr_part': 'ERROR'}, True)
    ]
)
def test_scraper(filename, result_dict, validation):
    """Test scraper"""
    correct = parse_results(filename, SUPPORT_MIME,
                            result_dict, validation)
    scraper = Pngcheck(correct.filename, correct.mimetype,
                       validation, correct.params)
    scraper.scrape_file()
    correct.streams[0]['version'] = None

    assert scraper.mimetype == correct.mimetype
    assert scraper.version == None
    assert scraper.streams == correct.streams
    assert scraper.info['class'] == 'Pngcheck'
    assert correct.stdout_part in scraper.messages()
    assert correct.stderr_part in scraper.errors()
    assert scraper.well_formed == correct.well_formed

def test_is_supported():
    """Test is_Supported method"""
    mime = SUPPORT_MIME
    ver = '1.2'
    assert Pngcheck.is_supported(mime, ver, True)
    assert Pngcheck.is_supported(mime, None, True)
    assert not Pngcheck.is_supported(mime, ver, False)
    assert Pngcheck.is_supported(mime, 'foo', True)
    assert not Pngcheck.is_supported('foo', ver, True)
