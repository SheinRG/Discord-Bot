import { SlashCommandBuilder, EmbedBuilder } from 'discord.js';

export const data = new SlashCommandBuilder()
  .setName('dice').setDescription('roll dice')
  .addIntegerOption(o => o.setName('sides').setDescription('number of sides (default 6)').setMinValue(2).setMaxValue(1000))
  .addIntegerOption(o => o.setName('count').setDescription('how many dice (default 1)').setMinValue(1).setMaxValue(20));

export async function execute(i) {
  const sides = i.options.getInteger('sides') ?? 6;
  const count = i.options.getInteger('count') ?? 1;
  const rolls = Array.from({ length: count }, () => 1 + Math.floor(Math.random() * sides));
  const total = rolls.reduce((a, b) => a + b, 0);
  await i.reply(`🎲 rolled \`${rolls.join(', ')}\` — total **${total}**`);
}
