"""
TwitScraper

Scraping twatter
"""

from importlib.metadata import version

__version__ = version(__package__)

from .scraper import Tweeter
