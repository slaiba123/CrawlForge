import pytest
from unittest.mock import patch, MagicMock
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def test_scrape_url_returns_text():
    """scrape_url should return a non-empty string for a valid URL."""
    from tools import scrape_url
    result = scrape_url.invoke("https://en.wikipedia.org/wiki/Artificial_intelligence")
    assert isinstance(result, str)
    assert len(result) > 100


def test_scrape_url_handles_bad_url():
    """scrape_url should return an error string, not raise an exception."""
    from tools import scrape_url
    result = scrape_url.invoke("https://this-url-does-not-exist-xyz.com")
    assert isinstance(result, str)
    assert "Could not scrape" in result


def test_web_search_returns_results():
    """web_search should return formatted results string."""
    from tools import web_search
    result = web_search.invoke("Python programming language")
    assert isinstance(result, str)
    assert "Title:" in result
    assert "URL:" in result


def test_writer_chain_returns_output():
    """writer_chain should return a non-empty report string."""
    from agents import writer_chain
    result = writer_chain.invoke({
        "topic": "artificial intelligence",
        "research": "AI is the simulation of human intelligence by machines."
    })
    assert isinstance(result, str)
    assert len(result) > 100


def test_critic_chain_returns_score():
    """critic_chain should return output containing a score."""
    from agents import critic_chain
    result = critic_chain.invoke({
        "report": "This is a test report about AI. It covers key findings and conclusions."
    })
    assert isinstance(result, str)
    assert "Score" in result or "score" in result