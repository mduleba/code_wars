from __future__ import annotations


def traverse_TCP_states(events):
    app = Context(Closed())
    try:
        for event in events:
            app(event)
        return app.get_state_value()
    except NotImplementedError:
        return 'ERROR'


class Context:

    _state = None

    def __init__(self, state: State) -> None:
        self.set_state(state)

    def get_state_value(self):
        return self._state.value

    def set_state(self, state: State):
        print(f"Context: Transitioning to {type(state).__name__}")
        self._state = state
        self._state.context = self

    def __call__(self, command):
        decision = {
            'APP_PASSIVE_OPEN': self._state.appselfpassiveopen,
            'APP_ACTIVE_OPEN': self._state.app_active_open,
            'RCV_SYN': self._state.rcv_syn,
            'APP_SEND': self._state.app_send,
            'APP_CLOSE': self._state.app_close,
            'RCV_ACK': self._state.rcv_ack,
            'RCV_SYN_ACK': self._state.rcv_syn_ack,
            'RCV_FIN': self._state.rcv_fin,
            'RCV_FIN_ACK': self._state.rcv_fin_ack,
            'APP_TIMEOUT': self._state.app_timeout,
        }
        decision[command]()


class State:
    value: str

    @property
    def context(self) -> Context:
        return self._context

    @context.setter
    def context(self, context: Context) -> None:
        self._context = context

    def appselfpassiveopen(self):
        raise NotImplementedError

    def app_active_open(self):
        raise NotImplementedError

    def rcv_syn(self):
        raise NotImplementedError

    def app_send(self):
        raise NotImplementedError

    def app_close(self):
        raise NotImplementedError

    def rcv_ack(self):
        raise NotImplementedError

    def rcv_syn_ack(self):
        raise NotImplementedError

    def rcv_fin(self):
        raise NotImplementedError

    def rcv_fin_ack(self):
        raise NotImplementedError

    def app_timeout(self):
        raise NotImplementedError


class Closed(State):
    value = 'CLOSED'
    def appselfpassiveopen(self):
        self.context.set_state(Listen())

    def app_active_open(self):
        self.context.set_state(SynSent())


class Listen(State):
    value = 'LISTEN'
    def rcv_syn(self):
        self.context.set_state(SynRcvd())

    def app_send(self):
        self.context.set_state(SynSent())

    def app_close(self):
        self.context.set_state(Closed())


class SynRcvd(State):
    value = 'SYN_RCVD'
    def app_close(self):
        self.context.set_state(FinWait1())

    def rcv_ack(self):
        self.context.set_state(Established())


class SynSent(State):
    value = 'SYN_SENT'
    def rcv_syn(self):
        self.context.set_state(SynRcvd())

    def rcv_syn_ack(self):
        self.context.set_state(Established())

    def app_close(self):
        self.context.set_state(Closed())


class Established(State):
    value = 'ESTABLISHED'
    def app_close(self):
        self.context.set_state(FinWait1())

    def rcv_fin(self):
        self.context.set_state(CloseWait())


class FinWait1(State):
    value = 'FIN_WAIT_1'
    def rcv_fin(self):
        self.context.set_state(Closing())

    def rcv_fin_ack(self):
        self.context.set_state(TimeWait())

    def rcv_ack(self):
        self.context.set_state(FinWait2())


class Closing(State):
    value = 'CLOSING'
    def rcv_ack(self):
        self.context.set_state(TimeWait())


class FinWait2(State):
    value = 'FIN_WAIT_2'
    def rcv_fin(self):
        self.context.set_state(TimeWait())


class TimeWait(State):
    value = 'TIME_WAIT'
    def app_timeout(self):
        self.context.set_state(Closed())


class CloseWait(State):
    value = 'CLOSE_WAIT'
    def app_close(self):
        self.context.set_state(LastAck())


class LastAck(State):
    value = 'LAST_ACK'
    def rcv_ack(self):
        self.context.set_state(Closed())
