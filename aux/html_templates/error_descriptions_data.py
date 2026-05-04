import dataclasses
import pathlib

registered_error_description_data = []

@dataclasses.dataclass
class SystemData:
    output_html_file_name: dataclasses.InitVar[str]
    output_html_folder: dataclasses.InitVar[str] = 'site/error-descriptions'
    jinja_template_name: str = 'error_description.jinja'
    output_html_file_path: pathlib.Path = dataclasses.field(init=False)

    def __post_init__(self, output_html_file_name: str, output_html_folder: str) -> None:
        self.output_html_file_path = pathlib.Path(
            output_html_folder,
            output_html_file_name,
        )

@dataclasses.dataclass(frozen=True)
class ErrorDescriptionData:
    title: str
    header: str

    summary: str
    suggested_status: str
    severity: str

    hr_description: str

    guidance: tuple[str, ...]

    system_data: SystemData

    def __post_init__(self) -> None:
        registered_error_description_data.append(self)


ErrorDescriptionData(
    title='Wrong ticker',
    header='You provided a ticker that does not exist.',
    summary='Ticker does not exist or has not been indexed yet.',
    suggested_status='400 (Bad Request)',
    severity='Low',
    hr_description='The request cannot be completed because the client provided an invalid ticker.',
    guidance=(
        'Find the list of all tickers on CoinGecko.',
        'Find the correct ticker for your coin.',
        'Update the request and send it again.',
    ),
    system_data=SystemData(
        output_html_file_name='wrong_ticker.html',
    ),
)
