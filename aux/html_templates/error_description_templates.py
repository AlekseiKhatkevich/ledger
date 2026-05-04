#!/usr/bin/env -S uv run

from dataclasses import asdict
from functools import cached_property

from jinja2 import Environment, FileSystemLoader, select_autoescape
from jinja2.environment import TemplateStream

from aux.html_templates.error_descriptions_data import ErrorDescriptionData, registered_error_description_data


class TemplateRenderer:

    @cached_property
    def env(self) -> Environment:
        return Environment(
            loader=FileSystemLoader('site/error-descriptions/templates'),
            autoescape=select_autoescape(('jinja',)),
        )

    def render_one(self, data: ErrorDescriptionData) -> TemplateStream:
        template = self.env.get_template(data.system_data.jinja_template_name)
        return template.stream(asdict(data.template_data))

    @staticmethod
    def dump(stream: TemplateStream, data: ErrorDescriptionData) -> None:
        stream.dump(str(data.system_data.output_html_file_path))

    def create_all(self) -> None:
        for data in registered_error_description_data:
            stream = self.render_one(data)
            self.dump(stream, data)


if __name__ == '__main__':
    renderer = TemplateRenderer()
    renderer.create_all()
