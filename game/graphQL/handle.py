from typing import List
from .schema import *
from strawberry.types import Info

import auth, store, score

@strawberry.type
class Query:
    @strawberry.field
    # {'query': 'query fetchSets($lim:NonNegativeInt $skip:NonNegativeInt $searchTitle:String $orderPlay:Int $orderTime:Int $hidden:Int $official:Int $ranked:Int){r:set(playCountOrder:$orderPlay publishTimeOrder:$orderTime limit:$lim skip:$skip isHidden:$hidden musicTitle:$searchTitle isOfficial:$official isRanked:$ranked){_id introduction coinPrice isGot isRanked noter{username}musicTitle composerName playCount chart{_id difficultyClass difficultyValue}}}
    # Discription: 主商店
    async def set(self, 
            playCountOrder: Optional[int],
            publishTimeOrder: Optional[int],
            limit: Optional[nonNegativeInt],
            skip: Optional[nonNegativeInt],
            isHidden: Optional[int],
            musicTitle: Optional[str],
            isOfficial: Optional[int],
            isRanked: Optional[int],
            info: Info) -> typing.List[Set]:
        #auth.security_manager.user_token_checker(info.context)
        rev_date = True if playCountOrder == -1 else False
        ranked = True if isRanked == 1 or isOfficial == 1 else False 
        unranked = True if isRanked == -1 else False 
        doc = await store.get_store_set(skip,limit,ranked=ranked,unranked=unranked,rev_date=rev_date,search=musicTitle)
        result = [
            Set(
                _id = c["_id"],
                musicTitle = c["musicTitle"],
                introduction = c["introduction"],
                coinPrice = 0,
                isGot = True,
                isRanked = False,
                composerName = c["composerName"],
                playCount = 0,
                chart = [
                    Chart(_id=i["_id"],difficultyClass=i["difficultyClass"],difficultyValue=i["difficultyValue"])
                    for i in c["chart"]
                ],
                noter = Noter(username=c["noter"]["userName"])
            )
            for c in doc
        ]
        return result

    @strawberry.field
    # {'query': 'query{r:self{gotSet{_id introduction coinPrice isGot isRanked noter{username}musicTitle composerName playCount chart{_id difficultyClass difficultyValue}}}}'}
    # Discription: 个人已有谱面，目前作为下载本地谱面通道
    async def self(self, info: Info) -> Self:
        result = Self(gotSet=[])
        try:
            user_id = auth.security_manager.user_token_checker(info.context, return_id=True)
        except Exception as e:
            return result

        local_chart = await store.get_local_set(user_id)
        if local_chart == None:
            return result
        for c in local_chart:
            result.gotSet.append(
                Set(
                    _id = c["_id"],
                    musicTitle = c["musicTitle"],
                    introduction = c["introduction"],
                    coinPrice = 0,
                    isGot = True,
                    isRanked = False,
                    composerName = c["composerName"],
                    playCount = 0,
                    chart = [
                        Chart(_id=i["_id"],difficultyClass=i["difficultyClass"],difficultyValue=i["difficultyValue"])
                        for i in c["chart"]
                    ],
                    noter = Noter(username=c["noter"]["userName"])
                )
            )
        return result
    
    @strawberry.field
    # {'query': 'query singleSet($id:String){r:setById(_id:$id){_id introduction coinPrice noter{username}musicTitle composerName chart{difficultyClass difficultyValue _id}isGot isRanked}}', 'variables': {'id': ''}}
    # Discription: 下载谱面时会请求
    async def setById(self, 
            _id: Optional[str],
            info: Info) -> Set:
        user_id = auth.security_manager.user_token_checker(info.context, return_id=True)
        print(user_id)

        if _id[2:7] == "local" and _id[0] == "0":
            local_chart = await store.get_local_set(user_id)
            for c in local_chart:
                if _id == c["_id"]:
                    return Set(
                        _id = c["_id"],
                        musicTitle = c["musicTitle"],
                        introduction = c["introduction"],
                        coinPrice = 0,
                        isGot = True,
                        isRanked = False,
                        composerName = c["composerName"],
                        playCount = 0,
                        chart = [
                            Chart(_id=i["_id"],difficultyClass=i["difficultyClass"],difficultyValue=i["difficultyValue"])
                            for i in c["chart"]
                        ],
                        noter = Noter(username=c["noter"]["userName"])
                    )
        else:
            c = await store.get_set_chart(_id)
            return Set(
                _id = c["_id"],
                musicTitle = c["musicTitle"],
                introduction = c["introduction"],
                coinPrice = 0,
                isGot = True,
                isRanked = c["isRanked"],
                composerName = c["composerName"],
                playCount = 0,
                chart = [
                    Chart(_id=i["_id"],difficultyClass=i["difficultyClass"],difficultyValue=i["difficultyValue"])
                    for i in c["chart"]
                ],
                noter = Noter(username=c["noter"]["userName"])
            ) if c != [] else Set()

    @strawberry.field
    # {'query': '{r:gameSetting{appVer}}'}
    # Discription: 会在打开本地谱面列表时请求
    async def gameSetting(self) -> gameVersion:
        return gameVersion

    @strawberry.field
    # Discription: Should be called as mutation
    async def loginUser(self, 
            username: Optional[str], 
            password: Optional[str]) -> User:
        return User

    @strawberry.field
    # {'query': 'mutation ap($bleed:Boolean $alive:Boolean $mirror:Boolean $s:Int $p:Int $g:Int $m:Int $rd: String)
    # {r:submitAfterPlay(randomId: $rd,playRecord:{mod:{narrow:1.0,speed:1.0,isBleed:$bleed,isMirror:$mirror} 
    # isAlive:$alive score:$s perfect:$p good:$g miss:$m}){coin RThisMonth diamond ranking{isPlayRankUpdated playRank{rank}}}}', 
    # 'variables': {'s': , 'p': , 'g': , 'm': , 'bleed': False, 'mirror': False, 'alive': True, 'rd': ''}}
    # Discription: Should be called as mutation
    async def submitAfterPlay(self,
            randomId: Optional[str]
            ) -> AfterPlay:
        return AfterPlay()



@strawberry.type
class Mutation:
    @strawberry.field
    # {'query': 'mutation login ($un: String, $pw: String) { r: loginUser (username: $un, password: $pw) { _id, username, token, coin, diamond, PPTime, RThisMonth, access { reviewer } } }', 'variables': {'un': '', 'pw': ''}}
    # Discription: 游戏登录时请求
    async def loginUser(self, 
            username: Optional[str], 
            password: Optional[str]) -> User:
        return await auth.login(username, password, User())

    @strawberry.field
    # {'query': 'mutation bp($cid:String,$pp:Int){r:submitBeforePlay(chartId:$cid,PPCost:$pp,eventArgs:""){PPTime playingRecord { randomId } }}', 'variables': {'cid': '', 'pp': 0}}
    # Discription: 开始游玩前请求
    async def submitBeforePlay(self, info: Info,
            chartId: Optional[str],
            PPCost: Optional[int],
            eventArgs: Optional[str]) -> PlayToken:
        user_id = auth.security_manager.user_token_checker(info.context, return_id=True)
        s_token = auth.security_manager.token_generator(user_id+chartId)
        auth.security_manager.store_score_token(user_id,s_token,chartId)
        return PlayToken(playingRecord=RdRecord(randomId=s_token))

    @strawberry.field
    # {'query': 'mutation ap($bleed:Boolean $alive:Boolean $mirror:Boolean $s:Int $p:Int $g:Int $m:Int $rd: String){r:submitAfterPlay(randomId: $rd,playRecord:{mod:{narrow:1.0,speed:1.0,isBleed:$bleed,isMirror:$mirror} isAlive:$alive score:$s perfect:$p good:$g miss:$m}){coin RThisMonth diamond ranking{isPlayRankUpdated playRank{rank}}}}', 'variables': {'s': , 'p': , 'g': , 'm': , 'bleed': False, 'mirror': False, 'alive': True, 'rd': ''}}
    # Discription: 游玩结束后请求
    async def submitAfterPlay(self, info: Info,
            randomId: Optional[str],
            playRecord: PlayRecord
            ) -> AfterPlay:
        user_id = auth.security_manager.user_token_checker(info.context, return_id=True)
        cid = auth.security_manager.score_token_checker(user_id, randomId)
        return await score.update_score(user_id,cid,playRecord,AfterPlay())
