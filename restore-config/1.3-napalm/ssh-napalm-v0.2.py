import yaml
from napalm import get_network_driver
import os

# Đọc danh sách thiết bị từ file YAML
with open('devices.yml', 'r') as ymlfile:
    devices = yaml.safe_load(ymlfile)

# Đường dẫn thư mục chứa file backup
backup_dir = r"I:\02_Job\python\Python_networking\python-scripts\backup-config\1.3-napalm"

for device in devices:
    try:
        driver = get_network_driver(device['device_type'])
        napalm_device = driver(
            hostname=device['host'],
            username=device['username'],
            password=device['password']
        )
        napalm_device.open()

        # Lấy hostname thực tế, fallback về device['host'] nếu không có
        facts = napalm_device.get_facts()
        hostname = facts.get('hostname', device['host'])

        # Tìm file backup mới nhất cho từng thiết bị (theo hostname)
        backup_files = [f for f in os.listdir(backup_dir) if f.startswith(hostname + '_') and f.endswith('.txt')]
        if not backup_files:
            print(f"Không tìm thấy file backup nào cho {hostname} trong thư mục: {backup_dir}")
            napalm_device.close()
            continue
        backup_files.sort(key=lambda x: os.path.getmtime(os.path.join(backup_dir, x)), reverse=True)
        restore_file = os.path.join(backup_dir, backup_files[0])
        print(f"Sẽ restore cho {hostname} ({device['host']}) từ file: {restore_file}")

        with open(restore_file, "r") as f:
            config_data = f.read()

        # Gửi cấu hình lên thiết bị (replace candidate config, sau đó commit)
        napalm_device.load_replace_candidate(config=config_data)
        diffs = napalm_device.compare_config()
        if diffs:
            print("Các thay đổi sẽ được áp dụng:\n", diffs)
            napalm_device.commit_config()
            print(f"✓ Đã restore cấu hình cho {hostname} ({device['host']}) từ file {restore_file}")
            with open("restore.log", "a") as logf:
                logf.write(f"Successfully restored configuration to device {device['host']} from {restore_file}\n")
        else:
            print("Không có thay đổi nào cần áp dụng.")
            napalm_device.discard_config()
        napalm_device.close()
    except Exception as e:
        with open("restore.log", "a") as logf:
            logf.write(f"Failed to restore configuration to device {device.get('host', 'unknown')} from {restore_file}: {e}\n")
        print(f"✗ {hostname} ({device.get('host', 'unknown')}): Lỗi restore - {e}")