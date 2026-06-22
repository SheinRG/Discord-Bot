import 'dotenv/config';
import { Client, GatewayIntentBits, Events, version as djsVersion } from 'discord.js';

const tok = process.env.DISCORD_TOKEN;
console.log('discord.js version :', djsVersion);
console.log('Events.ClientReady :', JSON.stringify(Events.ClientReady));
console.log('DISCORD_TOKEN set  :', tok ? `yes (len ${tok.length})` : 'NO / EMPTY');
console.log('CLIENT_ID set      :', process.env.CLIENT_ID ? 'yes' : 'no');
console.log('GUILD_ID set       :', process.env.GUILD_ID ? 'yes' : 'no');

if (!tok) { console.log('=> Cannot log in: token missing. Stop here.'); process.exit(0); }

const client = new Client({ intents: [GatewayIntentBits.Guilds] });
const timer = setTimeout(() => { console.log('=> LOGIN TIMED OUT after 15s (token rejected or no network?)'); process.exit(1); }, 15000);
client.once(Events.ClientReady, c => {
  clearTimeout(timer);
  console.log('=> LOGIN OK. Logged in as', c.user.tag);
  process.exit(0);
});
client.login(tok).catch(err => { clearTimeout(timer); console.log('=> LOGIN FAILED:', err.message); process.exit(1); });
