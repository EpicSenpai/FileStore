import motor.motor_asyncio
from datetime import datetime, timedelta

class MongoDB:
    _instances = {}

    def __new__(cls, uri: str, db_name: str):
        if (uri, db_name) not in cls._instances:
            instance = super().__new__(cls)
            instance.client = motor.motor_asyncio.AsyncIOMotorClient(uri)
            instance.db = instance.client[db_name]
            instance.user_data = instance.db["users"]
            instance.channel_data = instance.db["channels"]
            instance.premium_users = instance.db['pros']
            instance.fsub_status = instance.db['fsub_status']  
            instance.request_sub = instance.db['request_sub']  
            cls._instances[(uri, db_name)] = instance
        return cls._instances[(uri, db_name)]

    async def set_channels(self, channels: list[int]):
        await self.user_data.update_one(
            {"_id": 1},
            {"$set": {"channels": channels}},
            upsert=True
        )

    async def get_channels(self) -> list[int]:
        data = await self.user_data.find_one({"_id": 1})
        return data.get("channels", []) if data else []

    async def add_channel_user(self, channel_id: int, user_id: int):
        await self.channel_data.update_one(
            {"_id": channel_id},
            {"$addToSet": {"users": user_id}},
            upsert=True
        )

    async def remove_channel_user(self, channel_id: int, user_id: int):
        await self.channel_data.update_one(
            {"_id": channel_id},
            {"$pull": {"users": user_id}}
        )

    async def get_channel_users(self, channel_id: int) -> list[int]:
        doc = await self.channel_data.find_one({"_id": channel_id})
        return doc.get("users", []) if doc else []

    async def is_user_in_channel(self, channel_id: int, user_id: int) -> bool:
        doc = await self.channel_data.find_one(
            {"_id": channel_id, "users": {"$in": [user_id]}},
            {"_id": 1}
        )
        return doc is not None

    # ✅ PRO PREMIUM FEATURES (UPGRADED LAYER)

    async def add_pro(self, user_id: int, expiry_date: datetime = None, total_days: int = None, is_lifetime: bool = False):
        try:
            await self.premium_users.update_one(
                {'_id': user_id},
                {'$set': {
                    'expiry_date': expiry_date,
                    'total_days': total_days,
                    'is_lifetime': is_lifetime,
                    'added_at': datetime.now()
                }},
                upsert=True
            )
            return True
        except Exception as e:
            print(f"Failed to add premium user: {e}")
            return False

    async def remove_pro(self, user_id: int):
        try:
            await self.premium_users.delete_one({'_id': user_id})
            return True
        except Exception as e:
            print(f"Failed to remove premium user: {e}")
            return False

    async def is_pro(self, user_id: int):
        doc = await self.premium_users.find_one({'_id': user_id})
        if not doc:
            return False
        if doc.get('is_lifetime', False):
            return True
        if 'expiry_date' not in doc or doc['expiry_date'] is None:
            return True  
        return doc['expiry_date'] > datetime.now()

    async def get_pros_list(self):
        current_time = datetime.now()
        cursor = self.premium_users.find({
            '$or': [
                {'is_lifetime': True},
                {'expiry_date': None},  
                {'expiry_date': {'$exists': False}},  
                {'expiry_date': {'$gt': current_time}}  
            ]
        })
        return [doc['_id'] async for doc in cursor]
        
    async def get_expiry_date(self, user_id: int) -> datetime:
        doc = await self.premium_users.find_one({'_id': user_id})
        return doc.get('expiry_date') if doc else None

    # ✅ DYNAMIC GLOBAL SETTINGS LAYER
    async def get_set_credits_amount(self) -> int:
        doc = await self.user_data.find_one({"_id": "global_credits_config"})
        return doc.get("reward_amount", 3) if doc else 3

    async def set_global_credits_amount(self, amount: int):
        await self.user_data.update_one(
            {"_id": "global_credits_config"},
            {"$set": {"reward_amount": amount}},
            upsert=True
        )

    async def get_dbroadcast_latency(self) -> int:
        doc = await self.user_data.find_one({"_id": "global_dbroadcast_config"})
        return doc.get("latency_seconds", 0) if doc else 0

    async def set_dbroadcast_latency(self, seconds: int):
        await self.user_data.update_one(
            {"_id": "global_dbroadcast_config"},
            {"$set": {"latency_seconds": seconds}},
            upsert=True
        )

    # ✅ USER FUNCTIONS

    async def present_user(self, user_id: int) -> bool:
        found = await self.user_data.find_one({'_id': user_id})
        return bool(found)

    async def add_user(self, user_id: int, ban: bool = False):
        await self.user_data.insert_one({'_id': user_id, 'ban': ban})

    async def full_userbase(self) -> list[int]:
        cursor = self.user_data.find()
        return [doc['_id'] async for doc in cursor]

    async def del_user(self, user_id: int):
        await self.user_data.delete_one({'_id': user_id})

    async def ban_user(self, user_id: int):
        await self.user_data.update_one({'_id': user_id}, {'$set': {'ban': True}})

    async def unban_user(self, user_id: int):
        await self.user_data.update_one({'_id': user_id}, {'$set': {'ban': False}})

    async def is_banned(self, user_id: int) -> bool:
        user = await self.user_data.find_one({'_id': user_id})
        return user.get('ban', False) if user else False

    # ✅ FSUB CHANNELS FUNCTIONS

    async def set_fsub_channels(self, fsub_data: dict):
        await self.user_data.update_one(
            {"_id": "fsub_channels"},
            {"$set": {"channels": fsub_data}},
            upsert=True
        )

    async def get_fsub_channels(self) -> dict:
        data = await self.user_data.find_one({"_id": "fsub_channels"})
        return data.get("channels", {}) if data else {}

    async def add_fsub_channel(self, channel_id: int, channel_data: list):
        current_data = await self.get_fsub_channels()
        current_data[str(channel_id)] = channel_data
        await self.set_fsub_channels(current_data)

    async def remove_fsub_channel(self, channel_id: int):
        current_data = await self.get_fsub_channels()
        current_data.pop(str(channel_id), None)
        await self.set_fsub_channels(current_data)

    # ✅ UPGRADED MULTI-SHORTNER SETTINGS PERSISTENCE

    async def set_shortner_settings(self, shortner_data: dict):
        await self.user_data.update_one(
            {"_id": "shortner_settings"},
            {"$set": {"settings": shortner_data}},
            upsert=True
        )

    async def get_shortner_settings(self) -> dict:
        data = await self.user_data.find_one({"_id": "shortner_settings"})
        return data.get("settings", {}) if data else {}

    async def update_shortner_setting(self, key: str, value: str):
        current_data = await self.get_shortner_settings()
        current_data[key] = value
        await self.set_shortner_settings(current_data)

    async def get_shortner_status(self) -> bool:
        settings = await self.get_shortner_settings()
        return settings.get('enabled', True)  

    async def set_shortner_status(self, enabled: bool):
        await self.update_shortner_setting('enabled', enabled)

    async def get_specific_shortner(self, num: int) -> dict:
        data = await self.user_data.find_one({"_id": f"shortner_node_{num}"})
        return data.get("data", {}) if data else {}

    async def save_specific_shortner(self, num: int, short_data: dict):
        await self.user_data.update_one(
            {"_id": f"shortner_node_{num}"},
            {"$set": {"data": short_data}},
            upsert=True
        )

    # ✅ FSUB STATUS COLLECTION FUNCTIONS

    async def update_fsub_status(self, user_id: int, channel_id: int, status: str):
        await self.fsub_status.update_one(
            {"user_id": user_id, "channel_id": channel_id},
            {"$set": {"status": status, "last_updated": datetime.now()}},
            upsert=True
        )

    async def get_fsub_status(self, user_id: int, channel_id: int) -> str:
        doc = await self.fsub_status.find_one({"user_id": user_id, "channel_id": channel_id})
        return doc.get("status") if doc else None

    async def remove_fsub_status(self, user_id: int, channel_id: int):
        await self.fsub_status.delete_one({"user_id": user_id, "channel_id": channel_id})

    async def get_user_fsub_statuses(self, user_id: int) -> dict:
        cursor = self.fsub_status.find({"user_id": user_id})
        statuses = {}
        async for doc in cursor:
            statuses[doc["channel_id"]] = doc["status"]
        return statuses

    async def clear_expired_fsub_statuses(self, days: int = 7):
        cutoff_date = datetime.now() - timedelta(days=days)
        await self.fsub_status.delete_many({"last_updated": {"$lt": cutoff_date}})

    # ✅ REQUEST SUB COLLECTION FUNCTIONS

    async def add_join_request(self, user_id: int, channel_id: int, request_id: int = None):
        await self.request_sub.update_one(
            {"user_id": user_id, "channel_id": channel_id},
            {"$set": {
                "request_id": request_id,
                "status": "pending",
                "submitted_at": datetime.now(),
                "last_updated": datetime.now()
            }},
            upsert=True
        )

    async def update_join_request_status(self, user_id: int, channel_id: int, status: str):
        await self.request_sub.update_one(
            {"user_id": user_id, "channel_id": channel_id},
            {"$set": {"status": status, "last_updated": datetime.now()}}
        )

    async def get_join_request_status(self, user_id: int, channel_id: int) -> str:
        doc = await self.request_sub.find_one({"user_id": user_id, "channel_id": channel_id})
        return doc.get("status") if doc else None

    async def has_submitted_join_request(self, user_id: int, channel_id: int) -> bool:
        doc = await self.request_sub.find_one({"user_id": user_id, "channel_id": channel_id})
        return doc is not None

    async def remove_join_request(self, user_id: int, channel_id: int):
        await self.request_sub.delete_one({"user_id": user_id, "channel_id": channel_id})

    async def get_pending_requests_for_channel(self, channel_id: int) -> list:
        cursor = self.request_sub.find({"channel_id": channel_id, "status": "pending"})
        requests = []
        async for doc in cursor:
            requests.append({
                "user_id": doc["user_id"],
                "request_id": doc.get("request_id"),
                "submitted_at": doc["submitted_at"]
            })
        return requests

    async def clear_old_join_requests(self, days: int = 30):
        cutoff_date = datetime.now() - timedelta(days=days)
        await self.request_sub.delete_many({"submitted_at": {"$lt": cutoff_date}})

    async def cleanup_database(self):
        try:
            await self.clear_expired_fsub_statuses(7)
            await self.clear_old_join_requests(30)
            await self.cleanup_orphaned_records()
            return True
        except Exception as e:
            print(f"Database cleanup error: {e}")
            return False

    async def cleanup_orphaned_records(self):
        try:
            users = await self.full_userbase()
            async for doc in self.fsub_status.find({"user_id": {"$nin": users}}):
                await self.fsub_status.delete_one({"_id": doc["_id"]})
            async for doc in self.request_sub.find({"user_id": {"$nin": users}}):
                await self.request_sub.delete_one({"_id": doc["_id"]})
            return True
        except Exception as e:
            print(f"Error cleaning orphaned records: {e}")
            return False

    async def get_comprehensive_fsub_statistics(self):
        try:
            fsub_count = await self.fsub_status.count_documents({})
            request_count = await self.request_sub.count_documents({})
            pending_requests = await self.request_sub.count_documents({"status": "pending"})
            approved_requests = await self.request_sub.count_documents({"status": "approved"})
            rejected_requests = await self.request_sub.count_documents({"status": "rejected"})
            
            status_breakdown = {}
            async for doc in self.fsub_status.aggregate([
                {"$group": {"_id": "$status", "count": {"$sum": 1}}}
            ]):
                status_breakdown[doc["_id"]] = doc["count"]
            
            channel_stats = {}
            async for doc in self.fsub_status.aggregate([
                {"$group": {"_id": "$channel_id", "count": {"$sum": 1}}}
            ]):
                channel_stats[doc["_id"]] = doc["count"]
            
            yesterday = datetime.now() - timedelta(days=1)
            recent_fsub_updates = await self.fsub_status.count_documents({"last_updated": {"$gte": yesterday}})
            recent_requests = await self.request_sub.count_documents({"submitted_at": {"$gte": yesterday}})
            
            return {
                "total_fsub_records": fsub_count,
                "total_join_requests": request_count,
                "pending_requests": pending_requests,
                "approved_requests": approved_requests,
                "rejected_requests": rejected_requests,
                "status_breakdown": status_breakdown,
                "channel_statistics": channel_stats,
                "recent_activity": {
                    "fsub_updates_24h": recent_fsub_updates,
                    "join_requests_24h": recent_requests
                }
            }
        except Exception as e:
            print(f"Error getting comprehensive fsub statistics: {e}")
            return {}
        
# ============================================================
# ADD THESE FUNCTIONS TO YOUR helper/database.py FILE
# Add them after the existing fsub channel functions
# ============================================================

    # ✅ DB CHANNELS FUNCTIONS (ADD THESE TO database.py)

    async def get_db_channels(self) -> dict:
        data = await self.user_data.find_one({"_id": "db_channels"})
        return data.get("channels", {}) if data else {}

    async def add_db_channel(self, channel_id: int, channel_data: dict):
        current_data = await self.get_db_channels()
        current_data[str(channel_id)] = channel_data
        await self.user_data.update_one(
            {"_id": "db_channels"},
            {"$set": {"channels": current_data}},
            upsert=True
        )

    async def remove_db_channel(self, channel_id: int):
        current_data = await self.get_db_channels()
        current_data.pop(str(channel_id), None)
        await self.user_data.update_one(
            {"_id": "db_channels"},
            {"$set": {"channels": current_data}},
            upsert=True
        )

    async def set_primary_db_channel(self, channel_id: int):
        current_data = await self.get_db_channels()
        # Reset all primaries
        for ch_id_str in current_data:
            current_data[ch_id_str]['is_primary'] = False
        # Set new primary
        if str(channel_id) in current_data:
            current_data[str(channel_id)]['is_primary'] = True
        await self.user_data.update_one(
            {"_id": "db_channels"},
            {"$set": {"channels": current_data}},
            upsert=True
        )
        
