import os
from flask import Flask
from .routes import main as main_blueprint
from supabase import create_client


def create_app():
    app = Flask(__name__, 
                template_folder=os.path.join(os.path.dirname(__file__), '..', 'templates'),
                static_folder=os.path.join(os.path.dirname(__file__), '..', 'static'))
    app.secret_key = 'sua_chave_secreta'

    # Configurações do Supabase
    url = "https://ieedzrwbsaetrfijiyxx.supabase.co"
    key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImllZWR6cndic2FldHJmaWppeXh4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzA0MTU0ODYsImV4cCI6MjA0NTk5MTQ4Nn0.X79qMX49prHw6rPFJqX065Gv0uGtvyU0Ci5EiehEW2w"
    app.supabase = create_client(url, key)

    app.register_blueprint(main_blueprint)

    return app
