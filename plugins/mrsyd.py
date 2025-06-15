import math, time, random, os, tempfile, asyncio, re
from datetime import timedelta

from pyrogram import Client, enums, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from helper.database import db
from info import AUTH_CHANNEL
import ffmpeg
import shlex
# ── helper UI builders ─────────────────────────────────────────────────────────
from pyrogram.errors import UserNotParticipant
SYD_CHANNELS = ["Bot_Cracker", "Mod_Moviez_X", "MrSyD_Tg"]
SYD_BACKUP_LINK = "https://t.me/+0Zi1FC4ulo8zYzVl"        # your backup group

async def is_req_subscribed(bot, query):
    if await db.find_join_req(query.from_user.id):
        return True
    try:
        user = await bot.get_chat_member(AUTH_CHANNEL, query.from_user.id)
    except UserNotParticipant:
        pass
    except Exception as e:
        logger.exception(e)
    else:
        if user.status != enums.ChatMemberStatus.BANNED:
            return True

    return False
async def ensure_member(client, msg):
    """
    Returns True if the user is a member of every channel in SYD_CHANNELS.
    Otherwise sends a join-prompt and returns False.
    Works with both Message and CallbackQuery objects.
    """
    user_id   = msg.from_user.id
    chat_id   = msg.message.chat.id
    replyable = msg.message

    # Figure out the correct message to reply to
    reply_to_msg = replyable.reply_to_message or replyable

    not_joined = []
    for ch in SYD_CHANNELS:
        try:
            member = await client.get_chat_member(ch, user_id)
            if member.status in {"kicked", "left"}:
                not_joined.append(ch)
        except UserNotParticipant:
            not_joined.append(ch)
        except Exception:
            pass

    if not not_joined:
        return True

    join_rows = [[
        InlineKeyboardButton(
            text=f"✧ Jᴏɪɴ {str(ch).replace('_',' ').title()} ✧",
            url=f"https://t.me/{str(ch).lstrip('@')}"
        )
    ] for ch in not_joined]

    join_rows.append([InlineKeyboardButton("✧ Jᴏɪɴ Bᴀᴄᴋ Uᴩ ✧", url=SYD_BACKUP_LINK)])
    join_rows.append([InlineKeyboardButton("☑ ᴊᴏɪɴᴇᴅ ☑", callback_data="check_subscription")])

    text = (
        "**ꜱᴏʀʀʏ, ᴅᴜᴇ ᴛᴏ ᴏᴠᴇʀʟᴏᴀᴅ ᴜꜱᴇʀꜱ ᴊᴏɪɴᴇᴅ ɪɴ ᴏᴜʀ ᴄʜᴀɴɴᴇʟꜱ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ꜰᴇᴀᴛᴜʀᴇ.**\n"
        "ᴩʟᴇᴀꜱᴇ ᴊᴏɪɴ ᴀɴᴅ ᴘʀᴇꜱꜱ **ᴊᴏɪɴᴇᴅ** ᴛᴏ ᴄᴏɴᴛɪɴᴜᴇ.."
    )

    await reply_to_msg.reply_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(join_rows),
        quote=True,
        disable_web_page_preview=True
    )
    return False


async def handle_process_flags(client, query):
    user_id = query.from_user.id

    # ── read current flags (None → False) ────────────────────────────────────
    oneprocess = await db.get_user_value(user_id, "oneprocess") or False
    twoprocess = await db.get_user_value(user_id, "twoprocess") or False

    if oneprocess and twoprocess:
        await query.message.reply_text(
            "⚠️ Yᴏᴜ'ʀᴇ ᴀʟʀᴇᴀᴅʏ ɪɴ **ᴛᴡᴏ ᴀᴄᴛɪᴠᴇ ꜱᴇꜱꜱɪᴏɴꜱ**.\n"
            "Pʟᴇᴀꜱᴇ ᴡᴀɪᴛ ᴜɴᴛɪʟʟ ᴛʜᴇʏ ꜰɪɴɪꜱʜ ᴏʀ ɢᴇᴛ ᴩʀᴇᴍɪᴜᴍ.",
            quote=True
        )
        return False

    # first job is active → allow second only if member
    if oneprocess:
        if await ensure_member(client, query):
            if not twoprocess:
                await db.set_user_value(user_id, "twoprocess", True)
            return True
        return False  # ensure_member already sent join prompt

    # no job yet → start first one
    await db.set_user_value(user_id, "oneprocess", True)
    return True



def build_even_keyboard() -> InlineKeyboardMarkup:
    rows, row = [], []
    for sec in range(2, 22, 2):
        row.append(InlineKeyboardButton(str(sec), callback_data=f"getshot#{sec}"))
        if len(row) == 5:
            rows.append(row); row = []
    if row:
        rows.append(row)
    return InlineKeyboardMarkup(rows)

def generate_progress_bar(percentage: float) -> str:
    filled = "⬢" * math.floor(percentage / 5)
    empty  = "⬡" * (20 - math.floor(percentage / 5))
    return filled + empty
    
def parse_hms(text: str) -> int | None:
    """
    Convert h:m:s or m:s (hours optional) to seconds (int).
    Returns None if the format is invalid.
    """
    parts = text.strip().split(":")
    if not 2 <= len(parts) <= 3:
        return None
    try:
        parts = [int(p) for p in parts]
    except ValueError:
        return None
    if len(parts) == 2:  # m:s
        m, s = parts
        h = 0
    else:                # h:m:s
        h, m, s = parts
    if m > 59 or s > 59 or h < 0 or m < 0 or s < 0:
        return None
    return h * 3600 + m * 60 + s
def humanbytes(size: int) -> str:
    power, unit = 1024, 0
    units = ["B", "KiB", "MiB", "GiB", "TiB"]
    while size >= power and unit < len(units) - 1:
        size /= power; unit += 1
    return f"{size:.2f} {units[unit]}"

def calculate_times(diff, current, total, speed):
    if speed == 0:
        return diff, 0, ""
    time_to_completion = (total - current) / speed
    return diff, time_to_completion, time_to_completion + diff

async def progress_for_pyrogram(current, total, ud_type, message, start):
    now, diff = time.time(), time.time() - start
    if int(diff) % 5 == 0 or current == total:
        percentage = current * 100 / total
        speed      = current / diff if diff else 0
        _, eta, _  = calculate_times(diff, current, total, speed)

        bar = generate_progress_bar(percentage)
        text = (
            f"{ud_type}\n\n"
            f"{bar} `{percentage:.2f}%`\n"
            f"**{humanbytes(current)} / {humanbytes(total)}** "
            f"at **{humanbytes(speed)}/s**\n"
            f"ETA: `{round(eta)} s`"
        )
        try:
            await message.edit(text=text)
        except Exception as e:
            print("Progress update failed:", e)

# ── FFmpeg helpers ─────────────────────────────────────────────────────────────

async def ffmpeg_trim_async(src: str, start_sec: int, end_sec: int,
                            dst: str, reencode: bool = False):
    if not reencode:
        cmd = [
            "ffmpeg", "-ss", str(start_sec), "-to", str(end_sec),
            "-i", src, "-c", "copy", "-metadata", f"title=Trim By: @Videos_Sample_Bot 🧊", "-y", dst
        ]
    else:
        cmd = [
            "ffmpeg", "-ss", str(start_sec), "-to", str(end_sec),
            "-i", src, "-c:v", "libx264", "-c:a", "aac",
            "-preset", "medium", "-metadata", f"title=Trim By: @Videos_Sample_Bot 🧊", "-y", dst
        ]
    
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.DEVNULL
    )
    await proc.communicate()
    return proc.returncode

                                
async def ffmpeg_sample_async(src: str, start: int, length: int, dst: str):
    cmd = [
        "ffmpeg", "-ss", str(start), "-i", src, "-t", str(length),
        "-metadata", "title= Sample By: @Videos_Sample_Bot 🧊",
        "-c:v", "libx264", "-c:a", "aac",
        "-preset", "ultrafast", "-y", dst
    ]
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.DEVNULL
    )
    await process.communicate()

async def ffmpeg_screenshot_async(src: str, sec: int, dst: str):
    cmd = [
        "ffmpeg", "-ss", str(sec), "-i", src,
        "-vframes", "1", "-q:v", "2", "-y", dst
    ]
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.DEVNULL
    )
    await proc.communicate()

# ── main callback handler ──────────────────────────────────────────────────────
@Client.on_callback_query()
async def callback_handler(client: Client, query):
    if AUTH_CHANNEL and not await is_req_subscribed(client, query):
        btn = [[InlineKeyboardButton("⊛ Jᴏɪɴ Uᴘᴅᴀᴛᴇꜱ CʜᴀɴɴᴇL ⊛", url=invite_link.invite_link)],
               [InlineKeyboardButton("↻ Tʀʏ Aɢᴀɪɴ ↻", callback_data="checksub")]]

        await query.message.reply(
            text="Jᴏɪɴ Iɴ Oᴜʀ Uᴘᴅᴀᴛᴇꜱ Cʜᴀɴɴᴇʟ Aɴᴅ Tʜᴇɴ Cʟɪᴄᴋ Oɴ Tʀʏ Aɢᴀɪɴ Tᴏ Cᴏɴᴛɪɴᴜᴇ.",
            reply_markup=InlineKeyboardMarkup(btn),
            parse_mode=enums.ParseMode.MARKDOWN
        )
        return
    orig = query.message.reply_to_message
    if not orig or not (orig.video or orig.document):
        return await query.answer("Nᴏ Fɪʟᴇꜱ Fᴏᴜɴᴅ. Rᴇᴩᴏʀᴛ Aᴅᴍɪɴ Iꜰ Iᴛ'ꜱ Aɴ Eʀʀᴏʀ", show_alert=True)

    media = orig.video or orig.document
    duration = getattr(media, "duration", 120) or 120

    # ─ 1. 30-second sample
    if query.data == "sample":
        await query.answer("Gᴇɴᴇʀᴀᴛɪɴɢ ꜱᴀᴍᴩʟᴇ ᴠɪᴅᴇᴏ 🎐.....", show_alert=False)
        proceed = await handle_process_flags(client, query)
        if not proceed:
            return
            

        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
            full_path = tmp.name
        sample_path = full_path.replace(".mp4", "_@GetTGlinks_sample.mp4")

        try:
            progress_msg = await query.message.reply("Sᴛᴀʀᴛɪɴɢ ᴅᴏᴡɴʟᴏᴀᴅ...", quote=True)
            await client.download_media(
                message=media,
                file_name=full_path,
                progress=progress_for_pyrogram,
                progress_args=("__Dᴏᴡɴʟᴏᴀᴅɪɴɢ…__", progress_msg, time.time())
            )
            await progress_msg.edit("Gᴇɴᴇʀᴀᴛɪɴɢ...")
            start = random.randint(0, max(0, duration - 30))
            await ffmpeg_sample_async(full_path, start, 30, sample_path)
            await orig.reply_video(
                video=sample_path,
                caption=f"Sᴀᴍᴩʟᴇ 30ꜱ (Fʀᴏᴍ {start}s)",
                quote=True,
                progress=progress_for_pyrogram,                    # <<< NEW
                progress_args=("__Uᴩʟᴏᴀᴅɪɴɢ Sᴀᴍᴩʟᴇ__", progress_msg, time.time())  # <<< NEW
            )
            await progress_msg.delete()

        except Exception as e:
            await query.message.reply(
                f"❌ FFmpeg error:\n<code>{e.stderr.decode()}</code>",
                parse_mode=enums.ParseMode.HTML,
                quote=True
            )
        finally:
            for f in (full_path, sample_path):
                if os.path.exists(f):
                    os.remove(f)

        syd = await query.message.reply("Yᴏᴜ ʜᴀᴠᴇ ᴛᴏ ᴡᴀɪᴛ 5 ᴍɪɴᴜᴛᴇꜱ ꜰᴏʀ ɴᴇxᴛ ᴩʀᴏᴄᴇꜱꜱ ᴏʀ ɢᴏ ᴩᴀʀᴀʟʟᴇʟ..!")
        await asyncio.sleep(300)
        await syd.delete()
        await query.message.reply("Sᴇɴᴅ ꜰɪʟᴇ ꜰᴏʀ ɴᴇxᴛ ᴩʀᴏᴄᴇꜱꜱ...! 🧊")
        twoprocess = await db.get_user_value(query.from_user.id, "twoprocess") or False
        if twoprocess:
            await db.set_user_value(query.from_user.id, "twoprocess", False)
        else:
            await db.set_user_value(query.from_user.id, "oneprocess", False)


    # ─ 2. Ask for screenshot count
    elif query.data == "screenshot":
        await query.answer()
        await orig.reply(
            "Cʜᴏᴏꜱᴇ ɴᴜᴍʙᴇʀ ᴏꜰ ꜱᴄʀᴇᴇɴꜱʜᴏᴛꜱ ᴛᴏ ɢᴇɴᴇʀᴀᴛᴇ:",
            reply_markup=build_even_keyboard(),
            quote=True
        )

    # ─ 3. Take screenshots
    elif query.data.startswith("getshot#"):
        proceed = await handle_process_flags(client, query)
        if not proceed:
            return
        count = int(query.data.split("#")[1])
        await query.answer(f"Tᴀᴋɪɴɢ {count} ʀᴀɴᴅᴏᴍ ꜱᴄʀᴇᴇɴꜱʜᴏᴛꜱ…", show_alert=False)

        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
            full_path = tmp.name

        try:
            progress_msg = await query.message.reply("Sᴛᴀʀᴛɪɴɢ ᴅᴏᴡɴʟᴏᴀᴅ...!", quote=True)
            await client.download_media(
                message=media,
                file_name=full_path,
                progress=progress_for_pyrogram,
                progress_args=("__Dᴏᴡɴʟᴏᴀᴅɪɴɢ…__", progress_msg, time.time())
            )

            timestamps = sorted(random.sample(range(2, max(duration - 1, 3)), count))
            media_group = []
            paths = []

            for idx, ts in enumerate(timestamps, start=1):
                shot_path = full_path.replace(".mp4", f"_@GetTGlinks_{idx}.jpg")
                await ffmpeg_screenshot_async(full_path, ts, shot_path)
                paths.append(shot_path)
                media_group.append(InputMediaPhoto(
                    media=shot_path,
                    caption=f"Sᴄʀᴇᴇɴꜱʜᴏᴛꜱ {count}" if idx == 1 else None
                ))

            await client.send_media_group(
                chat_id=query.message.chat.id,
                media=media_group,
                reply_to_message_id=orig.id
            )
            await progress_msg.delete()
        except Exception as e:
            await query.message.reply(
                f"❌ FFmpeg error:\n<code>{e.stderr.decode()}</code> \n\nSend This Message To @SyD_Xyz For Help",
                parse_mode=enums.ParseMode.HTML,
                quote=True
            )
        finally:
            if os.path.exists(full_path):
                os.remove(full_path)
            for p in paths:
                if os.path.exists(p):
                    os.remove(p)
        syd = await query.message.reply("Yᴏᴜ ʜᴀᴠᴇ ᴛᴏ ᴡᴀɪᴛ 5 ᴍɪɴᴜᴛᴇꜱ ꜰᴏʀ ɴᴇxᴛ ᴩʀᴏᴄᴇꜱꜱ ᴏʀ ɢᴏ ᴩᴀʀᴀʟʟᴇʟ..!")
        await asyncio.sleep(300)
        await syd.delete()
        await query.message.reply("Sᴇɴᴅ ꜰɪʟᴇ ꜰᴏʀ ɴᴇxᴛ ᴩʀᴏᴄᴇꜱꜱ...! 🧊")
        twoprocess = await db.get_user_value(query.from_user.id, "twoprocess") or False
        if twoprocess:
            await db.set_user_value(query.from_user.id, "twoprocess", False)
        else:
            await db.set_user_value(query.from_user.id, "oneprocess", False)


    elif query.data == "extract_audio":
        await query.answer("Exᴛʀᴀᴄᴛɪɴɢ ᴀᴜᴅɪᴏ....🎧", show_alert=False)

        proceed = await handle_process_flags(client, query)
        if not proceed:
            return
        orig = query.message.reply_to_message
        if not orig or not (orig.video or orig.document):
            return await query.message.reply(
                "❌ Please reply to a video or audio-supported file.",
                quote=True
            )

        media = orig.video or orig.document

        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
            full_path = tmp.name
        audio_path = full_path.replace(".mp4", "_@GetTGlinks.m4a")

        try:
            await client.download_media(
                message=media,
                file_name=full_path,
                progress=progress_for_pyrogram,
                progress_args=("__Dᴏᴡɴʟᴏᴀᴅɪɴɢ…__", query.message, time.time())
            )
            await query.message.edit("Gᴇɴᴇʀᴀᴛɪɴɢ ᴀɴᴅ ᴜᴩʟᴏᴀᴅɪɴɢ ᴀᴜᴅɪᴏ")

            cmd = [
                "ffmpeg", "-i", full_path, "-vn",
                "-c:a", "aac", "-b:a", "192k", "-y", audio_path
            ]
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.PIPE
            )
            _, err = await proc.communicate()
            if proc.returncode != 0:
                raise RuntimeError(err.decode() or "ffmpeg failed")

            await orig.reply_audio(
                audio=audio_path,
                caption="Exᴛʀᴀᴄᴛᴇᴅ Aᴜᴅɪᴏ 🎙️",
                quote=True
            )
        except Exception as e:
            await query.message.reply(
                f"❌ FFmpeg error:\n<code>{e}</code>",
                parse_mode=enums.ParseMode.HTML,
                quote=True
            )
        finally:
            for f in (full_path, audio_path):
                if os.path.exists(f):
                    os.remove(f)
        syd = await query.message.reply("Yᴏᴜ ʜᴀᴠᴇ ᴛᴏ ᴡᴀɪᴛ 5 ᴍɪɴᴜᴛᴇꜱ ꜰᴏʀ ɴᴇxᴛ ᴩʀᴏᴄᴇꜱꜱ ᴏʀ ɢᴏ ᴩᴀʀᴀʟʟᴇʟ..!")
        await asyncio.sleep(300)
        await syd.delete()
        await query.message.reply("Sᴇɴᴅ ꜰɪʟᴇ ꜰᴏʀ ɴᴇxᴛ ᴩʀᴏᴄᴇꜱꜱ...! 🧊")
        twoprocess = await db.get_user_value(query.from_user.id, "twoprocess") or False
        if twoprocess:
            await db.set_user_value(query.from_user.id, "twoprocess", False)
        else:
            await db.set_user_value(query.from_user.id, "oneprocess", False)



    elif query.data == "trim":
        proceed = await handle_process_flags(client, query)
        if not proceed:
            return
       # await query.answer()
        prompt1 = await orig.reply(
            "Tʀɪᴍ: \nNᴏᴡ ꜱᴇɴᴅ **ꜱᴛᴀʀᴛ ᴛɪᴍᴇ**: \n\nᴇɢ: `0:00:30` (ʜᴏᴜʀ:ᴍɪɴ:ꜱᴇᴄ)",
            quote=True
        )

        try:
            start_msg = await client.listen(
                chat_id=query.from_user.id,
                timeout=90
            )
        except asyncio.TimeoutError:
            await prompt1.edit("Tɪᴍᴇ-ᴏᴜᴛ. ᴛʀɪᴍ ᴄᴀɴᴄᴇʟʟᴇᴅ, ᴩʟᴇᴀꜱᴇ ʀᴇꜱᴛᴀʀᴛ ᴀɢᴀɪɴ..")
            return
        except Exception as e:
            await orig.reply(f"Error {e}")

        start_sec = parse_hms(start_msg.text)
        await orig.reply(f"Sᴛᴀʀᴛ : {start_sec}")
        if start_sec is None:
            return await start_msg.reply("Iɴᴠᴀʟɪᴅ ᴛɪᴍᴇ ꜰᴏʀᴍᴀᴛ (ᴜꜱᴇ `0:00` ʟɪᴋᴇ). Tʀɪᴍ ᴄᴀɴᴄᴇʟʟᴇᴅ.", quote=True)

        # Ask for end time
        prompt2 = await start_msg.reply(
            "Nᴏᴡ ꜱᴇɴᴅ **ᴇɴᴅ ᴛɪᴍᴇ**: \n\nᴇɢ: `1:20:30` (ʜᴏᴜʀ:ᴍɪɴ:ꜱᴇᴄ)", quote=True
        )
        try:
            end_msg = await client.listen(
                chat_id=query.from_user.id,
                timeout=90
            )
        except asyncio.TimeoutError:
            await prompt2.edit("ᴛɪᴍᴇ-ᴏᴜᴛ. ᴛʀɪᴍ ᴄᴀɴᴄᴇʟʟᴇᴅ. ᴩʟᴇᴀꜱᴇ ʀᴇꜱᴛᴀʀᴛ ᴀɢᴀɪɴ.")
            return
        end_sec = parse_hms(end_msg.text)
        if end_sec is None:
            return await end_msg.reply("Iɴᴠᴀʟɪᴅ ᴛɪᴍᴇ ꜰᴏʀᴍᴀᴛ (ᴜꜱᴇ `0:00` ʟɪᴋᴇ). Tʀɪᴍ ᴄᴀɴᴄᴇʟʟᴇᴅ.", quote=True)

        await orig.reply(f"Eɴᴅ : {end_sec}")
        # Validation
        if end_sec <= start_sec:
            return await end_msg.reply("⚠️ End time must be greater than start time.", quote=True)
        if end_sec > duration:
            return await end_msg.reply("⚠️ End time exceeds video length.", quote=True)
        if end_sec - start_sec > 600:
            return await end_msg.reply("⚠️ Segment must be ≤ 10 minutes.", quote=True)

        # Start processing
        ack = await end_msg.reply("📥 Downloading for trim…", quote=True)
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
            full_path = tmp.name
        trimmed_path = full_path.replace(".mp4", "_@GetTGlinks_trim.mp4")
        try:
            await client.download_media(
                message=media,
                file_name=full_path,
                progress=progress_for_pyrogram,
                progress_args=("__Dᴏᴡɴʟᴏᴀᴅɪɴɢ…__", ack, time.time())
            )

            # First try a fast copy
            code = await ffmpeg_trim_async(full_path, start_sec, end_sec, trimmed_path)
            if code != 0:  # fallback to re-encode
                await ffmpeg_trim_async(
                    full_path, start_sec, end_sec,
                    trimmed_path, reencode=True
                )

            await orig.reply_video(
                video=trimmed_path,
                caption=f"Tʀɪᴍᴍᴇᴅ ꜰʀᴏᴍ {start_msg.text} ᴛᴏ {end_msg.text}",
                quote=True
            )
        except Exception as e:
            await ack.edit(
                f"❌ FFmpeg error:\n<code>{e}</code>",
                parse_mode=enums.ParseMode.HTML
            )
        finally:
            for p in (full_path, trimmed_path):
                if os.path.exists(p):
                    os.remove(p)
        syd = await query.message.reply("Yᴏᴜ ʜᴀᴠᴇ ᴛᴏ ᴡᴀɪᴛ 5 ᴍɪɴᴜᴛᴇꜱ ꜰᴏʀ ɴᴇxᴛ ᴩʀᴏᴄᴇꜱꜱ ᴏʀ ɢᴏ ᴩᴀʀᴀʟʟᴇʟ..!")
        await asyncio.sleep(300)
        await syd.delete()
        await query.message.reply("Sᴇɴᴅ ꜰɪʟᴇ ꜰᴏʀ ɴᴇxᴛ ᴩʀᴏᴄᴇꜱꜱ...! 🧊")
        twoprocess = await db.get_user_value(query.from_user.id, "twoprocess") or False
        if twoprocess:
            await db.set_user_value(query.from_user.id, "twoprocess", False)
        else:
            await db.set_user_value(query.from_user.id, "oneprocess", False)



    

    elif query.data == "hardcode":
        await query.answer("🎞 Send subtitle file…", show_alert=False)

        # 1️⃣ prompt user for subtitle
        prompt = await orig.reply(
            "📄 **Pʟᴇᴀꜱᴇ ꜱᴇɴᴅ ʏᴏᴜʀ ꜱᴜʙᴛɪᴛʟᴇ ꜰɪʟᴇ** "
            "(`.srt` or `.ass`).", quote=True
        )

        try:
            sub_msg = await client.listen(
                chat_id=query.from_user.id,
                timeout=90
            )
        except asyncio.TimeoutError:
            await prompt.edit("⏰ Timed-out. Hard-code cancelled.")
            return

        if not sub_msg.document:
            return await sub_msg.reply("❌ Subtitle must be sent as a file.", quote=True)

        # 2️⃣ download media + subtitle
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
            video_path = tmp.name
        with tempfile.NamedTemporaryFile(suffix=os.path.splitext(sub_msg.document.file_name)[1], delete=False) as tmp:
            sub_path = tmp.name

        burn_path = video_path.replace(".mp4", "_hardcoded.mp4")
        ass_path  = sub_path  # will overwrite if srt→ass

        try:
            # video download
            prog = await query.message.reply("Dᴏᴡɴʟᴏᴀᴅɪɴɢ ᴠɪᴅᴇᴏ…", quote=True)
            await client.download_media(
                message=media,
                file_name=video_path,
                progress=progress_for_pyrogram,
                progress_args=("__Downloading…__", prog, time.time())
            )

            await prog.edit("Dᴏᴡɴʟᴏᴀᴅɪɴɢ ꜱᴜʙᴛɪᴛʟᴇꜱ..")
            # subtitle download (tiny, no progress)
            await client.download_media(message=sub_msg, file_name=sub_path)

            # 3️⃣ convert SRT → ASS if needed, with styling
            if sub_path.endswith(".srt"):
                ass_path = sub_path.replace(".srt", ".ass")
                convert_cmd = ["ffmpeg", "-i", sub_path, ass_path]
                proc = await asyncio.create_subprocess_exec(
                    *convert_cmd,
                    stdout=asyncio.subprocess.DEVNULL,
                    stderr=asyncio.subprocess.DEVNULL
                )
                await proc.communicate()
                # prepend styling for white text / black outline, bottom-center
                style = (
                    "[Script Info]\n"
                    "ScriptType: v4.00+\n\n"
                    "[V4+ Styles]\n"
                    "Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, "
                    "Bold, Italic, Alignment, MarginL, MarginR, MarginV, Encoding, Outline, Shadow\n"
                    "Style: Default,Arial,48,&H00FFFFFF,&H00000000,0,0,2,10,10,30,1,2,0\n\n"
                )
                with open(ass_path, "r+", encoding="utf-8") as f:
                    content = f.read()
                    f.seek(0)
                    f.write(style + "[Events]\n" + content)

        
            # 4️⃣ burn subtitles + watermark  ─────────────────────────────────────────
                        # 4️⃣ burn subtitles + watermark  ─────────────────────────────────────────
            await prog.edit("Bᴜʀɴɪɴɢ ꜱᴜʙᴛɪᴛʟᴇꜱ... (ʜᴀʀᴅ ᴄᴏᴅɪɴɢ)")

            safe_ass_path = shlex.quote(ass_path)
            filter_graph = (
                f"[0:v]ass={safe_ass_path},"
                "drawtext="
                    "fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
                    "text='Hard Coded By : @Videos_Sample_Bot':"
                    "fontcolor=white@0.6:fontsize=18:borderw=0:"
                    "x=(w-text_w)/2:y=20:"
                    "enable='lt(mod(t\\,300)\\,5)'"
                "[v]"
            )

            burn_cmd = [
                "ffmpeg",
                "-i", video_path,
                "-filter_complex", filter_graph,
                "-map", "[v]",
                "-map", "0:a?",
                "-c:v", "libx264",
                "-preset", "medium",
                "-crf", "23",
                "-c:a", "copy",
                "-movflags", "+faststart",
                "-y", burn_path
            ]

            proc = await asyncio.create_subprocess_exec(
                *burn_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT  # Capture stderr (which shows progress)
            )

            
 
            try:
                # Get duration from media or probe
                durtion = getattr(media, "duration", None)
                debug1 = f"🔍 media.duration: {durtion}"
                
                if not durtion:
                    probe = ffmpeg.probe(video_path)
                    durtion = probe['format']['duration']
                    
                durton = float(durtion)
            except Exception as e:
                durton = 36.0
                await query.message.reply(f"⚠️ duration fallback: {e}")

            stderr_output = []
            pattern = re.compile(r"time=(\d{2}):(\d{2}):(\d{2}(?:\.\d+)?)")
            start_time = time.time()
            last_update = start_time
            
            progress = 0
            updates = 0

            
            loop_anim = ["▁ ▂ ▃ ▅ ▆ ▇ ▆ ▅ ▃ ▂", "▂ ▃ ▅ ▆ ▇ ▆ ▅ ▃ ▂ ▁", "▃ ▅ ▆ ▇ ▆ ▅ ▃ ▂ ▁ ▂", "▅ ▆ ▇ ▆ ▅ ▃ ▂ ▁ ▂ ▃", "▆ ▇ ▆ ▅ ▃ ▂ ▁ ▂ ▃ ▅", "▇ ▆ ▅ ▃ ▂ ▁ ▂ ▃ ▅ ▆"]
            anim_index = 0

            while True:
                line = await proc.stdout.readline()
                if not line:
                    break

                decoded_line = line.decode("utf-8", errors="ignore").strip()
                stderr_output.append(decoded_line)

                updates += 1

                match = pattern.search(decoded_line)
                if match:
                    h, m, s = map(float, match.groups())
                    elapsed = h * 3600 + m * 60 + s
                    progress = min(int((elapsed / durton) * 100), 100)
                else:
                    progress = progress

                anim = loop_anim[anim_index % len(loop_anim)]
                anim_index += 1
                percent_msg = "{anim} \nBᴜʀɴɪɴɢ ꜱᴜʙᴛɪᴛʟᴇꜱ: {progress}%"
                
                if time.time() - last_update >= 4:
                    try:
                        await prog.edit_text(percent_msg)
                        last_update = time.time()
                    except Exception as e:
                        await query.message.reply(f"⚠️ Progress update error: {e}")


            await query.message.reply("P ended")
            await proc.wait()

            # ✅ Check if output file exists
            if not os.path.exists(burn_path) or os.path.getsize(burn_path) == 0:
                error_log = "\n".join(stderr_output[-15:])
                await query.message.reply(
                    f"❌ ffmpeg failed:\n\n<code>{error_log}</code>",
                    parse_mode=enums.ParseMode.HTML,
                    quote=True
                )
                return

            # 5️⃣ upload result with progress
            await prog.edit("📤 Uploading hard-subbed video…")
            await orig.reply_video(
                video=burn_path,
                caption="🎬 Hard-subbed video (burned subtitles)",
                quote=True,
                progress=progress_for_pyrogram,
                progress_args=("__Uᴩʟᴏᴀᴅɪɴɢ ʜᴀʀᴅ ᴄᴏᴅᴇᴅ ꜰɪʟᴇ...__", prog, time.time())
            )
            await prog.delete()

        except Exception as e:
            await query.message.reply(
                f"❌ Error:\n<code>{e}</code>",
                parse_mode=enums.ParseMode.HTML,
                quote=True
            )
        finally:
            for f in (video_path, burn_path, sub_path, ass_path):
                if os.path.exists(f):
                    try:
                        os.remove(f)
                    except:
                        pass

    elif query.data == "harcode":
        await query.answer("🎞 Send subtitle file…", show_alert=False)

        # 1️⃣ prompt user for subtitle
        prompt = await orig.reply(
            "📄 **Pʟᴇᴀꜱᴇ ꜱᴇɴᴅ ʏᴏᴜʀ ꜱᴜʙᴛɪᴛʟᴇ ꜰɪʟᴇ** "
            "(`.srt` or `.ass`).", quote=True
        )

        try:
            sub_msg = await client.listen(
                chat_id=query.from_user.id,
                timeout=90
            )
        except asyncio.TimeoutError:
            await prompt.edit("⏰ Timed-out. Hard-code cancelled.")
            return

        if not sub_msg.document:
            return await sub_msg.reply("❌ Subtitle must be sent as a file.", quote=True)

        # 2️⃣ download media + subtitle
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
            video_path = tmp.name
        with tempfile.NamedTemporaryFile(suffix=os.path.splitext(sub_msg.document.file_name)[1], delete=False) as tmp:
            sub_path = tmp.name

        await prompt.delete()
        await sub_msg.delete()
        burn_path = video_path.replace(".mp4", "_hardcoded.mp4")
        ass_path  = sub_path  # will overwrite if srt→ass

        try:
            # video download
            pro = await query.message.reply("Dᴏᴡɴʟᴏᴀᴅɪɴɢ ᴠɪᴅᴇᴏ…", quote=True)
            await client.download_media(
                message=media,
                file_name=video_path,
                progress=progress_for_pyrogram,
                progress_args=("__Downloading…__", prog, time.time())
            )

            await pro.edit("Dᴏᴡɴʟᴏᴀᴅɪɴɢ ꜱᴜʙᴛɪᴛʟᴇꜱ..")
            # subtitle download (tiny, no progress)
            await client.download_media(message=sub_msg, file_name=sub_path)

            await pro.delete()
            
                        # Ask for subtitle delay
            syd = await query.message.reply(
                "⏱ **Enter delay for subtitles in seconds** (e.g., `-2` to show earlier, `3.5` to delay).\n"
                "Send `/skip` to use without delay."
            )
            try:
                delay_msg = await client.listen(query.from_user.id, timeout=30)
                if delay_msg.text and delay_msg.text.strip().lower() != "/skip":
                    delay = float(delay_msg.text.strip())
                else:
                    delay = 0.0
            except:
                delay = 0.0
            await query.message.reply(f"{delay}")
            await syd.delete()
            delayed_srt_path = None
            delayed_ass_path = None
            prog = await query.message.reply("Pʀᴏᴄᴇꜱꜱɪɴɢ...", quote=True)
            if delay != 0.0:
                if sub_path.endswith(".srt"):
                    delayed_srt_path = sub_path.replace(".srt", "_delayed.srt")

                    def shift_srt(text, delay_sec):
                        import re
                        from datetime import timedelta

                        def shift(ts):
                            h, m, s_ms = ts.split(":")
                            s, ms = s_ms.split(",")
                            t = timedelta(hours=int(h), minutes=int(m), seconds=int(s), milliseconds=int(ms))
                            t += timedelta(seconds=delay_sec)
                            if t.total_seconds() < 0:
                                t = timedelta(0)
                            total_ms = int(t.total_seconds() * 1000)
                            hh = total_ms // 3600000
                            mm = (total_ms % 3600000) // 60000
                            ss = (total_ms % 60000) // 1000
                            mss = total_ms % 1000
                            return f"{hh:02}:{mm:02}:{ss:02},{mss:03}"

                        def process_line(line):
                            match = re.match(r"(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})", line)
                            if match:
                                return f"{shift(match[1])} --> {shift(match[2])}"
                            return line

                        return "\n".join(process_line(l) for l in text.splitlines())

                    with open(sub_path, "r", encoding="utf-8") as f:
                        srt_data = f.read()
                    with open(delayed_srt_path, "w", encoding="utf-8") as f:
                        f.write(shift_srt(srt_data, delay))
                    sub_path = delayed_srt_path

                elif sub_path.endswith(".ass"):
                    delayed_ass_path = sub_path.replace(".ass", "_delayed.ass")

                    def shift_ass(text, delay_sec):
                        import re
                        from datetime import timedelta

                        def shift_time(ts):
                            h, m, s_cs = ts.split(":")
                            s, cs = s_cs.split(".")
                            t = timedelta(hours=int(h), minutes=int(m), seconds=int(s), milliseconds=int(cs) * 10)
                            t += timedelta(seconds=delay_sec)
                            if t.total_seconds() < 0:
                                t = timedelta(0)
                            total_cs = int(t.total_seconds() * 100)
                            hh = total_cs // 360000
                            mm = (total_cs % 360000) // 6000
                            ss = (total_cs % 6000) // 100
                            ccs = total_cs % 100
                            return f"{hh}:{mm:02}:{ss:02}.{ccs:02}"

                        def repl(line):
                            if line.startswith("Dialogue:"):
                                parts = line.split(",", 3)
                                if len(parts) >= 3:
                                    start = shift_time(parts[1])
                                    end = shift_time(parts[2])
                                    return f"{parts[0]},{start},{end},{parts[3]}"
                            return line

                        return "\n".join(repl(l) for l in text.splitlines())

                    with open(sub_path, "r", encoding="utf-8") as f:
                        ass_data = f.read()
                    with open(delayed_ass_path, "w", encoding="utf-8") as f:
                        f.write(shift_ass(ass_data, delay))
                    sub_path = delayed_ass_path

            prog = await query.message.reply("Pʀᴏᴄᴇꜱꜱɪɴɢ...", quote=True)
            # 3️⃣ convert SRT → ASS if needed, with styling
            if sub_path.endswith(".srt"):
                ass_path = sub_path.replace(".srt", ".ass")
                convert_cmd = ["ffmpeg", "-i", sub_path, ass_path]
                proc = await asyncio.create_subprocess_exec(
                    *convert_cmd,
                    stdout=asyncio.subprocess.DEVNULL,
                    stderr=asyncio.subprocess.DEVNULL
                )
                await proc.communicate()
                # prepend styling for white text / black outline, bottom-center
                style = (
                    "[Script Info]\n"
                    "ScriptType: v4.00+\n\n"
                    "[V4+ Styles]\n"
                    "Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, "
                    "Bold, Italic, Alignment, MarginL, MarginR, MarginV, Encoding, Outline, Shadow\n"
                    "Style: Default,Arial,48,&H00FFFFFF,&H00000000,0,0,2,10,10,30,1,2,0\n\n"
                )
                with open(ass_path, "r+", encoding="utf-8") as f:
                    content = f.read()
                    f.seek(0)
                    f.write(style + "[Events]\n" + content)
        
            # 4️⃣ burn subtitles + watermark  ─────────────────────────────────────────
                        # 4️⃣ burn subtitles + watermark  ─────────────────────────────────────────
            await prog.edit("Bᴜʀɴɪɴɢ ꜱᴜʙᴛɪᴛʟᴇꜱ... (ʜᴀʀᴅ ᴄᴏᴅɪɴɢ)")

            safe_ass_path = shlex.quote(ass_path)
            filter_graph = (
                f"[0:v]ass={safe_ass_path},"
                "drawtext="
                    "fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
                    "text='Hard Coded By \n@Videos_Sample_Bot':"
                    "fontcolor=white@0.6:fontsize=18:borderw=0:"
                    "x=(w-text_w)/2:y=20:"
                    "enable='lt(mod(t\\,300)\\,5)'"
                "[v]"
            )

            burn_cmd = [
                "ffmpeg",
                "-i", video_path,
                "-filter_complex", filter_graph,
                "-map", "[v]",
                "-map", "0:a?",
                "-c:v", "libx264",
                "-preset", "medium",
                "-crf", "23",
                "-c:a", "copy",
                "-movflags", "+faststart",
                "-y", burn_path
            ]

            proc = await asyncio.create_subprocess_exec(
                *burn_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT  # Capture stderr (which shows progress)
            )

            
 
            try:
                # Get duration from media or probe
                durtion = getattr(media, "duration", None)
                debug1 = f"🔍 media.duration: {durtion}"
                
                if not durtion:
                    probe = ffmpeg.probe(video_path)
                    durtion = probe['format']['duration']
                    
                durton = float(durtion)
            except Exception as e:
                durton = 36.0
                await query.message.reply(f"⚠️ duration fallback: {e}")

            stderr_output = []
            pattern = re.compile(r"time=(\d{2}):(\d{2}):(\d{2}(?:\.\d+)?)")
            start_time = time.time()
            last_update = start_time
            
            progress = 0
            updates = 0

            
            loop_anim = ["▁ ▂ ▃ ▅ ▆ ▇ ▆ ▅ ▃ ▂", "▂ ▃ ▅ ▆ ▇ ▆ ▅ ▃ ▂ ▁", "▃ ▅ ▆ ▇ ▆ ▅ ▃ ▂ ▁ ▂", "▅ ▆ ▇ ▆ ▅ ▃ ▂ ▁ ▂ ▃", "▆ ▇ ▆ ▅ ▃ ▂ ▁ ▂ ▃ ▅", "▇ ▆ ▅ ▃ ▂ ▁ ▂ ▃ ▅ ▆"]
            anim_index = 0

            while True:
                line = await proc.stdout.readline()
                if not line:
                    break

                decoded_line = line.decode("utf-8", errors="ignore").strip()
                stderr_output.append(decoded_line)

                updates += 1

                match = pattern.search(decoded_line)
                if match:
                    h, m, s = map(float, match.groups())
                    elapsed = h * 3600 + m * 60 + s
                    progress = min(int((elapsed / durton) * 100), 100)
                else:
                    elapsed_wall = time.time() - start_time
                    progress = min(int((elapsed_wall / (durton * 20)) * 100), 100)

                anim = loop_anim[anim_index % len(loop_anim)]
                anim_index += 1
                percent_msg = f"{anim} \nBᴜʀɴɪɴɢ ꜱᴜʙᴛɪᴛʟᴇꜱ: {progress}%"
                
                if time.time() - last_update >= 4:
                    try:
                        await prog.edit_text(percent_msg)
                        last_update = time.time()
                    except Exception as e:
                        await query.message.reply(f"⚠️ Progress update error: {e}")


            await query.message.reply("P ended")
            await proc.wait()

            # ✅ Check if output file exists
            if not os.path.exists(burn_path) or os.path.getsize(burn_path) == 0:
                error_log = "\n".join(stderr_output[-15:])
                await query.message.reply(
                    f"❌ ffmpeg failed:\n\n<code>{error_log}</code>",
                    parse_mode=enums.ParseMode.HTML,
                    quote=True
                )
                return

            # 5️⃣ upload result with progress
            await prog.edit("📤 Uploading hard-subbed video…")
            await orig.reply_video(
                video=burn_path,
                caption="🎬 Hard-subbed video (burned subtitles)",
                quote=True,
                progress=progress_for_pyrogram,
                progress_args=("__Uᴩʟᴏᴀᴅɴɢ ʜᴀʀᴅ ᴄᴏᴅᴇᴅ ꜰɪʟᴇ...__", prog, time.time())
            )
            await prog.delete()

        except Exception as e:
            await query.message.reply(
                f"❌ Error:\n<code>{e}</code>",
                parse_mode=enums.ParseMode.HTML,
                quote=True
            )
        finally:
            for f in (video_path, burn_path, sub_path, ass_path, delayed_ass_path, delayed_srt_path):
                if os.path.exists(f):
                    try:
                        os.remove(f)
                    except:
                        pass

                        
    elif query.data == "hardcod": ##Working
        await query.answer("🎞 Send subtitle file…", show_alert=False)

        # 1️⃣ prompt user for subtitle
        prompt = await orig.reply(
            "📄 **Pʟᴇᴀꜱᴇ ꜱᴇɴᴅ ʏᴏᴜʀ ꜱᴜʙᴛɪᴛʟᴇ ꜰɪʟᴇ (ꜱʀᴛ ᴏʀ ᴀᴄᴄ)** "
            "(`.srt` or `.ass`).", quote=True
        )

        try:
            sub_msg = await client.listen(
                chat_id=query.from_user.id,
                timeout=90
            )
        except asyncio.TimeoutError:
            await prompt.edit("⏰ Timed-out. Hard-code cancelled.")
            return

        if not sub_msg.document:
            return await sub_msg.reply("❌ Subtitle must be sent as a file.", quote=True)

        # 2️⃣ download media + subtitle
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
            video_path = tmp.name
        with tempfile.NamedTemporaryFile(suffix=os.path.splitext(sub_msg.document.file_name)[1], delete=False) as tmp:
            sub_path = tmp.name

        burn_path = video_path.replace(".mp4", "_hardcoded.mp4")
        ass_path  = sub_path  # will overwrite if srt→ass

        try:
            # video download
            prog = await query.message.reply("📥 Downloading video…", quote=True)
            await client.download_media(
                message=media,
                file_name=video_path,
                progress=progress_for_pyrogram,
                progress_args=("__Downloading…__", prog, time.time())
            )

            # subtitle download (tiny, no progress)
            await client.download_media(message=sub_msg, file_name=sub_path)

            # 3️⃣ convert SRT → ASS if needed, with styling
            if sub_path.endswith(".srt"):
                ass_path = sub_path.replace(".srt", ".ass")
                convert_cmd = ["ffmpeg", "-i", sub_path, ass_path]
                proc = await asyncio.create_subprocess_exec(
                    *convert_cmd,
                    stdout=asyncio.subprocess.DEVNULL,
                    stderr=asyncio.subprocess.DEVNULL
                )
                await proc.communicate()
                # prepend styling for white text / black outline, bottom-center
                style = (
                    "[Script Info]\n"
                    "ScriptType: v4.00+\n\n"
                    "[V4+ Styles]\n"
                    "Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, "
                    "Bold, Italic, Alignment, MarginL, MarginR, MarginV, Encoding, Outline, Shadow\n"
                    "Style: Default,Arial,48,&H00FFFFFF,&H00000000,0,0,2,10,10,30,1,2,0\n\n"
                )
                with open(ass_path, "r+", encoding="utf-8") as f:
                    content = f.read()
                    f.seek(0)
                    f.write(style + "[Events]\n" + content)

            # 4️⃣ burn subtitles (async ffmpeg)
            await prog.edit("🔥 Burning subtitles…")
            burn_cmd = [
                "ffmpeg", "-i", video_path, "-vf", f"ass={ass_path}",
                "-c:v", "libx264", "-preset", "medium", "-c:a", "copy", "-y", burn_path
            ]
            proc = await asyncio.create_subprocess_exec(
                *burn_cmd,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL
            )
            await proc.communicate()

            # 5️⃣ upload result with progress
            await prog.edit("📤 Uploading hard-subbed video…")
            await orig.reply_video(
                video=burn_path,
                caption="🎬 Hard-subbed video (burned subtitles)",
                quote=True,
                progress=progress_for_pyrogram,
                progress_args=("__Uploading…__", prog, time.time())
            )
            await prog.delete()

        except Exception as e:
            await query.message.reply(
                f"❌ Error:\n<code>{e}</code>",
                parse_mode=enums.ParseMode.HTML,
                quote=True
            )
        finally:
            for f in (video_path, burn_path, sub_path, ass_path, delayed_srt_path):
                if os.path.exists(f):
                    try:
                        os.remove(f)
                    except:
                        pass





    elif query.data == "check_subscription":
        if await ensure_member(client, query):
            await query.message.reply_text("**ᴄʟɪᴄᴋ ᴏɴ ᴩʀᴏᴄᴇꜱꜱ** ᴛᴏ ᴄᴏɴᴛɪɴᴜᴇ...!")
            await query.message.delete()
        else:
            await query.answer("ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴊᴏɪɴᴇᴅ ɪɴ ᴀʟʟ, ᴩʟᴇᴀꜱᴇ ᴊᴏɪɴ.... 🎐", show_alert=True)
    elif query.data == "checksub":
        await query.answer("🔍 Checking access…", show_alert=False)

        buttons = [
            [InlineKeyboardButton("Sᴀᴍᴩʟᴇ - 30ꜱ", callback_data="sample")],
            [InlineKeyboardButton("Gᴇɴᴇʀᴀᴛᴇ Sᴄʀᴇᴇɴꜱʜᴏᴛ", callback_data="screenshot")],
            [InlineKeyboardButton("Tʀɪᴍ", callback_data="trim")],
            [InlineKeyboardButton("Exᴛʀᴀᴄᴛ Aᴜᴅɪᴏ", callback_data="extract_audio")],
            [InlineKeyboardButton("Rᴇɴᴀᴍᴇ", url="https://t.me/MS_ReNamEr_BoT"),
             InlineKeyboardButton("Sᴛʀᴇᴀᴍ", url="https://t.me/Ms_FiLe2LINk_bOt")],
        
            [InlineKeyboardButton("Sᴜᴩᴩᴏʀᴛ", url="https://t.me/Bot_cracker")],
            [InlineKeyboardButton("Rᴇqᴜᴇꜱᴛ Mᴏʀᴇ Fᴇᴀᴛᴜʀᴇꜱ", url="https://t.me/syd_xyz")]
        ]


        await query.message.reply(
            "Cʜᴏᴏꜱᴇ ᴀɴ ᴀᴄᴛɪᴏɴ ʙᴇʟᴏᴡ:",
            reply_markup=InlineKeyboardMarkup(buttons),
            quote=True
        )
