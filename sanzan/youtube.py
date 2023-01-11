from yt_dlp import YoutubeDL

YDL_OPTS_DEFAULT = {
    "format": "bestvideo",
    "skip_download": True,
    # "quiet" : True,
    # Skip manifest files
    "extractor_args": {"youtube": {"skip": ["dash", "hls"]}},
}


def get_direct_url(source_url, audio=False):
    """
    Get direct url to best video or audio source via yt_dlp
    """

    ydl_opts = YDL_OPTS_DEFAULT

    if audio:
        ydl_opts["format"] = "bestaudio"

    with YoutubeDL(ydl_opts) as ydl:
        extracted_data = ydl.extract_info(source_url, download=False)

        direct_url = extracted_data.get("url")
        if not direct_url:
            raise Exception(f"Could not find direct url for {source_url}")

        return direct_url
