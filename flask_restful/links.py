
class Link(object):

    def __init__(self, linked_resource_class, title = None, params = None):
        self.linked_resource = linked_resource_class
        self._title = title
        self.params = params

    @property
    def href(self):
        uri = self.linked_resource._self
        if self.params: # TODO: basic brutal impl handle the other cases
            uri = uri.format(**self.params) # FIXME it is probably not even secure
        return uri

    @property
    def title(self):
        return self._title

    @property
    def templated(self):
        return self.params is not None

    def to_dict(self):
        answer = {}
        if self.title:
            answer['title'] = self.title
        answer['href'] = self.href
        return answer