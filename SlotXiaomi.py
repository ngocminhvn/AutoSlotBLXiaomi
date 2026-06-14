import subprocess
import sys
import os
import time
import platform

required_packages = ["requests", "ntplib", "pytz", "urllib3", "icmplib", "colorama", "browser-cookie3", "selenium", "pyperclip", "tkinter"]
for package in required_packages:
    try:
        __import__(package.replace("-", "_"))
    except ImportError:
        print(f"Đang cài đặt thư viện {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

os.system('cls' if os.name == 'nt' else 'clear')

import browser_cookie3
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import tkinter as tk
from tkinter import ttk
import hashlib
import random
from datetime import datetime, timezone, timedelta
import ntplib
import pytz
import urllib3
import json
import webbrowser
from icmplib import ping
from colorama import init, Fore, Style

init(autoreset=True)
col_g = Fore.GREEN
col_gb = Style.BRIGHT + Fore.GREEN
col_b = Fore.BLUE
col_y = Fore.YELLOW
col_yb = Style.BRIGHT + Fore.YELLOW
col_r = Fore.RED
col_rb = Style.BRIGHT + Fore.RED

ntp_servers = [
    "ntp.aliyun.com", "ntp.tencent.com", "cn.pool.ntp.org", 
    "edu.ntp.org.cn", "time.apple.com", "time.google.com", "pool.ntp.org"
]

def extract_firefox_token():
    try:
        subprocess.run(["taskkill", "/F", "/IM", "firefox.exe"], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass
    time.sleep(2)
    try:
        cj = browser_cookie3.firefox()
    except Exception as e:
        print(col_r + f"[!] Lỗi đọc cookie Firefox: {e}" + Fore.RESET)
        return None
    for cookie in cj:
        if "new_bbs_serviceToken" in cookie.name:
            return cookie.value
    return None

def extract_chromium_token(link, browser_name="chrome"):
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    
    if browser_name == "coccoc":
        coccoc_paths = [
            os.path.join(os.environ.get('LOCALAPPDATA', ''), r"CocCoc\Browser\Application\browser.exe"),
            os.path.join(os.environ.get('PROGRAMFILES', ''), r"CocCoc\Browser\Application\browser.exe"),
            os.path.join(os.environ.get('PROGRAMFILES(X86)', ''), r"CocCoc\Browser\Application\browser.exe")
        ]
        
        coccoc_exe = None
        for path in coccoc_paths:
            if os.path.exists(path):
                coccoc_exe = path
                break
                
        if coccoc_exe:
            chrome_options.binary_location = coccoc_exe
        else:
            print(col_r + "[!] Không tìm thấy Cốc Cốc trên máy!" + Fore.RESET)
            return None

    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(link)
        
        browser_title = "Cốc Cốc" if browser_name == "coccoc" else "Chrome"
        print(col_y + f"\n[*] Đang mở {browser_title}. Vui lòng đăng nhập tài khoản Xiaomi..." + Fore.RESET)
        
        token = None
        while True:
            try:
                _ = driver.title 
            except:
                print(col_r + "[!] Trình duyệt đã bị đóng trước khi lấy được Token." + Fore.RESET)
                break
                
            cookie = driver.get_cookie("new_bbs_serviceToken")
            if cookie:
                token = cookie['value']
                print(col_g + "[+] Đã bắt được Token Dài thành công!" + Fore.RESET)
                break 
            time.sleep(1) 
            
        driver.quit() 
        return token
        
    except Exception as e:
        print(col_r + f"[!] Lỗi khi lấy token từ {browser_name}: {e}" + Fore.RESET)
        try:
            driver.quit()
        except:
            pass
        return None

def show_taskbar_prompt_firefox(title, message, ok_text="OK"):
    root = tk.Tk()
    root.title(title)
    root.resizable(False, False)
    width, height = 420, 140
    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    x = (screen_w - width) // 2
    y = (screen_h - height) // 2
    root.geometry(f"{width}x{height}+{x}+{y}")
    root.attributes("-topmost", True)
    root.after(200, lambda: root.attributes("-topmost", False))
    frm = ttk.Frame(root, padding=12)
    frm.pack(expand=True, fill=tk.BOTH)
    lbl = ttk.Label(frm, text=message, wraplength=width - 30, justify=tk.LEFT)
    lbl.pack(pady=(6, 12), anchor=tk.W)
    result = {"ok": False}
    def on_ok():
        result["ok"] = True
        root.destroy()
    btn = ttk.Button(frm, text=ok_text, command=on_ok)
    btn.pack(side=tk.BOTTOM)
    root.update_idletasks()
    root.deiconify()
    root.lift()
    root.mainloop()
    return result["ok"]

class HTTP11Session:
    def __init__(self):
        self.http = urllib3.PoolManager(
            maxsize=10, retries=True,
            timeout=urllib3.Timeout(connect=2.0, read=15.0), headers={}
        )

    def make_request(self, method, url, headers=None, body=None):
        try:
            request_headers = {}
            if headers:
                request_headers.update(headers)
                request_headers['Content-Type'] = 'application/json; charset=utf-8'
           
            if method == 'POST':
                if body is None:
                    body = '{"is_retry":true}'.encode('utf-8')
                request_headers['Content-Length'] = str(len(body))
                request_headers['Accept-Encoding'] = 'gzip, deflate, br'
                request_headers['User-Agent'] = 'okhttp/4.12.0'
                request_headers['Connection'] = 'keep-alive'
           
            return self.http.request(method, url, headers=request_headers, body=body, preload_content=False)
        except Exception as e:
            print(col_r + f"[Lỗi mạng] {e}" + Fore.RESET)
            return None

def generate_device_id():
    random_data = f"{random.random()}-{time.time()}"
    return hashlib.sha1(random_data.encode('utf-8')).hexdigest().upper()

def calculate_dynamic_timeshift(host="sgp-api.buy.mi.com", count=10):
    print(col_y + f"\nĐang đo Ping thực tế tới {host}..." + Fore.RESET)
    try:
        host_alive = ping(host, count=count, interval=0.2, timeout=2, privileged=False)
        if host_alive.is_alive:
            avg_ping_ms = host_alive.avg_rtt
            one_way_latency = (avg_ping_ms / 2) + 15 
            print(col_g + f"[Ping trung bình]: " + Fore.RESET + f"{avg_ping_ms:.2f} ms")
            print(col_g + f"[Đã cài đặt bù giờ]: " + Fore.RESET + f"{one_way_latency:.2f} ms")
            return one_way_latency
        else:
            print(col_r + "[Lỗi] Không thể Ping tới server. Dùng giá trị mặc định (50ms)." + Fore.RESET)
            return 50.0 
    except Exception as e:
        print(col_r + f"[Lỗi đo Ping]: {e}. Dùng giá trị mặc định (50ms)." + Fore.RESET)
        return 50.0

def get_initial_beijing_time():
    client = ntplib.NTPClient()
    beijing_tz = pytz.timezone("Asia/Shanghai")
    for server in ntp_servers:
        try:
            print(col_y + f"\nĐang lấy giờ hiện tại ở Bắc Kinh..." + Fore.RESET)
            response = client.request(server, version=3)
            ntp_time = datetime.fromtimestamp(response.tx_time, timezone.utc)
            beijing_time = ntp_time.astimezone(beijing_tz)
            print(col_g + f"[Giờ Bắc Kinh]: " + Fore.RESET +  f"{beijing_time.strftime('%Y-%m-%d %H:%M:%S.%f')}")
            return beijing_time
        except Exception as e:
            print(f"Lỗi kết nối tới {server}: {e}")
    print(f"Không thể kết nối với bất kỳ máy chủ NTP nào.")
    return None

def get_synchronized_beijing_time(start_beijing_time, start_timestamp):
    return start_beijing_time + timedelta(seconds=(time.time() - start_timestamp))

def check_unlock_status(session, cookie_value, device_id):
    try:
        url = "https://sgp-api.buy.mi.com/bbs/api/global/user/bl-switch/state"
        headers = {"Cookie": f"new_bbs_serviceToken={cookie_value};versionCode=500411;versionName=5.4.11;deviceId={device_id};"}
       
        response = session.make_request('GET', url, headers=headers)
        if response is None:
            print(col_r + f"[Lỗi] Không thể lấy trạng thái unlock." + Fore.RESET)
            return False

        response_data = json.loads(response.data.decode('utf-8'))
        response.release_conn()

        if response_data.get("code") == 100004:
            print(col_r + f"[Lỗi] Cookie đã hết hạn, cần lấy lại token mới." + Fore.RESET)
            input(f"Nhấn Enter để đóng...")
            exit()

        data = response_data.get("data", {})
        is_pass = data.get("is_pass")
        button_state = data.get("button_state")
        deadline_format = data.get("deadline_format", "")

        if is_pass == 4:
            if button_state == 1:
                print(col_g + f"[Trạng thái tài khoản]: " + Fore.RESET + f"Có thể gửi yêu cầu unlock..")
                return True
            elif button_state == 2:
                print(col_r + f"[Trạng thái tài khoản]: " + Fore.RESET + f"Bị chặn gửi yêu cầu cho đến {deadline_format}.")
                status_2 = input(f"Tiếp tục chạy ({col_b}y/n{Fore.RESET})?: ")
                if status_2.lower() in ['y', 'yes']: return True
                else: exit()
            elif button_state == 3:
                print(col_y + f"[Trạng thái tài khoản]: " + Fore.RESET + f"Tài khoản tạo chưa đủ 30 ngày..")
                status_3 = input(f"Tiếp tục chạy ({col_b}y/n{Fore.RESET})?: ")
                if status_3.lower() in ['y', 'yes']: return True
                else: exit()
        elif is_pass == 1:
            print(col_gb + f"[Trạng thái tài khoản]: " + Fore.RESET + f"Đã được duyệt, có thể unlock cho đến {deadline_format}.")
            input(f"Nhấn Enter để đóng...")
            exit()
        else:
            print(col_y + f"[Trạng thái tài khoản]: " + Fore.RESET + f"Trạng thái không xác định.")
            input(f"Nhấn Enter để đóng...")
            exit()
    except Exception as e:
        print(col_r + f"[Lỗi kiểm tra trạng thái] {e}" + Fore.RESET)
        return False

def hunt_slot(cookie_value):
    print(col_y + f"\n=== CHUẨN BỊ CANH SLOT ===" + Fore.RESET)
    device_id = generate_device_id()
    session = HTTP11Session()

    if not check_unlock_status(session, cookie_value, device_id):
        return

    feed_time_shift_1 = calculate_dynamic_timeshift() / 1000
    start_beijing_time = get_initial_beijing_time()
    if start_beijing_time is None:
        print(col_r + f"Không thể thiết lập thời gian bắt đầu. Nhấn Enter để đóng..." + Fore.RESET)
        input()
        exit()

    start_timestamp = time.time()
    
    next_day = start_beijing_time + timedelta(days=1)
    target_time = next_day.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(seconds=feed_time_shift_1)
    prewarm_time = target_time - timedelta(seconds=3)
    
    print(col_y + f"\n[Pre-warm] Đang đợi đến lúc làm nóng kết nối..." + Fore.RESET)
    
    while True:
        current_time = get_synchronized_beijing_time(start_beijing_time, start_timestamp)
        if current_time >= prewarm_time:
            print(col_g + f"[{current_time.strftime('%H:%M:%S.%f')}] Khởi động kết nối TCP/TLS..." + Fore.RESET)
            url_prewarm = "https://sgp-api.buy.mi.com/bbs/api/global/user/bl-switch/state"
            headers_prewarm = {
                "Cookie": f"new_bbs_serviceToken={cookie_value};versionCode=500411;versionName=5.4.11;deviceId={device_id};",
                "Connection": "keep-alive"
            }
            session.make_request('GET', url_prewarm, headers=headers_prewarm)
            break
        else:
            time.sleep(0.01)

    print(col_y + f"[Pre-warm] Hoàn tất. Nín thở chờ bắn request chính thức vào {target_time.strftime('%H:%M:%S.%f')}..." + Fore.RESET)
    
    while True:
        current_time = get_synchronized_beijing_time(start_beijing_time, start_timestamp)
        if current_time >= target_time:
            print(f"\nGiờ G! Bắt đầu xả đạn: {current_time.strftime('%Y-%m-%d %H:%M:%S.%f')}")
            break

    url_apply = "https://sgp-api.buy.mi.com/bbs/api/global/apply/bl-auth"
    headers_apply = {
        "Cookie": f"new_bbs_serviceToken={cookie_value};versionCode=500411;versionName=5.4.11;deviceId={device_id};"
    }

    max_duration = 4    
    cooldown_time = 0.2   
    loop_start_time = time.time()

    try:
        while True:
            if time.time() - loop_start_time > max_duration:
                print(col_y + f"\n[Hết giờ]: Đã cắm chốt liên tục {max_duration} giây. Hết slot rồi, nghỉ ngơi bảo vệ tài khoản thôi bro!" + Fore.RESET)
                input("Nhấn Enter để đóng...")
                break

            request_time = get_synchronized_beijing_time(start_beijing_time, start_timestamp)
            print(col_g + f"\n[Gửi request]: " + Fore.RESET + f"Đang bắn lúc {request_time.strftime('%Y-%m-%d %H:%M:%S.%f')} (UTC+8)")
           
            response = session.make_request('POST', url_apply, headers=headers_apply)
            
            if response is None:
                print(col_r + "[!] Mất kết nối, đang thử lại..." + Fore.RESET)
                time.sleep(cooldown_time)
                continue

            response_time = get_synchronized_beijing_time(start_beijing_time, start_timestamp)
            print(col_g + f"[Phản hồi]: " + Fore.RESET + f"Nhận kết quả lúc {response_time.strftime('%Y-%m-%d %H:%M:%S.%f')} (UTC+8)")

            try:
                response_data = response.data
                response.release_conn()
                json_response = json.loads(response_data.decode('utf-8'))
                code = json_response.get("code")
                data = json_response.get("data", {})

                if code == 0:
                    apply_result = data.get("apply_result")
                    if apply_result == 1:
                        print(col_gb + f"[Trạng thái]: THÀNH CÔNG! Đã lấy được slot. Đang verify lại..." + Fore.RESET)
                        check_unlock_status(session, cookie_value, device_id)
                        break 
                    elif apply_result == 3:
                        deadline_format = data.get("deadline_format", "Không xác định")
                        print(col_r + f"[Trạng thái]: Server báo hết slot. Thử lại sau {deadline_format} (Tháng/Ngày)." + Fore.RESET)
                        input(f"Nhấn Enter để đóng...")
                        exit()
                    elif apply_result == 4:
                        deadline_format = data.get("deadline_format", "Không xác định")
                        print(col_r + f"[Trạng thái]: Bị block tạm thời đến {deadline_format} (Tháng/Ngày)." + Fore.RESET)
                        input(f"Nhấn Enter để đóng...")
                        exit()
                elif code == 100001:
                    print(col_y + f"[Trạng thái]: Bị từ chối (Reject) - Đang chờ gửi lại..." + Fore.RESET)
                elif code == 100003:
                    print(col_g + f"[Trạng thái]: Có thể đã được duyệt, đang kiểm tra trạng thái..." + Fore.RESET)
                    check_unlock_status(session, cookie_value, device_id)
                else:
                    print(col_y + f"[Trạng thái]: Mã lạ từ server: {code}" + Fore.RESET)

            except json.JSONDecodeError:
                print(col_r + f"[Lỗi]: Máy chủ trả về lỗi không thể giải mã (JSON Decode Error)." + Fore.RESET)
            except Exception as e:
                print(col_r + f"[Lỗi xử lý kết quả]: {e}" + Fore.RESET)

            print(col_b + f"[*] Đang nạp đạn (cooldown {cooldown_time}s) để lách tường lửa..." + Fore.RESET)
            time.sleep(cooldown_time)

    except Exception as e:
        print(col_r + f"[Lỗi gửi request]: {e}" + Fore.RESET)
        input(f"Nhấn Enter để đóng...")
        exit()

if __name__ == "__main__":
    print(col_gb + "=== AutoSlot Xiaomi AIO ===" + Fore.RESET)
    print("1. Đăng nhập qua Chrome")
    print("2. Đăng nhập qua Firefox")
    print("3. Đăng nhập qua Cốc Cốc")
    
    choice = input("\nChọn trình duyệt bro muốn sử dụng (1, 2 hoặc 3): ")
    
    final_token = None
    
    if choice == "1":
        final_token = extract_chromium_token("https://c.mi.com/global", "chrome")
    elif choice == "2":
        webbrowser.open("https://c.mi.com/global")
        show_taskbar_prompt_firefox(
            "Đăng nhập Firefox",
            "Vui lòng đăng nhập c.mi.com/global trên Firefox.\nSau khi đăng nhập xong, bấm OK để lấy token."
        )
        final_token = extract_firefox_token()
    elif choice == "3":
        final_token = extract_chromium_token("https://c.mi.com/global", "coccoc")
    else:
        print(col_r + "[✖] Lựa chọn không hợp lệ!" + Fore.RESET)
        sys.exit()

    if not final_token:
        print(col_r + "[✖] Lỗi: Không tìm thấy token. Hãy thử lại!" + Fore.RESET)
        sys.exit()
    
    hunt_slot(final_token)