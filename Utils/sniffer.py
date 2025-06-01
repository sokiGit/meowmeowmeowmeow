from PySide6.QtCore import Signal, QObject
from scapy.all import AsyncSniffer, UDP, IP, IPv6, DNS, ARP
import time

class Sniffer(QObject):
    packet_received = Signal(dict)
    async_sniffer : AsyncSniffer

    def __init__(self, iface_name : str, local_ip : str):
        super().__init__()
        
        # Properties
        self.iface_name = iface_name
        self.local_ip = local_ip

        # Flags
        self._is_sniffing = False

    def start_sniffing(self):
        '''
            Runs the sniffer. Captures useful UDP packets. Emits Sniffer.packet_received singal when a suitable packet is found.
            Thread this method.
        '''
        if self._is_sniffing: return
        self._is_sniffing = True
        
        try:
            self.async_sniffer = AsyncSniffer(
                iface=self.iface_name,
                filter=f"(udp) and (dst {self.local_ip}) and (src not {self.local_ip}) and (src portrange not 0-1023)",
                #filter="udp",
                #filter=f"(dst {self.local_ip}) and (src not {self.local_ip})",
                prn=self._packet_callback
            )

            self.async_sniffer.start()
        except PermissionError as e: print(f"Sniffing permission error: {e}")
        except Exception as e: print(f"Sniffing exception: {e}")
        finally:
            self._is_sniffing = False
        
    def stop_sniffing(self):
        '''
            Sets the _is_sniffing flag to False and attempts to stop the asynchronous sniffer.
        '''
        self._is_sniffing = False
        try:
            self.async_sniffer.stop()
        except Exception as e:
            print(f"Error trying AsyncSniffer.stop(): {e}")

    def _packet_callback(self, packet):
        '''
            Fires the packet_received signal if a suitable packet is received.
            Emits a dict with these fields: local_port : str, ip : str, port : str
        '''

        # Drop unwanted packets
        if packet.haslayer(DNS) or packet.haslayer(ARP):
            return

        # Handle IPv4/6, or return
        src_ip = "N/A"

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
