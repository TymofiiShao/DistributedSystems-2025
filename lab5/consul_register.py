import consul
import socket

def register_service(service_name, service_id, port, check_path="/health", health_port=None):
    import consul
    import socket

    c = consul.Consul(host="localhost", port=8500)
    hostname = socket.gethostbyname(socket.gethostname())
    health_port = health_port if health_port else port  # 👈 додаємо

    check = {
        "http": f"http://{hostname}:{health_port}{check_path}",
        "interval": "10s",
        "timeout": "1s"
    }

    c.agent.service.register(
        name=service_name,
        service_id=service_id,
        address=hostname,
        port=port,
        check=check
    )
    print(f"[CONSUL] Зареєстровано сервіс: {service_name} на {hostname}:{port}")
