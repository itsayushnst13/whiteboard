# infrastructure/

Reserved for infrastructure-as-code (Terraform, Kubernetes manifests, CDN
and DNS config) once SyncBoard has an environment to provision.

The foundation milestone runs entirely through `docker-compose.yml` for
local development, so there is nothing to provision yet. This directory
exists now so that when cloud infrastructure is introduced it has an
established home instead of being bolted on wherever is convenient.
