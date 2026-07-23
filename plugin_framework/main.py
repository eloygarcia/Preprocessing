# main.py

from plugin_manager import PluginManager


def main():

    # Crear el gestor de plugins
    plugin_manager = PluginManager()

    # Buscar todos los plugins instalados
    plugin_manager.load_plugins()

    # Mostrar los plugins encontrados
    for plugin in plugin_manager.plugins:
        print(plugin.name)

    # Aquí arrancaría la interfaz gráfica (Qt)
    # viewer = MainWindow(plugin_manager)
    # viewer.show()


if __name__ == "__main__":
    main()