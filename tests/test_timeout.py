import pytest

from anthill.test_client import TestClient
from anthill import app as ant_app


def run_anthill():
    app = ant_app.App(
        service_name='test_timeout',
        host='127.0.0.1',
        port=4222,
        app_strategy='asyncio',
    )

    @app.listen('publish.request.not.existing.topic')
    async def publish_request(topic, message):
        return await app.aio_publish_request({'data': 1}, topic='not-existing-topic')

    app.start()


client = TestClient(run_anthill).start()


def test_publish_request_timeout():
    with pytest.raises(OSError):
        client.request('publish.request.not.existing.topic', {})
