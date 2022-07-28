from dataclasses import dataclass, field
import strawberry
from strawberry.schema.config import StrawberryConfig
import typing
from typing import Optional, NewType

# Custom scalars
from pydantic import NonNegativeInt
nonNegativeInt = strawberry.scalar(
    NewType("NonNegativeInt", NonNegativeInt),
    serialize=lambda x:x,
    parse_value=lambda x:int(x),
)

# Not really important schema
@strawberry.type
class Reviewer:
    reviewer:bool = False

@strawberry.type
class gameVersion:
    appVer:str = "11.45.14"

@strawberry.type
class Noter:
    username:str = "not_init"

# Main
@strawberry.type
class User:
    _id:str = "not_init"
    username:str = "not_init"
    token:str = "not_init"
    coin:int = -1
    diamond:int = -1
    PPTime:str = "1643673600000"
    RThisMonth:int = -1
    access:Reviewer = Reviewer()

@strawberry.type
class Chart:
    _id:str = "not_init"
    difficultyClass:int = 0 # Can't be -1 or game will raise error
    difficultyValue:int = -1

@dataclass
@strawberry.type
class Set:
    _id:str = field(default_factory=lambda :"not_init")
    musicTitle:str = field(default_factory=lambda :"not_init")
    introduction:str = field(default_factory=lambda :"not_init")
    coinPrice:int = field(default_factory=lambda :0)
    isGot:bool = field(default_factory=lambda :False)
    isRanked:bool = field(default_factory=lambda :False)
    composerName:str = field(default_factory=lambda :"not_init")
    playCount:int = field(default_factory=lambda :0)
    chart:typing.List[Chart] = field(default_factory=lambda :[Chart()])
    noter:Noter = Noter()


# Not really important schema again
@dataclass
@strawberry.type
class Self:
    gotSet:typing.List[Set] = field(default_factory=lambda :[Set()])