import asyncio
import time

import nats
from nats import errors
from nats.aio.msg import Msg

from panini import app as panini_app

""" MAKE SURE JETSTREAM ENABLED IN NATS BROKER """

app = panini_app.App(
    service_name="async_js_push",
    host="127.0.0.1",
    port=4222,
    enable_js=True
)

log = app.logger

@app.listen('execution_system.*.*.balance_updated_event')
async def receive_messages(msg: Msg):
    log.info(f"subject {msg.subject}, got message {msg.data}")



message = {
    "key1": "value1",
    "key2": 2,
    "key3": 3.0,
    "key4": [1, 2, 3, 4],
    "key5": {"1": 1, "2": 2, "3": 3, "4": 4, "5": 5},
    "key6": {"subkey1": "1", "subkey2": 2, "3": 3, "4": 4, "5": 5},
    "key7": None,
}

TEST_STREAM = "test_stream2"
STREAM_SUBJECTS = [
    "some.js.subject2",
]
NUM = 0



@app.on_start_task()
async def create_js_staff():
    await app.js.delete_stream(name=TEST_STREAM)
    await app.js.add_stream(name=TEST_STREAM, subjects=STREAM_SUBJECTS)
    await app.js.add_consumer(stream=TEST_STREAM, durable_name=TEST_STREAM, deliver_group='ABCD')




@app.task(interval=2)
async def send_non_js():
    global NUM
    NUM+=1
    message = {'JS': NUM}
    await app.publish_js(subject=STREAM_SUBJECTS[0], message=message, stream=TEST_STREAM)
    log.info(f"JS message sent: {message}")



@app.js_listen(stream=TEST_STREAM)
async def receive_messages_from_js_listener(msg: Msg):
    log.info(f"subject {msg.subject}, got JS message {msg.data}")
    await msg.ack()


@app.listen(subject=STREAM_SUBJECTS[0])
async def receive_messages_from_non_js_listener(msg: Msg):
    log.info(f"subject {msg.subject}, got JS message from non js listener {msg.data}")



if __name__ == "__main__":
    app.start()
