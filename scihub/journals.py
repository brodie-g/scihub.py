import time
from typing import List, Dict
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from scihub.scihub import SciHub, CaptchaNeedException

HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:27.0) Gecko/20100101 Firefox/27.0'}


class JournalFetcher:

    def __init__(self):
        self.sess = requests.Session()
        self.sess.headers = HEADERS

    def _get_html(self, url: str):
        resp = self.sess.get(url)
        if resp.ok:
            print(resp.text)
            return resp.text
        else:
            print("Boo! {}".format(resp.status_code))
            print(resp.text)

    def _get_soup(self, html: str) -> BeautifulSoup:
        """
        Return html soup.
        """
        return BeautifulSoup(html, 'html.parser')


class ScienceDirectJournalFetcher(JournalFetcher):

    def __init__(self):
        super().__init__()
        self.scihub = SciHub()

    def get_journal_issue_article_urls(self, url: str) -> List[Dict[str, str]]:
        html = self._get_html(url)

        # find all article links in the html
        soup = self._get_soup(html)

        journal_title = soup.select('#journal-title span')[0].string.lower().replace(' ', '-')

        volume_text = soup.select('.js-vol-issue')[0].string.lower().replace(' ', '-')

        articles_content = soup.select('.article-content')
        articles = []
        for ac in articles_content:
            article_anchor = ac.select('a.article-content-title')[0]
            article_url = urljoin(url, article_anchor.get('href'))

            # article_title = article_anchor.select('.js-article-title')[0]
            # article_title_text = article_title.string.lower().replace(' ', '-')

            article_page_range = ac.select('.js-article-page-range')[0]
            article_page_range_text = article_page_range.string.lower().replace(' ', '-')

            filename = f'{journal_title}-{volume_text}-{article_page_range_text}.pdf'

            articles.append({
                'url': article_url,
                'filename': filename
            })

        return articles

    def get_journal_issue(self,
                          url: str,
                          destination: str = None,
                          return_val=False):
        articles_data = []
        # get all article links from the issue
        articles = self.get_journal_issue_article_urls(url)
        print(articles)
        articles_len = len(articles)
        process_num = 0

        # fetch and download all the articles via scihub
        for article in articles:
            try:
                process_num += 1
                print(f'Getting scihub article {process_num} of {articles_len} for {article}')
                scihub_article_data = self.scihub.download(article['url'],
                                                           destination=destination,
                                                           path=article['filename'])
                if 'err' in scihub_article_data:
                    print(scihub_article_data['err'])
                else:
                    articles_data.append(scihub_article_data)
            except CaptchaNeedException as e:
                print(str(e))
            except Exception as e:
                print(str(e))
            time.sleep(.25)

        print('Finished fetching issue')

        if return_val:
            return articles_data
