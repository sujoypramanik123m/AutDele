import motor.motor_asyncio
from config import Config

class Database:
    def __init__(self, uri, database_name):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self.client[database_name]
        self.users = self.db.users          # for storing users
        self.chats = self.db.chats          # for storing group auto-delete time
         # for userbot sessions

    # ─── USER METHODS ────────────────────────────────────────────────────────────

    async def is_user_exist(self, id):
        user = await self.users.find_one({'_id': int(id)})
        return bool(user)

    async def add_user(self, user_id: int):
        if not await self.users.find_one({"_id": user_id}):
            await self.users.insert_one({"_id": user_id})

    async def get_all_users(self):
        return self.users.find({})

    async def total_users_count(self):
        return await self.users.count_documents({})

    async def delete_user(self, user_id: int):
        await self.users.delete_one({"_id": user_id})

    # ─── CHAT METHODS (AUTO-DELETE) ──────────────────────────────────────────────

    async def set_chat_delete_time(self, chat_id: int, seconds: int):
        await self.chats.update_one(
            {"chat_id": chat_id},
            {"$set": {"delete_after": seconds}},
            upsert=True
        )

    async def get_chat_delete_time(self, chat_id: int):
        doc = await self.chats.find_one({"chat_id": chat_id})
        return doc.get("delete_after") if doc else None

    async def remove_chat_delete_time(self, chat_id: int):
        await self.chats.delete_one({"chat_id": chat_id})

    async def get_all_chats(self):
        return self.chats.find({})

    
db = Database(Config.DB_URL, Config.DB_NAME)
