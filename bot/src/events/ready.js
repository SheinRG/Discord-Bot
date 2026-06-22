export const name = 'clientReady';
export const once = true;
export function execute(client) {
  console.log(`🤖 Logged in as ${client.user.tag}`);
  client.user.setActivity('with the homies', { type: 0 });
}
