spotify_to_ytmusic
####################

.. |pypi-downloads| image:: https://img.shields.io/pypi/dm/spotify_to_ytmusic?style=flat-square
    :alt: PyPI Downloads
    :target: https://pypi.org/project/spotify_to_ytmusic/

.. |discuss| image:: https://img.shields.io/github/discussions/sigma67/spotify_to_ytmusic?style=flat-square
   :alt: Ask questions at Discussions
   :target: https://github.com/sigma67/spotify_to_ytmusic/discussions

.. |code-coverage| image:: https://img.shields.io/codecov/c/github/sigma67/spotify_to_ytmusic?style=flat-square
    :alt: Code coverage
    :target: https://codecov.io/gh/sigma67/spotify_to_ytmusic

.. |latest-release| image:: https://img.shields.io/github/v/release/sigma67/spotify_to_ytmusic?style=flat-square
    :alt: Latest release
    :target: https://github.com/sigma67/spotify_to_ytmusic/releases/latest

.. |commits-since-latest| image:: https://img.shields.io/github/commits-since/sigma67/spotify_to_ytmusic/latest?style=flat-square
    :alt: Commits since latest release
    :target: https://github.com/sigma67/spotify_to_ytmusic/commits


|pypi-downloads| |discuss| |code-coverage| |latest-release| |commits-since-latest|

A simple command line script to clone a Spotify playlist to YouTube Music.

- Transfer a single Spotify playlist
- Like all the songs in a Spotify playlist
- Update a transferred playlist on YouTube Music
- Transfer all playlists for a Spotify user
- Like all songs from all playlists for a Spotify user
- Remove playlists from YouTube Music
- **NEW**: Preserve Spotify's track order and create time differences in YouTube Music

Install
-------

- Python 3.10 or later - https://www.python.org
- pipx - https://pipx.pypa.io

.. code-block::

    pipx ensurepath

- Open a new shell. Install:

.. code-block::

    pipx install spotify_to_ytmusic


Setup
-------

1. Generate a new app at https://developer.spotify.com/dashboard
2. Generate a new app by following instructions at https://ytmusicapi.readthedocs.io/en/stable/setup/oauth.html
3. Run

.. code-block::

    spotify_to_ytmusic setup

For backwards compatibility you can also create your own file and pass it using ``--file settings.ini``.

If you want to transfer private playlists from Spotify (i.e. liked songs), choose "yes" for oAuth authentication, otherwise choose "no".
For oAuth authentication you should set ``https://127.0.0.1`` as redirect URI for your app in Spotify's developer dashboard.

Usage
------

After you've completed setup, you can simply run the script from the command line using:

.. code-block::

    spotify_to_ytmusic create <spotifylink>

where ``<spotifylink>`` is a link like https://open.spotify.com/playlist/0S0cuX8pnvmF7gA47Eu63M

The script will log its progress and output songs that were not found in YouTube Music to **noresults_youtube.txt**.

Preserving track order from Spotify
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can preserve the order of tracks as they were added to Spotify and create time differences in YouTube Music:

.. code-block::

    # Preserve Spotify order (oldest first) with 1 second delay between tracks
    spotify_to_ytmusic create <spotifylink> --add-delay 1
    
    # Reverse order (newest first) with 0.5 second delay
    spotify_to_ytmusic create <spotifylink> --reverse-order --add-delay 0.5

The ``--add-delay`` option adds a delay (in seconds) between each track addition, creating visible time differences in YouTube Music's "Recently added" sort option. This is useful for maintaining chronological order from Spotify.

Transfer all playlists of a Spotify user
----------------------------------------

For migration purposes, it is possible to transfer all public playlists of a user by using the Spotify user's ID (unique username).

.. code-block::

    spotify_to_ytmusic all <spotifyuserid>

Transfer liked tracks of the Spotify user
-----------------------------------------

**You must use oAuth authentication for transferring liked songs.**

.. code-block::

   spotify_to_ytmusic liked

This command will open browser where you should give access to your account (if you haven't done that before).
After authorization you will be redirected to 127.0.0.1, copy link you were redirected to (looks like 127.0.0.1/?code=...) and paste to command line.

Command line options
---------------------

There are some additional command line options for setting the playlist name and determining whether it's public or not. To view them, run

.. code::

    spotify_to_ytmusic -h

To view subcommand help, run i.e.

.. code-block::

    spotify_to_ytmusic setup -h

Available subcommands:

.. code-block::

    positional arguments:
      {setup,create,update,remove,all,liked,search,cache-clear}
                            Provide a subcommand
        setup               Set up credentials
        create              Create a new playlist on YouTube Music.
        update              Delete all entries in the provided Google Play Music playlist and update the playlist with entries from the Spotify playlist.
        remove              Remove playlists with specified regex pattern.
        all                 Transfer all public playlists of the specified user (Spotify User ID).
        liked               Transfer all liked songs of the user.
        search              Search for a song on YouTube Music.
        cache-clear         Clear cache file.

    create options:
      -d, --date           Append the current date to playlist name
      -i, --info           Provide playlist description
      -n, --name           Provide custom playlist name
      -p, --public         Make playlist public
      -l, --like           Like all songs in playlist
      --add-delay          Delay (in seconds) between adding songs
      --reverse-order      Reverse track order (newest first)
      --use-cached         Use cached search results

    options:
      -h, --help           show this help message and exit

Notes on track ordering
-----------------------

- YouTube Music's "Recently added" sort will show tracks in the order they were added
- Without ``--add-delay``, all tracks are added simultaneously and may appear in random order
- Recommended delays: 0.5-1 seconds for large playlists, 1-2 seconds for smaller ones
- Large playlists (300+ tracks) may take significant time with delays enabled

  Example timing:
  - 360 tracks with 0.5s delay ≈ 3 minutes
  - 360 tracks with 1s delay ≈ 6 minutes