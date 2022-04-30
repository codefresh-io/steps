import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

client = WebClient(token=os.environ['SLACK_TOKEN'])

def main():
    client = WebClient(token=os.environ['SLACK_TOKEN'])

    try:
        response = client.chat_postMessage(channel=os.environ['SLACK_CHANNEL'], text=os.environ['SLACK_MESSAGE'])
        assert response["message"]["text"] == os.environ['SLACK_MESSAGE']
    except SlackApiError as e:
        # You will get a SlackApiError if "ok" is False
        assert e.response["ok"] is False
        assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
        print(f"Got an error: {e.response['error']}")
    
if __name__ == "__main__":
    main()
