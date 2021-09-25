import core.twitter

sources = core.twitter.get_video_sources("https://twitter.com/firefox/status/1399712574812286986")
for source in sources:
    for url in source["urls"]:
        print(url)