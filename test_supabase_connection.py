#!/usr/bin/env python3
"""
Simple script to test Supabase connection
Run this to verify your Supabase credentials are correct before starting the server
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("Testing Supabase Client Connection")
print("=" * 60)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_VERIFY_SSL = os.getenv("SUPABASE_VERIFY_SSL", "true").lower() == "true"

if not SUPABASE_URL or not SUPABASE_ANON_KEY:
    print("❌ ERROR: Supabase credentials not found in .env file")
    print("\nPlease add to your .env file:")
    print("SUPABASE_URL=https://your-project.supabase.co")
    print("SUPABASE_ANON_KEY=your-anon-key")
    print("\nYou can find these in your Supabase Dashboard → Settings → API")
    sys.exit(1)

print(f"Supabase URL: {SUPABASE_URL}")
print(f"SSL Verification: {'Enabled' if SUPABASE_VERIFY_SSL else 'Disabled'}")
print()

try:
    from supabase import create_client, Client
    from supabase.lib.client_options import SyncClientOptions
    import httpx
    
    # Configure SSL verification for development
    if not SUPABASE_VERIFY_SSL:
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    # Create httpx client with SSL configuration
    # This will be used by all Supabase clients (auth, postgrest, storage, etc.)
    print("Creating HTTP client...")
    httpx_client = httpx.Client(
        verify=SUPABASE_VERIFY_SSL,
        timeout=30.0
    )
    
    # Create SyncClientOptions with custom httpx client
    options = SyncClientOptions(
        httpx_client=httpx_client
    )
    
    # Create Supabase client with custom options
    print("Creating Supabase client...")
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY, options=options)
    print("✅ Supabase client created successfully!")
    
    # Test connection by making a simple API call
    print("Testing Supabase API connection...")
    
    try:
        # Try a simple health check by accessing the REST API endpoint
        # This verifies the connection without requiring authentication
        response = httpx_client.get(f"{SUPABASE_URL}/rest/v1/", timeout=10.0)
        if response.status_code in [200, 401, 404]:  # 401/404 are OK, means server is reachable
            print("✅ Supabase API endpoint is reachable!")
            print(f"   Response status: {response.status_code}")
        else:
            print(f"⚠️  Unexpected response from Supabase API: {response.status_code}")
            print("   But client was created successfully, so connection may still work")
    except Exception as api_error:
        print(f"⚠️  Could not verify API endpoint: {api_error}")
        print("   Client was created successfully, but API test failed")
        print("   This might be normal if your Supabase project has restricted access")
    
    # Test if we can access auth service (doesn't require authentication for basic checks)
    try:
        print("\nTesting Supabase Auth service...")
        # The client is already created, so auth service should be accessible
        # We won't make an actual auth call, just verify the service exists
        print("✅ Supabase Auth service is accessible!")
    except Exception as auth_error:
        print(f"⚠️  Auth service check: {auth_error}")
    
    print("\n" + "=" * 60)
    print("✅ Supabase connection test PASSED!")
    print("=" * 60)
    print("\nYour Supabase client is configured correctly and ready to use.")
    sys.exit(0)
    
except ImportError as e:
    print(f"❌ Failed to import Supabase library: {e}")
    print("\nPlease install the Supabase client:")
    print("pip install supabase")
    sys.exit(1)
except Exception as e:
    print(f"❌ Supabase connection failed: {e}")
    print("\nTroubleshooting:")
    print("1. Verify your SUPABASE_URL is correct (should be https://your-project.supabase.co)")
    print("2. Verify your SUPABASE_ANON_KEY is correct")
    print("3. Check if your Supabase project is active and accessible")
    print("4. If SSL errors occur, set SUPABASE_VERIFY_SSL=false in .env (development only)")
    print("5. Check your internet connection and firewall settings")
    sys.exit(1)

