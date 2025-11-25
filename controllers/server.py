# server.py
from fastapi import FastAPI
from controllers.mxf_controller import MXFController
from controllers.health_controller import HealthController
from controllers.download_controller import DownloadController

class Server:
    def __init__(self):
        self.app = FastAPI(
            title="Audio Analysis API",
            description="API para Análise de Áudio em Arquivos MXF",
            version="1.0.0",
            docs_url="/docs",
            redoc_url="/redoc"
        )
        
        # Inicializa os controllers
        self.mxf_controller = MXFController()
        self.health_controller = HealthController()
        self.download_controller = DownloadController()
        
        # Registra as rotas
        self._register_routes()
    
    def _register_routes(self):

        """Registra todas as rotas dos controllers"""
        
        self.app.include_router(
            self.mxf_controller.router,
            prefix="/api/v1",
            tags=["Análise de Áudio"]
        )
        
        self.app.include_router(
            self.health_controller.router,
            prefix="/api/v1",
            tags=["Monitoramento"]
        )
        
        self.app.include_router(
            self.download_controller.router,
            prefix="/api/v1",
            tags=["Download de Arquivos"]   
        )

def create_app():
    server = Server()
    return server.app

if __name__ == "__main__":
    import uvicorn
    app = create_app()
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        timeout_keep_alive=300,
        log_level="info"
    )