# from redis.asyncio import Redis


# class RedisSessionManager:
#     """
#     使用redis管理语音面试的会话
#     """

#     def __init__(self, redis_client: Redis):
#         self.redis_client = redis_client
#         self.session_expire_time = 7200  # 2小时

#     def get_session(self, session_id: str):
#         return self.redis_client.get(session_id)

#     def create_session(self, session_id: str):
#         pass
