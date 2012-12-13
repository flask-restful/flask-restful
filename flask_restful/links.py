from flask.ext.restful.utils import rest_url_for

class Link(object):
    def __init__(self, title=None):
        self._title = title

    @property
    def title(self):
        return self._title

    @property
    def templated(self):
        return False


class ResourceLink(Link):
    def __init__(self, linked_resource_class, title=None, params=None):
        super(ResourceLink, self).__init__(title=title)
        self.linked_resource = linked_resource_class
        self.params = params


    def to_dict(self, additional_context=None):
        if not additional_context:
            additional_context = {}
        context = dict(self.params.items() + additional_context.items()) if self.params else additional_context
        response = {'href': rest_url_for(self.linked_resource._endpoint, **context)}
        if self.title:
            response['title'] = self.title
        return response

class PlainLink(Link):
    def __init__(self, url, title=None):
        super(PlainLink, self).__init__(title=title)
        self.url = url

    def to_dict(self, additional_context=None):
        response = {'href': self.url}
        if self.title:
            response['title'] = self.title
        return response


class Embed(object):
    def __init__(self, linked_resource_class, params=None):
        """
        :param linked_resource_class:
        :param params: the parameters used for calling the get function of the embedded LinkedResource
        :return:
        """
        self.linked_resource = linked_resource_class
        self.params = params if params is not None else {}

    def to_dict(self):
        """
        Emulate a rendering from flask for the embedding
        :return: the dictionary to embed in the response
        """
        return self.linked_resource().get(**self.params)

