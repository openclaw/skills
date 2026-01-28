#!/usr/bin/env node

import { Command } from "commander";
import ora from "ora";
import * as path from "path";
import { createMigrationFiles } from "./index";

const program = new Command();

program
  .name("ai-migrate")
  .description("Generate database migration SQL from your ORM schemas")
  .version("1.0.0")
  .requiredOption("--orm <type>", "ORM type (prisma, drizzle, typeorm, sequelize)")
  .requiredOption("--name <name>", "Migration name (e.g. add_users)")
  .option("-o, --output <dir>", "Output directory", "./migrations")
  .option("-d, --dir <dir>", "Project directory to scan", ".")
  .action(async (options: { orm: string; name: string; output: string; dir: string }) => {
    const spinner = ora(`Scanning ${options.orm} schemas...`).start();
    try {
      const cwd = path.resolve(options.dir);
      const outputDir = path.resolve(options.output);

      const { upPath, downPath } = await createMigrationFiles(
        options.orm as any,
        options.name,
        outputDir,
        cwd
      );

      spinner.succeed("Migration files created!");
      console.log(`  UP:   ${upPath}`);
      console.log(`  DOWN: ${downPath}`);
    } catch (err: any) {
      spinner.fail(`Error: ${err.message}`);
      process.exit(1);
    }
  });

program.parse();
