from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Lifecycle events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management."""
    # Startup
    print("Starting Cork Mobility Lab API...")
    yield
    # Shutdown
    print("Shutting down Cork Mobility Lab API...")

# Create FastAPI app
app = FastAPI(
    title="Cork Mobility Lab API",
    description="Agent-based traffic simulation and optimisation platform for Cork, Ireland",
    version="0.1.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "cork-mobility-api"}

# Network endpoints (placeholder)
@app.get("/api/network")
async def get_network():
    """Get transport network (placeholder)."""
    return {"message": "Network endpoint - to be implemented"}

# Simulation endpoints (placeholder)
@app.get("/api/simulations")
async def list_simulations():
    """List simulations (placeholder)."""
    return {"simulations": []}

# Scenario endpoints (placeholder)
@app.get("/api/scenarios")
async def list_scenarios():
    """List scenarios (placeholder)."""
    return {"scenarios": []}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
