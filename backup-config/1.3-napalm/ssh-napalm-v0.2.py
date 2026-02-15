import yaml
from napalm import get_network_driver
import difflib
import datetime
import os

# Đọc danh sách thiết bị từ file YAML
with open('devices.yml', 'r') as ymlfile:
    devices = yaml.safe_load(ymlfile)

for device in devices:
    try:
        driver = get_network_driver(device['device_type'])
        napalm_device = driver(
            hostname=device['host'],
            username=device['username'],
            password=device['password']
        )
        napalm_device.open()

        # Lấy hostname để đặt tên file backup
        facts = napalm_device.get_facts()
        hostname = facts.get('hostname', device.get('host', 'R1'))

        # Lấy cấu hình hiện tại
        config_dict = napalm_device.get_config()
        today_config = config_dict.get('running', '')

        napalm_device.close()

        # Tạo tên file backup có timestamp để lưu lịch sử
        now = datetime.datetime.now()
        backup_filename = f"{hostname}_{now.strftime('%Y-%m-%d_%H-%M-%S')}.txt"

        # Đọc file cấu hình hôm qua
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        yesterday_file = f"{hostname}_{yesterday}.txt"

        if os.path.exists(yesterday_file):
            with open(yesterday_file, "r") as f:
                yesterday_config = f.read()
            yesterday_config_lines = yesterday_config.splitlines()
        else:
            print(f"Không tìm thấy file cấu hình hôm qua: {yesterday_file}")
            yesterday_config_lines = []

        # So sánh và xuất ra file difference
        today_config_lines = today_config.splitlines()
        diff = difflib.HtmlDiff().make_file(
            yesterday_config_lines,
            today_config_lines,
            "Yesterday Configuration",
            "Today Configuration",
            context=True,
            numlines=3
        )

        diff_file = f"difference_{hostname}.html"
        with open(diff_file, "w") as f:
            f.write(diff)

        # Lưu cấu hình hôm nay vào file (backup lịch sử)
        with open(backup_filename, "w") as f:
            f.write(today_config)

        # Ngoài ra vẫn lưu file hôm nay (dạng cũ, ghi đè)
        today_file = f"{hostname}_{datetime.date.today()}.txt"
        with open(today_file, "w") as f:
            f.write(today_config)

        # Ghi log backup
        with open("backup.log", "a") as logf:
            logf.write(f"Successfully backed up configuration of device {device['host']} at {now} to {backup_filename}\n")
        print(f"✓ {hostname} ({device['host']}): Đã so sánh và lưu cấu hình thành công. Đã lưu lịch sử backup và ghi log.")
    except Exception as e:
        with open("backup.log", "a") as logf:
            logf.write(f"Failed to backup configuration of device {device.get('host', 'unknown')} at {datetime.datetime.now()}: {e}\n")
        print(f"✗ {device.get('host', 'unknown')}: Lỗi backup - {e}")