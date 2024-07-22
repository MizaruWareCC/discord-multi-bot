import json
import aiohttp
import asyncio
from asyncio import sleep
from typing import Optional
from .utils import get_cookie
import traceback

class NotOnline(Exception):
    pass

class RobloxPlayerFinder:
    def __init__(self, discord_id: int, place_id: int | None, limit: Optional[int]=9999999999999999999999999999):
        self.place_id = place_id
        self._discord_id = discord_id
        self._current_server = None
        self._current_server_index = None
        self._found = False
        self.limit = limit
        self._li = {}

    def add_listener(self) -> any:
        def decorator(func):
            self._li[func.__name__] = func
            return func
        return decorator

    async def dispatch_event(self, event_name, *args, **kwargs) -> None:
        if event_name in self._li:
            await self._li[event_name](*args, **kwargs)

    async def _get_user_id(self, name: str) -> int | None:
        request_body = {'usernames': [name]}
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        async with aiohttp.ClientSession() as session:
            async with session.post('https://users.roblox.com/v1/usernames/users', headers=headers, json=request_body) as response:
                user_data = await response.json()
                if len(user_data['data']) > 0:
                    return user_data['data'][0]['id']
                else:
                    return None

    async def _token_array_to_request_array(self, token_array: list[str]) -> list[dict[str, str]]:
        request_arrays = []
        for token in token_array:
            request = {'requestId': f"0:{token}:AvatarHeadshot:48x48:png:regular",
                       'type': "AvatarHeadShot",
                       'targetId': 0,
                       'format': "png",
                       'size': "48x48",
                       'token': token}
            request_arrays.append(request)
        return request_arrays

    async def _player_finder(self, tokens: list[dict[str, str]], img: str) -> bool:
        json_body = await self._token_array_to_request_array(tokens)
        async with aiohttp.ClientSession() as session:
            async with session.post('https://thumbnails.roblox.com/v1/batch', json=json_body) as response:
                root_data = await response.json()
                for plr in root_data['data']:
                    if plr['imageUrl'] == img:
                        return True
                return False

    async def _is_online(self, id: int) -> bool:
        async with aiohttp.ClientSession() as session:
            async with session.post('https://presence.roblox.com/v1/presence/users', json={"userIds": [id]}) as response:
                data = await response.json()
                res = data.get('userPresences')[0]['userPresenceType']
                return res == 2

    @property
    def current_server(self):
        return self._current_server

    @property
    def current_server_index(self):
        return self._current_server_index

    @property
    def found(self):
        return self._found

    @property
    def discord_id(self):
        return self._discord_id

    async def find_player(self, name: str) -> bool | None:
        await self.dispatch_event('on_find_start', name)
        user_id = await self._get_user_id(name)
        if user_id is None:
            self._found = False
            await self.dispatch_event('on_error', 'invaliduser')
            raise ValueError('Invalid ID')

        if not await self._is_online(user_id):
            await self.dispatch_event('on_error', 'notonline')
            raise NotOnline('')
        
        cookie = await get_cookie(self.discord_id)
        if self.place_id is None:
            if cookie:
                game = await player_game(user_id, self.discord_id)
                if game['placeId'] is not None:
                    await self.dispatch_event('on_player_find', None, 0, game['gameId'])
                    return game['jobId']


            else:
                await self.dispatch_event('on_error', 'notfriends')
                return
            
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://thumbnails.roblox.com/v1/users/avatar-headshot?size=48x48&format=png&userIds={user_id}') as our_avatar:
                avatar_data = await our_avatar.json()
                avatar = avatar_data['data'][0]
                img = avatar['imageUrl']

        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://games.roblox.com/v1/games/{self.place_id}/servers/public?limit=100') as places_response:
                places_data = await places_response.json()
                if 'errors' in places_data:
                    await self.dispatch_event('on_error', error='invalidplace')
                    raise ValueError('Invalid ID')

                self._current_server_index = 0

                for server_index, server in enumerate(places_data['data']):
                    self._current_server_index += 1
                    self._current_server = server
                    if self.limit:
                        if self.limit < self.current_server_index:
                            await self.dispatch_event('on_find_failure', name)
                            return False

                    await self.dispatch_event('on_server_change', server, self.current_server_index)

                    tokens = server['playerTokens']
                    if await self._player_finder(tokens, img):
                        self._found = True
                        await self.dispatch_event('on_player_find', server, self._current_server_index, server['id'])
                        return True

                await self.dispatch_event('on_find_failure', name)
                return False



async def player_status(id: int):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post('https://presence.roblox.com/v1/presence/users', json={"userIds": [id]}) as response:
                data = await response.json()
                res = data.get('userPresences')[0]['userPresenceType']
                return res
    except Exception as e:
        return 'err'


async def player_game(id, discord_id: int) -> dict[str, any]:  
    cookie = await get_cookie(discord_id)
    if not cookie:
        return {}
    try:
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Cookie': cookie}
        async with aiohttp.ClientSession() as session:
            async with session.post('https://presence.roblox.com/v1/presence/users', json={"userIds": [id]}, headers=headers) as response:
                data = await response.json()
                res = data.get('userPresences')[0]
                return res
    except Exception as e:
        traceback.print_exc()
        return 'err'


async def listen(name):
    online = False
    while not online:
        online = await is_online(name)
        await sleep(10)


async def player_data(id):
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://users.roblox.com/v1/users/{id}') as response:
            data = await response.json()
            return data

async def player_avatar(id):
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://thumbnails.roblox.com/v1/users/avatar-headshot?size=720x720&format=png&isCircular=true&userIds={id}') as response:
            data = await response.json()
            return data['data'][0]['imageUrl']

async def is_online(name):
    return await player_status(await get_user_id(name))

async def is_valid(name):
    return bool(await get_user_id(name))

async def get_user_id(name):
    request_body = {'usernames': [name]}
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    async with aiohttp.ClientSession() as session:
        async with session.post('https://users.roblox.com/v1/usernames/users', headers=headers, json=request_body) as response:
            user_data = await response.json()
            if len(user_data['data']) > 0:
                return user_data['data'][0]['id']
            else:
                return None


async def listen(name):
    online = False
    while not online:
        online = await is_online(name)
        await sleep(10)
