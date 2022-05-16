from typing import List, Optional

from loguru import logger
from rlbot.messages.flat.GameTickPacket import GameTickPacket as FBGameTickPacket
from rlbot.messages.flat.PlayerInfo import PlayerInfo as FBPlayerInfo
from rlbot.messages.flat.PlayerInputChange import (
    PlayerInputChange as FBPlayerInputChange,
)
from rlbot.messages.flat.PlayerSpectate import PlayerSpectate
from rlbot.socket.socket_manager_asyncio import SocketRelayAsyncio

from messages.game_state import GameState, PlayerInfo
from messages.spectate import Spectate
from server.message import Message


class SocketRelayEventHandlers:
    """
    Handles RLBot messages (such as game tick packets or player spectate),
    and generates messages to be sent.

    Idea is to hold game state here and queues of messages to be delivered.
    """

    def __init__(self) -> None:
        self.hooked_handlers = False

        self.packet: Optional[FBGameTickPacket] = None
        self.spectated_player: Optional[Spectate] = None

    def handle_spectate(self, spectate: PlayerSpectate, seconds: float, frame_num: int):
        player_index = spectate.PlayerIndex()
        if player_index == -1:
            # This is the documented behaviour, but never seems to happen.
            logger.info("Spectating player changed: No player")
            self.spectated_player = Spectate(
                player_index=None,
                player=None,
            )
        else:
            if self.packet:
                self.spectated_player = Spectate(
                    player_index=player_index,
                    player=PlayerInfo.from_flatbuffers(
                        self.packet.Players(player_index)
                    ),
                )
                logger.info(
                    f"Spectating player changed: ({self.packet.Players(player_index).Name()} "
                    "(index {player_index})"
                )
            else:
                logger.warning(
                    "Spectating player changed: Unknown player as we have no packets."
                )

    def handle_player_input_change(
        self, change: FBPlayerInputChange, seconds: float, frame_num: int
    ):
        raise NotImplementedError

    def handle_packet(self, packet: FBGameTickPacket):
        players = []
        for i in range(packet.PlayersLength()):
            p = packet.Players(i)
            players.append({"name": p.Name().decode("utf-8")})
        # logger.debug(f"Handling packet with players {players}")
        # asyncio.get_event_loop().create_task(
        #     self.socketio_server.emit("packet", {"data": players})
        # )
        # game_state = GameState.create_from_gametickpacket(packet)
        self.packet = packet

    def hook_handlers(self, socket_relay: SocketRelayAsyncio):
        if self.hooked_handlers:
            logger.warning(
                "Attempting to hook socket relay handlers when already hooked. Skipping..."
            )
            return

        # Do not hook unimplemented handlers
        socket_relay.player_spectate_handlers.append(self.handle_spectate)
        # socket_relay.player_input_change_handlers.append(self.input_change)
        socket_relay.packet_handlers.append(self.handle_packet)

        logger.info("Hooked socket relay handlers.")

    def generate_messages(self) -> List[Message]:
        messages: List[Message] = []
        if self.packet is not None:
            messages.append(
                Message(
                    event="packet", data=GameState.from_packet(self.packet).to_dict()
                )
            )
        if self.spectated_player is not None:
            # Send spectate message and set to None to avoid sending again
            messages.append(
                Message(event="spectate", data=self.spectated_player.to_dict())
            )
            self.spectated_player = None
        return messages
