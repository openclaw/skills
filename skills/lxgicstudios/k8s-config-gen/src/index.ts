import OpenAI from "openai";
import * as yaml from "js-yaml";
import * as fs from "fs";
import * as path from "path";

export interface K8sOptions {
  input: string;
  namespace?: string;
  output?: string;
}

function readInputFile(filePath: string): string {
  const resolved = path.resolve(process.cwd(), filePath);
  if (!fs.existsSync(resolved)) {
    throw new Error(`File not found: ${resolved}`);
  }
  return fs.readFileSync(resolved, "utf-8");
}

function isFilePath(input: string): boolean {
  return (
    input.endsWith(".yml") ||
    input.endsWith(".yaml") ||
    input.includes("docker-compose") ||
    fs.existsSync(path.resolve(process.cwd(), input))
  );
}

export async function generateK8sManifests(options: K8sOptions): Promise<string> {
  let source: string;
  let inputType: string;

  if (isFilePath(options.input)) {
    source = readInputFile(options.input);
    inputType = "docker-compose file";
  } else {
    source = options.input;
    inputType = "description";
  }

  const namespace = options.namespace || "default";

  const openai = new OpenAI();

  const response = await openai.chat.completions.create({
    model: "gpt-4o-mini",
    messages: [
      {
        role: "system",
        content: `You are a Kubernetes expert. Convert the given ${inputType} into production-ready Kubernetes YAML manifests. Include Deployments, Services, ConfigMaps, and Ingress as needed. Use namespace: ${namespace}. Add resource limits, health checks, and proper labels. Output only valid YAML with --- separators between documents. Add comments explaining each resource.`,
      },
      {
        role: "user",
        content: source,
      },
    ],
    temperature: 0.3,
  });

  return response.choices[0]?.message?.content || "# No manifests generated";
}
