from django import template
from django.contrib.staticfiles import finders
from django.core.cache import cache
from django.utils.safestring import mark_safe

from web.finders import AngularTemplateFinder

register = template.Library()

_T = '<script type="text/ng-template" id="/static/{}">{}</script>'


@register.simple_tag
def cached_angular_template(path):
    """Load a template from cache or from a file.

    Cache the file if not in cache.

    :param path: Relative path to angular template
    :type path: str
    :returns: Rendering of script type="text/ng-template" element
    :rtype: str
    """
    # Check from cache first
    key = '_angular_template_{}'.format(path)
    html = cache.get(key)
    # If not found, read from file then cache
    if not html:
        paths = []
        for finder in finders.get_finders():
            paths += finder.find(path, True)
        with open(paths[-1], 'r') as file:
            html = file.read()
        html = _T.format(path, html)
        cache.set(key, html)
    # Mark value as safe
    return mark_safe(html)


@register.simple_tag
def cached_angular_templates():
    """Loads all found angular templates and concatenates them together.

    :returns: Rendering of all angular templates
    :rtype: str
    """
    html = []
    atf = AngularTemplateFinder()
    for path, _ in atf.list(None):
        html.append(cached_angular_template(path))
    return mark_safe("\n".join(html))
