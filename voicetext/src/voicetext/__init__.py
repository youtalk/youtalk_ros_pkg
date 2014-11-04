#!/usr/bin/env python
# -*- coding: utf-8 -*-

import wave

import requests
from requests.auth import HTTPBasicAuth
import pyaudio
import rospy


class VoiceText(object):
    """
    Speech synthesizer by VoiceText Web API
    """
    URL = 'https://api.voicetext.jp/v1/tts'
    CHUNK = 1024
    _audio = pyaudio.PyAudio()

    def __init__(self, user_name, password='', speaker='hikari'):
        """
        :param user_name: Auth user name of VoiceText Web API
        :type user_name: str
        :param password: Auth password of VoiceText Web API
        :type password: str
        :param speaker: Speaker name
        :type speaker: str
        """
        if not user_name:
            rospy.logerr('Invalid "user_name"')
            raise Exception('Invalid "user_name"')

        self._auth = HTTPBasicAuth(user_name, password)
        self._data = {'speaker': speaker}
        rospy.loginfo('Initialized')

    def speaker(self, speaker):
        """
        Change speaker.
        :param speaker: Speaker name
        :type speaker: str
        :rtype: VoiceText
        """
        if speaker in ['show', 'haruka', 'hikari', 'takeru']:
            self._data['speaker'] = speaker
            rospy.loginfo('Speaker = %s' % speaker)
        else:
            rospy.logwarn('Unknown speaker: %s' % str(speaker))

        return self

    def emotion(self, emotion, level=1):
        """
        Change emotion and its level.
        :param emotion: Emotion type
        :type emotion: str
        :param level: Level of emotion
        :type level: int
        :rtype: VoiceText
        """
        if emotion in ['happiness', 'anger', 'sadness']:
            self._data['emotion'] = emotion
            if isinstance(level, int) and 1 <= level <= 2:
                self._data['emotion_level'] = level
                rospy.loginfo('Emotion = %s, Level = %d' % (emotion, level))
        else:
            rospy.logwarn('Unknown emotion: %s' % str(emotion))

        return self

    def pitch(self, pitch):
        """
        Change pitch.
        :param pitch: Amount of pitch
        :type pitch: int
        :rtype: VoiceText
        """
        if isinstance(pitch, int):
            if pitch < 50:
                pitch = 50
            elif 200 < pitch:
                pitch = 200
            self._data['pitch'] = pitch
            rospy.loginfo('Pitch = %s' % pitch)

        return self

    def speed(self, speed):
        """
        Change speed.
        :param speed: Amount of speed
        :type speed: int
        :rtype: VoiceText
        """
        if isinstance(speed, int):
            if speed < 50:
                speed = 50
            elif 400 < speed:
                speed = 400
            self._data['speed'] = speed
            rospy.loginfo('Speed = %s' % speed)

        return self

    def volume(self, volume):
        """
        Change volume.
        :param volume: Amount of volume
        :type volume: int
        :rtype: VoiceText
        """
        if isinstance(volume, int):
            if volume < 50:
                volume = 50
            elif 200 < volume:
                volume = 200
            self._data['Volume'] = volume
            rospy.loginfo('Volume = %s' % volume)

        return self

    def to_wave(self, text):
        """
        Convert text to wave binary.
        :param text: Text to synthesize
        :type text: str
        :return: bytearray
        """
        self._data['text'] = text
        rospy.logdebug('Post = %s' % str(self._data))
        request = requests.post(self.URL, self._data, auth=self._auth)
        rospy.logdebug('Status = %d' % request.status_code)
        if request.status_code != requests.codes.ok:
            rospy.logerr('Invalid status code: %d' % request.status_code)
            raise Exception('Invalid status code: %d' % request.status_code)
        return request.content

    def speak(self, text):
        """
        Speak text.
        :param text: Text to synthesize
        :type text: str
        """
        path = '/tmp/text.wav'
        with open(path, 'wb') as temp:
            temp.write(self.to_wave(text))

        temp = wave.open(path)
        stream = self._audio.open(
            format=self._audio.get_format_from_width(temp.getsampwidth()),
            channels=temp.getnchannels(),
            rate=temp.getframerate(),
            output=True)
        rospy.loginfo('Text = %s' % text)
        data = temp.readframes(self.CHUNK)
        while data:
            stream.write(data)
            data = temp.readframes(min(data, self.CHUNK))
        stream.close()
        temp.close()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description=VoiceText.__name__)
    parser.add_argument('--user', type=str, default='', help='user name')
    args, unknown = parser.parse_known_args()

    vt = VoiceText(user_name=args.user)
