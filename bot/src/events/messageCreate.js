// Edit triggers freely — key = regex (case-insensitive), value = array of possible replies
const triggers = [
  { match: /\bbruh\b/i, replies: ['bruh moment certified ✅', 'bruh ➡️ ☠️'] },
  { match: /\bskill issue\b/i, replies: ['confirmed skill issue', 'L + ratio + skill issue'] },
  { match: /\bdeploy\b/i, replies: ['it works on my machine 🤷', 'ship it, fix it in prod'] },
  // add your friend-specific ones here, e.g.:
  // { match: /\b@?aman\b/i, replies: ['aman sote hue bhi code likhta hai'] },
];

export const name = 'messageCreate';
export async function execute(message) {
  if (message.author.bot) return;
  for (const t of triggers) {
    if (t.match.test(message.content)) {
      const reply = t.replies[Math.floor(Math.random() * t.replies.length)];
      await message.reply({ content: reply, allowedMentions: { repliedUser: false } });
      return;
    }
  }
}
