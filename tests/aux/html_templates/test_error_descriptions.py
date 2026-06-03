import pytest
from polyfactory.factories.dataclass_factory import DataclassFactory

from aux.html_templates.error_description_templates import TemplateRenderer
from aux.html_templates.error_descriptions_data import ErrorDescriptionData, SystemData


class SystemDataFactory(DataclassFactory[SystemData]):
    __use_defaults__ = True

class ErrorDescriptionDataFactory(DataclassFactory[ErrorDescriptionData]):
    pass


@pytest.fixture
def data(tmp_path) -> ErrorDescriptionData:
    system_data = SystemDataFactory.build(output_html_file_name='test.html', output_html_folder=str(tmp_path))
    return ErrorDescriptionDataFactory.build(system_data=system_data)

def test_create_html_file(data):
    assert not data.system_data.output_html_file_path.exists()

    renderer = TemplateRenderer()
    renderer.create_all()

    assert data.system_data.output_html_file_path.exists()

    content = data.system_data.output_html_file_path.read_text()

    assert data.template_data.title in content
    assert data.template_data.header in content
    assert data.template_data.summary in content
    assert data.template_data.suggested_status in content
    assert data.template_data.severity in content
    assert data.template_data.hr_description in content
    for g in data.template_data.guidance:
        assert g in content
