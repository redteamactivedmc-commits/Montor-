"""
test_utils.py
-------------
Basic unit tests for utility functions.
"""

import unittest
from datetime import datetime

from media_monitor.utils import (
    extract_domain,
    lookup_outlet,
    parse_date,
    pct,
    truncate,
    number_fmt,
    estimate_impressions,
)


class TestDateParsing(unittest.TestCase):
    def test_parse_iso_date(self):
        dt = parse_date("2026-03-24")
        self.assertIsNotNone(dt)
        self.assertEqual(dt.year, 2026)
        self.assertEqual(dt.month, 3)
        self.assertEqual(dt.day, 24)

    def test_parse_long_date(self):
        dt = parse_date("March 24, 2026")
        self.assertIsNotNone(dt)
        self.assertEqual(dt.year, 2026)

    def test_parse_invalid(self):
        dt = parse_date("invalid date")
        self.assertIsNone(dt)


class TestDomainExtraction(unittest.TestCase):
    def test_extract_basic(self):
        domain = extract_domain("https://www.gulfnews.com/article/123")
        self.assertEqual(domain, "gulfnews.com")

    def test_extract_no_www(self):
        domain = extract_domain("https://arabianbusiness.com/news")
        self.assertEqual(domain, "arabianbusiness.com")

    def test_extract_http(self):
        domain = extract_domain("http://itp.net/story")
        self.assertEqual(domain, "itp.net")


class TestOutletLookup(unittest.TestCase):
    def test_lookup_known_outlet(self):
        outlet = lookup_outlet("gulfnews.com")
        self.assertEqual(outlet["name"], "Gulf News")
        self.assertEqual(outlet["tier"], "Tier 1")
        self.assertEqual(outlet["market"], "UAE")

    def test_lookup_unknown_outlet(self):
        outlet = lookup_outlet("unknown-site.com")
        self.assertEqual(outlet["tier"], "Unknown")
        self.assertEqual(outlet["market"], "Unknown")

    def test_lookup_with_www(self):
        outlet = lookup_outlet("www.arabianbusiness.com")
        self.assertEqual(outlet["name"], "Arabian Business")


class TestFormatting(unittest.TestCase):
    def test_truncate(self):
        text = "This is a very long text that should be truncated"
        result = truncate(text, max_len=20)
        self.assertLessEqual(len(result), 20)
        self.assertIn("…", result)

    def test_truncate_short(self):
        text = "Short"
        result = truncate(text, max_len=20)
        self.assertEqual(result, "Short")

    def test_pct(self):
        self.assertEqual(pct(0.5), "50%")
        self.assertEqual(pct(0.0), "0%")
        self.assertEqual(pct(1.0), "100%")

    def test_number_fmt(self):
        self.assertEqual(number_fmt(1000), "1,000")
        self.assertEqual(number_fmt(1000000), "1,000,000")
        self.assertEqual(number_fmt(0), "0")


class TestImpressionEstimator(unittest.TestCase):
    def test_estimate_news(self):
        impressions = estimate_impressions(100000, "news")
        self.assertEqual(impressions, 1500)  # 1.5%

    def test_estimate_feature(self):
        impressions = estimate_impressions(100000, "feature")
        self.assertEqual(impressions, 2500)  # 2.5%

    def test_estimate_exclusive(self):
        impressions = estimate_impressions(100000, "exclusive")
        self.assertEqual(impressions, 4000)  # 4.0%


if __name__ == "__main__":
    unittest.main()
