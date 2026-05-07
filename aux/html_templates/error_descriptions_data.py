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
class TemplateData:
    title: str
    header: str

    summary: str
    suggested_status: str
    severity: str

    hr_description: str

    guidance: tuple[str, ...]


@dataclasses.dataclass(frozen=True)
class ErrorDescriptionData:
    template_data: TemplateData
    system_data: SystemData

    def __post_init__(self) -> None:
        registered_error_description_data.append(self)


ErrorDescriptionData(
    template_data=TemplateData(
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
        )
    ),
    system_data=SystemData(
        output_html_file_name='wrong_ticker.html',
    ),
)

ErrorDescriptionData(
    template_data=TemplateData(
        title='Non unique user asset address',
        header='You provided a user asset address which is already exists',
        summary='You provided a user asset address which is already exists',
        suggested_status='400 (Bad Request)',
        severity='Low',
        hr_description='The request cannot be completed because the client provided an existing user'
                       ' asset address public key.',
        guidance=(
            'This public key already exists',
            'If you want to change this key to another - then you need to provide an alternative key',
            'Or you could leave it as it is as this key is already here.',
        )
    ),
    system_data=SystemData(
        output_html_file_name='user_asset_address_already_exists.html',
    ),
)


ErrorDescriptionData(
    template_data=TemplateData(
        title='User asset address 404',
        header='User asset address not found',
        summary='User asset address does not exists',
        suggested_status='400 (Bad Request)',
        severity='Low',
        hr_description='Provided public key has not been found.',
        guidance=(
            'Double check public key',
        )
    ),
    system_data=SystemData(
        output_html_file_name='user_asset_address_not_exists.html',
    ),
)