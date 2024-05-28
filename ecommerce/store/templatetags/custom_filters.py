import re
from django import template

register = template.Library()

@register.filter
def path_matches_pattern(path, pattern):
    return bool(re.match(pattern, path))