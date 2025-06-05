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

def get_iface_from_name(name: str) -> Iface | None:
    #TODO improve performance (caching?)
    for iface in get_ifaces():
        if iface.get_name() == name:
            return iface

    return None