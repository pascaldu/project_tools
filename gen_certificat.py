from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.x509.extensions import Extension, SubjectAlternativeName
from datetime import datetime, timedelta, timezone
from cryptography.hazmat.primitives import hashes

def generate_key():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    # Extraire la clé publique
    public_key = private_key.public_key()

    return private_key, public_key

def generate_csr(private_key, common_name, sans, organization, country, locality, software):
    subject = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, common_name),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, organization),
        x509.NameAttribute(NameOID.COUNTRY_NAME, country),
        x509.NameAttribute(NameOID.LOCALITY_NAME, locality),
        x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, software)
    ])
    alt_names = [x509.DNSName(san) for san in sans]

    builder = x509.CertificateSigningRequestBuilder().subject_name(subject)
    builder = builder.add_extension(x509.SubjectAlternativeName(alt_names), critical=False)
    csr = builder.sign(private_key, hashes.SHA256(), default_backend())

    return csr

def self_sign_certificate(csr, private_key, days=365):
    now = datetime.now(timezone.utc)
    alt_name_extension = csr.extensions[0]
    serial_number=x509.random_serial_number()
    print(f"\nSerial number : {serial_number}")
    print(f"\ndate de début : {now}")
    print(f"\ndate de fin : {now + timedelta(days=days)}")
    print(f"\nIssuer : {csr.subject}")
    print(f"\nPublic key : {csr.public_key}")


    cert = x509.CertificateBuilder().subject_name(
        csr.subject
    ).issuer_name(
        csr.subject
    ).public_key(
        csr.public_key()
    ).serial_number(
        serial_number
    ).not_valid_before(
        now
    ).not_valid_after(
        now + timedelta(days=days)
    ).add_extension(
        alt_name_extension.value,
        alt_name_extension.critical,
    ).sign(private_key, hashes.SHA256(), default_backend())

    return cert

def save_csr(csr):
    with open("certificate-request.csr", "wb") as csr_file:
        csr_file.write(csr.public_bytes(serialization.Encoding.PEM))


def save_key_and_cert(private_key, cert, public_key):
    with open("private-key.pem", "wb") as key_file:
        key_file.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.BestAvailableEncryption(b"passphrase"),
            )
        )
    
    with open("certificate.pem", "wb") as cert_file:
        cert_file.write(cert.public_bytes(serialization.Encoding.PEM))

    # Sauvegarder la clé publique dans un fichier
    with open("public_key.pem", "wb") as public_key_file:
        public_key_file.write(
            public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
        )


def main():
    common_name = "www.telepac.agriculture.gouv.fr"
    sans = [
        "isis1.telepac.agriculture.gouv.fr",
        "www.telepac.agriculture.gouv.fr",
        "www4.telepac.agriculture.gouv.fr",
        "www1.telepac.agriculture.gouv.fr",
        "www3.telepac.agriculture.gouv.fr",
        "mobile.telepac.agriculture.gouv.fr",
        "www2.telepac.agriculture.gouv.fr",
        "maintenance-www.telepac.agriculture.gouv.fr",
        "maintenance-isis.telepac.agriculture.gouv.fr",
        "isis4.telepac.agriculture.gouv.fr",
        "isis2.telepac.agriculture.gouv.fr",
        "isis.telepac.agriculture.gouv.fr",
        "isis3.telepac.agriculture.gouv.fr"
    ]
    
    organization = "MINISTERE DE L'AGRICULTURE ET DE LA SOUVERAINETE ALIMENTAIRE"
    country = "FR"
    locality = "Paris"
    software = "fortigate"

    print(f"\nCN : {common_name}")
    print(f"\nAlgorithme : sha256WithRSAEncryption")
    print(f"\nO : {organization}")
    print(f"\nC : {country}")
    print(f"\nL : {locality}")
    print(f"\nLogiciel : {software}")
    
    private_key, public_key = generate_key()
    print(f"Private key :\n{private_key}")
    print(f"Public key :\n{public_key}")

#    csr = generate_csr(private_key, common_name, sans)
    csr = generate_csr(private_key, common_name, sans, organization, country, locality, software)
    print(f"CSR : {csr}")

    save_csr(csr)
    cert = self_sign_certificate(csr, private_key)
    
    save_key_and_cert(private_key, cert, public_key)
 
    print(f"\nSan : \n")
    for san in sans:
        print(f"{san},")
   
    print(f"\nPrivate key dans : private-key.pem")
    print(f"CSR dans certificate-request.csr")
    print(f"Certificat dans certificate.pem")
    print(f"Public Key dans public_key.pem")

if __name__ == "__main__":
    main()
