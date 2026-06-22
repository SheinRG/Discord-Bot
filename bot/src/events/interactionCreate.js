export const name = 'interactionCreate';
export async function execute(interaction, client) {
  if (!interaction.isChatInputCommand()) return;
  const cmd = client.commands.get(interaction.commandName);
  if (!cmd) return;
  try {
    await cmd.execute(interaction, client);
  } catch (err) {
    console.error(err);
    const msg = { content: '💀 something broke. yell at raghav.', ephemeral: true };
    if (interaction.deferred || interaction.replied) await interaction.followUp(msg);
    else await interaction.reply(msg);
  }
}
