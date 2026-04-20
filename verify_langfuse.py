#!/usr/bin/env python3
"""
Verify traces in Langfuse dashboard.
"""
import os
from dotenv import load_dotenv
from langfuse import Langfuse

load_dotenv()

langfuse = Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host=os.getenv("LANGFUSE_BASE_URL") or os.getenv("LANGFUSE_HOST") or "https://cloud.langfuse.com",
)

print("=" * 70)
print("LANGFUSE TRACE VERIFICATION")
print("=" * 70)

# Get recent traces
print("\nFetching recent traces from Langfuse...")
try:
    traces = langfuse.fetch_traces(limit=10)
    
    if traces.data:
        print(f"\n✅ Found {len(traces.data)} recent traces:\n")
        for i, trace in enumerate(traces.data, 1):
            print(f"{i}. Trace ID: {trace.id}")
            print(f"   Name: {trace.name}")
            print(f"   User ID: {trace.user_id}")
            print(f"   Timestamp: {trace.timestamp}")
            print()
    else:
        print("\n⚠️ No traces found in Langfuse!")
        print("Possible reasons:")
        print("  1. Credentials might be invalid")
        print("  2. No traces have been sent yet")
        print("  3. You're looking at wrong region")
        
except Exception as e:
    print(f"\n❌ Error fetching traces: {e}")
    print("\nTroubleshooting:")
    print(f"  - Public Key: {os.getenv('LANGFUSE_PUBLIC_KEY')[:20]}...")
    print(f"  - Secret Key exists: {bool(os.getenv('LANGFUSE_SECRET_KEY'))}")
    print(f"  - Host: {os.getenv('LANGFUSE_BASE_URL') or os.getenv('LANGFUSE_HOST')}")

print("\n" + "=" * 70)
print("NEXT STEPS")
print("=" * 70)
print(f"1. Visit: https://us.cloud.langfuse.com")
print(f"2. Login with your Langfuse credentials")
print(f"3. Look for traces named:")
print(f"   - 'onboarding-session'")
print(f"   - 'debug-onboarding-session'")
print(f"4. Or search for trace IDs above")
print("=" * 70)
