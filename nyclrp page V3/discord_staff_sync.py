import asyncio
import base64
import json
import os
from datetime import datetime, timezone

import aiohttp
import discord


# ==========================================================
# CONFIG
# ==========================================================

GITHUB_REPO = os.getenv("GITHUB_REPO", "ishqqn/NYCLRP-page")
GITHUB_BRANCH = os.getenv("GITHUB_BRANCH", "main")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

GUILD_ID = int(os.getenv("DISCORD_GUILD_ID", "1475908093266100365"))

STAFF_ROLE_NAME = "New York City Staff"
STAFF_FILE = "staff.json"

# How often the GitHub file is checked/updated
SYNC_INTERVAL = 60


# ==========================================================
# GITHUB
# ==========================================================

GITHUB_API = "https://api.github.com"


async def github_request(method, url, **kwargs):
    if not GITHUB_TOKEN:
        raise RuntimeError("GITHUB_TOKEN is missing.")

    headers = kwargs.pop("headers", {})

    headers.update({
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    })

    async with aiohttp.ClientSession() as session:
        async with session.request(
            method,
            url,
            headers=headers,
            **kwargs,
        ) as response:

            text = await response.text()

            if response.status >= 400:
                raise RuntimeError(
                    f"GitHub API error {response.status}: {text}"
                )

            if not text:
                return None

            return json.loads(text)


async def get_github_file():
    url = (
        f"{GITHUB_API}/repos/"
        f"{GITHUB_REPO}/contents/{STAFF_FILE}"
        f"?ref={GITHUB_BRANCH}"
    )

    try:
        return await github_request("GET", url)
    except RuntimeError as error:
        # File doesn't exist yet
        if "404" in str(error):
            return None

        raise


async def update_github_file(data):
    existing = await get_github_file()

    content = json.dumps(
        data,
        indent=2,
        ensure_ascii=False,
    )

    encoded = base64.b64encode(
        content.encode("utf-8")
    ).decode("utf-8")

    url = (
        f"{GITHUB_API}/repos/"
        f"{GITHUB_REPO}/contents/{STAFF_FILE}"
    )

    payload = {
        "message": "Update staff online",
        "content": encoded,
        "branch": GITHUB_BRANCH,
    }

    if existing and existing.get("sha"):
        payload["sha"] = existing["sha"]

    await github_request(
        "PUT",
        url,
        json=payload,
    )


# ==========================================================
# DISCORD STAFF DATA
# ==========================================================

def get_member_status(member):
    """
    Convert Discord's status into the values
    used by the Staff Online page.
    """

    status = member.status

    if status == discord.Status.online:
        return "online"

    if status == discord.Status.idle:
        return "idle"

    if status == discord.Status.dnd:
        return "dnd"

    return "offline"


def get_staff_members(guild):
    role = discord.utils.get(
        guild.roles,
        name=STAFF_ROLE_NAME,
    )

    if role is None:
        print(
            f"[Staff Sync] Role '{STAFF_ROLE_NAME}' "
            f"was not found."
        )
        return []

    members = []

    for member in role.members:

        # Don't put bots into Staff Online
        if member.bot:
            continue

        members.append({
            "id": str(member.id),
            "username": member.name,
            "display_name": member.display_name,
            "avatar": (
                member.display_avatar.url
                if member.display_avatar
                else None
            ),
            "status": get_member_status(member),
        })

    # Keep the page stable
    members.sort(
        key=lambda member: member["display_name"].lower()
    )

    return members


# ==========================================================
# SYNC
# ==========================================================

class StaffSync:

    def __init__(self, bot):
        self.bot = bot
        self.task = None
        self.last_data = None

    async def sync(self):
        guild = self.bot.get_guild(GUILD_ID)

        if guild is None:
            print(
                f"[Staff Sync] Guild {GUILD_ID} not found."
            )
            return

        members = get_staff_members(guild)

        data = {
            "updated_at": datetime.now(
                timezone.utc
            ).isoformat(),
            "guild_id": str(GUILD_ID),
            "role": STAFF_ROLE_NAME,
            "members": members,
        }

        # Don't create a GitHub commit if nothing changed.
        comparison = {
            "guild_id": data["guild_id"],
            "role": data["role"],
            "members": data["members"],
        }

        if comparison == self.last_data:
            return

        try:
            await update_github_file(data)

            self.last_data = comparison

            print(
                f"[Staff Sync] Updated GitHub: "
                f"{len(members)} staff member(s)."
            )

        except Exception as error:
            print(
                f"[Staff Sync] GitHub update failed: "
                f"{error}"
            )

    async def loop(self):

        await self.bot.wait_until_ready()

        print("[Staff Sync] Started.")

        while not self.bot.is_closed():

            await self.sync()

            await asyncio.sleep(SYNC_INTERVAL)

    def start(self):

        if self.task is None:
            self.task = self.bot.loop.create_task(
                self.loop()
            )


# ==========================================================
# SETUP
# ==========================================================

def setup_staff_sync(bot):

    staff_sync = StaffSync(bot)

    bot.staff_sync = staff_sync

    staff_sync.start()

    print("[Staff Sync] Module loaded.")