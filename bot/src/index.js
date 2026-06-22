import 'dotenv/config';
import { Client, Collection, GatewayIntentBits, Partials } from 'discord.js';
import { readdirSync } from 'node:fs';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { dirname, join } from 'node:path';

// Safety net: a single bad song / stream error must never kill the whole bot.
process.on('unhandledRejection', err => console.error('unhandledRejection:', err));
process.on('uncaughtException', err => console.error('uncaughtException:', err));

const __dirname = dirname(fileURLToPath(import.meta.url));

const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.MessageContent,
    GatewayIntentBits.GuildMembers,
    GatewayIntentBits.GuildVoiceStates,
  ],
  partials: [Partials.Channel, Partials.Message],
});

client.commands = new Collection();

// load all commands from src/commands/**/*.js
const commandsRoot = join(__dirname, 'commands');
for (const folder of readdirSync(commandsRoot)) {
  for (const file of readdirSync(join(commandsRoot, folder)).filter(f => f.endsWith('.js'))) {
    const mod = await import(pathToFileURL(join(commandsRoot, folder, file)).href);
    if (mod.data && mod.execute) client.commands.set(mod.data.name, mod);
  }
}

// load events
const eventsRoot = join(__dirname, 'events');
for (const file of readdirSync(eventsRoot).filter(f => f.endsWith('.js'))) {
  const mod = await import(pathToFileURL(join(eventsRoot, file)).href);
  if (mod.once) client.once(mod.name, (...a) => mod.execute(...a, client));
  else client.on(mod.name, (...a) => mod.execute(...a, client));
}

client.login(process.env.DISCORD_TOKEN);
