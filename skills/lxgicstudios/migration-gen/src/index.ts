import OpenAI from "openai";
import * as fs from "fs";
import * as path from "path";
import { glob } from "glob";

const openai = new OpenAI();

type OrmType = "prisma" | "drizzle" | "typeorm" | "sequelize";

const SCHEMA_PATTERNS: Record<OrmType, string[]> = {
  prisma: ["**/prisma/schema.prisma"],
  drizzle: ["**/drizzle/**/*.ts", "**/src/db/schema*.ts"],
  typeorm: ["**/entities/**/*.ts", "**/entity/**/*.ts"],
  sequelize: ["**/models/**/*.ts", "**/models/**/*.js"],
};

export async function findSchemaFiles(orm: OrmType, cwd: string): Promise<string[]> {
  const patterns = SCHEMA_PATTERNS[orm];
  if (!patterns) throw new Error(`Unsupported ORM: ${orm}`);

  const files: string[] = [];
  for (const pattern of patterns) {
    const matches = await glob(pattern, { cwd, ignore: ["**/node_modules/**"], absolute: true });
    files.push(...matches);
  }
  return files;
}

export async function generateMigration(
  schemaContent: string,
  orm: OrmType,
  migrationName: string
): Promise<{ up: string; down: string }> {
  const response = await openai.chat.completions.create({
    model: "gpt-4o-mini",
    messages: [
      {
        role: "system",
        content: `You generate SQL migration files from ORM schema definitions. Rules:
- Generate both UP and DOWN migrations
- Use standard SQL (PostgreSQL dialect)
- Include CREATE TABLE, ALTER TABLE, CREATE INDEX as needed
- Add IF NOT EXISTS / IF EXISTS guards
- Separate UP and DOWN with exactly this marker: --- DOWN ---
- Return ONLY SQL, no explanations or markdown fences`
      },
      {
        role: "user",
        content: `ORM: ${orm}\nMigration name: ${migrationName}\n\nSchema:\n${schemaContent}`
      }
    ],
    temperature: 0.2,
  });

  const content = response.choices[0].message.content?.trim() || "";
  const parts = content.split("--- DOWN ---");
  return {
    up: parts[0]?.trim() || "",
    down: parts[1]?.trim() || "-- No down migration generated",
  };
}

export async function createMigrationFiles(
  orm: OrmType,
  name: string,
  outputDir: string,
  cwd: string
): Promise<{ upPath: string; downPath: string }> {
  const schemaFiles = await findSchemaFiles(orm, cwd);
  if (schemaFiles.length === 0) {
    throw new Error(`No schema files found for ${orm}. Check your project structure.`);
  }

  const schemaContent = schemaFiles
    .map((f) => `-- File: ${path.basename(f)}\n${fs.readFileSync(f, "utf-8")}`)
    .join("\n\n");

  const { up, down } = await generateMigration(schemaContent, orm, name);

  const timestamp = new Date().toISOString().replace(/[-:T]/g, "").slice(0, 14);
  const dir = path.join(outputDir, `${timestamp}_${name}`);
  fs.mkdirSync(dir, { recursive: true });

  const upPath = path.join(dir, "up.sql");
  const downPath = path.join(dir, "down.sql");
  fs.writeFileSync(upPath, up);
  fs.writeFileSync(downPath, down);

  return { upPath, downPath };
}
