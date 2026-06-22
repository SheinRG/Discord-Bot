import { SlashCommandBuilder, PermissionFlagsBits } from 'discord.js';

export const data = new SlashCommandBuilder()
  .setName('clear').setDescription('bulk delete messages (last 14 days only)')
  .setDefaultMemberPermissions(PermissionFlagsBits.ManageMessages)
  .addIntegerOption(o => o.setName('count').setDescription('1-100').setRequired(true).setMinValue(1).setMaxValue(100));

export async function execute(i) {
  const count = i.options.getInteger('count');
  const deleted = await i.channel.bulkDelete(count, true);
  await i.reply({ content: `🧹 deleted ${deleted.size} messages`, ephemeral: true });
}
