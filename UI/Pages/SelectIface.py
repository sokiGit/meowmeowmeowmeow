from pickle import EMPTY_LIST

from PySide6 import QtWidgets, QtCore

from Components.tableView import TableView
from UI.Pages.Sniffing import Sniffing
from UI.Page import Page
from UI.Pager import Pager
from Utils.IfaceManager import get_ifaces, get_iface_from_name
from Sniffer.SnifferConfig import SnifferConfig


class SelectIface(Page):
    def __init__(self, pager: Pager):
        super().__init__(pager)

    def _construct_callback(self):
        sniff_notice = QtWidgets.QLabel(
            text="Select an interface by clicking a row in the table, then click the Select button.")
        self._parent.addWidget(sniff_notice)

        bpf_preset_dropdown = QtWidgets.QComboBox()
        for txt in ["None", "GTA V", "UDP", "TCP", "Non-Self"]: bpf_preset_dropdown.addItem(txt)
        bpf_preset_dropdown.setCurrentIndex(0)

        self._parent.addWidget(bpf_preset_dropdown)

        # :3
        ifaces_table = TableView(3, ["Interface Name", "Description", "IP Addresses"])

        for ifaceInfo in get_ifaces():
            ifaces_table.add_row([ifaceInfo.get_name(), ifaceInfo.get_description(), ifaceInfo.get_ips().__str__()
                                 .removeprefix("[").removesuffix("]").replace("'", "")])

        ifaces_table.selectRow(0)
        self._parent.addWidget(ifaces_table)
        ifaces_table.resizeColumnsToContents()
        # :3c

        select_btn = QtWidgets.QPushButton()
        select_btn.setText("Select")

        def finish_selection():
            selected_row = ifaces_table.selectedIndexes()[0].row()
            selected_iface_item = ifaces_table.item(selected_row, 0)

            if not selected_iface_item:
                print("No interface row selected, select a row and try again.")
                return

            selected_iface = get_iface_from_name(selected_iface_item.text())
            if not selected_iface:
                print(f"Iface {selected_iface_item.text()} not found by IfaceManager.")

            iface_ips = selected_iface.get_ips()
            # TODO implement choosing or remove completely
            selected_local_ip = iface_ips[0] if iface_ips is not EMPTY_LIST else ""

            self._parent.removeWidget(sniff_notice)
            sniff_notice.deleteLater()

            self._parent.removeWidget(bpf_preset_dropdown)
            bpf_preset_dropdown.deleteLater()

            self._parent.removeWidget(ifaces_table)
            ifaces_table.deleteLater()

            self._parent.removeWidget(select_btn)
            select_btn.deleteLater()

            bpf_presets = {
                "None": "",
                "GTA V": f"(udp) and (dst {selected_local_ip}) and (src not {selected_local_ip}) and (src portrange not 0-1023)",
                "TCP": "tcp",
                "UDP": "udp",
                "Non-Self": f"(src not {selected_local_ip}) and (src not 127.0.0.1)"
                #TODO use 127.XXX.XXX.XXX range for loopback
            }

            selected_bpf_preset = bpf_preset_dropdown.currentText()
            bpf = "" if not selected_bpf_preset in bpf_presets.keys() else bpf_presets[selected_bpf_preset]

            SnifferConfig.iface = selected_iface
            SnifferConfig.bpf = bpf

            self._pager.navigate_to(Sniffing)

        select_btn.clicked.connect(finish_selection)
        ifaces_table.enterPressed.connect(finish_selection)

        self._parent.addWidget(select_btn)

        QtCore.QTimer.singleShot(0, lambda: ifaces_table.selectRow(0))

        # Add to self to be usable in _remove_callback
        self._select_btn = select_btn
        self._ifaces_table = ifaces_table

    def _remove_callback(self):
        pass