from pyrogram import Client, filters
from pyrogram.raw.functions.account import ReportPeer
from pyrogram.raw.types import *

# Bot and userbot configuration
api_id = "29400566"
api_hash = "8fd30dc496aea7c14cf675f59b74ec6f"
bot_token = "7561524299:AAFjfBmLNx0R9-5IZaN2tz2iJlQK1z3WXlU"
string_session = "BQHAnfYASMR-fjRi6DH3WS4E3CpvD5voiRN04SFib13F6D7TWkZyAiblSuwWYiIxjfmZm7vc-mJJqqBJlIoOQHKOkWnE1EJSnoUWqcwz0x_6ITB1PTSuIaKPJUgNz1AVuqBb01VIA6rus7_UVlbw1tmsApqYsu_-S22Bo3AqYrY-Me8nSKhdEaIMmdvt9QwpGQsUTEx0eSDT9d6ZfBPCHbALXOoMCP6xEwC5j7kPgUpSr42-ltnRhhkssPAnqvjbIAheILJHKWRyM3lS290g8KdkL-s1uj6LPAqbJumQC-Q9M7zc3Jawc5jmVvQ7dBRsbrDBwOVzJckRZ6HTQLt1ILtIdcrmaQAAAAGlMTQvAA"

# Initialize clients
app = Client("reporter_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)
userbot = Client(":memory:", api_id=api_id, api_hash=api_hash, session_string=string_session)

# Global variables
target_user = None
report_reason = None

# Function to resolve the report reason
def get_report_reason(reason_id):
    reasons_map = {
        1: InputReportReasonSpam(),
        2: InputReportReasonPornography(),
        3: InputReportReasonViolence(),
        4: InputReportReasonChildAbuse(),
        5: InputReportReasonOther(),
        6: InputReportReasonCopyright(),
        7: InputReportReasonFake(),
        8: InputReportReasonGeoIrrelevant(),
        9: InputReportReasonIllegalDrugs(),
        10: InputReportReasonPersonalDetails(),
    }
    return reasons_map.get(reason_id, InputReportReasonOther())

# /start command
@app.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply("🤖 **Welcome to Reporter Bot!**\n\nUse /report to start reporting.")

# /report command
@app.on_message(filters.command("report"))
async def report_start(client, message):
    global target_user
    await message.reply("Kindly enter the username or chat ID of the target:")

    @app.on_message(filters.chat(message.chat.id) & ~filters.command)
    async def handle_target(client, target_message):
        global target_user
        target_user = target_message.text

        try:
            # Userbot joins the channel/group if needed
            target_entity = await userbot.resolve_peer(target_user)
            if isinstance(target_entity, InputPeerChannel):
                await userbot.join_chat(target_user)

            await target_message.reply(
                f"✅ **Target Details:**\n"
                f"**Target:** `{target_user}`\n"
                f"Successfully joined if it is a channel/group!"
            )

            # Ask for the report reason
            await target_message.reply(
                "**Select the report type by sending the number:**\n\n"
                "[1] Spam\n[2] Pornography\n[3] Violence\n[4] Child Abuse\n[5] Other\n"
                "[6] Copyright\n[7] Fake Account\n[8] Geo Irrelevant\n[9] Illegal Drugs\n[10] Personal Details"
            )

            @app.on_message(filters.chat(target_message.chat.id) & ~filters.command)
            async def handle_reason(client, reason_message):
                global report_reason
                try:
                    reason_id = int(reason_message.text)
                    report_reason = get_report_reason(reason_id)

                    await reason_message.reply(
                        "Kindly enter the number of reports to send (or type `default` for continuous reports):"
                    )

                    @app.on_message(filters.chat(reason_message.chat.id) & ~filters.command)
                    async def handle_report_count(client, count_message):
                        await send_reports(count_message)

                except ValueError:
                    await reason_message.reply("❌ **Invalid input. Please send a valid number.**")

        except Exception as e:
            await target_message.reply(f"❌ **Error:** {e}")

# Send reports
async def send_reports(message):
    global userbot, target_user, report_reason
    try:
        num_reports = message.text.strip().lower()
        if num_reports == "default":
            num_reports = -1
        else:
            num_reports = int(num_reports)

        target_entity = await userbot.resolve_peer(target_user)
        count = 0

        await message.reply("🔄 **Starting the reporting process...**")
        while num_reports != 0:
            await userbot.invoke(
                ReportPeer(peer=target_entity, reason=report_reason, message="Automated report using Reporter Bot")
            )
            count += 1
            if num_reports > 0:
                num_reports -= 1

        await message.reply(f"✅ **Reporting completed!**\n\nTotal Reports Sent: `{count}`")
    except Exception as e:
        await message.reply(f"❌ **Error during reporting:** {e}")

# Run the bot
print("🤖 Reporter Bot is running...")
app.run()
