from napalm import get_network_driver
import os

# Đường dẫn thư mục chứa file backup
backup_dir = r"I:\02_Job\python\Python_networking\python-scripts\backup-config\1.3-napalm"

# Tìm file backup mới nhất trong thư mục
backup_files = [f for f in os.listdir(backup_dir) if f.endswith('.txt')]
if not backup_files:
    print("Không tìm thấy file backup nào trong thư mục:", backup_dir)
    exit(1)

backup_files.sort(key=lambda x: os.path.getmtime(os.path.join(backup_dir, x)), reverse=True)
restore_file = os.path.join(backup_dir, backup_files[0])
print("Sẽ restore từ file:", restore_file)

# Thông tin thiết bị (lưu ý: device_type cho napalm là 'ios')
device = {
    "hostname": "192.168.1.9",
    "username": "admin",
    "password": "cisco",
}

with open(restore_file, "r") as f:
    config_data = f.read()

try:
    driver = get_network_driver("ios")
    napalm_device = driver(
        hostname=device["hostname"],
        username=device["username"],
        password=device["password"]
    )
    napalm_device.open()

    # Gửi cấu hình lên thiết bị (replace candidate config, sau đó commit)
    napalm_device.load_replace_candidate(config=config_data)
    diffs = napalm_device.compare_config()
    if diffs:
        print("Các thay đổi sẽ được áp dụng:\n", diffs)
        napalm_device.commit_config()
        print(f"✓ Đã restore cấu hình cho {device['hostname']} từ file {restore_file}")
        with open("restore.log", "a") as logf:
            logf.write(f"Successfully restored configuration to device {device['hostname']} from {restore_file}\n")
    else:
        print("Không có thay đổi nào cần áp dụng.")
        napalm_device.discard_config()
    napalm_device.close()
except Exception as e:
    with open("restore.log", "a") as logf:
        logf.write(f"Failed to restore configuration to device {device['hostname']} from {restore_file}: {e}\n")
    print(f"✗ Lỗi restore: {e}")