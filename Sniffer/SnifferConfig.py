from Utils.Iface import Iface


class SnifferConfig:
    iface : Iface | None = None
    bpf : str = ""