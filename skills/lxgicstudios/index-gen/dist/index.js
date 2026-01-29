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
exports.suggestIndexes = suggestIndexes;
const openai_1 = __importDefault(require("openai"));
const fs = __importStar(require("fs"));
const path = __importStar(require("path"));
const openai = new openai_1.default();
async function suggestIndexes(dirPath) {
    const absDir = path.resolve(dirPath);
    const stat = fs.statSync(absDir);
    let queryCode = "";
    if (stat.isDirectory()) {
        const files = fs.readdirSync(absDir).filter(f => /\.(ts|js|sql)$/.test(f));
        for (const file of files) {
            const content = fs.readFileSync(path.join(absDir, file), "utf-8");
            queryCode += `\n// === ${file} ===\n${content}\n`;
        }
    }
    else {
        queryCode = fs.readFileSync(absDir, "utf-8");
    }
    const response = await openai.chat.completions.create({
        model: "gpt-4o-mini",
        messages: [
            {
                role: "system",
                content: `You are a database performance expert. Analyze query patterns and suggest optimal indexes.
For each suggestion include:
- The CREATE INDEX statement
- Which queries it optimizes
- Expected performance impact
- Whether it's a single-column, composite, or partial index
- Any trade-offs (write overhead, storage)
Be specific and practical. Return a well-formatted analysis.`
            },
            { role: "user", content: queryCode }
        ],
        temperature: 0.3,
    });
    return response.choices[0].message.content?.trim() || "";
}
