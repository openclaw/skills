"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.generateSeedData = generateSeedData;
const openai_1 = __importDefault(require("openai"));
const fs = __importStar(require("fs"));
const path = __importStar(require("path"));
const openai = new openai_1.default();
async function generateSeedData(schemaPath, count = 10) {
    const absPath = path.resolve(schemaPath);
    const schema = fs.readFileSync(absPath, "utf-8");
    const response = await openai.chat.completions.create({
        model: "gpt-4o-mini",
        messages: [
            {
                role: "system",
                content: `You generate realistic database seed data from schema definitions.
Rules:
- Generate ${count} records per model/table
- Use realistic names, emails, dates, addresses (not "test1", "foo", etc.)
- Respect foreign key relationships and constraints
- Include proper data types (dates as ISO strings, UUIDs where needed)
- Generate a complete seed script that can be run directly
- Detect the ORM (Prisma, Drizzle, TypeORM, Knex, raw SQL) from the schema format
- Return ONLY the seed script code, no explanations`
            },
            { role: "user", content: schema }
        ],
        temperature: 0.5,
    });
    const result = response.choices[0].message.content?.trim() || "";
    return result.replace(/^```[\w]*\n?/, "").replace(/\n?```$/, "");
}
