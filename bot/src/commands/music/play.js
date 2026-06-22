import { SlashCommandBuilder } from 'discord.js';
import {
  joinVoiceChannel, createAudioPlayer, createAudioResource,
  AudioPlayerStatus, VoiceConnectionStatus, entersState,
} from '@discordjs/voice';
import play from 'play-dl';
import ytdl from '@distube/ytdl-core';

// Per-guild queue: { connection, player, queue: [{title,url,requester}] }
const queues = new Map();

async function playNext(guildId) {
  const q = queues.get(guildId);
  if (!q || q.queue.length === 0) {
    q?.connection.destroy();
    queues.delete(guildId);
    return;
  }
  const track = q.queue[0];
  try {
    // play-dl's stream extraction breaks whenever YouTube rotates its player,
    // returning undefined format URLs. @distube/ytdl-core is actively maintained
    // and handles the signature/format extraction reliably.
    const stream = ytdl(track.url, {
      filter: 'audioonly',
      quality: 'highestaudio',
      highWaterMark: 1 << 25,
    });
    // Without this listener, a stream 'error' (e.g. on /stop or YouTube cutting
    // us off) is an unhandled emitter error and crashes the whole process.
    stream.on('error', err => console.error('stream error:', err));
    const resource = createAudioResource(stream);
    q.player.play(resource);
  } catch (err) {
    console.error('failed to stream', track.url, err);
    q.textChannel?.send(`⚠️ couldn't play **${track.title}**, skipping`).catch(() => {});
    q.queue.shift();
    playNext(guildId).catch(e => console.error('playNext:', e));
  }
}

export const data = new SlashCommandBuilder()
  .setName('play').setDescription('play a song from YouTube')
  .addStringOption(o => o.setName('query').setDescription('YouTube URL or search').setRequired(true));

export async function execute(i) {
  await i.deferReply();
  const vc = i.member.voice.channel;
  if (!vc) return i.editReply('join a voice channel first');

  const query = i.options.getString('query');
  let info;
  if (play.yt_validate(query) === 'video') {
    info = (await play.video_info(query)).video_details;
  } else {
    const results = await play.search(query, { limit: 1 });
    if (!results.length) return i.editReply('nothing found');
    info = results[0];
  }
  const track = { title: info.title, url: info.url, requester: i.user.tag };

  let q = queues.get(i.guild.id);
  if (!q) {
    const connection = joinVoiceChannel({
      channelId: vc.id,
      guildId: i.guild.id,
      adapterCreator: i.guild.voiceAdapterCreator,
    });
    const player = createAudioPlayer();
    connection.subscribe(player);
    q = { connection, player, queue: [], textChannel: i.channel };
    queues.set(i.guild.id, q);

    player.on(AudioPlayerStatus.Idle, () => {
      q.queue.shift();
      playNext(i.guild.id).catch(err => console.error('playNext:', err));
    });
    player.on('error', err => console.error('player error', err));
    await entersState(connection, VoiceConnectionStatus.Ready, 30_000).catch(() => {});
  }

  q.queue.push(track);
  if (q.queue.length === 1) playNext(i.guild.id).catch(err => console.error('playNext:', err));

  await i.editReply(q.queue.length === 1
    ? `🎶 now playing **${track.title}**`
    : `➕ queued **${track.title}** (position ${q.queue.length - 1})`);
}

export { queues };
