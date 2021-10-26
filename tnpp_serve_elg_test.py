from elg import Service

service = Service.from_docker_image("tnpp:latest", "http://localhost:8000/process",8080)
service("Tämä on testilause. Koirat ovat kivaa, eikö niin?",sync_mode=True)



