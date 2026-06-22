import { Events } from 'discord.js';

export const name = Events.ClientReady; // 'ready' in discord.js v14
export const once = true;
export function execute(client) {
  console.log(`🤖 Logged in as ${client.user.tag}`);
  client.user.setActivity('with the homies', { type: 0 });
}
