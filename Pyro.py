import asyncio
from pyrogram import Client, filters
from pyrogram.raw.functions.account import ReportPeer
from pyrogram.raw.types import InputPeerChannel, InputPeerUser, InputReportReasonSpam, InputReportReasonPornography, InputReportReasonViolence, InputReportReasonChildAbuse, InputReportReasonOther, InputReportReasonCopyright, InputReportReasonFake, InputReportReasonGeoIrrelevant, InputReportReasonIllegalDrugs, InputReportReasonPersonalDetails
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# Your provided details
BOT_TOKEN = "7561524299:AAFjfBmLNx0R9-5IZaN2tz2iJlQK1z3WXlU"
STRING_SESSION = "BQHAnfYASMR-fjRi6DH3WS4E3CpvD5voiRN04SFib13F6D7TWkZyAiblSuwWYiIxjfmZm7vc-mJJqqBJlIoOQHKOkWnE1EJSnoUWqcwz0x_6ITB1PTSuIaKPJUgNz1AVuqBb01VIA6rus7_UVlbw1tmsApqYsu_-S22Bo3AqYrY-Me8nSKhdEaIMmdvt9QwpGQsUTEx0eSDT9d6ZfBPCHbALXOoMCP6xEwC5j7kPgUpSr42-ltnRhhkssPAnqvjbIAheILJHKWRyM3lS290g8KdkL-s1uj6LPAqbJumQC-Q9M7zc3Jawc5jmVvQ7dBRsbrDBwOVzJckRZ6HTQLt1ILtIdcrmaQAAAAGlMTQvAA"
api_id = "29400566"
api_hash = "8fd30dc496aea7c14cf675f59b74ec6f"

# Initialize the bot and userbot clients
app = Client("reporter_bot", api_id=api_id, api_hash=api_hash, bot_token=BOT_TOKEN)
userbot_client = Client("userbot", api_id=api_id, api_hash=api_hash, session_string=STRING_SESSION)

userbot_connected = False
is_reporting = False
target_user = None
report_reason = None

def get_report_reason(text):
    if text == "Spam":
        return InputReportReasonSpam()
    elif text == "Pornography":
        return InputReportReasonPornography()
    elif text == "Violence":
        return InputReportReasonViolence()
    elif text == "Child Abuse":
        return InputReportReasonChildAbuse()
    elif text == "Other":
        return InputReportReasonOther()
    elif text == "Copyright":
        return InputReportReasonCopyright()
    elif text == "Fake":
        return InputReportReasonFake()
    elif text == "Geo Irrelevant":
        return InputReportReasonGeoIrrelevant()
    elif text == "Illegal Drugs":
        return InputReportReasonIllegalDrugs()
    elif text == "Personal Details":
        return InputReportReasonPersonalDetails()
    return InputReportReasonOther()

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply(
        "🤖 **Welcome to Reporter Bot!**\n\n"
        "Userbot is not yet connected. Use `/connect` to connect the userbot."
    )

@app.on_message(filters.command("connect"))
async def connect(client, message):
    global userbot_connected
    if not userbot_connected:
        await message.reply("🔗 Connecting Userbot...")
        await userbot_client.start()
        userbot_connected = True
        await message.reply("✅ Userbot connected!")
    else:
        await message.reply("❌ Userbot is already connected.")

@app.on_message(filters.command("report"))
async def report_start(client, message):
    global userbot_connected, target_user
    if not userbot_connected:
        await message.reply("❌ **Userbot is not connected.**")
        return

    await message.reply("Kindly enter the username or chat ID of the target:")
    target_user_message = await client.listen(message.chat.id)
    target_user = target_user_message.text

    try:
        # Attempt to join the channel or group
        await userbot_client.join_chat(target_user)
        target_entity = await userbot_client.get_chat(target_user)
        entity_type = "Channel" if target_entity.type == "channel" else "Group"
        await message.reply(
            f"✅ **Target Details:**\n"
            f"**Target:** `{target_user}`\n"
            f"**Target Name:** {target_entity.title}\n"
            f"Successfully joined the {entity_type}!"
        )

        # Send report buttons
        buttons = [
            [InlineKeyboardButton("Spam", callback_data="1"), InlineKeyboardButton("Pornography", callback_data="2"),
             InlineKeyboardButton("Violence", callback_data="3"), InlineKeyboardButton("Child Abuse", callback_data="4"),
             InlineKeyboardButton("Other", callback_data="5")],
            [InlineKeyboardButton("Copyright", callback_data="6"), InlineKeyboardButton("Fake", callback_data="7"),
             InlineKeyboardButton("Geo Irrelevant", callback_data="8"), InlineKeyboardButton("Illegal Drugs", callback_data="9"),
             InlineKeyboardButton("Personal Details", callback_data="10")]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)

        await message.reply(
            "Select the report type:", reply_markup=reply_markup
        )
    except Exception as e:
        await message.reply(f"❌ **Failed to find or join the target:** {e}")

@app.on_callback_query()
async def select_report_type(client, callback_query):
    global report_reason
    try:
        report_type = int(callback_query.data)
        reasons = [
            "Spam", "Pornography", "Violence", "Child Abuse", "Other", 
            "Copyright", "Fake", "Geo Irrelevant", "Illegal Drugs", "Personal Details"
        ]

        report_reason = get_report_reason(reasons[report_type - 1])
        await callback_query.message.reply("Kindly enter the number of reports to send (or type `default` for continuous reports):")
    except Exception as e:
        await callback_query.message.reply(f"❌ **Error selecting report type:** {e}")

@app.on_message(filters.text)
async def send_reports(client, message):
    global userbot_client, is_reporting, report_reason, target_user
    if not is_reporting and target_user and report_reason:
        is_reporting = True
        try:
            target_entity = await userbot_client.get_chat(target_user)
        except Exception as e:
            await message.reply(f"❌ **Failed to find the target:** {e}")
            is_reporting = False
            return

        num_reports = message.text.strip().lower()
        if num_reports == "default":
            num_reports = -1
        else:
            try:
                num_reports = int(num_reports)
                if num_reports <= 0:
                    raise ValueError("Invalid number")
            except ValueError:
                await message.reply("❌ **Invalid number. Enter a valid number or `default` for continuous.**")
                is_reporting = False
                return

        await message.reply("🔄 **Starting the reporting process...**")
        count = 0
        try:
            while num_reports != 0:
                try:
                    peer = app.resolve_peer(target_user)
                    if isinstance(peer, dict) and "channel_id" in peer:
                        channel = InputPeerChannel(channel_id=peer["channel_id"], access_hash=peer["access_hash"])
                    else:
                        channel = InputPeerUser(user_id=peer["user_id"], access_hash=peer["access_hash"])

                    report_peer = ReportPeer(
                        peer=channel,
                        reason=report_reason,
                        message="Automated report using Reporter Bot"
                    )

                    await app.send(report_peer)
                    count += 1
                    await asyncio.sleep(2)
                    if num_reports > 0:
                        num_reports -= 1
                except Exception as e:
                    await message.reply(f"❌ **Error during reporting:** {e}")
                    break
        except Exception as e:
            await message.reply(f"❌ **Userbot disconnected:** {e}")

        await message.reply(f"✅ **Reporting process completed!**\n\nTotal Reports Sent: `{count}`")
        is_reporting = False

@app.on_message(filters.command("disconnect"))
async def disconnect_userbot(client, message):
    global userbot_connected
    if not userbot_connected:
        await message.reply("❌ **No userbot is connected.**")
        return

    if is_reporting:
        await message.reply("⚠️ Reporting is in progress. Disconnecting will stop the process.")
        is_reporting = False

    try:
        await userbot_client.stop()
        userbot_connected = False
        await message.reply("✅ **Userbot disconnected successfully!**")
    except Exception as e:
        await message.reply(f"❌ **Failed to disconnect:** {e}")

print("🤖 Reporter Bot is running...")
app.run()
