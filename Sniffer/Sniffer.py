from PySide6.QtCore import Signal, QObject
from scapy.all import AsyncSniffer, UDP, IP, IPv6, DNS, ARP

class Sniffer(QObject):
    packet_received: Signal(dict) = Signal(dict)
    async_sniffer: AsyncSniffer

    def __init__(self):
        super().__init__()

        # Flags
        self._is_sniffing = False

    def start_sniffing(self, iface_name : str, bpf : str = ""):
        """
            Runs the sniffer. Captures useful UDP packets. Emits Sniffer.packet_received signal when a suitable packet is found.
        """
        if self._is_sniffing: return
        self._is_sniffing = True
        
        try:
            self.async_sniffer = AsyncSniffer(
                iface=iface_name,
                filter=bpf,
                prn=self._packet_callback
            )

            self.async_sniffer.start()

            self._is_sniffing = True
        except PermissionError as e: print(f"Sniffing permission error: {e}")
        except Exception as e: print(f"Sniffing exception: {e}")
        #finally:
        #    self._is_sniffing = False
        
    def stop_sniffing(self):
        """
            Sets the _is_sniffing flag to False and attempts to stop the asynchronous sniffer.
        """
        if not self._is_sniffing: return

        self._is_sniffing = False

        try:
            self.async_sniffer.stop()
        except Exception as e:
            print(f"Error trying AsyncSniffer.stop(): {e}")

    def _packet_callback(self, packet):
        """
            Fires the packet_received signal if a suitable packet is received.
            Emits a dict with these fields: local_port : str, ip : str, port : str
        """
        # Drop unwanted packets
        if packet.haslayer(DNS) or packet.haslayer(ARP):
            return

        # Handle IPv4/6, or return
        if packet.haslayer(IP): src_ip = packet[IP].src
        elif packet.haslayer(IPv6): src_ip = packet[IPv6].src
        else:
            print(f"[DEBUG] Received non-IP/IPv6 UDP packet: {packet.summary()}")
            return
        
        # Emit if packet is UDP
        if packet.haslayer(UDP):
            src_port = str(packet[UDP].sport)
            dst_port = str(packet[UDP].dport)

            self.packet_received.emit({"local_port":dst_port, "ip":src_ip, "port":src_port})
