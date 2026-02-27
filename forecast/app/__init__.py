from flask import Flask
import os

def create_app():
    # 🚀 Definir o diretório raiz do projeto (um nível acima de app/)
    basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    # 🚀 Especificar template_folder e static_folder explicitamente
    app = Flask(__name__,
                template_folder=os.path.join(basedir, 'templates'),
                static_folder=os.path.join(basedir, 'static'))
    
    app.config.from_object('app.config.Config')
    
    with app.app_context():
        from . import routes
    
    return app