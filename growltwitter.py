#! /usr/bin/env python
# coding:utf-8

#
# Last Updated on 2012/02/02 22:14:47 .
#

u"""
====================
growltwitter.py
====================

ToDo
=====

- growltwitter.png の作成
- ~/.growltwitter/icons にデフォルトの画像を配置するようにする

"""

import sys, re, itertools, time, datetime, pprint, os, threading, traceback, urllib
import Growl
# カレントディレクトリのtwitter_oauth ディレクトリをPYTHONPATH に加える
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'twitter_oauth'))
import twitter_oauth

# あいこんのpath
_ICON_PATH = os.path.join(os.environ['HOME'], '.growltwitter/icons')
# ディレクトリの作成
_HOMEDIR = os.environ['HOME']
if not '.growltwitter' in os.listdir(_HOMEDIR):
    print "Creating ~/.growltwitter/icons"
    try:
        os.mkdir(os.path.join(_HOMEDIR, '.growltwitter'))
        os.mkdir(os.path.join(_HOMEDIR, '.growltwitter', 'icons'))
    except:
        print "ERROR: Creating directory ~/.growltwitter/icons"
        # ディレクトリを作成できない場合はエラーログを出して終了する
        traceback.print_exc()
        sys.exit()

class GrowlTwitterConf(object):
    def __init__(self):
        #vimtterimage = Growl.Image.imageFromPath(os.path.join(_ICON_PATH, 'growltwitter.png'))
        vimtterimage = Growl.Image.imageFromPath(os.path.join(_ICON_PATH, 'uiharu.png'))
        self._growl = Growl.GrowlNotifier(
                    applicationName = u'GrowlTwitter',
                    notifications = ['Status', 'Mension'],
                    applicationIcon = vimtterimage,
        )
        self._growl.register()
    def notify(self, iconpath, title, description):
        self._growl.notify(
            noteType = 'Status',
            title = title,
            description = description,
            icon = Growl.Image.imageFromPath(iconpath),
            sticky = False,
        )
    def mention_notify(self, iconpath, title, description):
        self._growl.notify(
            noteType = 'Mension',
            title = title,
            description = description,
            icon = Growl.Image.imageFromPath(iconpath),
            sticky = True,
        )

class GrowlTwitter():
    def __init__(self,
                 twitter_api,
                 stream_count=10000):
        #threading.Thread.__init__(self)
        # api の作成
        self._api = twitter_api
        self._stream_count = stream_count
        # streaming api のList
        self._stream_list = [] # 長さstream_count のキューを作成する
        # growl
        self._growl = GrowlTwitterConf()
        # icon_dict
        self._icon_dict = self._make_icon_dict()

    def _get_api(self):
        return self._get_api()
    def _get_stream_count(self):
        return self._stream_count
    def _get_stream_list(self):
        return self._stream_list

    def _set_stream(self, status):
        '''
        self._stream_list にstatus を加える
        '''
        self._stream_list = [status] + self._stream_list
        if len(self._stream_list) > self._stream_count:
            self._stream_list = self._stream_list[:self._stream_count]

    api = property(_get_api)
    stream_count = property(_get_stream_count)
    stream_list = property(_get_stream_list, _set_stream)

    def _make_icon_dict(self):
        icon_dict = {}
        for iconname in os.listdir(_ICON_PATH):
            fllist = iconname.split(".")
            icon_dict[fllist[0]] = iconname
        return icon_dict

    def run(self):

        for status in self._api.user_stream():
            name = status.user.screen_name
            # 次のif 文でiconpath の設定をする
            if name in self._icon_dict.keys():
                # アイコンが既に取得済みの場合
                iconpath = os.path.join(_ICON_PATH, self._icon_dict[name])
            else:
                # アイコンが取得済みでない場合
                url = status.user.profile_image_url
                filename = url.split('/')[-1]
                filelst = filename.split('.')
                # アイコンに拡張子が付いているかの判定
                if len(filelst) != 1:
                    filetype = filelst[-1]
                    iconname = '{name}.{filetype}'.format(name=name, filetype=filetype)
                else:
                    iconname = name
                # アイコンパスの設定
                iconsavepath = os.path.join(_ICON_PATH, iconname)
                try:
                    # アイコンの取得
                    print "Getting image from %s" % url
                    urllib.urlretrieve(url, iconsavepath)
                    print "  Image get done. Save to {iconpath}".format(iconpath=iconsavepath)
                    iconpath = iconsavepath
                except:
                    # アイコン取得に失敗した時
                    # アイコンは取得に失敗した時のデフォルトのアイコンにする
                    iconpath = os.path.join(_ICON_PATH, "uiharu.png")
                    print "ERROR: cannot retrieve USER IMAGE"
                    print "  imageurl: {imageurl}".format(imageurl=url)
                    traceback.print_exc()
            # ストリームキューへの設定
            self._set_stream(status)
            # growl の表示
            self._growl.notify(iconpath=iconpath, title=status.user.screen_name, description=status.text)
            # メンションがあった場合の表示
            for part in [u'@kenkov']:
                if part in status.text:
                    self._growl.mention_notify(iconpath=iconpath, title=status.user.screen_name, description=status.text)
                    break

if __name__=='__main__':
    # input your keys
    consumer_key = '***'
    consumer_secret = '***'
    oauth_token = '***'
    oauth_token_secret = '***'

    api = twitter_oauth.Api(consumer_key, consumer_secret,
                            oauth_token, oauth_token_secret)
    gt = GrowlTwitter(twitter_api=api, stream_count=10000)

    try:
        gt.run()
    except KeyboardInterrupt:
        print "Exit TwitterGrowl, Bye＞ω＜ノ"
        sys.exit()
