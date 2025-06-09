"""
Provides a consistent way of using ifaces and getting their information like name, description and ip list.
Is used to remove any inconsistencies that might come from using different libraries.
"""

class Iface:
    _name: str = "N/A"
    _description: str = "N/A"
    _ips: list[str] = list()

    def __init__(self, name: str, description: str, ips: list[str]):
        self._name = name
        self._description = description
        self._ips = ips

    def get_name(self) -> str:
        return self._name or "N/A"

    def get_description(self) -> str:
        return self._description or "N/A"

    def get_ips(self) -> list[str]:
        return self._ips

    def __str__(self):
        return f"Iface {self.get_name()}, description: {self.get_description()}, ips: {self.get_ips()}"