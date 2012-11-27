from flask_restful.utils import hal

class Link(object):

    def __init__(self, linked_resource_class, title = None, params = None):
        self.linked_resource = linked_resource_class
        self._title = title
        self.params = params

    @property
    def title(self):
        return self._title

    @property
    def templated(self):
        return False

    def to_dict(self, additional_context = None):
        if not additional_context:
            additional_context = {}
        context = dict(self.params.items() + additional_context.items()) if self.params else additional_context
        response = {'href': hal(self.linked_resource._self, context)}
        if self.title:
            response['title'] = self.title
        return response

class Embed(object):
    def __init__(self, linked_resource_class, get_parameters = None):
        self.linked_resource = linked_resource_class
        self.params = get_parameters if get_parameters is not None else {}

    def to_dict(self):
        """
        Emulate a rendering from flask for the embedding
        :return: the dictionary to embed in the response
        """
        return self.linked_resource().get(**self.params)

