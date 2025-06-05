import threading

from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtWidgets import QMenuBar

from Components.tableView import TableView
from Sniffer.SniffManager import SniffManager
from UI.Page import Page
from UI import Pages
from Utils.SnifferConfig import SnifferConfig
from Utils.getIpInfo import get_ip_info


class Sniffing(Page):
    def __init__(self, pager: Page):
        super().__init__(pager)

    def _construct_callback(self):
        iface = SnifferConfig.iface.get_name()
        bpf = SnifferConfig.bpf
        local_ip = SnifferConfig.iface.get_ips()[0]

        # Create widgets
        sniff_notice = QtWidgets.QLabel(text=f"Capturing packets on {iface}, filter: {bpf}")
        sniff_table = TableView(5, ["Remote IP", "Location", "ISP", "Flags", "Packet Count"])
        topbar = QMenuBar(nativeMenuBar=True)

        # Add widgets to layout
        self._parent.addWidget(topbar)
        self._parent.addWidget(sniff_notice)
        self._parent.addWidget(sniff_table)

        # Request window title change
        self.change_title.emit(f"iface: {iface}, local_ip: {SnifferConfig.iface.get_ips()[0]}")

        # Add topbar menu item for the Sniffer
        sniffer_menu = topbar.addMenu("&Sniffer")

        pause_resume_action = QtGui.QAction(text="&Pause Sniffer", parent=sniffer_menu)
        iface_selection_action = QtGui.QAction(text="Go to iface &selection", parent=sniffer_menu)
        clear_table_action = QtGui.QAction(text="&Clear table", parent=sniffer_menu)

        sniffer_menu.addAction(pause_resume_action)
        sniffer_menu.addAction(iface_selection_action)
        sniffer_menu.addAction(clear_table_action)

        # Socket pair cache
        socket_pair_cache = {}

        def sniff_callback(data: dict):
            # Retrieve cached socket pair
            socket_pair_id = data.get("ip")

            # Check whether socket pair has been cached
            if socket_pair_id in socket_pair_cache.keys():
                # This socket pair is cached, return
                socket_pair_cache[socket_pair_id]["packet_count"] += 1
                sniff_table.modify_item(socket_pair_cache[socket_pair_id]["row"], 4,
                                        str(socket_pair_cache[socket_pair_id]["packet_count"]))
                return
            else:
                # Create row for new socket pair, cache the new socket pair.

                # Don't show T2's servers
                # TODO Find out T2 ip ranges and make it range-based
                if data.get("ip") in ["192.81.241.191", "185.56.65.167", "185.56.65.171", "185.56.65.170",
                                      "185.56.65.169"]:
                    return

                #  Add new row to sniff_table
                row_index = sniff_table.add_row([data.get("ip"), "N/A", "N/A", "", "1"])

                # Add to cache
                socket_pair_cache[socket_pair_id] = {"packet_count": 1, "row": row_index}

                def update_row_with_ip_info():
                    try:
                        ip_api_data = get_ip_info(data.get("ip"))

                        if not ip_api_data:
                            ip_api_data = {
                                "country": "N/A",
                                "regionName": "N/A",
                                "city": "N/A",
                                "isp": "N/A",
                                "proxy": False
                            }

                        sniff_table.modify_item(row_index, 1,
                                                f"{ip_api_data.get("country")}, {ip_api_data.get("regionName")},{ip_api_data.get("city")}")
                        sniff_table.modify_item(row_index, 2, ip_api_data.get("isp"))
                        sniff_table.modify_item(row_index, 3, "Proxy" if ip_api_data.get("proxy") else "")
                    except Exception as e:
                        print(f"Thread exception when updating row {row_index} with info from ip-api: {e}")

                try:
                    threading.Thread(target=update_row_with_ip_info, daemon=True).start()
                except Exception as ex:
                    print(f"Exception starting thread for row {row_index}: {ex}")

        # Create sniff_manager and connect packet_received callback
        sniff_manager = SniffManager(iface_name=iface, bpf=bpf)
        sniff_manager.packet_received.connect(sniff_callback)
        self._sniff_manager = sniff_manager

        # Start new sniffer thread
        sniff_manager.start_sniffing()

        # Connect Sniffer menu actions
        def go_to_iface_selection():
            sniff_manager.stop_sniffing()

            self._parent.removeWidget(sniffer_menu)
            self._parent.removeWidget(sniff_notice)
            self._parent.removeWidget(sniff_table)

            sniffer_menu.deleteLater()
            sniff_notice.deleteLater()
            sniff_table.deleteLater()

            # self.prompt_iface_selection()
            self._pager.navigate_to(Pages.SelectIface.SelectIface)

        iface_selection_action.triggered.connect(go_to_iface_selection)

        def resume_sniffer():
            sniff_manager.start_sniffing()

            pause_resume_action.setText("&Pause Sniffer")
            pause_resume_action.triggered.connect(pause_sniffer, type=QtCore.Qt.ConnectionType.SingleShotConnection)

            self.change_title.emit(f"iface: {iface}, local_ip: {local_ip}")

        def pause_sniffer():
            sniff_manager.stop_sniffing()

            pause_resume_action.setText("&Resume Sniffer")
            pause_resume_action.triggered.connect(resume_sniffer, type=QtCore.Qt.ConnectionType.SingleShotConnection)

            self.change_title.emit(f"[PAUSED] iface: {iface}, local_ip: {local_ip}")

        pause_resume_action.triggered.connect(pause_sniffer, type=QtCore.Qt.ConnectionType.SingleShotConnection)

        def clear_sniffer_table():
            sniff_table.setRowCount(0)

            socket_pair_cache.clear()

            sniff_table.insertRow(0)
            sniff_table.selectRow(0)

        clear_table_action.triggered.connect(clear_sniffer_table)

        # Select first row (to allow arrow selection)
        sniff_table.selectRow(0)
        QtCore.QTimer.singleShot(0, sniff_table.setFocus)  # What the F#@K

    def _remove_callback(self):
        self._sniff_manager.stop_sniffing()
