import { SlashCommandBuilder } from 'discord.js';
import { queues } from './play.js';

export const data = new SlashCommandBuilder()
  .setName('skip').setDescription('skip current song');

export async function execute(i) {
  const q = queues.get(i.guild.id);
  if (!q) return i.reply({ content: 'nothing playing', ephemeral: true });
  q.player.stop(); // triggers Idle → next track
  await i.reply('⏭️ skipped');
}
