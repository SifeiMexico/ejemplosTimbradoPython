import base64
#instalar con > pip install pycryptodome que es mas nuevo y mantiene soporte a diferencia de pycrypto
from Cryptodome.Hash import SHA256 
from Cryptodome.Signature import PKCS1_v1_5
from Cryptodome.PublicKey import RSA
from Cryptodome.IO import PEM

from base64 import b64decode

import lxml.etree as ET # para generar cadenaOriginal
class CFDIUtils:
    def sellar(self,cadenaOriginal,llavePem,passw,mode='PEM'):
        digest = SHA256.new()
        #print(cadenaOriginal)
        digest.update(cadenaOriginal.encode('utf-8'))
        read=''
        if mode=='PEM':
            read='r'
        elif mode=='DER':
            read='rb'

        else:
            raise Exception('Modo no valido'+read)
        with open (llavePem, read) as llavePEM:
            private_key = RSA.importKey(llavePEM.read(),passw)

        signer = PKCS1_v1_5.new(private_key)
        sig = signer.sign(digest)
        #por ultimo se codifica en base64
        return base64.b64encode(sig) #base64 sin nueva linea

    def generaCadenaOriginal(self,xml_filename):
        dom = ET.parse(xml_filename)
        xslt = ET.parse("./sat/xslt/cadenaoriginal_3_3.xslt")
        transform = ET.XSLT(xslt)
        return str(transform(dom))

def pegarSello(xml_filename,sello):
   dom = ET.parse(xml_filename)
   xsi="http://www.w3.org/2001/XMLSchema-instance"

   #ns = {"xsi": xsi,"cfdi": "http://www.sat.gob.mx/cfd/3"}
   dom.getroot().attrib['Sello']=sello
   #ET.SubElement(dom.getroot(),'{cfdi}Comprobante',nsmap=ns).set('Sello',sello)
   dom.write('./assets/file_new.xml')
    
 

xmlPath="./assets/CFDI33_sellado.xml"
cfdiUtils= CFDIUtils()

cadenaOriginal=cfdiUtils.generaCadenaOriginal(xmlPath)

#con PEM,suponiendo que el pem no tenga password
print("con pem:")
sello=cfdiUtils.sellar(cadenaOriginal,"llave.pem",None)
print(sello)
print('Con key(DER):')
sello=cfdiUtils.sellar(cadenaOriginal,"CSD.key","12345678a",'DER')
print(sello)


print(cadenaOriginal)

pegarSello(xmlPath,sello)

pemKeyWithPassPhrase=PEM.encode(open('key.key','rb').read(),'ENCRYPTED PRIVATE KEY')
print(pemKeyWithPassPhrase)
open('ENCRYPTED_KEY.pem','w').write(pemKeyWithPassPhrase)
sello2=cfdiUtils.sellar(cadenaOriginal,"ENCRYPTED_KEY.pem","12345678a",'PEM')
print(sello2)
