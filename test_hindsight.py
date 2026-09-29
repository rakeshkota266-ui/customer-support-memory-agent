import os
from dotenv import load_dotenv
from hindsight_client import Hindsight

load_dotenv(override=True)

client = Hindsight(
    base_url=os.getenv("HINDSIGHT_BASE_URL"),
    api_key=os.getenv("HINDSIGHT_API_KEY")
)

bank_id = os.getenv("HINDSIGHT_BANK_ID")

client.retain(
    bank_id=bank_id,
    content="""
    Customer name is Rahul.
    Rahul uses a TP-Link router.
    Rahul's internet connection disconnects every evening.
    A previous support agent suggested restarting the router,
    but the problem happened again.
    """
)

print("Memory stored successfully!")

result = client.recall(
    bank_id=bank_id,
    query="What do we know about Rahul's previous internet problem?"
)

print("\nRecalled memories:")

for memory in result.results:
    print("-", memory.text)

client.close()