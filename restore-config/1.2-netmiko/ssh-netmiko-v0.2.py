import yaml
from netmiko import ConnectHandler
import os

# Đọc danh sách thiết bị từ file YAML
with open('devices.yml', 'r') as ymlfile:
    devices = yaml.safe_load(ymlfile)

# Đường dẫn thư mục chứa file backup
backup_dir = r"I:\02_Job\python\Python_networking\python-scripts\backup-config\1.2-netmiko"

for device in devices:
    try:
        # Kết nối để lấy hostname thực tế từ thiết bị
        net_connect = ConnectHandler(**device)
        hostname_line = net_connect.send_command("show run | include hostname")
        if "hostname" in hostname_line:
            hostname = hostname_line.split()[1].strip()
        else:
            hostname = device.get('host', 'R1')
        net_connect.disconnect()

        # Tìm file backup mới nhất cho từng thiết bị (theo hostname thực tế)
        backup_files = [f for f in os.listdir(backup_dir) if f.startswith(hostname + '_') and f.endswith('.txt')]
        if not backup_files:
            print(f"Không tìm thấy file backup nào cho {hostname} trong thư mục: {backup_dir}")
            continue
        backup_files.sort(key=lambda x: os.path.getmtime(os.path.join(backup_dir, x)), reverse=True)
        restore_file = os.path.join(backup_dir, backup_files[0])
        print(f"Sẽ restore cho {hostname} ({device['host']}) từ file: {restore_file}")

        with open(restore_file, "r") as f:
            config_lines = f.read().splitlines()

        # Kết nối lại để gửi cấu hình
        net_connect = ConnectHandler(**device)
        output = net_connect.send_config_set(config_lines)
        net_connect.save_config()
        net_connect.disconnect()

        with open("restore.log", "a") as logf:
            logf.write(f"Successfully restored configuration to device {device['host']} from {restore_file}\n")
        print(f"✓ Đã restore cấu hình cho {hostname} ({device['host']}) từ file {restore_file}")
    except Exception as e:
        with open("restore.log", "a") as logf:
            logf.write(f"Failed to restore configuration to device {device.get('host', 'unknown')} from {restore_file}: {e}\n")
        print(f"✗ {hostname} ({device.get('host', 'unknown')}): Lỗi restore - {e}")
