import uvicorn
from dotenv import load_dotenv
import os

if __name__ == "__main__":
    # Charger les variables d'environnement
    load_dotenv()
    
    # Configurer le serveur
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    debug = os.getenv("DEBUG", "True").lower() == "true"
    
    # Lancer le serveur
    uvicorn.run(
        "backend.app.main:app",
        host=host,
        port=port,
        reload=debug,
        workers=4
    )
