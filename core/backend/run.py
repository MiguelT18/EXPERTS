from app import create_app
import uvicorn

app = create_app()

if __name__ == "__main__":
  # Ejecutar el servidor en modo desarrollo
  uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)