import scrapy
import re

from wikicrawler.items import WikicrawlerItem

base_url = "https://en.wikipedia.org"


class WikiSpider(scrapy.Spider):

    # the start of every search
    random_article_url = "https://en.wikipedia.org/wiki/Special:Random"
    # a dictionary will map each path root to the list of visited pages
    visited_urls_in_path = {}

    name = "wikiSpider"
    allowed_domains = ["wikipedia.org"]
    start_urls = [random_article_url] * 500

    # used for extracting the href tag via regex
    pattern = r'(?<=<a href=")/wiki/[a-zA-Z\(\)\-\,_#]*?(?=")'

    def parse(self, response):

        path_root = response.meta.get('path_root_url')

        doc_text_list = response.xpath("//div[@id = 'mw-content-text']/p").extract()
        href = ''

        # find links in main body paragraphs
        for doc_text in doc_text_list:
            clean_text = remove_paren(doc_text.encode('utf8'))
            match = re.search(self.pattern, clean_text)
            if match:
                # some pages link to a section within themselves - this catches that behavior
                href = match.group(0).split('#')[0]
                break

        # sometimes there are links in pages without paragraphs, only lists
        if href == '':
            doc_text = ''.join(response.xpath("//div[@id = 'mw-content-text']/li").extract())
            clean_text = remove_paren(doc_text.encode('utf8'))
            match = re.search(self.pattern, clean_text)
            if match:
                # some pages link to a section within themselves - this catches that behavior
                href = match.group(0).split('#')[0]

        # if no link is found we have reached a dead end
        if href == '':
            item = WikicrawlerItem()
            item['path_root'] = path_root
            item['depth'] = -1
            item['status'] = 'dead end'
            yield item
            return

        next_page_url = base_url + str(href)
        current_depth = response.meta['depth']

        # if a page links to another page in its path or to itself we have found a cycle
        if next_page_url in self.visited_urls_in_path[path_root] or next_page_url == response.url:
            item = WikicrawlerItem()
            item['path_root'] = path_root
            item['depth'] = -1
            item['status'] = 'cycle'
            yield item

        # if the next page is philosophy there is no need to request it - it marks the end of our search
        elif href == "/wiki/Philosophy":
            # we are at the end of our search - report the depth of the root page from the philosophy page
            item = WikicrawlerItem()
            item['path_root'] = path_root
            item['depth'] = current_depth + 1
            item['status'] = 'success'
            yield item

        # if no other conditions are met, there is another page to visit
        else:
            yield scrapy.Request(next_page_url, callback=self.parse)


# removes all body text within parentheses (while ignoring parentheses within tags) from page text
def remove_paren(html):
    paren_count = 0
    bracket_count = 0
    cleaned_string = ""
    for c in html:
        if c == '<':
            bracket_count += 1
        elif c == '>':
            bracket_count -= 1
        elif c == '(' and bracket_count == 0:
            paren_count += 1
        elif c == ')' and bracket_count == 0:
            paren_count -= 1
            continue
        if paren_count == 0:
            cleaned_string += c
    return cleaned_string

