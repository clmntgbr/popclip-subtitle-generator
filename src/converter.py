import json
from src.Protobuf.Message_pb2 import Clip, Video, Configuration


class ProtobufConverter:
    @staticmethod
    def json_to_protobuf(message: str) -> Clip:
        data = json.loads(message)
        print(data)

        clip_data = data["clip"]

        clip = Clip()
        clip.id = clip_data["id"]
        clip.userId = clip_data["userId"]

        if "cover" in clip_data:
            clip.cover = clip_data["cover"]

        video = Video()
        video.id = clip_data["originalVideo"]["id"]
        video.name = clip_data["originalVideo"]["name"]
        video.originalName = clip_data["originalVideo"]["originalName"]
        video.mimeType = clip_data["originalVideo"]["mimeType"]
        video.size = int(clip_data["originalVideo"]["size"])

        if "length" in clip_data["originalVideo"]:
            video.length = int(clip_data["originalVideo"]["length"])

        if "audios" in clip_data["originalVideo"]:
            video.audios.extend(clip_data["originalVideo"]["audios"])

        if "subtitles" in clip_data["originalVideo"]:
            video.subtitles.extend(clip_data["originalVideo"]["subtitles"])

        if "ass" in clip_data["originalVideo"]:
            video.ass = clip_data["originalVideo"]["ass"]

        if "subtitle" in clip_data["originalVideo"]:
            video.subtitle = clip_data["originalVideo"]["subtitle"]

        video.IsInitialized()
        clip.originalVideo.CopyFrom(video)

        if "processedVideo" in clip_data:
            processed_video = Video()
            processed_video.id = clip_data["processedVideo"]["id"]
            processed_video.name = clip_data["processedVideo"]["name"]
            processed_video.originalName = clip_data["processedVideo"]["originalName"]
            processed_video.mimeType = clip_data["processedVideo"]["mimeType"]
            processed_video.size = int(clip_data["processedVideo"]["size"])

            if "length" in clip_data["processedVideo"]:
                processed_video.length = int(clip_data["processedVideo"]["length"])

            if "audios" in clip_data["processedVideo"]:
                processed_video.audios.extend(clip_data["processedVideo"]["audios"])

            if "subtitles" in clip_data["processedVideo"]:
                processed_video.subtitles.extend(
                    clip_data["processedVideo"]["subtitles"]
                )

            if "ass" in clip_data["processedVideo"]:
                processed_video.ass = clip_data["processedVideo"]["ass"]

            if "subtitle" in clip_data["processedVideo"]:
                processed_video.subtitle = clip_data["processedVideo"]["subtitle"]

            processed_video.IsInitialized()
            clip.processedVideo.CopyFrom(processed_video)

        configuration = Configuration()
        configuration.subtitleFont = clip_data["configuration"]["subtitleFont"]
        configuration.subtitleSize = clip_data["configuration"]["subtitleSize"]
        configuration.subtitleColor = clip_data["configuration"]["subtitleColor"]
        configuration.subtitleBold = clip_data["configuration"]["subtitleBold"]
        configuration.subtitleItalic = clip_data["configuration"]["subtitleItalic"]
        configuration.privacyOptions = clip_data["configuration"]["privacyOptions"]
        configuration.subtitleUnderline = clip_data["configuration"][
            "subtitleUnderline"
        ]
        configuration.subtitleOutlineColor = clip_data["configuration"][
            "subtitleOutlineColor"
        ]
        configuration.subtitleOutlineThickness = clip_data["configuration"]["subtitleOutlineThickness"]
        configuration.subtitleShadow = clip_data["configuration"]["subtitleShadow"]
        configuration.subtitleShadowColor = clip_data["configuration"][
            "subtitleShadowColor"
        ]
        configuration.format = clip_data["configuration"]["format"]
        configuration.split = clip_data["configuration"]["split"]
        configuration.marginV = clip_data["configuration"]["marginV"]

        configuration.IsInitialized()
        clip.configuration.CopyFrom(configuration)

        clip.IsInitialized()

        return clip
