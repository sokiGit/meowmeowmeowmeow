from PySide6 import QtWidgets, QtGui, QtCore
from PySide6.QtCore import QObject
from PySide6.QtWidgets import QLayout, QMenuBar
from Components.tableView import TableView
from Utils.getInterfaces import GetInterfaces
from Utils.sniffer import Sniffer
from Utils.getIpInfo import GetIpInfo
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
        ifacesTable = TableView(3, ["Interface Name", "Description", "IP Address"])

        for ifaceInfo in GetInterfaces():
            ifacesTable.addRow([ifaceInfo.name, ifaceInfo.description, ifaceInfo.ip])

        ifacesTable.table.selectRow(0)
        self.layout.addWidget(ifacesTable.table)
        ifacesTable.table.resizeColumnsToContents()
        # :3c

        select_btn = QtWidgets.QPushButton()
        select_btn.setText("Select")

        def finish_selection():
            selected_row = ifacesTable.table.selectedIndexes()[0].row()
            selected_iface_item = ifacesTable.table.item(selected_row, 0)
            selected_local_ip_item = ifacesTable.table.item(selected_row, 2)

            if not selected_iface_item:
                print("No interface row selected, select a row and try again.")
                return

            selected_iface = selected_iface_item.text()
            selected_local_ip = selected_local_ip_item.text()

            self.layout.removeWidget(sniff_notice)
            sniff_notice.deleteLater()

            self.layout.removeWidget(ifacesTable.table)
            ifacesTable.table.deleteLater()

            self.layout.removeWidget(select_btn)
            select_btn.deleteLater()

            self.sniff_on_iface(selected_iface, selected_local_ip)

        select_btn.clicked.connect(finish_selection)

        self.layout.addWidget(select_btn)

    def create_topbar(self):
        self.topbar = QMenuBar(nativeMenuBar=True)
        self.layout.addWidget(self.topbar)

    def sniff_on_iface(self, iface: str, local_ip: str):
        # Create widgets
        sniff_notice = QtWidgets.QLabel(text=f"Sniffing incoming UDP datagrams on interface {iface}")
        sniff_table = TableView(7,
                                ["Local Port", "Remote IP", "Remote Port", "Location", "ISP", "Flags", "Packet Count"])

        # Add widgets to layout
        self.layout.addWidget(sniff_notice)
        self.layout.addWidget(sniff_table.table)

        # Request window title change
        self.request_change_title.emit(f"iface: {iface}, local_ip: {local_ip}")

        # Add topbar menu item for the Sniffer
        sniffer_menu = self.topbar.addMenu("&Sniffer")

        kill_action = QtGui.QAction(text="&Kill Sniffer", parent=sniffer_menu)
        iface_selection_action = QtGui.QAction(text="Go to iface &selection", parent=sniffer_menu)

        sniffer_menu.addAction(kill_action)
        sniffer_menu.addAction(iface_selection_action)

        # Socket pair cache
        socket_pair_cache = []

        def sniff_callback(data: dict):
            # Retrieve cached socket pair
            socket_pair_id = f"{data.get("local_port")}|{data.get("ip")}|{data.get("port")}"

            # Check whether socket pair has been cached
            if socket_pair_id in socket_pair_cache:
                # This socket pair is cached, return
                return
                '''BROKEN CODE
                new_packet_count = cached_data.get("packet_count") + 1
                cached_data.set("packet_count", new_packet_count)
                sniff_table.modifyItem(cached_data.get("row"), 6, str(new_packet_count))
                '''
            else:
                socket_pair_cache.append(socket_pair_id)
                # Create row for new socket pair, cache the new socket pair.

                # Don't show T2's servers
                # TODO Find out T2 ip ranges and make it range-based
                if data.get("ip") in ["192.81.241.191", "185.56.65.167", "185.56.65.171", "185.56.65.170",
                                      "185.56.65.169"]: return

                #  Add new row to sniff_table
                row_index = sniff_table.addRow([
                    data.get("local_port"),
                    data.get("ip"),
                    data.get("port"),
                    "N/A",
                    "N/A",
                    "",
                    "Untracked"
                ])

                def update_row_with_ip_info():
                    try:
                        ip_api_data = GetIpInfo(data.get("ip"))

                        if not ip_api_data:
                            ip_api_data = {
                                "country": "N/A",
                                "regionName": "N/A",
                                "city": "N/A",
                                "isp": "N/A",
                                "proxy": False
                            }

                        sniff_table.modifyItem(row_index, 3,
                                               f"{ip_api_data.get("country")}, {ip_api_data.get("regionName")}, {ip_api_data.get("city")}")
                        sniff_table.modifyItem(row_index, 4, ip_api_data.get("isp"))
                        sniff_table.modifyItem(row_index, 5, "Proxy" if ip_api_data.get("proxy") else "")

                    except Exception as e:
                        print(f"Thread exception when updating row {row_index} with info from ip-api: {e}")

                try:
                    threading.Thread(target=update_row_with_ip_info, daemon=True).start()
                except Exception as e:
                    print(f"Exception starting thread for row {row_index}: {e}")

                '''BROKEN CODE
                # Cache the socket pair
                socket_pair_cache.set(socket_pair_id, {
                    "row": row_index,
                    "packet_count": 1
                })
                '''

        # Create sniffer and connect packet_received callback
        # TODO make sniffer accept only iface
        # TODO make sniffer accept args only when starting the sniffer to avoid having to re-instantiate it for every new iface
        sniffer = Sniffer(iface, local_ip)
        sniffer.packet_received.connect(sniff_callback)

        # Start new sniffer thread
        '''
        threading.Thread(
            target=sniffer.start_sniffing,
            daemon=True
        ).start()
        '''
        sniffer.start_sniffing()

        # Connect Sniffer menu actions
        kill_action.triggered.connect(sniffer.stop_sniffing)

        def go_to_iface_selection():
            sniffer.stop_sniffing()

            self.layout.removeWidget(sniffer_menu)
            self.layout.removeWidget(sniff_notice)
            self.layout.removeWidget(sniff_table.table)

            sniffer_menu.deleteLater()
            sniff_notice.deleteLater()
            sniff_table.table.deleteLater()

            self.prompt_iface_selection()

        iface_selection_action.triggered.connect(go_to_iface_selection)