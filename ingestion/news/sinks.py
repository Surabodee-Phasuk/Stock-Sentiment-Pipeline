"""ปลายทางของ news event: Kafka topic `stock-news` (key = ticker) หรือ stdout สำหรับทดสอบ."""

from __future__ import annotations

import logging
import sys
from typing import Protocol, TextIO

from ingestion.news.event import NewsEvent

log = logging.getLogger(__name__)

DEFAULT_TOPIC = "stock-news"


class NewsSink(Protocol):
    def send(self, event: NewsEvent) -> None: ...

    def flush(self) -> None: ...


class StdoutSink:
    """เขียน JSON Lines ใช้ตอนไม่มี Kafka (`--sink stdout`)."""

    def __init__(self, stream: TextIO = sys.stdout) -> None:
        self._stream = stream

    def send(self, event: NewsEvent) -> None:
        self._stream.write(event.to_json() + "\n")

    def flush(self) -> None:
        self._stream.flush()


class KafkaSink:
    """Producer ไป topic `stock-news` โดยใช้ ticker เป็น key (docs/05)."""

    def __init__(self, bootstrap_servers: str, topic: str = DEFAULT_TOPIC) -> None:
        # import ตอนใช้ เพื่อให้ stdout/test ไม่ต้องลง Kafka client
        from confluent_kafka import Producer

        self.topic = topic
        self.failed = 0
        self._producer = Producer(
            {
                "bootstrap.servers": bootstrap_servers,
                "client.id": "news-collector",
                "acks": "all",
                "enable.idempotence": True,
                "compression.type": "zstd",
                "linger.ms": 50,
            }
        )

    def send(self, event: NewsEvent) -> None:
        self._producer.produce(
            self.topic,
            key=event.ticker.encode("utf-8"),
            value=event.to_json().encode("utf-8"),
            on_delivery=self._on_delivery,
        )
        self._producer.poll(0)

    def flush(self, timeout: float = 30.0) -> None:
        remaining = self._producer.flush(timeout)
        if remaining:
            raise RuntimeError(
                f"{remaining} message(s) not delivered to Kafka within {timeout}s"
            )

    def _on_delivery(self, err, msg) -> None:
        if err is not None:
            self.failed += 1
            log.error("delivery failed for key=%s: %s", msg.key(), err)
