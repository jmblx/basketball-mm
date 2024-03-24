from aiokafka import AIOKafkaProducer
import config
import asyncio

producer_instance = None


class AIOWebProducer(object):
    def __init__(self):
        self.__producer = AIOKafkaProducer(
            bootstrap_servers=config.KAFKA_BOOTSTRAP_SERVERS,
        )
        self.__produce_topic = config.PRODUCE_TOPIC

    async def start(self) -> None:
        await self.__producer.start()

    async def stop(self) -> None:
        await self.__producer.stop()

    async def send(self, value: bytes) -> None:
        try:
            await self.__producer.send(
                topic=self.__produce_topic,
                value=value,
            )
        finally:
            await self.stop()


async def get_producer() -> AIOWebProducer:
    global producer_instance
    if producer_instance is None:
        producer_instance = AIOWebProducer()
        await producer_instance.start()
    try:
        yield producer_instance
    finally:
        await producer_instance.stop()
