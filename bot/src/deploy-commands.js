import 'dotenv/config';
import { REST, Routes } from 'discord.js';
import { readdirSync } from 'node:fs';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { dirname, join } from 'node:path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const commands = [];
const root = join(__dirname, 'commands');

for (const folder of readdirSync(root)) {
  for (const file of readdirSync(join(root, folder)).filter(f => f.endsWith('.js'))) {
    const mod = await import(pathToFileURL(join(root, folder, file)).href);
    if (mod.data) commands.push(mod.data.toJSON());
  }
}

const rest = new REST().setToken(process.env.DISCORD_TOKEN);
const data = await rest.put(
  Routes.applicationGuildCommands(process.env.CLIENT_ID, process.env.GUILD_ID),
  { body: commands },
);
console.log(`✅ Registered ${data.length} commands to guild ${process.env.GUILD_ID}`);
