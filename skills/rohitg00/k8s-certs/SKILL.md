---
name: k8s-certs
description: Kubernetes certificate management with cert-manager. Use when managing TLS certificates, configuring issuers, or troubleshooting certificate issues.
---

# Certificate Management with cert-manager

Manage TLS certificates using kubectl-mcp-server's cert-manager tools.

## Check Installation

```python
certmanager_detect_tool()
```

## Certificates

### List Certificates

```python
# List all certificates
certmanager_certificates_list_tool(namespace="default")

# Check certificate status
# - True: Certificate ready
# - False: Certificate not ready (check events)
```

### Get Certificate Details

```python
certmanager_certificate_get_tool(
    name="my-tls",
    namespace="default"
)
# Shows:
# - Issuer reference
# - Secret name
# - DNS names
# - Expiry date
# - Renewal time
```

### Create Certificate

```python
kubectl_apply(manifest="""
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: my-tls
  namespace: default
spec:
  secretName: my-tls-secret
  issuerRef:
    name: letsencrypt-prod
    kind: ClusterIssuer
  dnsNames:
  - app.example.com
  - www.example.com
""")
```

## Issuers

### List Issuers

```python
# Namespace issuers
certmanager_issuers_list_tool(namespace="default")

# Cluster-wide issuers
certmanager_clusterissuers_list_tool()
```

### Get Issuer Details

```python
certmanager_issuer_get_tool(name="my-issuer", namespace="default")
certmanager_clusterissuer_get_tool(name="letsencrypt-prod")
```

### Create Let's Encrypt Issuer

```python
# Staging (for testing)
kubectl_apply(manifest="""
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-staging
spec:
  acme:
    server: https://acme-staging-v02.api.letsencrypt.org/directory
    email: admin@example.com
    privateKeySecretRef:
      name: letsencrypt-staging-key
    solvers:
    - http01:
        ingress:
          class: nginx
""")

# Production
kubectl_apply(manifest="""
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@example.com
    privateKeySecretRef:
      name: letsencrypt-prod-key
    solvers:
    - http01:
        ingress:
          class: nginx
""")
```

### Create Self-Signed Issuer

```python
kubectl_apply(manifest="""
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: selfsigned
spec:
  selfSigned: {}
""")
```

## Certificate Requests

```python
# List certificate requests
certmanager_certificaterequests_list_tool(namespace="default")

# Get request details (for debugging)
certmanager_certificaterequest_get_tool(
    name="my-tls-xxxxx",
    namespace="default"
)
```

## Troubleshooting

### Certificate Not Ready

```python
1. certmanager_certificate_get_tool(name, namespace)  # Check status
2. certmanager_certificaterequests_list_tool(namespace)  # Check request
3. get_events(namespace)  # Check events
4. # Common issues:
   # - Issuer not ready
   # - DNS challenge failed
   # - Rate limited by Let's Encrypt
```

### Issuer Not Ready

```python
1. certmanager_clusterissuer_get_tool(name)  # Check status
2. get_events(namespace="cert-manager")  # Check events
3. # Common issues:
   # - Invalid credentials
   # - Network issues
   # - Invalid configuration
```

## Ingress Integration

```python
# Automatic certificate via ingress annotation
kubectl_apply(manifest="""
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-ingress
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - app.example.com
    secretName: app-tls
  rules:
  - host: app.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: my-service
            port:
              number: 80
""")
```

## Related Skills

- [k8s-networking](../k8s-networking/SKILL.md) - Ingress configuration
- [k8s-security](../k8s-security/SKILL.md) - Security best practices
