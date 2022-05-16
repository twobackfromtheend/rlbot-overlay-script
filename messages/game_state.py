from dataclasses import asdict, dataclass
from typing import Optional

from rlbot.messages.flat.BallInfo import BallInfo as FBBallInfo
from rlbot.messages.flat.GameInfo import GameInfo as FBGameInfo
from rlbot.messages.flat.GameTickPacket import GameTickPacket as FBGameTickPacket
from rlbot.messages.flat.PlayerInfo import PlayerInfo as FBPlayerInfo
from rlbot.messages.flat.ScoreInfo import ScoreInfo as FBScoreInfo
from rlbot.messages.flat.TeamInfo import TeamInfo as FBTeamInfo
from rlbot.messages.flat.Touch import Touch as FBTouch
from rlbot.messages.flat.Vector3 import Vector3 as FBVector3

from .utils import dict_factory


@dataclass
class Vector3:
    x: float
    y: float
    z: float

    @classmethod
    def from_flatbuffers(cls, vector_3: FBVector3):
        return cls(
            x=vector_3.X(),
            y=vector_3.Y(),
            z=vector_3.Z(),
        )


@dataclass
class Touch:
    player_name: str
    time_seconds: float
    hit_location: Vector3
    # hit_normal: Vector3
    team: int
    player_index: int

    @classmethod
    def from_flatbuffers(cls, touch: FBTouch):
        return cls(
            player_name=touch.PlayerName().decode("utf-8"),
            time_seconds=touch.GameSeconds(),
            hit_location=Vector3.from_flatbuffers(touch.Location()),
            team=touch.Team(),
            player_index=touch.PlayerIndex(),
        )


@dataclass
class BallInfo:
    location: Vector3
    latest_touch: Optional[Touch]

    @classmethod
    def from_flatbuffers(cls, ball: FBBallInfo):
        touch = ball.LatestTouch()
        return cls(
            location=Vector3.from_flatbuffers(ball.Physics().Location()),
            latest_touch=Touch.from_flatbuffers(touch) if touch is not None else None,
        )


@dataclass
class ScoreInfo:
    score: int
    goals: int
    own_goals: int
    assists: int
    saves: int
    shots: int
    demolitions: int

    @classmethod
    def from_flatbuffers(cls, score: FBScoreInfo):
        return cls(
            score=score.Score(),
            goals=score.Goals(),
            own_goals=score.OwnGoals(),
            assists=score.Assists(),
            saves=score.Saves(),
            shots=score.Shots(),
            demolitions=score.Demolitions(),
        )


@dataclass
class PlayerInfo:
    location: Vector3
    is_demolished: bool
    # True if your wheels are on the ground, the wall, or the ceiling. False if you're midair or turtling.
    has_wheel_contact: bool
    is_supersonic: bool
    is_bot: bool
    # True if the player has jumped. Falling off the ceiling / driving off the goal post does not count.
    # jumped: bool
    # True if player has double jumped. False does not mean you have a jump remaining, because the
    # aerial timer can run out, and that doesn't affect this flag.
    # double_jumped: bool
    name: str
    team: int
    boost: int
    score_info: ScoreInfo

    @classmethod
    def from_flatbuffers(cls, player: FBPlayerInfo):
        return cls(
            location=Vector3.from_flatbuffers(player.Physics().Location()),
            is_demolished=bool(player.IsDemolished()),
            has_wheel_contact=bool(player.HasWheelContact()),  # Can return 0
            is_supersonic=bool(player.IsSupersonic()),
            is_bot=bool(player.IsBot()),
            name=player.Name().decode("utf8"),
            team=player.Team(),
            boost=player.Boost(),
            score_info=ScoreInfo.from_flatbuffers(player.ScoreInfo()),
        )


@dataclass
class GameInfo:
    seconds_elapsed: float
    game_time_remaining: float
    is_overtime: float
    is_unlimited_time: bool
    # True when cars are allowed to move, and during the pause menu. False during replays.
    is_round_active: bool
    # Only false during a kickoff, when the car is allowed to move, and the ball has not been hit,
    # and the game clock has not started yet. If both players sit still, game clock will eventually
    # start and this will become true.
    is_kickoff_pause: bool
    # Turns true after final replay, the moment the 'winner' screen appears. Remains true during next match
    # countdown. Turns false again the moment the 'choose team' screen appears.
    is_match_ended: bool
    # Number of physics frames which have elapsed in the game.
    # May increase by more than one across consecutive packets.
    frame_num: int

    @classmethod
    def from_flatbuffers(cls, game: FBGameInfo):
        return cls(
            seconds_elapsed=game.SecondsElapsed(),
            game_time_remaining=game.GameTimeRemaining(),
            is_overtime=bool(game.IsOvertime()),
            is_unlimited_time=bool(game.IsUnlimitedTime()),
            is_round_active=bool(game.IsRoundActive()),
            is_kickoff_pause=bool(game.IsKickoffPause()),
            is_match_ended=bool(game.IsMatchEnded()),
            frame_num=game.FrameNum(),
        )


@dataclass
class TeamInfo:
    team_index: int
    score: int

    @classmethod
    def from_flatbuffers(cls, team: FBTeamInfo):
        return cls(
            team_index=team.TeamIndex(),
            score=team.Score(),
        )


@dataclass
class GameState:
    game_cars: "list[PlayerInfo]"
    game_ball: BallInfo
    game_info: GameInfo
    teams: TeamInfo

    def to_dict(self):
        return asdict(self, dict_factory=dict_factory)

    @classmethod
    def from_packet(cls, packet: FBGameTickPacket) -> "GameState":
        return cls(
            game_cars=[
                PlayerInfo.from_flatbuffers(packet.Players(i))
                for i in range(packet.PlayersLength())
            ],
            game_ball=BallInfo.from_flatbuffers(packet.Ball()),
            game_info=GameInfo.from_flatbuffers(packet.GameInfo()),
            teams=[
                TeamInfo.from_flatbuffers(packet.Teams(i))
                for i in range(packet.TeamsLength())
            ],
        )
