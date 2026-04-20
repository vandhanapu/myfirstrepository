from langfuse import Langfuse
import os
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

def validate_langfuse_credentials():
    """Validate that required Langfuse credentials are present."""
    public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
    secret_key = os.getenv("LANGFUSE_SECRET_KEY")
    
    if not public_key:
        raise ValueError("❌ LANGFUSE_PUBLIC_KEY not found in .env file")
    if not secret_key:
        raise ValueError("❌ LANGFUSE_SECRET_KEY not found in .env file")
    
    logger.info("✅ Langfuse credentials validated successfully")
    return public_key, secret_key

try:
    public_key, secret_key = validate_langfuse_credentials()
    
    # Prefer BASE_URL (region-specific), fallback to HOST, then default
    host = os.getenv("LANGFUSE_BASE_URL") or os.getenv("LANGFUSE_HOST") or "https://cloud.langfuse.com"
    
    langfuse = Langfuse(
        public_key=public_key,
        secret_key=secret_key,
        host=host,
    )
    logger.info(f"✅ Langfuse client initialized with host: {host}")
except ValueError as e:
    logger.error(str(e))
    raise


def get_langfuse_client():
    return langfuse


def score_response(trace_id: str, name: str, value: float, comment: str = ""):
    langfuse.score(
        trace_id=trace_id,
        name=name,
        value=value,
        comment=comment,
    )


def flush():
    """Flush all pending traces to Langfuse."""
    try:
        langfuse.flush()
        logger.info("✅ Langfuse traces flushed successfully")
    except Exception as e:
        logger.error(f"❌ Error flushing Langfuse traces: {str(e)}")
        raise
