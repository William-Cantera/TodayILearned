"""
Today I Learned Example: Distributed Tracing with Correlation IDs
Date: 2026-11-20
"""

# Distributed Tracing with Correlation IDs
# ==============================================
# This pattern assigns a unique ID to each request/operation that flows through
# multiple services or components. Every log message includes this ID, making it
# possible to trace the complete journey of a request across a distributed system.
#
# WHEN TO USE:
#   - Microservices architectures where requests span multiple services
#   - Async workflows where operations are processed by different workers
#   - Any system where you need to correlate logs across components
#
# BEST PRACTICES:
#   - Generate IDs at the entry point (API gateway, message consumer, etc.)
#   - Propagate IDs via headers (HTTP), message metadata, or context variables
#   - Use Python's contextvars for thread/async-safe storage (no global state)
#   - Include correlation ID in ALL log messages within a request's scope
#   - Use UUID4 for unpredictable, globally unique IDs

import uuid
import logging
import contextvars
import time
from datetime import datetime

# contextvars.ContextVar stores a value per-execution-context (thread or async task).
# This is the modern, safe alternative to threading.local() and works with asyncio.
correlation_id_var: contextvars.ContextVar[str] = contextvars.ContextVar(
    'correlation_id', default='NO-CORRELATION-ID'
)

# --- Custom Log Formatter ---
# Automatically injects the current correlation ID into every log record.
# This means developers don't need to manually add the ID to each log call.
class CorrelationIdFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        # Pull the current correlation ID from the context variable
        record.correlation_id = correlation_id_var.get()
        return super().format(record)

def setup_logger() -> logging.Logger:
    logger = logging.getLogger("distributed_app")
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    # Format includes timestamp, correlation ID, level, component, and message
    fmt = CorrelationIdFormatter(
        "%(asctime)s | CID:%(correlation_id)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%H:%M:%S"
    )
    handler.setFormatter(fmt)
    logger.addHandler(handler)
    return logger

logger = setup_logger()

# --- Context Manager for Tracing Scope ---
# Sets the correlation ID for the duration of a block, then restores the previous value.
# This is critical for nested calls — each scope gets its own ID without leaking.
class traced_operation:
    def __init__(self, operation_name: str, correlation_id: str = None):
        self.operation_name = operation_name
        # Accept an incoming ID (from upstream service) or generate a fresh one
        self.correlation_id = correlation_id or str(uuid.uuid4())[:8]
        self._token = None  # Stores the reset token to restore previous context

    def __enter__(self):
        # Set the new ID; save the token so we can revert when the block exits
        self._token = correlation_id_var.set(self.correlation_id)
        logger.info(f">>> START [{self.operation_name}]")
        return self.correlation_id

    def __exit__(self, *args):
        logger.info(f"<<< END   [{self.operation_name}]")
        # Restore the previous correlation ID (handles nested scopes correctly)
        correlation_id_var.reset(self._token)

# --- Simulated Service Functions ---
def validate_user(user_id: int):
    logger.debug(f"Validating user {user_id} in auth-service")
    time.sleep(0.01)  # Simulate I/O
    logger.info(f"User {user_id} validated successfully")

def fetch_inventory(item_id: str):
    logger.debug(f"Querying inventory-service for item '{item_id}'")
    time.sleep(0.01)
    logger.warning(f"Item '{item_id}' stock is low — only 3 remaining")

def process_payment(amount: float):
    logger.debug(f"Initiating payment of ${amount:.2f} via payment-service")
    time.sleep(0.01)
    logger.info(f"Payment of ${amount:.2f} processed successfully")

# --- Entry Point: Simulating Two Separate Incoming Requests ---
if __name__ == "__main__":
    print("\n=== Request 1: Normal order flow ===")
    with traced_operation("order-request") as cid:
        validate_user(user_id=42)
        fetch_inventory(item_id="SKU-999")
        process_payment(amount=49.99)

    print("\n=== Request 2: Replayed with an upstream correlation ID
