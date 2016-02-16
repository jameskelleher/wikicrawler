# wikicrawler

The goal of the project was to write a web scraper that started on random Wikipedia pages and continuously clicked on the first link that wasn't italicized or in parentheses until the page on Philosophy was reached. I then answered the following questions:

- What percentage of pages eventually lead to philosophy? 
- What is the distribution of path lengths for 500 random pages, ignoring those paths that never reach the Philosophy page? 
- How can you reduce the number of http requests necessary for 500 random starting pages?

Just a quick overview on the scraper itself:

- I've written the answers to the specific questions in a file called 'result.txt'. If you want to just see my responses, that's the place to go.
- You need to have scrapy and matplotlib installed before running
- To run the web crawlers / perform the analyses, all you need to do is run the script titled 'main.py'
