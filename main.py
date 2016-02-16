# This is the script the both initiates the web crawlers and processes the retrieved data

import json

import matplotlib.pyplot as plt

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from wikicrawler.spiders.wikispider import WikiSpider

# crawl the web
# at the end of this process, a file 'items.json' will be generated
process = CrawlerProcess(get_project_settings())
process.crawl(WikiSpider)
process.start()

# process the data
with open('items.json') as item_file:
    items = json.load(item_file)

path_lengths = []

for item in items:
    if item['status'] == 'success':
        path_lengths.append(int(item['depth']))

success_count = len(path_lengths)
success_pct = (float(success_count) / len(items)) * 100
avg_path_len = float(sum(path_lengths)) / len(path_lengths)

path_length_dict = {}

for l in path_lengths:
    if l not in path_length_dict:
        path_length_dict[l] = 1
    else:
        path_length_dict[l] += 1

distribution_explanation = '''
The distribution appears to be bimodal, with the first mode located approx at 9 and the second approx at 15/16
'''

reduction_explanation = '''
One way to greatly reduce the number of http requests necessary is to check to see if the current page has been visited
in another path. Given that the crawling behavior is purely deterministic, any path that overlaps with another will have
the same outcome as that other path. So, if path A reaches a page P that has been crawled in another path B, we need
only to add the path length from A-P to the path length from P-Philosophy (or, if B becomes a cycle/dead end, report
that A will as well). The upside is that we do save a large number or HTTP requests; as there are only about 8 pages
one link away from Philosophy, this technique will immediately reduce about 490 HTTP requests in that last step alone.
The downside is that we must track the path length to Philosophy for each of these intermediate pages. Since the average
path length is %s, we must now store data for about an additional %s pages.
''' % (avg_path_len, int((avg_path_len - 1) * 500))

# write the results to a text file so that they are easily accessible
with open('result.txt', 'wb') as result_file:
    result_file.write('There were ' + str(success_count) + ' successful paths\n')
    result_file.write('Approximately ' + str(success_pct) + '% of pages will eventually lead to Philosophy\n')
    result_file.write('Average path length: ' + str(avg_path_len) + '\n')
    result_file.write('Path Length Distribution: ' + str(path_length_dict) + '\n')
    result_file.write(distribution_explanation)
    result_file.write(reduction_explanation)

# plot the distribution of path lengths
xaxis = []
yaxis = []

for path_length in path_length_dict.keys():
    xaxis.append(path_length)
    yaxis.append(path_length_dict[path_length])

plt.bar(xaxis, yaxis, align='center')
plt.xlabel('Path Length')
plt.ylabel('Frequency')
plt.title('Frequency of Path Lengths to the Philosophy Page')
plt.savefig('fig.png')
