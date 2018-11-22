# -*- coding: utf-8 -*-

from  ParserConfig.parser import Parser
from PB.playback import PlaybackScript
import time
import sys

if __name__ == '__main__':

    try:
        parser = Parser()
        devices = parser.getDevices()
        if len(sys.argv) > 1:
            id = sys.argv[1]
            targetDevice = None
            for device in devices:
                if device.deviceID == id:
                    targetDevice = device
                    break
            if targetDevice:
                playbackScript = PlaybackScript(device=targetDevice)
                playbackScript.start()
                playbackScript.join()
            else:
                print 'Error:Target device {id} not found'.format(id=id)
        else:
            playbackThreads=[]
            for device in devices:
                playbackScript = PlaybackScript(device=device)
                playbackThreads.append(playbackScript)
            for pbThread in playbackThreads:
                pbThread.start()
                time.sleep(2)
            for pbThread in playbackThreads:
                pbThread.join()
    except BaseException ,e:
        print 'Error:' + str(e)






