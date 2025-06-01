from scapy.all import get_working_ifaces

def GetInterfaces():
    try:
        return get_working_ifaces()
    except Exception as e:
        print(f"Err listing ifaces (try sudo?): {e}")
        return None
