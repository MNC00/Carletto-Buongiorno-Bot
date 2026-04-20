from collections.abc import Callable
from typing import Any

from carlo_bot.agents import tasks


TASK_REGISTRY: dict[str, Callable[..., Any]] = {
    "load_inputs": tasks.load_inputs,
    "select_content": tasks.select_content,
    "compose_message": tasks.compose_message,
    "build_email": tasks.build_email,
    "send_email": tasks.dispatch_email,
}


def register_task(name: str, task: Callable[..., Any]) -> None:
    TASK_REGISTRY[name] = task


def get_task(name: str) -> Callable[..., Any]:
    return TASK_REGISTRY[name]
