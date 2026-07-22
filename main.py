import asyncio
import time
import psutil
from aiohttp import web

# Configuration
PORT = 8080

async def get_telemetry(request):
    """Exposes real-time system & container resource telemetry."""
    cpu_percent = psutil.cpu_percent(interval=0.5)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    net_io = psutil.net_io_counters()

    telemetry_payload = {
        "provider_telemetry": {
            "timestamp": int(time.time()),
            "status": "HEALTHY",
            "cpu": {
                "usage_percent": cpu_percent,
                "cores_logical": psutil.cpu_count(logical=True)
            },
            "memory": {
                "total_mb": round(memory.total / (1024 * 1024), 2),
                "used_mb": round(memory.used / (1024 * 1024), 2),
                "percent": memory.percent
            },
            "storage": {
                "total_gb": round(disk.total / (1024 * 1024 * 1024), 2),
                "used_gb": round(disk.used / (1024 * 1024 * 1024), 2),
                "percent": disk.percent
            },
            "network": {
                "bytes_sent": net_io.bytes_sent,
                "bytes_recv": net_io.bytes_recv
            }
        }
    }
    return web.json_response(telemetry_payload)

async def health_check(request):
    return web.json_response({"status": "UP", "service": "akash-depin-telemetry"})

app = web.Application()
app.add_routes([
    web.get('/health', health_check),
    web.get('/telemetry', get_telemetry)
])

if __name__ == '__main__':
    print(f"Starting Akash DePIN Telemetry Daemon on port {PORT}...")
    web.run_app(app, host='0.0.0.0', port=PORT)
