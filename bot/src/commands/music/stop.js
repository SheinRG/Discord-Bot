import { SlashCommandBuilder } from 'discord.js';
import { queues } from './play.js';

export const data = new SlashCommandBuilder()
  .setName('stop').setDescription('stop music and leave');

export async function execute(i) {
  const q = queues.get(i.guild.id);
  if (!q) return i.reply({ content: 'nothing playing', ephemeral: true });
  q.queue = [];
  q.player.stop();
  q.connection.destroy();
  queues.delete(i.guild.id);
  await i.reply('🛑 stopped');
}
