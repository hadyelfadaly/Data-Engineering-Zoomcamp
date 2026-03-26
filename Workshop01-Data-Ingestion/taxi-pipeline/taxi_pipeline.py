"""dlt pipeline for NYC taxi data from the Zoomcamp REST API."""

import os

import dlt
from dlt.sources.rest_api import rest_api_resources
from dlt.sources.rest_api.typing import RESTAPIConfig


@dlt.source
def taxi_rest_api_source(max_pages: int | None = None):
    """Define dlt resources for the paginated NYC taxi REST API."""
    paginator: dict[str, object] = {
        "type": "page_number",
        "base_page": 1,
        "page_param": "page",
        # API returns a bare list without total-pages metadata.
        "total_path": None,
        # Stops automatically when API returns [] for a page.
        "stop_after_empty_page": True,
    }
    if max_pages is not None:
        paginator["maximum_page"] = max_pages

    config: RESTAPIConfig = {
        "client": {
            "base_url": "https://us-central1-dlthub-analytics.cloudfunctions.net/data_engineering_zoomcamp_api",
        },
        "resources": [
            {
                "name": "nyc_taxi_data",
                "endpoint": {
                    # Base URL is the endpoint, so path stays empty.
                    "path": "",
                    "method": "GET",
                    "params": {
                        "page": 1,
                    },
                    "paginator": paginator,
                },
                "write_disposition": "replace",
            }
        ],
    }

    yield from rest_api_resources(config)


pipeline = dlt.pipeline(
    pipeline_name="taxi_pipeline",
    destination="duckdb",
    progress="log",
)


if __name__ == "__main__":
    max_pages_env = os.getenv("TAXI_MAX_PAGES")
    max_pages = int(max_pages_env) if max_pages_env else None
    load_info = pipeline.run(taxi_rest_api_source(max_pages=max_pages))
    print(load_info)  # noqa: T201
