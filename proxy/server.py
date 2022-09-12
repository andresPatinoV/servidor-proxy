import zmq
import sys
import os
import errno

def crearDirectorio(_CARPETA):
    try:
        os.mkdir(_CARPETA)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


def main():
    IP = sys.argv[1]
    PUERTO = sys.argv[2]
    CARPETA = f'servidor{PUERTO}'

    PROXY_IP = IP
    PROXY_PUERTO = 5555

    crearDirectorio(CARPETA)
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect(f'tcp://{PROXY_IP}:{PROXY_PUERTO}')
    socket.send_multipart(['serverConexion'.encode(), f'{IP}:{PUERTO}'.encode()])
    respuesta = socket.recv()

    if respuesta.decode() == 'permitirConexion':
        print(f'Servidor {IP}:{PUERTO} conectado al Proxy')
        socket.close()
        socket = context.socket(zmq.REP)
        socket.bind(f'tcp://{IP}:{PUERTO}')
        
        
        while True:
            mensaje = socket.recv_multipart()
            print(mensaje[0])

            if mensaje[0].decode() == 'subirArchivo':
                file_info = mensaje[1]
                file_name = mensaje[2].decode()
                archivo = open(f'{CARPETA}/{file_name}', 'wb')
                archivo.write(file_info)
                archivo.close()
                socket.send(f'El fragmento {file_name} se escribio en el Servidor {IP}:{PUERTO}'.encode())

            if mensaje[0].decode() == 'bajarArchivo':
                file_name = mensaje[1].decode()
                archivo = open(f'{CARPETA}/{file_name}', 'rb')
                info = archivo.read()
                archivo.close()
                socket.send(info)


    elif respuesta.decode() == 'negarConexion':
        print(f'Servidor {IP}:{PUERTO} YA esta conectado al proxy.')
    else:
        print('NO se pudo establecer conexion con el Proxy')

    

if __name__ == "__main__":
    main()