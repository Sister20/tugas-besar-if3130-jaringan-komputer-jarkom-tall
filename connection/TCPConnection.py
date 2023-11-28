import socket
import struct

from typing import List

import Config as Config
from threading import Thread
from utils.Terminal import Terminal
from message.MessageInfo import MessageInfo
from message.Segment import Segment
from message.SegmentFlag import SegmentFlag
from connection.Connection import Connection
from connection.OncomingConnection import OncomingConnection
from random import randint
import math
from file.FileMark import FileMark
from message.MessageQuery import MessageQuery

class TCPConnection(Connection):
    def __init__(self, ip: str, port: int, handler: callable = None) -> None:
        super().__init__(ip, port, handler)

    def requestHandshake(self, ip_remote: str, port_remote: int) -> OncomingConnection:
        seq_num = randint(0, 4294967295)

        remote_address = (ip_remote, port_remote)
        Terminal.log("Initiating three way handshake", Terminal.ALERT_SYMBOL)
        retries = Config.SEND_RETRIES
        while retries > 0:
            try:
                Terminal.log(f"Sending SYN request to {ip_remote}:{port_remote}", Terminal.ALERT_SYMBOL,
                            "Handshake NUM=" + str(seq_num))
                self.socket.sendto(Segment.syn(seq_num).pack(), remote_address)

                Terminal.log("Waiting for response...", Terminal.ALERT_SYMBOL, "Handshake")
                if(ip_remote == "<broadcast>"):
                    message = self.listen(MessageQuery(
                        flags = SegmentFlag.FLAG_SYN | SegmentFlag.FLAG_ACK
                    ), Config.HANDSHAKE_TIMEOUT)
                else:
                    message = self.listen(MessageQuery(
                        ip = remote_address[0],
                        port = remote_address[1],
                        flags = SegmentFlag.FLAG_SYN | SegmentFlag.FLAG_ACK
                    ), Config.HANDSHAKE_TIMEOUT)

                data = message.segment

                Terminal.log(f"Accepted SYN-ACK from {message.ip}:{message.port}",
                            Terminal.ALERT_SYMBOL, "Handshake NUM=" + str(data.ack_num))

                ack_num = data.seq_num + 1
                seq_num = seq_num + 1

                self.socket.sendto(Segment.ack(seq_num, ack_num).pack(), (message.ip, message.port))
                Terminal.log(f"Sending ACK to {message.ip}:{message.port}",
                            Terminal.ALERT_SYMBOL, "Handshake NUM=" + str(seq_num))

                return OncomingConnection(True, (message.ip, message.port), seq_num, ack_num)

            except TimeoutError:
                Terminal.log(f"Handshake timeout", Terminal.CRITICAL_SYMBOL, "Handshake")
                retries -= 1

        self.socket.sendto(Segment.rst().pack(), remote_address)
        return OncomingConnection(False, (ip_remote, port_remote), 0, 0, OncomingConnection.ERR_TIMEOUT)

    def acceptHandshake(self, target_address = None, timeout = Config.HANDSHAKE_TIMEOUT) -> OncomingConnection:
        seq_num = randint(0, 4294967295)

        if(target_address is None):
            print("waiting for handshake from: ", target_address)
            syn_message = self.listen(MessageQuery(
                flags = SegmentFlag.FLAG_SYN
            ), timeout)
        else:
            syn_message = self.listen(MessageQuery(
                ip = target_address[0],
                port = target_address[1],
                flags = SegmentFlag.FLAG_SYN
            ), timeout)
        Terminal.log(f"Received SYN from {syn_message.ip}:{syn_message.port}", Terminal.ALERT_SYMBOL,
                        "Handshake NUM=" + str(seq_num))

        ack_num = syn_message.segment.seq_num + 1

        self.socket.sendto(Segment.syn_ack(seq_num, ack_num).pack(), (syn_message.ip, syn_message.port))
        Terminal.log(f"Sending SYN-ACK to {syn_message.ip}:{syn_message.port}", Terminal.ALERT_SYMBOL,
                        "Handshake NUM=" + str(seq_num))

        retries = Config.SEND_RETRIES
        while retries > 0:
            try:
                ack_message = self.listen(MessageQuery(
                        ip = syn_message.ip,
                        port = syn_message.port,
                        flags = SegmentFlag.FLAG_ACK,
                        ack_num = seq_num + 1
                    ), Config.HANDSHAKE_TIMEOUT)
                Terminal.log(f"Received ACK from {ack_message.ip}:{ack_message.port}",
                            Terminal.ALERT_SYMBOL, "Handshake NUM=" + str(ack_message.segment.ack_num))
                
                return OncomingConnection(True, (ack_message.ip, ack_message.port), ack_message.segment.ack_num, ack_message.segment.seq_num + 1)

            except TimeoutError:
                Terminal.log(f"ACK timeout from {ack_message.ip}:{ack_message.port}", Terminal.CRITICAL_SYMBOL, "Handshake")
                retries -= 1

        Terminal.log(f"No ACK received from {syn_message.ip}:{syn_message.port}", Terminal.CRITICAL_SYMBOL, "Handshake")
        return OncomingConnection(False, (syn_message.ip, syn_message.port), 0, 0, OncomingConnection.ERR_TIMEOUT)

    def requestTeardown(self, to_ip: str, to_port: int, fin_seq_num: int):
        to_address = (to_ip, to_port)
        Terminal.log("Initiating teardown", Terminal.ALERT_SYMBOL)
        
        retries = Config.SEND_RETRIES
        try:
            Terminal.log(f"Sending FIN request to {to_ip}:{to_port}", Terminal.ALERT_SYMBOL)
            self.socket.sendto(Segment.fin(fin_seq_num).pack(), to_address)

            while retries > 0:
                Terminal.log("Waiting for response...", Terminal.ALERT_SYMBOL, "Teardown")
                response = self.listen(MessageQuery(
                    flags = SegmentFlag.FLAG_FIN | SegmentFlag.FLAG_ACK,
                    ip = to_ip,
                    port = to_port
                ), Config.TEARDOWN_TIMEOUT)

                Terminal.log(f"Accepted FIN-ACK from {response.ip}:{response.port}",
                                Terminal.ALERT_SYMBOL)
                break

        except TimeoutError:
            retries -= 1
            Terminal.log(f"Teardown timeout", Terminal.CRITICAL_SYMBOL, "Teardown")

    def acceptTeardown(self, fin_ack_seq_num: int):
        Terminal.log("Accepting teardown", Terminal.ALERT_SYMBOL)
        retries = Config.SEND_RETRIES
        try:
            request = self.listen(MessageQuery(
                flags= SegmentFlag.FLAG_FIN
            ), Config.TEARDOWN_TIMEOUT)

            Terminal.log(f"Received FIN from {request.ip}:{request.port}", Terminal.ALERT_SYMBOL,
                        "Teardown NUM=" + str(request.segment.seq_num))

            ack_num = request.segment.seq_num + 1

            self.socket.sendto(Segment.fin_ack(fin_ack_seq_num, ack_num).pack(), (request.ip, request.port))
            Terminal.log(f"Sending FIN-ACK to {request.ip}:{request.port}", Terminal.ALERT_SYMBOL,
                        "Teardown NUM=" + str(fin_ack_seq_num))
        except TimeoutError:
            retries -= 1
            Terminal.log(f"Teardown timeout", Terminal.CRITICAL_SYMBOL, "Teardown")

    # ARQ stop and wait gatau gak sengaja kebikin
    def sendStopNWait(self, message: MessageInfo, timeout: int = Config.RETRANSMIT_TIMEOUT) -> OncomingConnection:

        Terminal.log(f"Sending data reliably to {message.ip}:{message.port}", Terminal.ALERT_SYMBOL, f"OUTGOING NUM={message.segment.seq_num}")
        retries = Config.SEND_RETRIES
        while retries > 0:
            try:
                self.send(message.segment.pack(), message.ip, message.port)

                response = self.listen(MessageQuery(
                    ip = message.ip,
                    port = message.port,
                    ack_num = message.segment.seq_num + 1
                ), timeout)

                Terminal.log(f"Received ACK from {message.ip}:{message.port}", Terminal.ALERT_SYMBOL, f"OUTGOING NUM={response.segment.ack_num}")
                return OncomingConnection(True, (response.ip, response.port), response.segment.ack_num, response.segment.seq_num + 1)

            except TimeoutError:
                print("Response timeout!")
                retries -= 1
                if(retries > 0):
                    print("Retrying")
                else:
                    print("Stopped retrying")

        return OncomingConnection(False, (message.ip, message.port), message.segment.seq_num, message.segment.ack_num, OncomingConnection.ERR_TIMEOUT)

    def receiveStopNWait(self, timeout: int = 30) -> (OncomingConnection, Segment):
        while True:
            try:
                response = self.listen(timeout = timeout)

                Terminal.log(f"Received data from {response.ip}:{response.port}", Terminal.ALERT_SYMBOL, f"INCOMING NUM={response.segment}")
                self.send(Segment.ack(response.segment.ack_num, response.segment.seq_num + 1).pack(), response.ip, response.port)
                Terminal.log(f"Sending ACK from {response.ip}:{response.port}", Terminal.ALERT_SYMBOL, f"INCOMING NUM={response.segment.ack_num}")
                return OncomingConnection(True, (response.ip, response.port), response.segment.ack_num, response.segment.seq_num + 1), response.segment.payload

            except TimeoutError:
                print("Request timeout!")
                return OncomingConnection(False, None, 0, 0, OncomingConnection.ERR_TIMEOUT), None

    def goBackNSendFrame(self, message: MessageInfo, last_ack: List[int]) :
        Terminal.log(f"Sending data reliably to {message.ip}:{message.port}", Terminal.ALERT_SYMBOL, f"OUTGOING NUM={message.segment.seq_num}")

        try:
            self.send(message.segment.pack(), message.ip, message.port)

            response = self.listen(MessageQuery(
                ip = message.ip,
                port = message.port,
                flags = SegmentFlag.FLAG_ACK,
            ), Config.RETRANSMIT_TIMEOUT)

            if(last_ack[0] < response.segment.ack_num - 1): last_ack[0] = response.segment.ack_num -1
            Terminal.log(f"Segment {message.segment.seq_num} received ACK from {message.ip}:{message.port} with ack {response.segment.ack_num}, last ack is {last_ack[0]}", Terminal.ALERT_SYMBOL, f"OUTGOING NUM={response.segment.ack_num}")

        except TimeoutError:
            print("Timeout happened at sequence: ", message.segment.seq_num)

    def sendGoBackN(self, messages: List[Segment], ip : str, port : int) -> OncomingConnection:
        import time
        SWS = Config.WINDOW_SIZE
        # retries = Config.SEND_RETRIES

        threads = []

        LAR = 0
        LFS = 0
        offset = messages[0].seq_num
        last_ack = [offset]

        while True:
            while LFS - LAR <= SWS and LFS < len(messages):
                time.sleep(0.1)

                thread = Thread(target=self.goBackNSendFrame, args=[
                    MessageInfo(
                        ip,
                        port,
                        messages[LFS]
                    ),
                    last_ack
                ])

                threads.append(thread)
                thread.start()
                LFS += 1

            print("Waiting for frames")
            for thread in threads:
                thread.join()

            LFS = (last_ack[0] - offset) + 1
            print("LFS from last_ack is ", LFS)
            print("Next we'll send: ", last_ack[0] + 1)
            LAR = LFS

            if LFS >= len(messages):
                print("Done!")
                last_message = messages[len(messages) - 1]
                return OncomingConnection(True, (ip, port), last_message.ack_num, last_message.ack_num + 1)

    def receiveGoBackN(self, oncomingConnection: OncomingConnection, timeout: int = 30,) -> (OncomingConnection, Segment):
        buffer = []

        # while True:
        last_ack = oncomingConnection.ack_num
        try :
            i = 0

            while True: # TODO: EOF?
                print("Waiting for:", last_ack)
                
                response = self.listen(MessageQuery(
                    ip = oncomingConnection.address[0],
                    port = oncomingConnection.address[1],
                    seq_num = last_ack
                ))

                print("in seq_num:", response.segment.seq_num)
                print("in ack_num:", response.segment.ack_num)

                if response.segment.seq_num == last_ack:
                    last_ack += 1
                    self.send(Segment.ack(response.segment.ack_num, last_ack).pack(), response.ip,
                                            response.port)
                    Terminal.log(f"Sending ACK from {response.ip}:{response.port}", Terminal.INFO_SYMBOL,
                                    f"INCOMING NUM={response.segment.ack_num}")

                    # if metadata
                    if  (response.segment.flags == (SegmentFlag.FLAG_RST | SegmentFlag.FLAG_FIN)):
                        metadata = response.segment.payload.decode().split(FileMark.METADATA)
                        Terminal.log(f'Received file metadata: name = {metadata[0]}, extension = {metadata[1]}, size = {metadata[2]}', Terminal.INFO_SYMBOL)
                    # if eof
                    elif (response.segment.flags == (SegmentFlag.FLAG_SYN | SegmentFlag.FLAG_FIN)):
                        Terminal.log(f'Received EOF', Terminal.INFO_SYMBOL)
                        return OncomingConnection(True, (response.ip, response.port), response.segment.ack_num, response.segment.seq_num + 1), buffer
                    else:
                        buffer.append(response.segment.payload.rstrip(b'\x00'))

        except struct.error as e:
            print(e)
