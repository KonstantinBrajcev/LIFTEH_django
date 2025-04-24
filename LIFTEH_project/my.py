import psutil

def find_process_using_port(port):
    for proc in psutil.process_iter(['pid', 'name', 'connections']):
        for conn in proc.info['connections']:
            if conn.laddr.port == port:
                print(f"Процесс {proc.info['name']} (PID: {proc.info['pid']}) использует порт {port}")

port_to_check = 8000
find_process_using_port(port_to_check)
