import dataclasses

_registered_error_description_data = []

@dataclasses.dataclass
class SystemData:
    template_name: str

@dataclasses.dataclass
class ErrorDescriptionData:
    title: str
    header: str

    summary: str
    suggested_status: str
    severity: str

    hr_description: str

    guidance: tuple[str, ...]

    system_data: SystemData

    def __post_init__(self):
        _registered_error_description_data.append(self)


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
    system_data=SystemData(template_name='wrong_ticker.html'),
)
