import xsensdeviceapi as xda
from threading import Lock

class XdaCallback(xda.XsCallback):
    def __init__(self, max_buffer_size=5):
        super().__init__()
        self.m_maxNumberOfPacketsInBuffer = max_buffer_size
        self.m_packetBuffer = []
        self.m_lock = Lock()

    def packetAvailable(self):
        with self.m_lock:
            return len(self.m_packetBuffer) > 0

    def getNextPacket(self):
        with self.m_lock:
            assert len(self.m_packetBuffer) > 0
            return xda.XsDataPacket(self.m_packetBuffer.pop(0))

    def onLiveDataAvailable(self, dev, packet):
        with self.m_lock:
            assert packet != 0
            while len(self.m_packetBuffer) >= self.m_maxNumberOfPacketsInBuffer:
                self.m_packetBuffer.pop()
            self.m_packetBuffer.append(xda.XsDataPacket(packet))