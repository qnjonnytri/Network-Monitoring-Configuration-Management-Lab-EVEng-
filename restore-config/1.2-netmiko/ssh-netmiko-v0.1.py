
from netmiko import ConnectHandler
import os

# Đường dẫn thư mục chứa file backup
backup_dir = r"I:\02_Job\python\Python_networking\python-scripts\backup-config\1.2-netmiko"

# Tìm file backup mới nhất trong thư mục
backup_files = [f for f in os.listdir(backup_dir) if f.endswith('.txt')]
if not backup_files:
    print("Không tìm thấy file backup nào trong thư mục:", backup_dir)
    exit(1)

# Sắp xếp theo thời gian chỉnh sửa, lấy file mới nhất
backup_files.sort(key=lambda x: os.path.getmtime(os.path.join(backup_dir, x)), reverse=True)
restore_file = os.path.join(backup_dir, backup_files[0])
print("Sẽ restore từ file:", restore_file)

# Thông tin thiết bị
device = {
    "device_type": "cisco_ios",
    "host": "192.168.1.9",
    "username": "admin",
    "password": "cisco",
}

with open(restore_file, "r") as f:
    config_lines = f.read().splitlines()

try:
    net_connect = ConnectHandler(**device)
    output = net_connect.send_config_set(config_lines)
    net_connect.save_config()
    net_connect.disconnect()

    with open("restore.log", "a") as logf:
        logf.write(f"Successfully restored configuration to device {device['host']} from {restore_file}\n")
    print(f"✓ Đã restore cấu hình cho {device['host']} từ file {restore_file}")
except Exception as e:
    with open("restore.log", "a") as logf:
        logf.write(f"Failed to restore configuration to device {device['host']} from {restore_file}: {e}\n")
    print(f"✗ Lỗi restore: {e}")