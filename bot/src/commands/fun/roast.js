import { SlashCommandBuilder } from 'discord.js';

const roasts = [
  "you write code like git blame is gonna find someone else",
  "your commit messages are 'fix' and somehow that's the most accurate part",
  "bro deploys to prod on friday and wonders why weekends are stressful",
  "tu LeetCode easy ko bhi 'tomorrow' bolta hai",
  "your VS Code has more extensions than your project has users",
  "you Ctrl+S like the file is gonna run away",
];

export const data = new SlashCommandBuilder()
  .setName('roast').setDescription('roast someone (lovingly)')
  .addUserOption(o => o.setName('target').setDescription('victim').setRequired(true));

export async function execute(i) {
  const target = i.options.getUser('target');
  await i.reply(`${target}, ${roasts[Math.floor(Math.random() * roasts.length)]}`);
}
