from fastapi import FastAPI
from plugin_manager import PluginManager

app = FastAPI()

plugin_manager = PluginManager()

@app.get("/algorithms")
def algorithms():
    return plugin_manager.get_catalog()