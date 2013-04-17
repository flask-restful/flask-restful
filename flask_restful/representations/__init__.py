try:
    #noinspection PyUnresolvedReferences
    from collections import OrderedDict
except ImportError:
    from flask.ext.restful.utils import OrderedDict

import inspect
import urllib
import re


def hyperlinker(resource_self, verb_self, result, hal_context):
    from flask.ext.restful.utils import rest_url_for
    from flask.ext.restful.links import PlainLink

    base_url = rest_url_for(resource_self._endpoint, **hal_context)
    links = {'self': {'href': base_url}}
    links_desc = verb_self.links
    if verb_self.paging:
        result, paging_info, result_size = result
        for url_param in re.search(r"<([A-Za-z0-9_]+)>", resource_self._self).groups():  # FIXME this won't work with more complex flask descriptions
            del (paging_info[url_param])
        for name, value in dict(paging_info).iteritems():
            if value is None:
                del (paging_info[name])
        links['next'] = PlainLink(base_url + '?' + urllib.urlencode(paging_info), "Next results")
        links_desc = dict(links_desc.items() + [('next', resource_self.__class__)])

    result['_links'] = links

    return halmarshal(result, verb_self.fields, links_desc, hal_context)


def halmarshal(data, fields, links=None, hal_context=None):
    from flask.ext.restful import LinkedResource
    from flask.ext.restful.links import ResourceLink

    def make(cls):
        if isinstance(cls, type):
            return cls()
        return cls

    if isinstance(data, (list, tuple)):
        return [halmarshal(d, fields) for d in data]

    # handle the magic JSON HAL sections
    items = []
    embedded = []
    for k, v in fields.items():
        if inspect.isclass(v) and issubclass(v, LinkedResource):  # this is the special case of embedded resources
            embedded.append((k, data[k].to_dict()))
        elif isinstance(v, list) and inspect.isclass(v[0]) and issubclass(v[0], LinkedResource):  # an array of resources
            embedded.append((k, [resource.to_dict() for resource in data[k]]))
        elif isinstance(v, dict):
            items.append((k, halmarshal(data, v)))  # recursively go down the dictionaries
        else:
            items.append((k, make(v).output(k, data)))  # normal field output

    if '_links' in data and links is not None:
        ls = data['_links'].items()  # preset links like self
        for link_key, link_value in links.items():
            if inspect.isclass(link_value) and issubclass(link_value, LinkedResource):  # simple straigh linked resource
                if link_key in data:  # it means we specified a value for this link in the output
                    ls.append((link_key, data[link_key].to_dict(hal_context)))
                elif link_key in data['_links']:  # it means we specified a value for this link in the output as a link
                    ls.append((link_key, data['_links'][link_key].to_dict(hal_context)))
                else:  # We need to autogenerate one from the signature as it is not specified
                    ls.append((link_key, ResourceLink(link_value).to_dict(hal_context)))
            elif isinstance(link_value, list):  # an array of resources
                list_of_links = [link_obj.to_dict(hal_context) for link_obj in data[link_key]]
                ls.append((link_key, list_of_links))

        items = [('_links', dict(ls))] + items

    if embedded:
        items.append(('_embedded', OrderedDict(embedded)))

    return OrderedDict(items)



def simple(resource_self, verb_self, result, hal_context):
    from flask.ext.restful.utils import rest_url_for

    base_url = rest_url_for(resource_self._endpoint, **hal_context)
    if verb_self.paging:
        result, paging_info, result_size = result
        for url_param in re.search(r"<([A-Za-z0-9_]+)>", resource_self._self).groups():  # FIXME this won't work with more complex flask descriptions
            del (paging_info[url_param])
        for name, value in dict(paging_info).iteritems():
            if value is None:
                del (paging_info[name])
        result['next'] = base_url + '?' + urllib.urlencode(paging_info)

    return simplemarshal(result, verb_self.fields)



def simplemarshal(data, fields):
    from flask.ext.restful import LinkedResource

    def make(cls):
        if isinstance(cls, type):
            return cls()
        return cls

    if isinstance(data, (list, tuple)):
        return [simplemarshal(d, fields) for d in data]

    items = []
    embedded = []
    for k, v in fields.items():
        if inspect.isclass(v) and issubclass(v, LinkedResource):  # this is the special case of embedded resources
            embedded.append((k, data[k].to_dict()))
        elif isinstance(v, list) and inspect.isclass(v[0]) and issubclass(v[0], LinkedResource):  # an array of resources
            embedded.append((k, [resource.to_dict() for resource in data[k]]))
        elif isinstance(v, dict):
            items.append((k, simplemarshal(data, v)))  # recursively go down the dictionaries
        else:
            items.append((k, make(v).output(k, data)))  # normal field output

    return OrderedDict(items)
