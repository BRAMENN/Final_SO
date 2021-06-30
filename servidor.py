import json, socket


def registrar_cliente(lista_clientes):
    f = open("clientes.txt", "w")
    for cliente in lista_clientes:
        f.write("-" + cliente)
    f.close()


def cargar_clientes():
    f = open("clientes.txt", "r+")
    clientes = f.read()
    lista_clientes = []
    if len(clientes) > 0:
        clientes.replace("\n", "")
        clientes = clientes.split("-")
        clientes = clientes[1:]
        lista_clientes = clientes
    return lista_clientes
    f.close()


def listar_ficheros(id_cliente):
    f = open(str(id_cliente) + ".txt", "r")
    data = f.read()
    data = json.loads(data)
    f.close()
    ficheros = []
    for fichero in data["ficheros"]:
        for key in fichero.keys():
            ficheros.append(key)

    return ficheros


# PETICIONES DE SALIDA
def HTTP_salientes(id_cliente, peticion, tipo, contenido):
    if peticion == "POST":
        if tipo == "notificacion_OK":
            mensaje = {"peticion": peticion, "tipo": tipo, "contenido": contenido}
        if tipo == "notificacion_FAIL":
            mensaje = {"peticion": peticion, "tipo": tipo, "contenido": contenido}
        if tipo == "notificacion_LISTAR_F":
            ficheros = listar_ficheros(id_cliente)

    JSON = json.dumps(mensaje)
    return JSON


def HTTP_entrantes(HTTP, lista_clientes, contenido):
    HTTP = eval(HTTP)
    if HTTP["peticion"] == "POST":
        if HTTP["tipo"] == "creacion_c" and not HTTP["id_cliente"] in lista_clientes:
            id_cliente_f = HTTP["id_cliente"] + ".txt"
            f = open(id_cliente_f, "w")
            lista_clientes.append(HTTP["id_cliente"])
            registrar_cliente(lista_clientes)
            cliente = {"id_cliente": HTTP["id_cliente"], "ficheros": HTTP["ficheros"]}
            CLI = json.dumps(cliente)
            f.write(CLI)
            f.close()
            contenido = "Se creo el cliente correctamente {}".format(HTTP["id_cliente"])
            return HTTP_salientes(HTTP["id_cliente"], "POST", "notificacion_OK", contenido)
        else:
            id_cliente_f = HTTP["id_cliente"] + ".txt"
            f = open(id_cliente_f, "w")
            cliente = {"id_cliente": HTTP["id_cliente"], "ficheros": HTTP["ficheros"]}
            CLI = json.dumps(cliente)
            f.write(CLI)
            f.close()
            contenido = "Se creo el actualizo correctamente {}".format(HTTP["id_cliente"])
            return HTTP_salientes(HTTP["id_cliente"], "POST", "notificacion_OK", contenido)

    elif HTTP["peticion"] == "GET":
        print(lista_clientes)
        if HTTP["tipo"] == "notificacion_LISTAR_F" and  HTTP["id_cliente"] in lista_clientes:
            ficheros = listar_ficheros(HTTP["id_cliente"])
            contenido = "Los ficheros del cliente {} son: ".format(HTTP["id_cliente"])
            for fichero in ficheros:
                contenido += "\n" + fichero
            return HTTP_salientes(HTTP["id_cliente"], "POST", "notificacion_OK", contenido)
        else:
            contenido = "NO se encontro el cliente a listar {}".format(HTTP["id_cliente"])
        return HTTP_salientes("", "POST", "notificacion_FAIL", contenido)
    else:
        contenido = "NO se reconocio la peticion {}".format(HTTP)
        return HTTP_salientes("", "POST", "notificacion_FAIL", contenido)


if __name__ == "__main__":

    mi_socket = socket.socket()
    mi_socket.bind(("localhost", 8001))
    mi_socket.listen(5)

    while True:
        conexion, addr = mi_socket.accept()
        print("Nueva conexion establecida", addr)

        pet = conexion.recv(1024)
        if pet != "NoneType":
            pet = pet.decode("ascii")
            print(pet)
            lista_clientes = cargar_clientes()
            res = HTTP_entrantes(pet, lista_clientes, "")
        else:
            contenido = "La peticion NO se ejecuto correctamente no se envio informacio en la data"
            res = HTTP_salientes("", "POST", "notificacion_FAIL", contenido)
        conexion.send(res.encode("ascii"))

        conexion.close()