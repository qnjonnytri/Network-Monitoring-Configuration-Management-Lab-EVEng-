# Sử dụng Napalm để backup, so sánh cấu hình, lưu lịch sử và log
from napalm import get_network_driver
import difflib
import datetime
import os

# 1. Kết nối đến router Cisco bằng Napalm
driver = get_network_driver("ios")
device = driver(
	hostname="192.168.1.9",
	username="admin",
	password="cisco"
)
device.open()

# Lấy hostname để đặt tên file backup
facts = device.get_facts()
hostname = facts.get("hostname", "R1")

# Lấy cấu hình hiện tại
config_dict = device.get_config()
today_config = config_dict.get("running", "")

# Đóng kết nối
device.close()

# Tạo tên file backup có timestamp để lưu lịch sử
now = datetime.datetime.now()
backup_filename = f"{hostname}_{now.strftime('%Y-%m-%d_%H-%M-%S')}.txt"

# 2. Đọc file cấu hình hôm qua
yesterday = datetime.date.today() - datetime.timedelta(days=1)
yesterday_file = f"R1_{yesterday}.txt"

if os.path.exists(yesterday_file):
	with open(yesterday_file, "r") as f:
		yesterday_config = f.read()
	yesterday_config_lines = yesterday_config.splitlines()
else:
	print(f"Không tìm thấy file cấu hình hôm qua: {yesterday_file}")
	yesterday_config_lines = []

# 3. So sánh và xuất ra file difference.html
today_config_lines = today_config.splitlines()
diff = difflib.HtmlDiff().make_file(
	yesterday_config_lines,
	today_config_lines,
	"Yesterday Configuration",
	"Today Configuration",
	context=True,
	numlines=3
)

with open("difference.html", "w") as f:
	f.write(diff)

# 4. Lưu cấu hình hôm nay vào file (backup lịch sử)
with open(backup_filename, "w") as f:
	f.write(today_config)

# Ngoài ra vẫn lưu file hôm nay (dạng cũ, ghi đè)
today_file = f"R1_{datetime.date.today()}.txt"
with open(today_file, "w") as f:
	f.write(today_config)

# 5. Ghi log backup
try:
	with open("backup.log", "a") as logf:
		logf.write(f"Successfully backed up configuration of device 192.168.1.18 at {now} to {backup_filename}\n")
except Exception as e:
	with open("backup.log", "a") as logf:
		logf.write(f"Failed to backup configuration of device 192.168.1.18 at {now}: {e}\n")

print("✓ Đã so sánh và lưu cấu hình thành công. Đã lưu lịch sử backup và ghi log.")
