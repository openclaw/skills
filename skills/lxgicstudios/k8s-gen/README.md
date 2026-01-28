# ai-k8s

Got a docker-compose file and need to move to Kubernetes? Don't spend hours translating YAML by hand. Just feed it in and get proper K8s manifests back.

## Install

```bash
npm install -g ai-k8s
```

## Usage

```bash
# From a docker-compose file
npx ai-k8s docker-compose.yml --namespace production

# From a description
npx ai-k8s "3 replicas of a node app with redis and postgres"

# Save output
npx ai-k8s docker-compose.yml -o k8s-manifests.yml
```

## Setup

```bash
export OPENAI_API_KEY=your-key-here
```

## Options

- `-n, --namespace <ns>` - Target namespace (defaults to "default")
- `-o, --output <file>` - Write to a file

## License

MIT
