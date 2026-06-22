import { SlashCommandBuilder, EmbedBuilder } from 'discord.js';

export const data = new SlashCommandBuilder()
  .setName('meme').setDescription('fetch a random meme from r/memes');

export async function execute(i) {
  await i.deferReply();
  try {
    const res = await fetch('https://meme-api.com/gimme');
    const m = await res.json();
    const embed = new EmbedBuilder()
      .setTitle(m.title).setURL(m.postLink).setImage(m.url)
      .setFooter({ text: `👍 ${m.ups} • r/${m.subreddit}` });
    await i.editReply({ embeds: [embed] });
  } catch (e) {
    await i.editReply('meme api ded rn, try again');
  }
}
