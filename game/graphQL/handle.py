
from typing import List
from .schema import *
from auth import *
from strawberry.types import Info

@strawberry.type
class Query:
    @strawberry.field
    # {'query': '{r:gameSetting{appVer}}'}
    def gameSetting(self) -> gameVersion:
        return gameVersion

    @strawberry.field
    # Should be called as mutation
    def loginUser(self, 
            username: Optional[str], 
            password: Optional[str]) -> User:
        return User

    @strawberry.field
    # {'query': 'query fetchSets($lim:NonNegativeInt $skip:NonNegativeInt $searchTitle:String $orderPlay:Int $orderTime:Int $hidden:Int $official:Int $ranked:Int){r:set(playCountOrder:$orderPlay publishTimeOrder:$orderTime limit:$lim skip:$skip isHidden:$hidden musicTitle:$searchTitle isOfficial:$official isRanked:$ranked){_id introduction coinPrice isGot isRanked noter{username}musicTitle composerName playCount chart{_id difficultyClass difficultyValue}}}
    def set(self, 
            playCountOrder: Optional[int],
            publishTimeOrder: Optional[int],
            limit: Optional[nonNegativeInt],
            skip: Optional[nonNegativeInt],
            isHidden: Optional[int],
            musicTitle: Optional[str],
            isOfficial: Optional[int],
            isRanked: Optional[int],
            info: Info) -> typing.List[Set]:
        #security_manager.user_token_checker(info.context)
        return [Set(),Set(),Set(),Set(),Set(),Set(),Set(),Set(),Set()]


    @strawberry.field
    # {'query': 'query{r:self{gotSet{_id introduction coinPrice isGot isRanked noter{username}musicTitle composerName playCount chart{_id difficultyClass difficultyValue}}}}'}
    def self(self, info: Info) -> Self:
        #security_manager.user_token_checker(info.context)
        return Self()

@strawberry.type
class Mutation:
    @strawberry.field
    # {'query': 'mutation login ($un: String, $pw: String) { r: loginUser (username: $un, password: $pw) { _id, username, token, coin, diamond, PPTime, RThisMonth, access { reviewer } } }', 'variables': {'un': '', 'pw': ''}}
    async def loginUser(self, 
            username: Optional[str], 
            password: Optional[str]) -> User:
        return await login(username, password, User())


