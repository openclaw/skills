import fs from 'fs';
import path from 'path';
import { program } from 'commander';

program
  .requiredOption('-t, --text <text>', 'Text to convert to speech')
  .requiredOption('-o, --output <path>', 'Output file path (e.g., output.mp3)')
  .option('-v, --voice <voice>', 'Voice ID to use', '9e1f9e4f-691a-4bb0-b87c-e306a4c838ef')
  .parse(process.argv);

const options = program.opts();

async function main() {
  const apiKey = process.env.HUME_API_KEY;

  if (!apiKey) {
    console.error('Error: HUME_API_KEY environment variable must be set.');
    process.exit(1);
  }

  try {
    console.log(`Generating speech via Hume AI for: "${options.text.substring(0, 50)}..."`);
    
    const response = await fetch('https://api.hume.ai/v0/tts', {
      method: 'POST',
      headers: {
        'X-Hume-Api-Key': apiKey,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        utterances: [
          {
            text: options.text,
            voice: {
              id: options.voice
            }
          }
        ]
      })
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Hume API error (${response.status}): ${errorText}`);
    }

    const json = await response.json();
    if (!json.generations || json.generations.length === 0) {
      throw new Error('Hume API returned no audio generations.');
    }

    const base64Audio = json.generations[0].audio;
    const buffer = Buffer.from(base64Audio, 'base64');
    await fs.promises.writeFile(options.output, buffer);
    
    const absolutePath = path.resolve(options.output);
    console.log(`Audio saved: ${absolutePath}`);
    console.log(`MEDIA: ${absolutePath}`);
  } catch (error) {
    console.error('Error generating speech with Hume:', error);
    process.exit(1);
  }
}

main();
