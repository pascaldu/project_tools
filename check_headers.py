import requests
import json
from datetime import datetime

def main(url, noclear):
    if noclear is None or noclear.lower() != "true":
        print("\033c")  # Clear console

    print("===================================================================")
    print("=                       HTTP Headers check                        =")
    print("===================================================================")

    while url is None or url == "":
        print("\nurl parameter is not specified.")
        url = input("Enter URL to check (ex. https://www.mysite.com) or 'exit' to terminate this script: ")
        if url.lower() == "exit":
            exit()

    try:
        response = requests.get(url, headers={"Cache-Control": "no-cache"})
        response.raise_for_status()  # Raise HTTPError for bad responses
    except requests.exceptions.RequestException as e:
        print("-------------------------------------------")
        print(f" Error while requesting URL {url}")
        print(f" >> {e}")
        print("-------------------------------------------")
        exit()

    with open('headers-config.json', 'r') as config_file:
        #config = json.load(config_file)
        config = get_config()  # Assuming you have a function to load your configuration
        verify_headers(response.headers, config)

    exp = datetime.strptime(config['Expires'], '%Y-%m-%d')
    today = datetime.now()

    print("\nVersion :".ljust(15), config['Version'])
    print("Expire :".ljust(15), exp.strftime('%d/%m/%Y'), "|", "Expired !" if exp <= today else "Valid")

    print("Checking :".ljust(15), url)

    if exp <= today:
        print("\n -------------------------------------------")
        print(" >> Please update 'headers-config.json' file")
        print(" -------------------------------------------")
        print("Last version :".ljust(15), "https://capgemini.sharepoint.com/:f:/r/sites/CyberSecurityFR2/Shared%20Documents/General/PowerShell%20Scripts?csf=1&web=1&e=0rbJMN")

    print("\n===================================================================")
    print("=                            Raw view                             =")
    print("===================================================================\n")

    for h, value in response.headers.items():
        print(f"{h}: {value}")

    print("\n===================================================================")
    print("=                        Consider to ADD Header                   =")
    print("===================================================================")

    hashit = False
    for ha in config['ToVerify']:
        present = ha['Name'] in response.headers
        if not present:
            hashit = True
            print("\n", ha['Name'])
            for ms in ha['RequiredValues']:
                print(f"Required :{' '.ljust(20)} {ms['Label']}")
                if ms['Description']:
                    print(f"{' '.ljust(20)} {ms['Description']}")
                if ms['Links']:
                    for url in ms['Links'].split("|"):
                        print(f"{'See :'.ljust(26)} {url}")
    if not hashit:
        print("None - No action required")

    print("\n===================================================================")
    print("=                       Consider to VERIFY Value                  =")
    print("===================================================================")

    hashit = False
    nothing_to_write = True
    for ha in config['ToVerify']:
        present = ha['Name'] in response.headers
        if present:
            actual_value = response.headers[ha['Name']]
            nothing_to_write = False
            print("\n", ha['Name'])
            print(f"Actual :{' '.ljust(20)} {actual_value}")
            for ms in ha['RequiredValues']:
                if not actual_value or not re.search(ms['Value'], actual_value):
                    hashit = True
                    print(f"Required :{' '.ljust(20)} {ms['Label']}")
                    if ms['Description']:
                        print(f"{' '.ljust(20)} {ms['Description']}")
                    if ms['Links']:
                        for url in ms['Links'].split("|"):
                            print(f"{'See :'.ljust(26)} {url}")
            for fv in ha['ForbidenValues']:
                if actual_value and re.search(fv['Value'], actual_value):
                    hashit = True
                    print(f"Forbiden :{' '.ljust(20)} {fv['Label']}")
                    if fv['Description']:
                        print(f"{' '.ljust(20)} {fv['Description']}")
                    if fv['Links']:
                        for url in fv['Links'].split("|"):
                            print(f"{'See :'.ljust(26)} {url}")
            for rv in ha['RecommandedValues']:
                if not actual_value or not re.search(rv['Value'], actual_value):
                    hashit = True
                    print(f"Recommanded :{' '.ljust(20)} {rv['Label']}")
                    if rv['Description']:
                        print(f"{' '.ljust(20)} {rv['Description']}")
                    if rv['Links']:
                        for url in rv['Links'].split("|"):
                            print(f"{'See :'.ljust(26)} {url}")
            for nrv in ha['NotRecommandedValues']:
                if actual_value and re.search(nrv['Value'], actual_value):
                    hashit = True
                    print(f"Not recommanded :{' '.ljust(20)} {nrv['Label']}")
                    if nrv['Description']:
                        print(f"{' '.ljust(20)} {nrv['Description']}")
                    if nrv['Links']:
                        for url in nrv['Links'].split("|"):
                            print(f"{'See :'.ljust(26)} {url}")
            for wrnv in ha['Warnings']:
                if actual_value and re.search(wrnv['Value'], actual_value):
                    hashit = True
                    print(f"Warning :{' '.ljust(20)} {wrnv['Label']}")
                    if wrnv['Description']:
                        print(f"{' '.ljust(20)} {wrnv['Description']}")
                    if wrnv['Links']:
                        for url in wrnv['Links'].split("|"):
                            print(f"{'See :'.ljust(26)} {url}")
            if not hashit:
                print(f"Status :{' '.ljust(20)} Ok - No action required")
            else:
                print("\nSuggested :".ljust(20), ha['SuggestedValue'])

    if nothing_to_write:
        print("None.")

    print("\n===================================================================")
    print("=                       Consider to REMOVE Header                 =")
    print("===================================================================")

    hashit = False
    for hr in config['ToRemove']:
        present = hr['Name'] in response.headers
        if present:
            hashit = True
            print("\n", hr['Name'])
            print(f"Actual :{' '.ljust(20)} {response.headers[hr['Name']]}")
            if hr['Description']:
                print(f"{' '.ljust(20)} {hr['Description']}")
            if hr['Links']:
                for url in hr['Links'].split("|"):
                    print(f"{'See :'.ljust(26)} {url}")

    if not hashit:
        print("None - No action required")

    print("\n--- End ---")
 

def verify_headers(headers, config):
    to_verify = config.get("ToVerify", [])
    for ha in to_verify:
        name = ha.get('Name')
        if name is None:
            print("Error: 'Name' key not found in header configuration.")
            continue

        present = name in headers
        # Rest of the code remains unchanged...

        required_values = ha.get('RequiredValues', [])
        if not isinstance(required_values, list):
            print(f"Error: 'RequiredValues' is not a list for header '{name}'.")
            continue

        for ms in required_values:
            if not isinstance(ms, dict):
                print(f"Error: 'RequiredValues' item is not a dictionary for header '{name}'.")
                continue

            value = ms.get('Value')
            if value is None:
                print(f"Error: 'Value' key not found in 'RequiredValues' of header '{name}'.")
                continue

def get_config():
    with open('.\headers-config.json') as config_file:
        return json.load(config_file)

if __name__ == "__main__":
    url = None
    noclear = None
    main(url, noclear)
