#!/usr/bin/env node

import { Command } from "commander";
import ora from "ora";
import * as fs from "fs";
import { generateK8sManifests } from "./index";

const program = new Command();

program
  .name("ai-k8s")
  .description("Generate Kubernetes manifests from docker-compose or descriptions")
  .version("1.0.0")
  .argument("<input>", "Docker-compose file path or a plain English description")
  .option("-n, --namespace <ns>", "Kubernetes namespace", "default")
  .option("-o, --output <file>", "Write manifests to a file")
  .action(async (input: string, options: { namespace: string; output?: string }) => {
    const spinner = ora("Generating Kubernetes manifests...").start();

    try {
      const manifests = await generateK8sManifests({
        input,
        namespace: options.namespace,
      });

      spinner.succeed("Done!");
      console.log("\n" + manifests);

      if (options.output) {
        fs.writeFileSync(options.output, manifests, "utf-8");
        console.log(`\nWritten to ${options.output}`);
      }
    } catch (err: any) {
      spinner.fail(err.message);
      process.exit(1);
    }
  });

program.parse();
