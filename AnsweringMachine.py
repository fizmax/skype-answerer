__author__ = 'max'

import time
import os

import Skype4Py

CallIsFinished = {Skype4Py.clsFailed, Skype4Py.clsFinished, Skype4Py.clsMissed, Skype4Py.clsRefused, Skype4Py.clsBusy,
                  Skype4Py.clsCancelled}

class AnsweringMachine:
    def __init__(self):
        self.WavFile = os.path.abspath('outofoffice.wav')       # File with reply
        self.IncomingCallsDir = os.path.abspath('incoming')     # Folder with recordings
        self.time2wait = 15                                     # Time to wait before autoansering
        self.callsanswered = dict()                             # Dictionary to hold incoming calls state
        if not os.path.exists(self.IncomingCallsDir):
            os.mkdir(self.IncomingCallsDir)

    def OnCall(self, call, status):
        if status == Skype4Py.clsRinging and call.Type.startswith('INCOMING'):
            print 'Incoming call from:', call.PartnerHandle
            time.sleep(self.time2wait)
            if call.Duration == 0:
                try:
                    call.Answer()
                except:
                    pass
                self.callsanswered[call.Id] = 'Answered'
            else:
                self.callsanswered[call.Id] = 'HumanAnswered'

        if status == Skype4Py.clsInProgress and self.callsanswered[call.Id] == 'Answered':
            self.callsanswered[call.Id] = 'Playing'
            print ' playing ' + self.WavFile
            call.InputDevice(Skype4Py.callIoDeviceTypeFile, self.WavFile)
        if status in CallIsFinished:
            print 'call ', status.lower()

    def OnInputStatusChanged(self, call, status):
        if not status and 'FILE' in call.InputDevice() and call.InputDevice()['FILE'] == self.WavFile \
                and self.callsanswered[call.Id] == 'Playing':
            self.callsanswered[call.Id] = 'Recording'
            print ' play finished'
            if not os.path.exists(self.IncomingCallsDir + call.PartnerHandle):
                os.mkdir(self.IncomingCallsDir + call.PartnerHandle)
            OutFile = self.IncomingCallsDir + call.PartnerHandle + '/' + time.strftime("%Y-%m-%d_%H-%M-%S") + '.wav'
            call.InputDevice(Skype4Py.callIoDeviceTypeFile, None)
            print ' recording ' + OutFile
            call.OutputDevice(Skype4Py.callIoDeviceTypeFile, OutFile)


def OnAttach(status):
    global skype
    print 'Attachment status: ' + skype.Convert.AttachmentStatusToText(status)
    if status == Skype4Py.apiAttachAvailable:
        skype.Attach()


def main():
    global skype
    am = AnsweringMachine()
    skype = Skype4Py.Skype()
    skype.OnAttachmentStatus = OnAttach
    skype.OnCallStatus = am.OnCall
    skype.OnCallInputStatusChanged = am.OnInputStatusChanged

    if not skype.Client.IsRunning:
        print 'Starting Skype..'
        skype.Client.Start()

    print 'Connecting to Skype process..'
    skype.Attach()
    print 'Waiting for incoming calls'
    try:
        while True:
            time.sleep(1)
    except:
        pass


if __name__ == '__main__':
    main()