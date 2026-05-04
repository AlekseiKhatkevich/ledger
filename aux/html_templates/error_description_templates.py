from functools import cached_property
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape

class TemplateRenderer:

    @cached_property
    def env(self):
        return Environment(
            loader=FileSystemLoader('site/error-descriptions/templates'),
            autoescape=select_autoescape(('html',)),
        )