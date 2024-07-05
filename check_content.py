import requests
import json
import re
from datetime import datetime

def color_word(keyword, line):
    index = line.lower().find(keyword.lower())
    while index >= 0:
        print(line[:index], end='', flush=True)
        print('\033[90m', end='', flush=True)  # DarkGray
        print(line[index:index + len(keyword)].strip(), end='', flush=True)
        print('\033[39m', end='', flush=True)  # Default color
        used = len(keyword) + index
        remain = len(line) - used
        line = line[used:used + remain]
        index = line.lower().find(keyword.lower())

    print(line, end='', flush=True)

def check_content(url, config):
    print("=" * 65)
    print("=             HTTP HTMLContent check                          =")
    print("=" * 65)

    exp = datetime.strptime(config["Expires"], "%Y-%m-%d")
    today = datetime.now()

    print(f"Version : {str(config['Version']).rjust(14)}", end='')
    print(f"Expire : {exp.strftime('%d/%m/%Y')} |", end='')

    if exp <= today:
        print("\033[91m Expired !\033[39m")
    else:
        print("\033[92m Valid\033[39m")

    print("Checking :".rjust(15), url)
    print("=" * 65)

    if exp <= today:
        print("\n -------------------------------------------")
        print(" >> Please update 'headers-config.json' file")
        print(" -------------------------------------------")
        print(" Last version :")
        print(" https://capgemini.sharepoint.com/:f:/r/sites/CyberSecurityFR2/Shared%20Documents/General/PowerShell%20Scripts?csf=1&web=1&e=0rbJMN")

    response = requests.get(url)
    html = response.text

    print("\n\n== Important findings ==")
    hashit = False
    for tr in config["Errors"]:
        pattern = re.compile(tr["Value"])
        match_items = pattern.finditer(html)
        for mt in match_items:
            hashit = True
            print(f"{tr['Label']} '", end='')
            print(mt.group(), end='')
            print("' : ", end='')
            str_val = re.sub(r"[\n\r]+", " ", mt.group())
            str_val = str_val.strip()
            color_word(tr["Value"], str_val)
            print("     ->", tr["Description"])
            print()

    if not hashit:
        print("None  - No action required")

    print("\n== Warning findings ==")
    hashit = False
    for tr in config["Warnings"]:
        pattern = re.compile(tr["Value"])
        match_items = pattern.finditer(html)
        for mt in match_items:
            hashit = True
            print(f"{tr['Label']} '", end='')
            print(mt.group(), end='')
            print("' : ", end='')
            str_val = re.sub(r"[\n\r]+", " ", mt.group())
            str_val = str_val.strip()
            color_word(tr["Value"], str_val)
            print("     ->", tr["Description"])
            print()

    if not hashit:
        print("None  - No action required")

    print("\n--- End  ---")

if __name__ == "__main__":
    url = input("Enter URL to check (e.g., https://www.mysite.com) or 'exit' to terminate this script: ")

    if url.lower() == "exit":
        exit()

    with open("content-config.json", "r") as config_file:
        config = json.load(config_file)

    check_content(url, config)
    input("Press Enter to continue...")
