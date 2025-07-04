"""
Provides a simple way to handle advanced controls of the sniffer.
"""
from PySide6.QtCore import Signal, QObject

from Sniffer.Sniffer import Sniffer
from Sniffer.SnifferConfig import SnifferConfig
from Utils.Iface import Iface


class SniffManager(QObject):
    _iface: Iface | None = None
    _bpf: str
    _sniffing: bool
    _sniffer: Sniffer
    packet_received: Signal(dict)
    sniffing_stopped: Signal() = Signal()
    sniffing_started: Signal() = Signal()

    def __init__(self, ):
        super().__init__()
        self._iface = SnifferConfig.iface
        self._bpf = SnifferConfig.bpf
        self._sniffing = False
        self._sniffer = Sniffer()
        self.packet_received = self._sniffer.packet_received

    def start_sniffing(self):
        if self._sniffing: return
        self._sniffing = True
        self._sniffer.start_sniffing(self._iface, self._bpf)
        self.sniffing_started.emit()

    def stop_sniffing(self):
        if not self._sniffing: return
        self._sniffer.stop_sniffing()
        self._sniffing = False
        self.sniffing_stopped.emit()

    def change_iface(self, iface: Iface):
        self._iface = iface
        SnifferConfig.iface = iface

        if self._sniffing:
            # Restart sniffer if it is currently running
            self._sniffer.stop_sniffing()
            self._sniffer.start_sniffing(self._iface, self._bpf)

    def change_bpf(self, bpf: str):
        self._bpf = bpf

        if self._sniffing:
            # Restart sniffer if it is currently running
            self._sniffer.stop_sniffing()
            self._sniffer.start_sniffing(self._iface, self._bpf)