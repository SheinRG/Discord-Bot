export const name = 'guildMemberAdd';
export async function execute(member) {
  const channelId = process.env.WELCOME_CHANNEL_ID;
  if (!channelId) return;
  const ch = member.guild.channels.cache.get(channelId);
  if (!ch) return;
  const lines = [
    `yo <@${member.id}> just pulled up 🫡`,
    `<@${member.id}> entered the chat. behave.`,
    `welcome <@${member.id}> — read #rules or don't, idc`,
    `oye <@${member.id}> aagaya bhai, swagat hai 🎉`,
  ];
  await ch.send(lines[Math.floor(Math.random() * lines.length)]);
}
