import os

from flask import Flask
from flask_caching import Cache
from flask_sqlalchemy import SQLAlchemy
from app.config import cache_config, factory

# Instancia global de extensiones
db = SQLAlchemy()
cache = Cache()

import redis
from app.config.cache_config import cache_config

# Crear una instancia de Redis
redis_client = redis.StrictRedis(
    host=cache_config['REDIS_HOST'],
    port=cache_config['REDIS_PORT'],
    db=cache_config['REDIS_DB'],
    password=cache_config.get('REDIS_PASSWORD', None),
    decode_responses=True
)

def create_app():
    """Crea e inicializa la aplicación Flask."""
    app = Flask(__name__)

    # Cargar configuración según el entorno
    app_context = os.getenv('FLASK_ENV', 'development')
    try:
        app.config.from_object(factory(app_context))
        app.config.update(cache_config)  # Agregar configuración de caché al app.config
    except KeyError as e:
        raise RuntimeError(f"Error al cargar la configuración: {e}")

    # Inicializar extensiones
    try:
        db.init_app(app)
        cache.init_app(app)  # Inicializa la caché usando app.config
    except Exception as e:
        raise RuntimeError(f"Error al inicializar extensiones: {e}")

    # Registrar Blueprints
    try:
        from app.routes import Stock
        app.register_blueprint(Stock, url_prefix='/api/v1')
    except ImportError as e:
        raise RuntimeError(f"Error al registrar blueprints: {e}")

    # Ruta de prueba
    @app.route('/ping', methods=['GET'])
    def ping():
        return {"message": "El servicio de stocks está en funcionamiento"}

    return app

