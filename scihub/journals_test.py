import pytest


def test_get_journal_issue():
    from scihub.journals import ScienceDirectJournalFetcher

    issue_url = 'https://www.sciencedirect.com/journal/ecological-economics/vol/173'

    journal_fetcher = ScienceDirectJournalFetcher()

    journal_fetcher.get_journal_issue(issue_url, destination='downloads/173')

    assert True
