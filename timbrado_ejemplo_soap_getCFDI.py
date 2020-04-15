#Ejemplo de ws de timbrado getCFDI(). Para timbrado masivo(con miles de conceptos enviar a )
#Para usar este ejemplo debes instalar Zeep mediante pip
#Comando
#>pip install zeep

from zeep import Client #En este caso de utiliza la libreria Zeep para clientes SOAP. Puede utilizar la libreria de su eleccion
from zeep.exceptions import Fault
from zeep.plugins import HistoryPlugin # con este plugin puedes obtener el historico de peticiones y respuestas

import io
import configparser
from os import path
import os
import time;
from lxml import etree
from zipfile import ZipFile #necesario para extraer el zip donde viene el XML timbrado

#Para evitar colocar accesos directamente en codigo se lee de un archivo.
if not path.exists('config.ini'):
    print ("Archivo de configuracion no existe")
else:      
    config = configparser.ConfigParser()
    config.read('config.ini')

    usuario = config['timbrado']['UsuarioSIFEI']#"Usuario SIFEI"
    password =config['timbrado']['PasswordSIFEI']# "Password SIFEI"
    idEquipo =config['timbrado']['IdEquipoGenerado']# "ID de Equipo SIFEI"

    #directorio relativo a este script compatible con windows y linux(para luego generar el path para leer el XML sellado)
    xmlDIR=os.path.dirname(os.path.abspath(__file__))
    workDir=os.path.dirname(os.path.abspath(__file__))
    timestamp=str(time.time())
    try:
        #Para este ejmplo se envia a timbrar un XML ya sellado  desde una ruta:
        xml_path = os.path.join(xmlDIR,"assets/CFDI33_sellado.xml")
        zipPath = os.path.join(xmlDIR,"assets/CFDI33_timbrado.zip")
        destino_path = os.path.join(xmlDIR,"assets/")
        
        serie = "" #Serie vacia para usuarios de timbrado    
        
        #Se lee el archivo xml establecido en la variable xml_path
        file = open(xml_path, 'r')
        readxml = file.read()
        file.close()
        
        #Se transforma el xml en array de bytes
        xml_bytesArray = bytearray(readxml,'utf-8')
        #Se crea history para cliente SOAP
        history = HistoryPlugin()
        #Se establece el cliente SOAP mediante la clase 'Cliente' de Zeep
        client = Client(
            wsdl="http://devcfdi.sifei.com.mx:8080/SIFEI33/SIFEI?wsdl",
            plugins=[history]  #Plugin para guardar el request y response para la fase de intregracion(podras ver alli los errores arrojados)
        )
        #Se pasan los parametros requeridos para el metodo de timbrado getCFDI()
        result = client.service.getCFDI(usuario, password, xml_bytesArray, serie, idEquipo)
        #Se recibe el xml en caso de ser timbrado(viene dentro de un zip)
        if result != None:
            
            f = open(zipPath, 'wb')
            writer = io.BufferedWriter(f)
            writer.write(result)
            writer.close()
            #una vez escrito el zip, debemos extraer el XML timbrado
            with ZipFile(zipPath, 'r') as zipObj:
                zipObj.extractall(destino_path)

            print("Comprobante almacenado en su sistema.")

    except Fault as fault:
        #Se extrae el request en caso de excepcion
        detail_decoded = client.wsdl.types.deserialize(fault.detail[0])
    #    timbrado = detail_decoded.xml        #Para extraer xml timbrado en caso de utilizar el metodo getCFDISign()
        print(detail_decoded)
    finally:
         #En ambiente de pruebas mandamos el requets y response  a un archivo respecticamente para inspeccionarlos en caso de error, se asigna un timestamp para identificarlos:
        with open(os.path.join(workDir,"timbrado_request_"+timestamp+".xml"),'w', encoding="utf-8") as request:
            request.write(etree.tostring(history.last_sent["envelope"], encoding="unicode", pretty_print=True))
        with open(os.path.join(workDir,"timbrado_response_"+timestamp+".xml"),'w', encoding="utf-8") as request:
            request.write(etree.tostring(history.last_received["envelope"], encoding="unicode", pretty_print=True)) 
#Para extraer xml timbrado en caso de utilizar el metodo getCFDISign()    
#    if timbrado != None:
        
#        f = open(zipPath, 'wb')
#        writer = io.BufferedWriter(f)
#        writer.write(timbrado)
#        writer.close()
#        print("Comprobante almacenado en su sistema.")    
       
        
    
