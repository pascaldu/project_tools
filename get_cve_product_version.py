import sys
import requests
import json

def get_cve_info(vendor_name,product_name, product_version):

    url = f"https://services.nvd.nist.gov/rest/json/cves/2.0?cpeName=cpe:2.3:a:{vendor_name}:{product_name}:{product_version}:*:*:*:*:*:*:*"
    print(f"url : {url}")
    response = requests.get(url)
    vulnerabilities_list = []

    if response.status_code == 200:
        data = json.loads(response.content)
        if data["totalResults"] > 0:
            print(f"Nombre total de vulnérabilités trouvées: {data['totalResults']}")
            
            for vulnerability in data["vulnerabilities"]:
                cve_id = vulnerability["cve"]["id"]
                description = vulnerability["cve"]["descriptions"][0]["value"]
                # Vérifier si le score CVSS V3 est disponible
                if "cvssMetricV30" in vulnerability["cve"]["metrics"]:
                    cvss_score = vulnerability["cve"]["metrics"]["cvssMetricV30"][0]["cvssData"]["baseScore"]
                # Sinon, essayer le score CVSS V2
                elif "cvssMetricV2" in vulnerability["cve"]["metrics"]:
                    cvss_score = vulnerability["cve"]["metrics"]["cvssMetricV2"][0]["cvssData"]["baseScore"]
                else:
                    cvss_score = None

                vulnerabilities_list.append({
                    "CVE ID": cve_id,
                    "Description": description,
                    "CVSS Score": cvss_score
                })

            # Affichage de la liste des vulnérabilités
            for vuln in vulnerabilities_list:
                print("CVE ID:", vuln["CVE ID"])
                print("Description:", vuln["Description"])
                print("CVSS Score:", vuln["CVSS Score"])
                print()
        else:
            print("Aucune vulnérabilité trouvée pour ce produit et cette version.")
    else:
        print("Une erreur s'est produite lors de la récupération des données.")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python script.py <vendor> <product> <version>")
        sys.exit(1)

    vendor =  sys.argv[1]
    product = sys.argv[2]
    version = sys.argv[3]

    get_cve_info(vendor,product, version)
