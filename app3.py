import asyncio
from telethon import TelegramClient, events, functions, types
from telethon.sessions import StringSession

BOT_TOKEN = "7561524299:AAFjfBmLNx0R9-5IZaN2tz2iJlQK1z3WXlU"
STRING_SESSION = "1BVtsOGsBu0dh6biDxWvQ3DrJPveqhte2HmVTq_Q6yok97CNCuYT_vB6RoS6SioKj5nsOqqWuSCE4ZQvsACMYY8mnBY46xhxrqSS0-JRQXUU0EbR8VGxVKmsnRJC1VjcRoTTbKKv80Na2f4rJyyZmGlFyfGFd8lRGAc07oj5iLQinalaKwCJPLdwsYXtPjeLXdxocmdTv1aeBAtMODKw328Bc3lt35LSe_ujaE5k_-OI63A9ep7WvvEKesDhPfuiAWb8phTTeN6JsQZbO8cc3tUfIbK_FK7BUg_dyXNVWuGiNhjAVcifcM5iNlAhfKx3XpPWdfLYl6kkIk8Qxf6a2e3VYpIdl_VY="

userbot_client = TelegramClient(StringSession(STRING_SESSION), api_id="29400566", api_hash="8fd30dc496aea7c14cf675f59b74ec6f")
userbot_connected = True  # Directly set to True as the userbot is connected via string session
is_reporting = False
target_user = None
report_reason = None

bot = TelegramClient("reporter_bot", api_id="29400566", api_hash="8fd30dc496aea7c14cf675f59b74ec6f").start(bot_token=BOT_TOKEN)


@bot.on(events.NewMessage(pattern="/start"))
async def start(event):
    await event.respond(
        "🤖 **Welcome to Reporter Bot!**\n\n"
        "Userbot is already connected via the provided string session.\n"
        "Now you can start reporting using `/report`."
    )


@bot.on(events.NewMessage(pattern="/report"))
async def report_start(event):
    global userbot_connected, target_user
    if not userbot_connected:
        await event.respond("❌ **Userbot is not connected.**")
        return

    await event.respond("Kindly enter the username or chat ID of the target:")
    target_user_message = await bot.wait_for(events.NewMessage(from_users=event.sender_id))
    target_user = target_user_message.text  # Get the text of the user's message

    try:
        target_entity = await userbot_client.get_entity(target_user)  # Use the text as input
        entity_type = "Channel" if target_entity.broadcast else "Group"
        await event.respond(
            f"✅ **Target Details:**\n"
            f"**Target:** `{target_user}`\n"
            f"**Target Name:** {target_entity.title}\n"
            f"Successfully joined the {entity_type}!"
        )

        # Send report buttons as before
        buttons = [
            [types.KeyboardButtonCallback("1", b"1"), types.KeyboardButtonCallback("2", b"2"),
             types.KeyboardButtonCallback("3", b"3"), types.KeyboardButtonCallback("4", b"4"),
             types.KeyboardButtonCallback("5", b"5")],
            [types.KeyboardButtonCallback("6", b"6"), types.KeyboardButtonCallback("7", b"7"),
             types.KeyboardButtonCallback("8", b"8"), types.KeyboardButtonCallback("9", b"9"),
             types.KeyboardButtonCallback("10", b"10")]
        ]

        await event.respond(
            "**Select the report type:**\n\n"
            "[1] Spam\n[2] Pornography\n[3] Violence\n[4] Child Abuse\n[5] Other\n"
            "[6] Copyright\n[7] Fake Account\n[8] Geo Irrelevant\n[9] Illegal Drugs\n[10] Personal Details",
            buttons=buttons
        )
    except Exception as e:
        await event.respond(f"❌ **Failed to find the target:** {e}")


@bot.on(events.CallbackQuery)
async def select_report_type(event):
    global report_reason
    try:
        report_type = int(event.data.decode())
        reasons_map = {
            1: types.InputReportReasonSpam(),
            2: types.InputReportReasonPornography(),
            3: types.InputReportReasonViolence(),
            4: types.InputReportReasonChildAbuse(),
            5: types.InputReportReasonOther(),
            6: types.InputReportReasonCopyright(),
            7: types.InputReportReasonFake(),
            8: types.InputReportReasonGeoIrrelevant(),
            9: types.InputReportReasonIllegalDrugs(),
            10: types.InputReportReasonPersonalDetails(),
        }

        report_reason = reasons_map.get(report_type, types.InputReportReasonOther())
        await event.respond("Kindly enter the number of reports to send (or type `default` for continuous reports):")
    except Exception as e:
        await event.respond(f"❌ **Error selecting report type:** {e}")


@bot.on(events.NewMessage(from_users=lambda u: True))
async def send_reports(event):
    global userbot_client, is_reporting, report_reason, target_user
    if not is_reporting and target_user and report_reason:
        is_reporting = True
        try:
            target_entity = await userbot_client.get_entity(target_user)
        except Exception as e:
            await event.respond(f"❌ **Failed to find the target:** {e}")
            is_reporting = False
            return

        num_reports = event.text.strip().lower()
        if num_reports == "default":
            num_reports = -1
        else:
            try:
                num_reports = int(num_reports)
                if num_reports <= 0:
                    raise ValueError("Invalid number")
            except ValueError:
                await event.respond("❌ **Invalid number. Enter a valid number or `default` for continuous.**")
                is_reporting = False
                return

        await event.respond("🔄 **Starting the reporting process...**")
        count = 0
        try:
            while num_reports != 0:
                try:
                    await userbot_client(
                        functions.account.ReportPeerRequest(
                            peer=target_entity,
                            reason=report_reason,
                            message="Automated report using Reporter Bot"
                        )
                    )
                    count += 1
                    await asyncio.sleep(2)
                    if num_reports > 0:
                        num_reports -= 1
                except Exception as e:
                    await event.respond(f"❌ **Error during reporting:** {e}")
                    break
        except Exception as e:
            await event.respond(f"❌ **Userbot disconnected:** {e}")

        await event.respond(f"✅ **Reporting process completed!**\n\nTotal Reports Sent: `{count}`")
        is_reporting = False


@bot.on(events.NewMessage(pattern="/disconnect"))
async def disconnect_userbot(event):
    global userbot_client, userbot_connected, is_reporting
    if not userbot_connected:
        await event.respond("❌ **No userbot is connected.**")
        return

    if is_reporting:
        await event.respond("⚠️ Reporting is in progress. Disconnecting will stop the process.")
        is_reporting = False

    try:
        await userbot_client.disconnect()
        userbot_connected = False
        userbot_client = None
        await event.respond("✅ **Userbot disconnected successfully!**")
    except Exception as e:
        await event.respond(f"❌ **Failed to disconnect:** {e}")


print("🤖 Reporter Bot is running...")
bot.run_until_disconnected()
