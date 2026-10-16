from agente import responder_pregunta, generar_consulta_sql

print("===================================")
print("       AGENTE EXPERTO EN SQL")
print("===================================")

while True:
    print("\nMENU PRINCIPAL")
    print("1. Consultar conocimientos de SQL")
    print("2. Generar una consulta SQL")
    print("3. Salir")

    opcion = input("\nSelecciona una opcion: ").strip()

    if opcion == "1":
        pregunta = input("\nEscribe tu pregunta sobre SQL: ")
        respuesta = responder_pregunta(pregunta)

        print("\nRESPUESTA:")
        print(respuesta)

    elif opcion == "2":
        solicitud = input(
            "\nDescribe la consulta SQL que necesitas: "
        )

        consulta = generar_consulta_sql(solicitud)

        print("\nCONSULTA SQL GENERADA:")
        print(consulta)

    elif opcion == "3":
        print("Agente SQL finalizado.")
        break

    else:
        print("Opcion no valida. Selecciona 1, 2 o 3.")