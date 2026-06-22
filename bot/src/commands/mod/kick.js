import { SlashCommandBuilder, PermissionFlagsBits } from 'discord.js';

export const data = new SlashCommandBuilder()
  .setName('kick').setDescription('kick a member')
  .setDefaultMemberPermissions(PermissionFlagsBits.KickMembers)
  .addUserOption(o => o.setName('target').setDescription('user').setRequired(true))
  .addStringOption(o => o.setName('reason').setDescription('reason'));

export async function execute(i) {
  const target = i.options.getMember('target');
  const reason = i.options.getString('reason') ?? 'no reason given';
  if (!target) return i.reply({ content: 'user not in server', ephemeral: true });
  if (!target.kickable) return i.reply({ content: "can't kick that user", ephemeral: true });
  await target.kick(reason);
  await i.reply(`👢 kicked **${target.user.tag}** — ${reason}`);
}
