"""
API Test Example - Example of using Behavior Framework for API testing
This file is for reference only, actual test cases should be written in .feature files in the features directory
"""

import asyncio
from behavior_framework.api.request import APIRequest
from behavior_framework.api.assertions import APIAssertions


async def example_api_test():
    """API test example"""
    # Initialize API client
    async with APIRequest(base_url="https://jsonplaceholder.typicode.com") as client:
        # Send GET request
        response = await client.get("posts/1")
        
        # Assert response
        assertions = APIAssertions(response)
        assertions.assert_status(200)
        assertions.assert_json("id", 1)
        
        print("API test passed")


if __name__ == "__main__":
    asyncio.run(example_api_test())
