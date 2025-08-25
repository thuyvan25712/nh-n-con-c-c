from time import strftime
from datetime import datetime, timedelta
import re, os, sys
from curl_cffi import requests
from datetime import date
from time import sleep
from datetime import datetime

# Enhanced Color Definitions
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    PURPLE = '\033[35m'
    BOLD_PURPLE = '\033[1;35m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    CYAN = '\033[36m'
    
    # Bold Colors
    BOLD_BLACK = "\033[1;30m"
    BOLD_RED = "\033[1;31m"
    BOLD_GREEN = "\033[1;32m"
    BOLD_YELLOW = "\033[1;33m"
    BOLD_BLUE = "\033[1;34m"
    BOLD_MAGENTA = "\033[1;35m"
    BOLD_CYAN = "\033[1;36m"
    BOLD_WHITE = "\033[1;37m"
    
    # Background Colors
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"
    
    # Special Effects
    DIM = "\033[2m"
    UNDERLINE = "\033[4m"
    BLINK = "\033[5m"
    REVERSE = "\033[7m"
    
    # Gradient Colors
    PINK = "\033[96m"
    ORANGE = "\033[91m"
    LIGHT_GREEN = "\033[92m"
    LIGHT_BLUE = "\033[94m"

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def animated_loading():
    """Professional animated loading screen"""
    clear_screen()
    
    title = f"{Colors.BOLD_CYAN}🚀 LOADING INTO BETAPCODE SYSTEM{Colors.RESET}"
    subtitle = f"{Colors.BOLD_MAGENTA}┃ Initializing Professional Interface...{Colors.RESET}"
    
    loading_chars = ["◐", "◓", "◑", "◒"]
    
    print(f"\n{Colors.BOLD_WHITE}{'='*60}{Colors.RESET}")
    print(f"{title:^70}")
    print(f"{subtitle:^70}")
    print(f"{Colors.BOLD_WHITE}{'='*60}{Colors.RESET}\n")
    
    for i in range(101):
        char = loading_chars[i % len(loading_chars)]
        progress = int(i * 50 / 100)
        bar = f"{Colors.BOLD_GREEN}{'█' * progress}{Colors.BOLD_BLACK}{'░' * (50 - progress)}{Colors.RESET}"
        
        percentage = f"{Colors.BOLD_YELLOW}{i:3d}%{Colors.RESET}"
        spinner = f"{Colors.BOLD_PURPLE}[{char}]{Colors.RESET}"
        
        sys.stdout.write(f"\r{Colors.BOLD_WHITE}Progress: {spinner} {percentage} {bar} {Colors.BOLD_CYAN}Loading...{Colors.RESET}")
        sys.stdout.flush()
        sleep(0.02)
    
    print(f"\n\n{Colors.BOLD_GREEN}✓ System loaded successfully!{Colors.RESET}")
    sleep(0.5)
    clear_screen()

def create_banner():
    """Create professional banner"""
    info_box = f"""
{Colors.BOLD_CYAN}╔════════════════════════════════════════════════════════════════╗
{Colors.BOLD_CYAN}║{Colors.BOLD_WHITE}                    🌟 BÉ TẬP CODE TOOL 🌟                      {Colors.BOLD_CYAN}║
{Colors.BOLD_CYAN}╠════════════════════════════════════════════════════════════════╣
{Colors.BOLD_CYAN}║ {Colors.BOLD_YELLOW}📋 TOOL BY        {Colors.BOLD_WHITE}: Bé Tập Code                          {Colors.BOLD_CYAN}║
{Colors.BOLD_CYAN}║ {Colors.BOLD_YELLOW}📺 YOUTUBER       {Colors.BOLD_WHITE}: HVHTOOL                              {Colors.BOLD_CYAN}║
{Colors.BOLD_CYAN}║ {Colors.BOLD_YELLOW}🔗 YOUTUBE LINK   {Colors.BOLD_WHITE}: https://www.youtube.com/@HVHTOOL     {Colors.BOLD_CYAN}║
{Colors.BOLD_CYAN}║ {Colors.BOLD_YELLOW}⚡ VERSION        {Colors.BOLD_WHITE}: Professional v2.0                    {Colors.BOLD_CYAN}║
{Colors.BOLD_CYAN}║ {Colors.BOLD_YELLOW}📅 DATE           {Colors.BOLD_WHITE}: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}                 {Colors.BOLD_CYAN}║
{Colors.BOLD_CYAN}╚════════════════════════════════════════════════════════════════╝{Colors.RESET}
"""
    
    system_info = f"""
{Colors.BOLD_MAGENTA}╔══════════════════════════════════════════════════════════════════╗
{Colors.BOLD_MAGENTA}║{Colors.BOLD_WHITE}                        SYSTEM INFORMATION                        {Colors.BOLD_MAGENTA}║
{Colors.BOLD_MAGENTA}╠══════════════════════════════════════════════════════════════════╣
{Colors.BOLD_MAGENTA}║ {Colors.BOLD_GREEN}✅ Tool chạy trên: CMD, Codespace, Termux (Ubuntu)             {Colors.BOLD_MAGENTA}║
{Colors.BOLD_MAGENTA}║ {Colors.BOLD_GREEN}✅ Tool đã được test kỹ lưỡng trước khi phát hành             {Colors.BOLD_MAGENTA}║
{Colors.BOLD_MAGENTA}║ {Colors.BOLD_GREEN}✅ Nếu có lỗi: Liên hệ AD hoặc cài lại Python đúng version    {Colors.BOLD_MAGENTA}║
{Colors.BOLD_MAGENTA}╚══════════════════════════════════════════════════════════════════╝{Colors.RESET}
"""
    
    return info_box + system_info

def create_menu():
    """Create professional menu interface"""
    menu = f"""
{Colors.BOLD_CYAN}╔═══════════════════════════════════════════════════════════════════╗
{Colors.BOLD_CYAN}║{Colors.BOLD_YELLOW}                    📱 GOLIKE PC|IOS|ANDROID                       {Colors.BOLD_CYAN}║
{Colors.BOLD_CYAN}╚═══════════════════════════════════════════════════════════════════╝{Colors.RESET}

{Colors.BOLD_MAGENTA}┌─────────────────────────────────────────────────────────────────────┐{Colors.RESET}
{Colors.BOLD_WHITE}│ {Colors.BOLD_YELLOW}[1.1]{Colors.BOLD_GREEN} 🔗 LinkedIn Auto        {Colors.BOLD_WHITE}            │ {Colors.BOLD_CYAN}PC|CODESPACES|TERMUX    {Colors.BOLD_WHITE}│
{Colors.BOLD_WHITE}│ {Colors.BOLD_YELLOW}[1.2]{Colors.BOLD_GREEN} 📸 Instagram Random UA  {Colors.BOLD_WHITE}            │ {Colors.BOLD_CYAN}PC|CODESPACES|TERMUX    {Colors.BOLD_WHITE}│
{Colors.BOLD_WHITE}│ {Colors.BOLD_YELLOW}[1.3]{Colors.BOLD_GREEN} 🐦 X (Twitter) Auto     {Colors.BOLD_WHITE}            │ {Colors.BOLD_CYAN}PC|CODESPACES|TERMUX    {Colors.BOLD_WHITE}│
{Colors.BOLD_WHITE}│ {Colors.BOLD_YELLOW}[1.4]{Colors.BOLD_GREEN} 🧵 Threads Auto         {Colors.BOLD_WHITE}            │ {Colors.BOLD_CYAN}PC|CODESPACES|TERMUX    {Colors.BOLD_WHITE}│
{Colors.BOLD_WHITE}│ {Colors.BOLD_YELLOW}[1.5]{Colors.BOLD_GREEN} 🎵 TikTok Auto          {Colors.BOLD_WHITE}            │ {Colors.BOLD_CYAN}TERMUX ONLY             {Colors.BOLD_WHITE}│
{Colors.BOLD_WHITE}│ {Colors.BOLD_YELLOW}[1.6]{Colors.BOLD_GREEN} 🛒 Lazada Auto          {Colors.BOLD_WHITE}            │ {Colors.BOLD_CYAN}PC|CODESPACES|TERMUX    {Colors.BOLD_WHITE}│
{Colors.BOLD_WHITE}│ {Colors.BOLD_YELLOW}[1.7]{Colors.BOLD_GREEN} 👻 Snapchat Auto        {Colors.BOLD_WHITE}            │ {Colors.BOLD_CYAN}PC|CODESPACES|TERMUX    {Colors.BOLD_WHITE}│
{Colors.BOLD_MAGENTA}└─────────────────────────────────────────────────────────────────────┘{Colors.RESET}

{Colors.BOLD_CYAN}╔═══════════════════════════════════════════════════════════════════╗
{Colors.BOLD_CYAN}║{Colors.BOLD_YELLOW}                    💎 GOLIKE PC VIP EDITION                       {Colors.BOLD_CYAN}║
{Colors.BOLD_CYAN}╚═══════════════════════════════════════════════════════════════════╝{Colors.RESET}

{Colors.BOLD_MAGENTA}┌─────────────────────────────────────────────────────────────────────┐{Colors.RESET}
{Colors.BOLD_WHITE}│ {Colors.BOLD_YELLOW}[2.1]{Colors.BOLD_GREEN} 🔗 LinkedIn VIP (No Cookie) {Colors.BOLD_WHITE}        │ {Colors.BOLD_CYAN}PC ONLY                 {Colors.BOLD_WHITE}│
{Colors.BOLD_WHITE}│ {Colors.BOLD_YELLOW}[2.2]{Colors.BOLD_GREEN} 🧵 Threads VIP (No Cookie)  {Colors.BOLD_WHITE}        │ {Colors.BOLD_CYAN}PC ONLY                {Colors.BOLD_WHITE}│
{Colors.BOLD_WHITE}│ {Colors.BOLD_YELLOW}[2.3]{Colors.BOLD_GREEN} 🎵 TikTok VIP    {Colors.BOLD_WHITE}                   │ {Colors.BOLD_CYAN}PC ONLY                 {Colors.BOLD_WHITE}│
{Colors.BOLD_WHITE}│ {Colors.BOLD_YELLOW}[2.4]{Colors.BOLD_GREEN} 👻 Snapchat(No Cookie)Trick VIP     {Colors.BOLD_WHITE}│ {Colors.BOLD_CYAN}PC ONLY                 {Colors.BOLD_WHITE}│
{Colors.BOLD_WHITE}│ {Colors.BOLD_YELLOW}[2.5]{Colors.BOLD_GREEN} 👻 pintset(No Cookie)Trick VIP      {Colors.BOLD_WHITE}│ {Colors.BOLD_CYAN}PC ONLY                 {Colors.BOLD_WHITE}│
{Colors.BOLD_WHITE}│ {Colors.BOLD_YELLOW}[2.6]{Colors.BOLD_GREEN} 🌃 Instagram VIP   {Colors.BOLD_WHITE}                 │ {Colors.BOLD_CYAN}PC ONLY                {Colors.BOLD_WHITE}│
{Colors.BOLD_MAGENTA}└─────────────────────────────────────────────────────────────────────┘{Colors.RESET}

{Colors.BOLD_WHITE}{'='*70}{Colors.RESET}
"""
    return menu

# Show loading animation and display interface
animated_loading()
print(create_banner())
print(create_menu())

# Function mapping dictionary
chucnang = {
    1.1: 'obf-AutoLinkedin_PC.py',
    1.2: 'obf-ig_c25.py', 
    1.3: 'obf-AUTO-X_PC.py',
    1.4: 'obf-AutoTheads.py',
    1.5: 'obf-goliketiktok.py',
    1.6: 'obf-lazada.py',
    1.7: 'obf-golikesnapchat.py',

    2.1: 'obf-linkdei_vip.py',
    2.2: 'obf-thead_vip.py',
    2.3: 'TIKTOK_ADB_FROM.py',
    2.4: 'obf-snapchat.py',
    2.5: 'obf-pintset.py',
    2.6: 'obf-ig_betav6_frommo_pyqt5.py',
}
# Animated input prompt

loading_dots = ""
for i in range(3):
    sys.stdout.write(f"\r{Colors.BOLD_CYAN}🔄 Đang chờ lựa chọn{loading_dots}{Colors.RESET}")
    sys.stdout.flush()
    sleep(0.3)
    loading_dots += "."


# Professional input with multiple styling elements
nhap = float(input(f'''
{Colors.BOLD_RED}╭─[{Colors.BOLD_CYAN}💻 BÉ TẬP CODE SYSTEM{Colors.BOLD_RED}]
{Colors.BOLD_RED}├─[{Colors.BOLD_YELLOW}⚡ Status: Ready{Colors.BOLD_RED}]
{Colors.BOLD_RED}╰─[{Colors.BOLD_GREEN}🎯 Nhập Chức Năng{Colors.BOLD_RED}]─>{Colors.BOLD_WHITE} '''))

print(f"{Colors.RESET}\n{Colors.BOLD_CYAN}⏳ Đang xử lý lựa chọn của bạn...{Colors.RESET}")
sleep(0.5)

# Execute based on user selection - ORIGINAL LOGIC PRESERVED
if nhap in [1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7]:
    base_url = "https://raw.githubusercontent.com/thuyvan25712/nh-n-con-c-c/refs/heads/main/obf-MOBI/"
    url = base_url + chucnang[nhap]
    response = requests.get(url, verify=False)
    response.encoding = 'utf-8'
    exec(response.text)
elif nhap in [2.1,2.2,2.3,2.4,2.5,2.6]:
    base_url = "https://raw.githubusercontent.com/thuyvan25712/nh-n-con-c-c/refs/heads/main/obf_vip/"
    url = base_url + chucnang[nhap]
    response = requests.get(url, verify=False)
    response.encoding = 'utf-8'  # Set encoding to UTF-8
    exec(response.text)
if nhap == 00:
    exit()
else:
    exit()