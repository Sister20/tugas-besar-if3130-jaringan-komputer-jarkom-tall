import socket
import struct
import Config as Config
from threading import Thread
from utils.Terminal import Terminal
from message.MessageInfo import MessageInfo
from message.Segment import Segment
from message.SegmentFlag import SegmentFlag
from connection.Connection import Connection
from connection.OncomingConnection import OncomingConnection
from random import randint


class TCPConnection(Connection):
    def __init__(self, ip: str, port: int, handler: callable = None) -> None:
        super().__init__(ip, port, handler)

    def requestHandshake(self, ip_remote: str, port_remote: int) -> OncomingConnection:
        seq_num = randint(0, 4294967295)

        self.setTimeout(Config.HANDSHAKE_TIMEOUT)
        remote_address = (ip_remote, port_remote)
        Terminal.log("Initiating three way handshake", Terminal.ALERT_SYMBOL)
        try:
            Terminal.log(f"Sending SYN request to {ip_remote}:{port_remote}", Terminal.ALERT_SYMBOL,
                         "Handshake NUM=" + str(seq_num))
            self.socket.sendto(Segment.syn(seq_num).pack(), remote_address)

            while True:
                Terminal.log("Waiting for response...", Terminal.ALERT_SYMBOL, "Handshake")
                data, client_address = self.listen()
                if (client_address == ip_remote or ip_remote == '<broadcast>'):
                    try:
                        data, checksum = Segment.unpack(data)
                        if data.flags == SegmentFlag.FLAG_SYN | SegmentFlag.FLAG_ACK:
                            Terminal.log(f"Accepted SYN-ACK from {client_address[0]}:{client_address[1]}",
                                         Terminal.ALERT_SYMBOL, "Handshake NUM=" + str(data.ack_num))

                            ack_num = data.seq_num + 1
                            seq_num = seq_num + 1

                            self.socket.sendto(Segment.ack(seq_num, ack_num).pack(), client_address)
                            Terminal.log(f"Sending ACK to {client_address[0]}:{client_address[1]}",
                                         Terminal.ALERT_SYMBOL, "Handshake NUM=" + str(seq_num))

                            self.setTimeout(None)
                            return OncomingConnection(True, client_address, seq_num, ack_num)

                    except struct.error as e:
                        print(e)
                        Terminal.log(f"Received bad response from {client_address[0]}:{client_address[1]}",
                                     Terminal.ALERT_SYMBOL, "Error")

        except TimeoutError:
            self.socket.sendto(Segment.rst().pack(), remote_address)
            Terminal.log(f"Handshake timeout", Terminal.CRITICAL_SYMBOL, "Handshake")
            self.setTimeout(None)
            return OncomingConnection(False, (ip_remote, port_remote), 0, 0, OncomingConnection.ERR_TIMEOUT)

    def acceptHandshake(self) -> OncomingConnection:
        seq_num = randint(0, 4294967295)

        data, client_address = self.listen()
        try:
            data, checksum = Segment.unpack(data)
        except struct.error:
            Terminal.log(f"Received bad request from {client_address[0]}:{client_address[1]}", Terminal.ALERT_SYMBOL,
                         "Error")
            return OncomingConnection(False, client_address, 0, 0, OncomingConnection.ERR_INVALID_SEGMENT)

        if data.flags == SegmentFlag.FLAG_SYN:
            Terminal.log(f"Received SYN from {client_address[0]}:{client_address[1]}", Terminal.ALERT_SYMBOL,
                         "Handshake NUM=" + str(seq_num))

            ack_num = data.seq_num + 1

            self.socket.sendto(Segment.syn_ack(seq_num, ack_num).pack(), client_address)
            Terminal.log(f"Sending SYN-ACK to {client_address[0]}:{client_address[1]}", Terminal.ALERT_SYMBOL,
                         "Handshake NUM=" + str(seq_num))

            client = client_address

            self.setTimeout(Config.HANDSHAKE_TIMEOUT)
            try:
                while True:
                    data, client_address = self.listen()
                    while (client_address != client):
                        continue

                    try:
                        data, checksum = Segment.unpack(data)
                    except:
                        Terminal.log(f"Received bad response from {client_address[0]}:{client_address[1]}",
                                     Terminal.ALERT_SYMBOL, "Error")
                        continue

                    if data.flags == SegmentFlag.FLAG_ACK and data.ack_num == seq_num + 1:
                        Terminal.log(f"Received ACK from {client_address[0]}:{client_address[1]}",
                                     Terminal.ALERT_SYMBOL, "Handshake NUM=" + str(data.ack_num))

                        self.setTimeout(None)
                        return OncomingConnection(True, client_address, data.seq_num, data.ack_num)

                    if data.flags == SegmentFlag.FLAG_RST:
                        Terminal.log(f"Received RST from {client_address[0]}:{client_address[1]}",
                                     Terminal.CRITICAL_SYMBOL, "Handshake")

                        self.setTimeout(None)
                        return OncomingConnection(False, client_address, 0, 0, OncomingConnection.ERR_RESET)

            except TimeoutError:
                Terminal.log(f"No ACK received from {client[0]}:{client[1]}", Terminal.CRITICAL_SYMBOL, "Handshake")

                self.setTimeout(None)
                return OncomingConnection(False, client_address, 0, 0, OncomingConnection.ERR_TIMEOUT)

    def requestTeardown(self, to_ip: str, to_port: int, fin_seq_num: int):
        self.setTimeout(Config.TEARDOWN_TIMEOUT)
        to_address = (to_ip, to_port)
        Terminal.log("Initiating teardown", Terminal.ALERT_SYMBOL)
        try:
            Terminal.log(f"Sending FIN request to {to_ip}:{to_port}", Terminal.ALERT_SYMBOL)
            self.socket.sendto(Segment.fin(fin_seq_num).pack(), to_address)

            while True:
                Terminal.log("Waiting for response...", Terminal.ALERT_SYMBOL, "Teardown")
                data, res_address = self.listen()
                if (res_address == to_ip):
                    try:
                        data, checksum = Segment.unpack(data)
                        if data.flags == SegmentFlag.FLAG_FIN | SegmentFlag.FLAG_ACK:
                            Terminal.log(f"Accepted FIN-ACK from {res_address[0]}:{res_address[1]}",
                                         Terminal.ALERT_SYMBOL)
                            self.setTimeout(None)
                            break

                    except struct.error as e:
                        print(e)
                        Terminal.log(f"Received bad response from {res_address[0]}:{res_address[1]}",
                                     Terminal.ALERT_SYMBOL, "Error")

        except TimeoutError:
            Terminal.log(f"Teardown timeout", Terminal.CRITICAL_SYMBOL, "Teardown")
            self.setTimeout(None)

    def acceptTeardown(self, fin_ack_seq_num: int):
        data, from_address = self.listen()

        try:
            data, checksum = Segment.unpack(data)
            if data.flags == SegmentFlag.FLAG_FIN:
                Terminal.log(f"Received FIN from {from_address[0]}:{from_address[1]}", Terminal.ALERT_SYMBOL,
                            "Teardown NUM=" + str(data.seq_num))

                ack_num = data.seq_num + 1

                self.socket.sendto(Segment.fin_ack(fin_ack_seq_num, ack_num).pack(), from_address)
                Terminal.log(f"Sending FIN-ACK to {from_address[0]}:{from_address[1]}", Terminal.ALERT_SYMBOL,
                            "Teardown NUM=" + str(fin_ack_seq_num))
        except struct.error:
            Terminal.log(f"Received bad request from {from_address[0]}:{from_address[1]}", Terminal.ALERT_SYMBOL,
                         "Error")

    # ARQ stop and wait
    # Kemungkinan rusak kalo dipake multithreading soalnya manfaatin setTimeout
    def sendStopNWait(self, message: MessageInfo) -> OncomingConnection:
        previousTimeout = self.socket.gettimeout()
        self.setTimeout(Config.RETRANSMIT_TIMEOUT)
        
        Terminal.log(f"Sending data reliably to {message.ip}:{message.port}", Terminal.ALERT_SYMBOL, f"OUTGOING NUM={message.segment.seq_num}")
        retries = Config.SEND_RETRIES
        while retries > 0:
            try:
                self.send(message.segment.pack(), message.ip, message.port)
                response, client_address = self.listen()

                if(client_address == (message.ip, message.port)):
                    try:
                        data, checksum = Segment.unpack(response)
                        if data.flags == SegmentFlag.FLAG_ACK:
                            if data.ack_num == message.segment.seq_num + 1:
                                Terminal.log(f"Received ACK from {message.ip}:{message.port}", Terminal.ALERT_SYMBOL, f"OUTGOING NUM={data.ack_num}")
                                self.setTimeout(previousTimeout)
                                return OncomingConnection(True, client_address, data.ack_num, data.seq_num + 1)
                            
                    except struct.error as e:
                        print(e)

            except TimeoutError:
                print("Response timeout!")
                retries -= 1
                if(retries > 0):
                    print("Retrying")
                else:
                    print("Stopped retrying")

        self.setTimeout(previousTimeout)
        return OncomingConnection(False, (message.ip, message.port), message.segment.seq_num, message.segment.ack_num, OncomingConnection.ERR_TIMEOUT)

    def receiveStopNWait(self, timeout: int = 30) -> (OncomingConnection, Segment):
        previousTimeout = self.socket.gettimeout()
        self.setTimeout(timeout)

        # TODO: Gimana kalo ACK-nya ga nyampe? tau dari mana harus stop listen?
        # Yang dikomen solusinya nunggu sampe timeout tapi ga reliable bjir

        # responded = False
        # saved_response = None
        while True:
            try:
                response, client_address = self.listen()


                data, checksum = Segment.unpack(response)
                segment = Segment(data.flags, data.seq_num, data.ack_num, data.payload)

                if not(segment.is_valid_checksum()) :
                    Terminal.log(f"Received bad data from {client_address[0]}:{client_address[1]}", Terminal.ALERT_SYMBOL, f"INCOMING NUM={data.ack_num}")
                    self.send(Segment.ack(data.ack_num, data.seq_num + 1).pack(), client_address[0], client_address[1])
                    Terminal.log(f"Sending ACK from {client_address[0]}:{client_address[1]}", Terminal.ALERT_SYMBOL, f"INCOMING NUM={data.ack_num}")
                    continue

                Terminal.log(f"Received data from {client_address[0]}:{client_address[1]}", Terminal.ALERT_SYMBOL, f"INCOMING NUM={data.ack_num}")

                # if(saved_response == None):
                # responded = True
                # saved_response = (response, client_address)
                self.send(Segment.ack(data.ack_num, data.seq_num + 1).pack(), client_address[0], client_address[1])
                Terminal.log(f"Sending ACK from {client_address[0]}:{client_address[1]}", Terminal.ALERT_SYMBOL, f"INCOMING NUM={data.ack_num}")
                return OncomingConnection(True, client_address, data.ack_num, data.seq_num + 1), response

                # elif(saved_response == (response, client_address)):
                #     self.send(Segment.ack(data.ack_num, data.seq_num + 1).pack(), client_address[0], client_address[1])
                #     Terminal.log(f"Resending ACK from {client_address[0]}:{client_address[1]}", Terminal.ALERT_SYMBOL, f"INCOMING NUM={data.ack_num}")

                # elif (client_address == saved_response[1]):
                #     return OncomingConnection(True, client_address, data.ack_num, data.seq_num + 1), saved_response[0].unpack().payload
                        
            except struct.error as e:
                print(e)

            except TimeoutError:
                print("Request timeout!")
                self.setTimeout(previousTimeout)
                # if(responded):
                #     print("Assumed successful")
                #     data, checksum = Segment.unpack(saved_response[0])
                #     return OncomingConnection(False, saved_response[1], data.ack_num, data.seq_num + 1, OncomingConnection.ERR_TIMEOUT), data.payload
                # else:
                # print("Assumed unsuccessful")
                return OncomingConnection(False, None, 0, 0, OncomingConnection.ERR_TIMEOUT), None

    # def