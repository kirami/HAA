from django import template

import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(str(key))

