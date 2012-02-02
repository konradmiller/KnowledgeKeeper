import urllib
import xml.etree.ElementTree as et
#import settings
import sys
from orm.models import *
from feedwrapper import *

SHOWCITING_URL = """http://citeseerx.ist.psu.edu/showciting?doi=%s&sort=cite&feed=atom"""
SUMMARY_URL = """http://citeseerx.ist.psu.edu/viewdoc/summary?doi=%s&xml=true"""
SEARCH_URL = """http://citeseerx.ist.psu.edu/search?q=%s&sort=rlv&feed=atom"""

## see http://effbot.org/zone/element-rss-wrapper.htm
## for some comments about these wrappers
class ElementWrapper:
    def __init__(self, element, ns=None):
        self.element_ = element
        self.ns_ = ns or ""

    def __getattr__(self, tag):
        return self.element_.findtext(self.ns_ + tag)

class RSSWrapper(ElementWrapper):
    def __init__(self, channel, items, ns=None):
        self.items_ = items
        ElementWrapper.__init__(self, channel, ns)

    def __iter__(self):
        return iter([self[i] for i in range(len(self))])

    def __len__(self):
        return len(self.items_)

    def __getitem__(self, index):
        return ElementWrapper(self.items_[index], self.ns_)

class RSS2Wrapper(RSSWrapper):
    def __init__(self, feed):
        channel = feed.find("channel")
        RSSWrapper.__init__(
            self, channel, channel.findall("item")
            )

class AtomWrapper(RSSWrapper):
    def __init__(self, feed):
        ns = feed.tag[:feed.tag.index('}')+1]
        RSSWrapper.__init__(
            self, feed, feed.findall(ns + "entry"), ns
            )

def getfeed(url):
    tree = et.parse(urllib.urlopen(url))
    feed = tree.getroot()
    if feed.tag.endswith('feed'):
        return AtomWrapper(feed)
    if feed.tag == 'rss':
        return RSS2Wrapper(feed)

    raise IOError('unknown feed format')

class DoiFeed:
    def __init__(self, url_scheme):
        self.dois_ = []
        self.url_scheme_ = url_scheme.strip() + "&start=%d"
        self.max_len_ = -1

    def _extract_doi(self, url):
        url = url.strip()
        prefix = 'http://citeseerx.ist.psu.edu/document/'
        if not url.startswith(prefix):
            return None
        return url[len(prefix):]

    def retrieve(self, start = 0):
        feed = getfeed(self.url_scheme_ % start)
        if len(feed) == 0:
            if (self.max_len_ == -1) or (self.max_len_ > start):
                self.max_len_ = start
            return

        # extract dois from search results
        for entry in feed:
            doi = self._extract_doi(entry.id)
            if doi is not None:
                self.dois_.append(doi)

    def __iter__(self):
        i = 0
        while True:
            try: yield self[i]
            except: return
            i = i+1

    def __getitem__(self, index):
        while index >= len(self.dois_):
            if self.max_len_ >= 0 and index >= self.max_len_:
                raise IndexError
            self.retrieve(len(self.dois_))
        return self.dois_[index]
    
class Search(DoiFeed):
    def __init__(self, search_string):
        def fixup(s):
            return s.strip().replace(' ', '+')

        url_scheme = SEARCH_URL % fixup(search_string)
        DoiFeed.__init__(self, url_scheme)

class Citings(DoiFeed):
    def __init__(self, doi):
        url_scheme = SHOWCITING_URL % doi
        DoiFeed.__init__(self, url_scheme)


def fetch_document(doi):
    url = SUMMARY_URL % doi
    
    parser = et.XMLParser()
    parser.entity["nbsp"] = unichr(160)
    parser.entity["copy"] = unichr(169)
    xmldoc = et.parse(source=urllib.urlopen(url), parser=parser).getroot()
    citings = list(Citings(doi))

    document = CiteSeerDocument(
        doi = doi,
        title = xmldoc.findtext('title') or "",
        abstract = xmldoc.findtext('abstract') or "",
        year = int(xmldoc.findtext('year') or 0),
        clusterid = int(xmldoc.findtext('clusterid') or 0),
        citings = ';'.join(citings)
        )
    document.save()

    for author in xmldoc.findall('authors/author'):
        author_id = int(author.get('id'))
        a, created = CiteSeerAuthor.objects.get_or_create(id=author_id)
        if created:
            a.clusterid = int(author.findtext('clusterid'))
            a.name = author.findtext('name')
            a.save()
        else:
            name = author.findtext('name')
            clusterid = int(author.findtext('clusterid'))
            if a.name != name:
                print "Author name mismatch: ", a.name, name
            if a.clusterid != clusterid:
                print "Author clusterid mismatch", a.clusterid, clusterid
        document.authors.add(a)

    ## self.citations = []
    ## for citation in doc.findall('citations/citation'):
    ##     doi = citation.findtext('paperid')
    ##     id = int(citation.get('id'))
    ##     self.citations.append(Citation(doi, id))

    document.save()
    return document

def get_document(doi):
    try:
        doc = CiteSeerDocument.objects.get(doi=doi)
    except CiteSeerDocument.DoesNotExist:
        doc = fetch_document(doi)
    return doc

def getDocuments( searchterm, max ):
    s = Search( searchterm )
    res = []
    for i, doi in enumerate(s):
        if i == max: break
        doc = get_document(doi)
        res.append( doc )
    return res


if __name__ == '__main__':
    import sys
    res = getDocuments(sys.argv[1], 10)
    for doc in res:
        print doc
