
import os
import sys
from anthropic import Anthropic, APIError

# Read company Bifrost configuration from environment
api_key = os.getenv("BIFROST_API_KEY")
base_url = os.getenv("BIFROST_BASE_URL")

if not api_key:
    sys.exit("Error: BIFROST_API_KEY is not configured.")

if not base_url:
    sys.exit("Error: BIFROST_BASE_URL is not configured.")

try:
    # Connect to your company's Bifrost gateway
    client = Anthropic(
        api_key=api_key,
        base_url=base_url,
    )

    response = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=150,
        messages=[
            {
                "role": "user",
                "content": "Hello! Confirm that the API connection works."
            }
        ],
    )

    for block in response.content:
        if block.type == "text":
            print(block.text)

except APIError as e:
    print(f"API error: HTTP {e.status_code}")
    print(e.message)

except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
