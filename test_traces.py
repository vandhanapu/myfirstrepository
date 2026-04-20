#!/usr/bin/env python3
"""
Quick test to verify Langfuse is properly configured and traces are sent.
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Test 1: Verify credentials
print("=" * 60)
print("TEST 1: Verifying Langfuse Credentials")
print("=" * 60)

public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
secret_key = os.getenv("LANGFUSE_SECRET_KEY")
host = os.getenv("LANGFUSE_BASE_URL") or os.getenv("LANGFUSE_HOST")

print(f"✓ Public Key exists: {bool(public_key)}")
print(f"✓ Secret Key exists: {bool(secret_key)}")
print(f"✓ Host: {host}")

if not public_key or not secret_key:
    print("\n❌ MISSING CREDENTIALS - Cannot connect to Langfuse!")
    sys.exit(1)

# Test 2: Initialize Langfuse client
print("\n" + "=" * 60)
print("TEST 2: Initializing Langfuse Client")
print("=" * 60)

try:
    from tracing.langfuse_setup import get_langfuse_client, flush
    langfuse = get_langfuse_client()
    print("✓ Langfuse client initialized successfully")
except Exception as e:
    print(f"❌ Failed to initialize Langfuse: {e}")
    sys.exit(1)

# Test 3: Create a test trace
print("\n" + "=" * 60)
print("TEST 3: Creating Test Trace")
print("=" * 60)

try:
    trace = langfuse.trace(
        name="test-trace",
        user_id="test-user",
        metadata={"test": True}
    )
    print(f"✓ Trace created: {trace.id}")
    
    span = trace.span(
        name="test-span",
        input={"test": "input"}
    )
    print(f"✓ Span created")
    
    span.end(output={"test": "output"})
    print(f"✓ Span ended successfully")
    
except Exception as e:
    print(f"❌ Error creating trace: {e}")
    sys.exit(1)

# Test 4: Flush traces
print("\n" + "=" * 60)
print("TEST 4: Flushing Traces to Langfuse")
print("=" * 60)

try:
    flush()
    print("✓ Traces flushed successfully")
    print("\n✅ All tests passed! Check Langfuse dashboard for the test trace.")
except Exception as e:
    print(f"❌ Error flushing traces: {e}")
    sys.exit(1)
