"""
Provides a consistent way of getting interface info regardless of the underlying library.
Uses the custom Iface class to provide consistent interface information.
"""

from scapy.all import get_working_ifaces
from Utils.Iface import Iface

def get_ifaces() -> list[Iface]:
    ifaces: list[Iface] = []
    for iface in get_working_ifaces():
        print(iface.ips)
        ifaces.append(Iface(iface.name, iface.description, []))

    return ifaces