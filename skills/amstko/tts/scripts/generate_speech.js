import fs from 'fs';
import path from 'path';
import OpenAI from 'openai';
import { program } from 'commander';

program
  .requiredOption('-t, --text <text>', 'Text to convert to speech')
  .requiredOption('-o, --output <path>', 'Output file path (e.g., output.mp3)')
  .option('-v, --voice <voice>', 'Voice to use (alloy, echo, fable, onyx, nova, shimmer)', 'nova')
  .option('-m, --model <model>', 'Model to use (tts-1, tts-1-hd)', 'tts-1')
  .parse(process.argv);

const options = program.opts();

async function main() {
  const apiKey = process.env.OPENAI_API_KEY;
  if (!apiKey) {
    console.error('Error: OPENAI_API_KEY environment variable is not set.');
    process.exit(1);
  }

  const openai = new OpenAI({ apiKey });

  try {
    console.log(`Generating speech for: "${options.text.substring(0, 50)}..."`);
    const mp3 = await openai.audio.speech.create({
      model: options.model,
      voice: options.voice,
      input: options.text,
    });

    const buffer = Buffer.from(await mp3.arrayBuffer());
    await fs.promises.writeFile(options.output, buffer);
    
    const absolutePath = path.resolve(options.output);
    console.log(`Audio saved: ${absolutePath}`);
    console.log(`MEDIA: ${absolutePath}`);
  } catch (error) {
    console.error('Error generating speech:', error);
    process.exit(1);
  }
}

main();
