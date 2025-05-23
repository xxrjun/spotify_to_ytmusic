import re
import time
from collections import OrderedDict, Counter
from pathlib import Path

from ytmusicapi import YTMusic
from ytmusicapi.auth.oauth import OAuthCredentials

from spotify_to_ytmusic.settings import Settings
from spotify_to_ytmusic.utils.cache_manager import CacheManager
from spotify_to_ytmusic.utils.match import get_best_fit_song_id

cacheManager = CacheManager()


class YTMusicTransfer:
    def __init__(self):
        settings = Settings()
        headers = settings["youtube"]["headers"]
        assert headers.startswith("{"), "ytmusicapi headers not set or invalid"
        oauth_credentials = (
            None
            if settings["youtube"]["auth_type"] != "oauth"
            else OAuthCredentials(
                client_id=settings["youtube"]["client_id"],
                client_secret=settings["youtube"]["client_secret"],
            )
        )
        self.api = YTMusic(
            headers, settings["youtube"]["user_id"], oauth_credentials=oauth_credentials
        )

    import time

    def create_playlist(self, name, info, privacy="PRIVATE", tracks=None, add_delay=0):
        if not add_delay or not tracks:
            return self.api.create_playlist(name, info, privacy, video_ids=tracks)
        
        playlist_id = self.api.create_playlist(name, info, privacy)
        
        time.sleep(2)
        
        total_songs = len(tracks)
        print(f"Adding {total_songs} songs to playlist one by one...")
        
        for i, video_id in enumerate(tracks):
            try:
                self.api.add_playlist_items(playlist_id, [video_id])
                
                if (i + 1) % 10 == 0 or i == total_songs - 1:
                    print(f"Added {i+1}/{total_songs} songs")
                
                if add_delay > 0 and i < total_songs - 1:
                    time.sleep(add_delay)
                    
            except Exception as e:
                print(f"Error adding song {i+1}: {e}")
                time.sleep(2)
                try:
                    self.api.add_playlist_items(playlist_id, [video_id])
                except:
                    print(f"Failed to add song {i+1}, skipping...")
                    continue
        
        return playlist_id

    def rate_song(self, id, rating):
        return self.api.rate_song(id, rating)

    def search_songs(self, tracks, use_cached: bool = False):
        videoIds = []
        songs = list(tracks)
        notFound = []
        duplicates = []
        lookup_ids = cacheManager.load_lookup_table()

        if use_cached:
            print("Use of cache file is enabled.")

        print("Searching YouTube...")
        for i, song in enumerate(songs):
            name = re.sub(r" \(feat.*\..+\)", "", song["name"])
            query = song["artist"] + " " + name
            query = query.replace(" &", "")

            if use_cached and query in lookup_ids:
                vid = lookup_ids[query]
            else:
                result = self.api.search(query)
                if not result:
                    notFound.append(query)
                    if i > 0 and i % 10 == 0:
                        print(f"YouTube tracks: {i}/{len(songs)}")
                    continue

                targetSong = get_best_fit_song_id(result, song)
                if targetSong is None:
                    notFound.append(query)
                    if i > 0 and i % 10 == 0:
                        print(f"YouTube tracks: {i}/{len(songs)}")
                    continue

                vid = targetSong
                if use_cached:
                    lookup_ids[query] = vid
                    cacheManager.save_to_lookup_table(lookup_ids)

            if vid in videoIds:
                duplicates.append(query)

            videoIds.append(vid)

            if i > 0 and i % 10 == 0:
                print(f"YouTube tracks: {i}/{len(songs)}")

        with open(Path.cwd() / "noresults_youtube.txt", "w", encoding="utf-8") as f:
            for q in notFound:
                f.write(q + "\n")

        with open(Path.cwd() / "duplicates.txt", "w", encoding="utf-8") as f:
            for q in duplicates:
                f.write(q + "\n")

        return videoIds

    def add_playlist_items(self, playlistId, videoIds):
        unique_ids = list(OrderedDict.fromkeys(videoIds))
        self.api.add_playlist_items(playlistId, unique_ids)

    def get_playlist_id(self, name):
        pl = self.api.get_library_playlists(10000)
        try:
            playlist = next(x for x in pl if x["title"].find(name) != -1)["playlistId"]
            return playlist
        except StopIteration:
            raise Exception("Playlist title not found in playlists")

    def remove_songs(self, playlistId):
        items = self.api.get_playlist(playlistId, 10000)
        if "tracks" in items:
            self.api.remove_playlist_items(playlistId, items["tracks"])

    def remove_playlists(self, pattern):
        playlists = self.api.get_library_playlists(10000)
        p = re.compile(f"{pattern}")
        matches = [pl for pl in playlists if p.match(pl["title"])]
        print("The following playlists will be removed:")
        print("\n".join([pl["title"] for pl in matches]))
        print("Please confirm (y/n):")

        choice = input().lower()
        if choice[:1] == "y":
            [self.api.delete_playlist(pl["playlistId"]) for pl in matches]
            print(str(len(matches)) + " playlists deleted.")
        else:
            print("Aborted. No playlists were deleted.")
