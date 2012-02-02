import xml.etree.ElementTree as et

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
