from auth_provider_aws import aws_auth_provider
from graph_client import GraphClient

# Setup
print("Initializing...")
graph_client = GraphClient()
graph_client.auth_provider = aws_auth_provider

# List
print("Fetching subscriptions...")
subs = graph_client.list_subscriptions()
print(f"Found {len(subs)} active subscriptions.")

# Delete
for sub in subs:
    sub_id = sub['id']
    url = sub.get('notificationUrl', 'Unknown URL')
    print(f"Deleting subscription {sub_id} (URL: {url})...")
    try:
        graph_client.delete_subscription(sub_id)
        print("  ✓ Deleted")
    except Exception as e:
        print(f"  ✗ Failed: {e}")

print("Cleanup complete!")
