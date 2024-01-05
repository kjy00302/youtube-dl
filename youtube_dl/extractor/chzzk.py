# coding: utf-8
from __future__ import unicode_literals

from .common import InfoExtractor
from ..utils import ExtractorError


class ChzzkVodIE(InfoExtractor):
    _VALID_URL = r'https?://chzzk\.naver\.com/video/(?P<id>\d+)'
    _URL_TEMPLATE = 'https://chzzk.naver.com/video/{video_id}'

    _TESTS = [{
        'url': 'https://chzzk.naver.com/video/1808',
        'md5': '225f46a2a87d86a8975a2ee6e66cb89f',
        'info_dict': {
            'id': '1808',
            'ext': 'ts',
            'title': '플러리의 라이브 방송',
            'uploader_id': 'fe558c6d1b8ef3206ac0bc0419f3f564',
            'uploader': '플러리',
            'timestamp': 1702992423,
            'upload_date': '20231219',
            'duration': 54,
            'age_limit': 0,
        }
    }, {
        'url': 'https://chzzk.naver.com/video/10106',
        'info_dict': {
            'id': '10106',
            'ext': 'ts',
            'title': '240105-1',
            'uploader_id': '17aa057a8248b53affe30512a91481f5',
            'uploader': '김도 KimDoe',
            'timestamp': 1704468746,
            'upload_date': '20240106',
            'duration': 4484,
            'age_limit': 18,
        },
        'skip': 'Age-restricted video',
    }]

    def chzzk_callapi(self, path, video_id):
        resp = self._download_json(
            "https://api.chzzk.naver.com" + path, video_id)
        if resp['code'] != 200:
            raise ExtractorError(
                'chzzk api call returned %d: %s' %
                (resp['code'], resp['message']), expected=True)
        return resp['content']

    def _real_extract(self, url):
        video_id = self._match_id(url)

        vod_data = self.chzzk_callapi(
            '/service/v2/videos/' + video_id, video_id)
        channel_data = vod_data['channel']

        is_adult = vod_data.get('adult', False)
        if is_adult and not vod_data['videoId']:
            raise ExtractorError(
                'Video is age-restricted. Login required.',
                expected=True)

        formats = []
        mpd_quary = {
            'key': vod_data['inKey'],
            'sid': 2099,  # for HTML5 PC, HTML5 Mobile returns 22099
            'env': 'real',
            'lc': 'ko_KR',
            'cpl': 'ko_KR',
        }

        formats.extend(self._extract_mpd_formats(
            'https://apis.naver.com/neonplayer/vodplay/v1/playback/' + vod_data['videoId'],
            video_id, query=mpd_quary))

        return {
            'id': video_id,
            'title': vod_data.get('videoTitle'),
            'formats': formats,
            'thumbnail': vod_data.get('thumbnailImageUrl'),
            'timestamp': vod_data.get('publishDateAt') // 1000,
            'uploader': channel_data.get('channelName'),
            'uploader_id': channel_data.get('channelId'),
            'duration': vod_data.get('duration'),
            'view_count': vod_data.get('readCount'),
            'age_limit': 18 if is_adult else 0
        }
