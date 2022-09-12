import zmq
import sys      
import json   
 
def escogerServidor(_servidor_actual, _cantidad_servers):
    if _servidor_actual >= _cantidad_servers-1:
        _servidor_actual = 0
    else:
        _servidor_actual +=1
    return(_servidor_actual)

def cargarData():
    with open('data.json') as archivo:
        data = json.load(archivo)
        servidores = data['servidores']
        archivos = data['archivos']
        return(servidores, archivos)

def guardarData(_servidores, _archivos):
    with open("data.json", 'w') as archivo:
        data = {'servidores': _servidores, 'archivos': _archivos}
        json.dump(data, archivo, indent=4)

def indexServidor(_server_direccion, _servidores):
    for server in _servidores:
        if server['direccion'] == _server_direccion:
            return(server['id']-1)
    return(False)

def buscarServidor(_server_direccion, _servidores):
    for server in _servidores:
        if server['direccion'] == _server_direccion:
            return(server)
    return(False)

def estadoServidor(_server_direccion, _servidores):
    servidor = buscarServidor(_server_direccion, _servidores)
    if servidor:
        if servidor['estado'] == 'conectado':
            return('negarConexion')
        else:
            return('permitirConexion')
    return('serverNoExiste')

def buscarArchivoHash(_hash, _archivos):
    for archivo in _archivos:
        if archivo['hash'] == _hash:
            return(archivo)
    return(False)

def buscarArchivoNombre(_nombre_archivo, _archivos):
    for archivo in _archivos:
        if archivo['nombre'] == _nombre_archivo:
            return(archivo)
    return(False)

def ubicacionArchivo(_nombre_archivo, _archivos):
    ubicacion = ''
    archivo = buscarArchivoNombre(_nombre_archivo, _archivos)
    if archivo:
        for u in archivo['ubicacion']:
            ubicacion += u+' '
        return(ubicacion)
    else:
        return(False)



def main():
    IP = sys.argv[1]
    PUERTO = sys.argv[2]

    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind(f'tcp://{IP}:{PUERTO}')
    print('Servidor Proxy iniciado')

    servidores, archivos = cargarData()
    print(servidores)
    print(archivos)
    cantidad_servers = 0
    servidor_actual = 0

    archivo = buscarArchivoHash('54651da5d1sa5d4sa65d1asd', archivos)
    print(archivo)
    archivo = buscarArchivoNombre('b.txt', archivos)
    print(archivo)
    archivo = ubicacionArchivo('a.txt', archivos)
    print(archivo)

    print('PROXY ESCUCHANDO')
    while True:
        print('-------------------------------------------------------------------')
        print(servidores)
        print('-------------------------------------------------------------------')
        print(archivos)
        print('-------------------------------------------------------------------')
        mensaje = socket.recv_multipart()
        print(mensaje)

        if mensaje[0].decode() == 'serverConexion':
            server_direccion = mensaje[1].decode()
            print(server_direccion)
            estado_servidor = estadoServidor(server_direccion, servidores)
            if estado_servidor == 'permitirConexion':
                socket.send('permitirConexion'.encode())
                index = indexServidor(server_direccion, servidores)
                servidores[index]['estado'] = 'conectado'

            elif estado_servidor == 'negarConexion':
                socket.send('negarConexion'.encode())

            else:
                nuevo_server = {
                    'id': len(servidores)+1,
                    'direccion': server_direccion,
                    'estado': 'conectado'
                }
                servidores.append(nuevo_server)
                guardarData(servidores, archivos)
                cantidad_servers += 1
                print(servidores)
                print(f'Servidores Disponibles: {cantidad_servers}')
                socket.send('permitirConexion'.encode())
            
            print(servidores)

        if mensaje[0].decode() == 'verificarArchivo':
            hash_archivo = mensaje[1].decode()
            nombre_archivo = mensaje[2].decode()
            if buscarArchivoHash(hash_archivo, archivos):
                socket.send('archivoExiste'.encode())
            else:
                if buscarArchivoNombre(nombre_archivo, archivos):
                    socket.send('nombreArchivoExiste'.encode())
                else:
                    nuevo_archivo = {
                        'nombre': nombre_archivo,
                        'hash': hash_archivo,
                        'ubicacion': []
                    }
                    archivos.append(nuevo_archivo)
                    socket.send('subidaAceptada'.encode())

        if mensaje[0].decode() == 'subirArchivo':
            hash_archivo = mensaje[1].decode()
            archivo = buscarArchivoHash(hash_archivo, archivos)
            print(archivo)
            if archivo:
                print(f'El archivo {archivo["nombre"]} se esta subiendo')
                print(servidor_actual)
                servidor_enviar = servidores[servidor_actual]['direccion']
                print(servidor_enviar)
                socket.send(str(servidor_enviar).encode())
                print(archivo['ubicacion'])
                archivo['ubicacion'].append(servidor_enviar)
                print(archivo)
            else:
                print('En subirArchivo no se encontro el archivo')
                socket.send('Error durante la subida del archivo'.encode())

            
            servidor_actual = escogerServidor(servidor_actual, cantidad_servers)

        if mensaje[0].decode() == 'exitoSubirArchivo':
            guardarData(servidores, archivos)
            socket.send('archivoSubidoConExito'.encode())

        if mensaje[0].decode() == 'bajarArchivo':
            nombre_archivo = mensaje[1].decode()
            archivo = buscarArchivoNombre(nombre_archivo, archivos)
            print(archivo)

            if archivo:
                ubicacion_archivo = ''
                for u in archivo['ubicacion']:
                    ubicacion_archivo += f'{u} '
                print(ubicacion_archivo)
                hash = archivo['hash']
                socket.send_multipart([hash.encode(), ubicacion_archivo.encode()])
            else:
                print(f'El archivo {nombre_archivo} NO se encontro')
                socket.send(f'archivoNoExiste'.encode())

        if mensaje[0].decode() == 'verArchivos':
            archivos_disponibles = ''
            for archivo in archivos:
                archivos_disponibles += f'{archivo["nombre"]}, '
            socket.send(archivos_disponibles.encode())
        


    

if __name__ == "__main__":
    main()