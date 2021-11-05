import json
import re
import urllib.parse
from .req import Request


def get_guest_token(bearer_token: str) -> str:
    url = "https://api.twitter.com/1.1/guest/activate.json"
    response = Request.post(
        url, headers={"Authorization": "Bearer " + bearer_token})
    return json.loads(response.content.decode("utf-8"))["guest_token"]


def get_access_tokens(video_url) -> tuple:
    response = Request.get(video_url).content.decode("utf-8")
    script_url = re.search(
        r"https://abs.twimg.com/responsive-web/client-web/main.[a-f0-9]+.js", response)[0]
    script = Request.get(script_url).content.decode("utf-8")
    bearer_token = re.search(r"\"([a-zA-Z0-9%]{104})\"", script)[1]
    graphql_query_id = re.search(
        r"{queryId:\"([a-zA-Z0-9\-_]+)\",operationName:\"TweetDetail\",operationType:\"query\"}", script)[1]
    return (bearer_token, graphql_query_id)


def get_video_as_json(video_id: str, graphql_query: str, bearer_token: str, guest_token: str) -> dict:
    variables = json.dumps({"focalTweetId": video_id, "includePromotedContent": False, "withHighlightedLabel": False,
                            "withCommunity": False, "withTweetQuoteCount": False, "withBirdwatchNotes": False,
                            "withBirdwatchPivots": False, "withTweetResult": False, "withReactions": False,
                            "withSuperFollowsTweetFields": False, "withSuperFollowsUserFields": False, "withUserResults": False,
                            "withVoice": False, "withReactionsMetadata": False, "withNftAvatar": False, "withReactionsPerspective": False}).replace(' ', '')

    url = "https://twitter.com/i/api/graphql/" + graphql_query + \
        "/TweetDetail?variables=" + urllib.parse.quote(variables)

    response = Request.get(url, headers={
        "Authorization": "Bearer " + bearer_token,
        "X-Guest-Token": guest_token,
    })

    content = response.content.decode("utf-8")
    data = json.loads(content)
    print(data)
    item = data["data"]["threaded_conversation_with_injections"]["instructions"][0]["entries"][0]["content"][
        "itemContent"]

    if "tweet" in item.keys():
        legacy = item["tweet"]["legacy"]
    else:
        legacy = item["tweet_results"]["result"]["legacy"]
    return legacy["extended_entities"]["media"] if "extended_entities" in legacy.keys() else None


def get_video_sources(username: str, video_id: str) -> list:
    video_url = "https://twitter.com/"+username+"/status/"+video_id

    # Initializing tokens to use the API as a guest.
    # Getting GraphQL Hash ID to perform 'TwitterDetails' request.
    bearer, graphql_query = get_access_tokens(video_url)
    guest_token = get_guest_token(bearer)

    video_as_json = get_video_as_json(
        video_id, graphql_query, bearer, guest_token)

    if video_as_json is None:
        return []

    sources = []
    sid = 0
    for media in video_as_json:
        if "video_info" not in media.keys():
            continue

        media_urls = media["video_info"]["variants"]
        urls = [None] * len(media_urls)
        for i in range(len(urls)):
            urls[i] = media_urls[i]["url"]

        sources.append(dict(id=sid, urls=urls))
        sid += 1

    return sources
