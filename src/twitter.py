import re
import json
import urllib.parse
from .req import Request


class GuestAccount:
    def __init__(self, username: str, video_id: str):
        self.username = username
        self.video_id = video_id
        self.__bearer_token, self.__graphql_query = self.__credentials()
        self.__guest_token = self.__activate()

    def __credentials(self) -> tuple:
        video_url = "https://twitter.com/" + self.username + "/status/" + self.video_id
        response = Request.get(video_url).content.decode("utf-8")
        script_url = re.search(
            r"https:\/\/abs.twimg.com\/responsive-web\/client-web-legacy\/main.[a-f0-9]+.js", response)[0]
        script = Request.get(script_url).content.decode("utf-8")

        bearer_token = re.search(r"\"([a-zA-Z0-9%]{104})\"", script)[1]
        graphql_query_id = re.search(
            r"{queryId:\"([a-zA-Z0-9\-_]+)\",operationName:\"TweetDetail\",operationType:\"query\"", script, re.M)[1]
        return (bearer_token, graphql_query_id)

    def __activate(self) -> str:
        url = "https://api.twitter.com/1.1/guest/activate.json"
        response = Request.post(
            url, headers={"Authorization": "Bearer " + self.__bearer_token})
        return json.loads(response.content.decode("utf-8"))["guest_token"]

    @property
    def bearer_token(self):
        return self.__bearer_token

    @property
    def guest_token(self):
        return self.__guest_token

    @property
    def graphql_query(self):
        return self.__graphql_query


def get_video_as_json(video_id: str, guest_account: GuestAccount) -> dict:
    variables = json.dumps(
        {
            "focalTweetId": video_id, "includePromotedContent": False, "withHighlightedLabel": False,
            "withCommunity": False, "withTweetQuoteCount": False, "withBirdwatchNotes": False,
            "withBirdwatchPivots": False, "withTweetResult": False, "withReactions": False,
            "withSuperFollowsTweetFields": False, "withSuperFollowsUserFields": False,
            "withUserResults": False, "withVoice": False, "withReactionsMetadata": False,
            "withNftAvatar": False, "withReactionsPerspective": False, "withDownvotePerspective": False
        }).replace(' ', '')

    url = "https://twitter.com/i/api/graphql/" + guest_account.graphql_query + \
        "/TweetDetail?variables=" + urllib.parse.quote(variables)
    response = Request.get(url, headers={
        "Authorization": "Bearer " + guest_account.bearer_token,
        "X-Guest-Token": guest_account.guest_token,
    })

    content = response.content.decode("utf-8")
    data = json.loads(content)
    if "data" not in data:
        raise "This repo needs to be updated. Please, open an issue at https://github.com/Ximaz/twitter-downloader and past the following error :\n" + \
            json.dumps(data)

    item = data["data"]["threaded_conversation_with_injections"]["instructions"][0]["entries"][0]["content"][
        "itemContent"]

    if "tweet" in item.keys():
        legacy = item["tweet"]["legacy"]
    else:
        legacy = item["tweet_results"]["result"]["legacy"]

    if "extended_entities" in legacy.keys():
        return legacy["extended_entities"]["media"]


def get_video_sources(username: str, video_id: str) -> list:
    guest_account = GuestAccount(username, video_id)
    video_as_json = get_video_as_json(video_id, guest_account)

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
