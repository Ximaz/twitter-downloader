import src.twitter

def main():
    username = "Amouranth"
    video_id = "1427690549637681156"

    sources = src.twitter.get_video_sources(username, video_id)
    for source in sources:
        for url in source["urls"]:
            print(url)

main()