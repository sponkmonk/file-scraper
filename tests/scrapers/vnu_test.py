"""
Tests for Vnu scraper.
"""
import pytest
from dpres_scraper.scrapers.vnu import Vnu
from tests.scrapers.common import parse_results


MIMETYPE = 'text/html'


@pytest.mark.parametrize(
    ['filename', 'result_dict'],
    [
        ('valid_5.0.html', {
            'purpose': 'Test valid file.',
            'stdout_part': 'valid_5.0.html',
            'stderr_part': ''})
    ]
)
def test_scraper(filename, result_dict):
    """Test scraper"""
    correct = parse_results(filename, MIMETYPE,
                            result_dict, True)
    scraper = Vnu(correct.filename, correct.mimetype,
                  True, correct.params)
    scraper.scrape_file()

    assert scraper.mimetype == correct.mimetype
    assert scraper.version == correct.version
    assert scraper.streams == correct.streams
    assert scraper.info['class'] == 'Vnu'
    assert correct.stdout_part in scraper.messages()
    assert correct.stderr_part in scraper.errors()
    assert scraper.well_formed == correct.well_formed

def test_is_supported():
    """Test is_Supported method"""
    mime = MIMETYPE
    ver = '5.0'
    assert Vnu.is_supported(mime, ver, True)
    assert Vnu.is_supported(mime, None, True)
    assert not Vnu.is_supported(mime, ver, False)
    assert not Vnu.is_supported(mime, 'foo', True)
    assert not Vnu.is_supported('foo', ver, True)
