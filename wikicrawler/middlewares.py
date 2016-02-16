import logging

from scrapy.http import Request
from scrapy.spidermiddlewares.depth import DepthMiddleware

logger = logging.getLogger(__name__)


# this class is needed to pass the path's root page from response to request
# it also maintains the dictionary that maps each root page to its list of paths urls
class PathRootUrlMiddleware(object):

    rootKey = 'path_root_url'

    def process_spider_output(self, response, result, spider):
        def _filter(request):
            if isinstance(request, Request):
                stored_path_root = response.meta.get(self.rootKey)
                request.meta[self.rootKey] = stored_path_root
                spider.visited_urls_in_path[stored_path_root].append(response.url)
            return True

        if self.rootKey not in response.meta:
            path_root = response.url
            response.meta[self.rootKey] = path_root
            spider.visited_urls_in_path[path_root] = []

        return (r for r in result or () if _filter(r))


# this class is used to report the depth, while not counting the first step
# i.e. from the random link to the first actual page
# the only change from the default depth middleware is the added condition 'and response.url != random_url'
class IgnoreRandomDepthMiddleware(DepthMiddleware):

    def process_spider_output(self, response, result, spider):
        def _filter(request):
            if isinstance(request, Request):
                depth = response.meta['depth'] + 1
                request.meta['depth'] = depth
                if self.prio:
                    request.priority -= depth * self.prio
                if self.maxdepth and depth > self.maxdepth:
                    logger.debug("Ignoring link (depth > %(maxdepth)d): %(requrl)s ",
                                 {'maxdepth': self.maxdepth, 'requrl': request.url},
                                 extra={'spider': spider})
                    return False
                elif self.stats:
                    if self.verbose_stats:
                        self.stats.inc_value('request_depth_count/%s' % depth, spider=spider)
                    self.stats.max_value('request_depth_max', depth, spider=spider)
            return True

        random_url = "https://en.wikipedia.org/wiki/Special:Random"

        # base case (depth=0)
        if self.stats and 'depth' not in response.meta and response.url != random_url:
            response.meta['depth'] = 0
            if self.verbose_stats:
                self.stats.inc_value('request_depth_count/0', spider=spider)

        return (r for r in result or () if _filter(r))