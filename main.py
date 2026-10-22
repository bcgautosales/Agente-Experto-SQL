
"""
Programa principal del agente experto en SQL.
"""

from orquestador import ejecutar_agente


def main():
    """Ejecuta el agente experto en SQL desde la terminal."""
    print("AGENTE EXPERTO EN SQL")
    print("=====================")
    print("Memoria conversacional activada.")
    print("Escribe 'salir' para terminar.")

    while True:
        solicitud = input("\nTú: ").strip()

        if solicitud.lower() == "salir":
            print("\nConversación finalizada.")
            break

        resultado = ejecutar_agente(solicitud)

        print("\nPROCESO DEL AGENTE")
        print("==================")
        print("Herramienta:", resultado["herramienta"])
        print("Origen:", resultado["origen"])

        print("\nAgente:")
        print(resultado["respuesta"])


if __name__ == "__main__":
    main()
