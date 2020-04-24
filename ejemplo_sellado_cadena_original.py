import base64

from Crypto.Hash import SHA256 
from Crypto.Signature import PKCS1_v1_5
from Crypto.PublicKey import RSA

import lxml.etree as ET # para generar cadenaOriginal

def sellar(cadenaOriginal,llavePem):
    digest = SHA256.new()
    print(cadenaOriginal)
    digest.update(cadenaOriginal.encode('utf-8'))

    with open (llavePem, "r") as llavePEM:
        private_key = RSA.importKey(llavePEM.read())

    signer = PKCS1_v1_5.new(private_key)
    sig = signer.sign(digest)
    #por ultimo se codifica en base64
    return base64.encodebytes(sig)

def generaCadenaOriginal(xml_filename):
    dom = ET.parse(xml_filename)
    xslt = ET.parse("./xslt/cadenaoriginal_3_3.xslt")
    transform = ET.XSLT(xslt)
    return str(transform(dom))
    
    

cadenaOriginal=generaCadenaOriginal("./assets/CFDI33_sellado.xml")
sello=sellar(cadenaOriginal,"llave.pem")
print(cadenaOriginal)
print(sello)
