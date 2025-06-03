from PySide6 import QtWidgets, QtGui, QtCore
from PySide6.QtCore import QObject
from PySide6.QtWidgets import QLayout, QMenuBar

from Components.tableView import TableView
from Utils.getInterfaces import get_interfaces
from Sniffer.sniffer import Sniffer
from Utils.getIpInfo import get_ip_info
import threading

class Manager(QObject):
    layout : QLayout
    topbar : QMenuBar

    request_change_title = QtCore.Signal(str)

    def __init__(self, layout : QLayout):
        super().__init__()
        self.layout = layout

    def prompt_iface_selection(self):
        sniff_notice = QtWidgets.QLabel(
            text="Select an interface by clicking a row in the table, then click the Select button.")
        self.layout.addWidget(sniff_notice)

        # :3
        ifaces_table = TableView(3, ["Interface Name", "Description", "IP Address"])

        for ifaceInfo in get_interfaces():
            ifaces_table.add_row([ifaceInfo.name, ifaceInfo.description, ifaceInfo.ip])

        ifaces_table.selectRow(0)
        self.layout.addWidget(ifaces_table)
        ifaces_table.resizeColumnsToContents()
        # :3c

        select_btn = QtWidgets.QPushButton()
        select_btn.setText("Select")

        def finish_selection():
            selected_row = ifaces_table.selectedIndexes()[0].row()
            selected_iface_item = ifaces_table.item(selected_row, 0)
            selected_local_ip_item = ifaces_table.item(selected_row, 2)

            if not selected_iface_item:
                print("No interface row selected, select a row and try again.")
                return

            selected_iface = selected_iface_item.text()
            selected_local_ip = selected_local_ip_item.text()

            self.layout.removeWidget(sniff_notice)
            sniff_notice.deleteLater()

            self.layout.removeWidget(ifaces_table)
            ifaces_table.deleteLater()

            self.layout.removeWidget(select_btn)
            select_btn.deleteLater()

            self.sniff_on_iface(selected_iface, selected_local_ip)

        select_btn.clicked.connect(finish_selection)

        ifaces_table.enterPressed.connect(finish_selection)

        self.layout.addWidget(select_btn)

    def create_topbar(self):
        self.topbar = QMenuBar(nativeMenuBar=True)
        self.layout.addWidget(self.topbar)

    def sniff_on_iface(self, iface: str, local_ip: str):
        # Create widgets
        sniff_notice = QtWidgets.QLabel(text=f"Sniffing incoming UDP datagrams on interface {iface}")
        sniff_table = TableView(5, ["Remote IP", "Location", "ISP", "Flags", "Packet Count"])

        # Add widgets to layout
        self.layout.addWidget(sniff_notice)
        self.layout.addWidget(sniff_table)

        # Request window title change
        self.request_change_title.emit(f"iface: {iface}, local_ip: {local_ip}")

        # Add topbar menu item for the Sniffer
        sniffer_menu = self.topbar.addMenu("&Sniffer")

        pause_resume_action = QtGui.QAction(text="&Pause Sniffer", parent=sniffer_menu)
        iface_selection_action = QtGui.QAction(text="Go to iface &selection", parent=sniffer_menu)

        sniffer_menu.addAction(pause_resume_action)
        sniffer_menu.addAction(iface_selection_action)

        # Socket pair cache
        socket_pair_cache = {}

        def sniff_callback(data: dict):
            # Retrieve cached socket pair
            #socket_pair_id = f"{data.get("local_port")}|{data.get("ip")}|{data.get("port")}"

            socket_pair_id = data.get("ip")

            # Check whether socket pair has been cached
            if socket_pair_id in socket_pair_cache.keys():
                # This socket pair is cached, return
                socket_pair_cache[socket_pair_id]["packet_count"] += 1
                sniff_table.modify_item(socket_pair_cache[socket_pair_id]["row"], 4, str(socket_pair_cache[socket_pair_id]["packet_count"]))
                return
            else:
                # Create row for new socket pair, cache the new socket pair.

                # Don't show T2's servers
                # TODO Find out T2 ip ranges and make it range-based
                if data.get("ip") in ["192.81.241.191", "185.56.65.167", "185.56.65.171", "185.56.65.170", "185.56.65.169"]:
                    return

                #  Add new row to sniff_table
                row_index = sniff_table.add_row([
                    data.get("ip"),
                    "N/A",
                    "N/A",
                    "",
                    "Untracked"
                ])

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
                                                f"{ip_api_data.get("country")}, {ip_api_data.get("regionName")}, {ip_api_data.get("city")}")
                        sniff_table.modify_item(row_index, 2, ip_api_data.get("isp"))
                        sniff_table.modify_item(row_index, 3, "Proxy" if ip_api_data.get("proxy") else "")
                    except Exception as e:
                        print(f"Thread exception when updating row {row_index} with info from ip-api: {e}")

                try:
                    threading.Thread(target=update_row_with_ip_info, daemon=True).start()
                except Exception as e:
                    print(f"Exception starting thread for row {row_index}: {e}")

        # Create sniffer and connect packet_received callback
        # TODO make sniffer accept only iface, not local ip
        sniffer = Sniffer()
        sniffer.packet_received.connect(sniff_callback)

        # Start new sniffer thread
        #bpf = f"(udp) and (dst {local_ip}) and (src not {local_ip}) and (src portrange not 0-1023)"
        bpf = ""
        sniffer.start_sniffing(iface_name=iface, bpf = bpf)

        # Connect Sniffer menu actions
        def go_to_iface_selection():
            sniffer.stop_sniffing()

            self.layout.removeWidget(sniffer_menu)
            self.layout.removeWidget(sniff_notice)
            self.layout.removeWidget(sniff_table)

            sniffer_menu.deleteLater()
            sniff_notice.deleteLater()
            sniff_table.deleteLater()

            self.prompt_iface_selection()

        iface_selection_action.triggered.connect(go_to_iface_selection)

        def resume_sniffer():
            sniffer.start_sniffing(iface, bpf=bpf)

            pause_resume_action.setText("&Pause Sniffer")
            pause_resume_action.triggered.connect(pause_sniffer, type=QtCore.Qt.ConnectionType.SingleShotConnection)

            self.request_change_title.emit(f"iface: {iface}, local_ip: {local_ip}")

        def pause_sniffer():
            sniffer.stop_sniffing()

            pause_resume_action.setText("&Resume Sniffer")
            pause_resume_action.triggered.connect(resume_sniffer, type=QtCore.Qt.ConnectionType.SingleShotConnection)

            self.request_change_title.emit(f"[PAUSED] iface: {iface}, local_ip: {local_ip}")

        pause_resume_action.triggered.connect(pause_sniffer, type=QtCore.Qt.ConnectionType.SingleShotConnection)