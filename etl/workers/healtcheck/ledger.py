from temporalio.api.taskqueue.v1 import TaskQueue
from temporalio.api.workflowservice.v1 import DescribeTaskQueueRequest

from config import settings
from workers.base import get_client
from workers.task_queues import LEDGER_TASK_QUEUE


async def healthcheck() -> dict:
    client = await get_client(settings.TEMPORAL_ADDRESS)
    return await client.workflow_service.describe_task_queue(
        DescribeTaskQueueRequest(
            namespace=settings.TEMPORAL_NAMESPACE,
            task_queue=TaskQueue(name=LEDGER_TASK_QUEUE),
        )
    )
