# Hands-on DevOps Tasks Roadmap

A structured, phased practice roadmap to build, containerize, and deploy this two-tier application from scratch.

**How to use this guide**:
- Follow the milestones below in order.
- Research and implement each task independently to build real-world DevOps muscle memory.
- If you get stuck or want to verify your approach, refer to the configuration files and manifests in this repository for guidance and reference solutions.

## Tasks

### Phase 1: Basic Containerization
- [ ] Create a single-stage simple Dockerfile for the application using a standard Python base image.
- [ ] Build your image locally, run a local MongoDB container, and verify that your application container connects and serves traffic on port 8000.

### Phase 2: Multi-Stage Build & Distroless Hardening
- [ ] Write an optimized multi-stage Dockerfile with builder and runtime stages using a distroless image.
- [ ] Tag and push your optimized container image to your Docker Hub repository.

### Phase 3: Multi-Container Setup with Docker Compose
- [ ] Write a `docker-compose.yml` file defining the API and MongoDB database services.
- [ ] Configure custom container networking for service discovery and a named persistent volume for database storage.
- [ ] Verify multi-container communication and data persistence across container restarts.

### Phase 4: Kubernetes Deployment on Minikube
- [ ] Create Kubernetes Secret manifests for MongoDB root and application credentials.
- [ ] Create a ConfigMap manifest containing the database initialization script.
- [ ] Deploy MongoDB using a StatefulSet with dynamic storage provisioning (PVC) and a Headless Service.
- [ ] Deploy the FastAPI application using a Deployment manifest with resource limits and health probes (startup, liveness, readiness).
- [ ] Expose the application via a NodePort Service and verify endpoint connectivity on Minikube.
