"""
Custom PostgreSQL database backend with DNS retry logic for Render cold starts.
Handles intermittent DNS resolution failures during container startup.
"""
import time
import logging
from django.db.backends.postgresql import base
from django.db.utils import OperationalError

logger = logging.getLogger(__name__)


class DatabaseWrapper(base.DatabaseWrapper):
    """
    PostgreSQL wrapper with DNS retry logic.
    Retries DNS lookups with exponential backoff to handle cold start race conditions.
    """

    def ensure_connection(self):
        """
        Override to add retry logic for DNS failures during cold starts.
        """
        if self.connection is not None:
            return

        max_retries = 10
        retry_delay = 1.0  # Start with 1 second

        for attempt in range(max_retries):
            try:
                # Call parent's ensure_connection method
                super().ensure_connection()
                return  # Success!
            except OperationalError as e:
                # Check if it's a DNS failure
                error_msg = str(e).lower()
                is_dns_error = any(phrase in error_msg for phrase in [
                    'could not translate host name',
                    'name or service not known',
                    'temporary failure in name resolution',
                    'nodename nor servname provided'
                ])

                if is_dns_error and attempt < max_retries - 1:
                    logger.warning(
                        f"[DNS RETRY] Attempt {attempt + 1}/{max_retries} failed. "
                        f"Retrying in {retry_delay}s..."
                    )
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    # Either not a DNS error, or we've exhausted retries
                    if is_dns_error:
                        logger.error(f"[DNS RETRY] Failed after {max_retries} attempts")
                    raise
