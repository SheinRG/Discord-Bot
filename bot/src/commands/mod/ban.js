import { SlashCommandBuilder, PermissionFlagsBits } from 'discord.js';

export const data = new SlashCommandBuilder()
  .setName('ban').setDescription('ban a member')
  .setDefaultMemberPermissions(PermissionFlagsBits.BanMembers)
  .addUserOption(o => o.setName('target').setDescription('user').setRequired(true))
  .addStringOption(o => o.setName('reason').setDescription('reason'));

export async function execute(i) {
  const target = i.options.getMember('target');
  const reason = i.options.getString('reason') ?? 'no reason given';
  if (!target) return i.reply({ content: 'user not in server', ephemeral: true });
  if (!target.bannable) return i.reply({ content: "can't ban that user", ephemeral: true });
  await target.ban({ reason });
  await i.reply(`🔨 banned **${target.user.tag}** — ${reason}`);
}
