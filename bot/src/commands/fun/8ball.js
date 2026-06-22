import { SlashCommandBuilder } from 'discord.js';

const answers = [
  'yes 💯', 'absolutely not', 'maybe lol', 'ask again when sober',
  'signs point to yes', 'big no from me', 'bhai sochke bata raha hu... haan',
  'nope, cope', '100% certified yes', 'mat kar yaar',
];

export const data = new SlashCommandBuilder()
  .setName('8ball').setDescription('ask the magic 8-ball')
  .addStringOption(o => o.setName('question').setDescription('your question').setRequired(true));

export async function execute(i) {
  const q = i.options.getString('question');
  await i.reply(`🎱 **Q:** ${q}\n**A:** ${answers[Math.floor(Math.random() * answers.length)]}`);
}
