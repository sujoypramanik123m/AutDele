import motor.motor_asyncio
from config import Config

class Database:
    def __init__(self, uri, database_name):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self.client[database_name]
        self.users = self.db.users          # for storing users
        self.chats = self.db.chats
        self.chas = self.db.chas # for storing group auto-delete time
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

    async def add_grp(self, user_id: int):
        if not await self.chas.find_one({"_id": user_id}):
            await self.chas.insert_one({"_id": user_id})

    async def get_all_grps(self):
        return self.chas.find({})

    async def total_grps_count(self):
        return await self.chas.count_documents({})
        
    async def delete_user(self, user_id: int):
        await self.users.delete_one({"_id": user_id})


db = Database(Config.LNK_URL, Config.DB_NAME)
