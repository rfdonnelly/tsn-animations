from manim import *
from typing import Optional

def time_to_points(relative_to, time):
    return relative_to.get_bottom() + DOWN * (MED_LARGE_BUFF + time)

class LabeledArrow(Arrow):
    def __init__(
        self,
        label: str,
        bottom_label = None,
        color: ParsableManimColor = WHITE,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, color=color, **kwargs)

        def angle():
            if self.get_angle() < -PI/2:
                # down left
                return self.get_angle() - PI
            else:
                # down right
                return self.get_angle()

        self.add(
            Text(label, color=color)
                .rotate(angle())
                .move_to(self)
                .shift(UP * MED_SMALL_BUFF)
        )

        if bottom_label is not None:
            self.add(
                bottom_label
                    .copy()
                    .set_color(color)
                    .scale(0.5)
                    .move_to(self)
                    .shift(DOWN * 0.2)
            )

class Envelope(Rectangle):
    def __init__(
        self,
        color: ParsableManimColor = WHITE,
        *args,
        **kwargs,
    ) -> None:
        size = 0.4

        super().__init__(*args, height=size, width=size*1.5, color=color, **kwargs)

        self.add(Line(start=self.get_corner(UL), end=self.get_center(), color=color))
        self.add(Line(start=self.get_center(), end=self.get_corner(UR), color=color))

class Transmission():
    arrow: LabeledArrow
    envelope: Envelope
    timestamp_idx: Optional[int]
    timestamp_idx_side: int
    start_pt = 0
    end_pt = 0
    tx_timestamp: Optional[Mobject]
    rx_timestamp: Optional[Mobject]
    txr: Mobject
    rxr: Mobject
    payload: Optional[Mobject]

    def __init__(
            self,
            label: str,
            txr: Mobject,
            rxr: Mobject,
            time: int,
            timestamp_idx: Optional[int] = None,
            payload: Optional[Mobject] = None,
            color: ParsableManimColor = WHITE,
    ):
        self.start_pt = time_to_points(txr, time)
        self.end_pt = time_to_points(rxr, time + 1)
        self.arrow = LabeledArrow(label, start=self.start_pt, end=self.end_pt, color=color)
        self.envelope = Envelope(color=color).move_to(txr).shift(DOWN * MED_LARGE_BUFF)
        self.timestamp_idx = timestamp_idx
        self.timestamp_idx_side = 1 if txr.get_x() > 0 else -1
        self.timestamp_idx = timestamp_idx
        self.txr = txr
        self.rxr = rxr
        self.payload = payload
        if self.payload is not None:
            self.payload.set_color(color)

    def create(self, scene = None):
        scene.play(GrowFromCenter(self.envelope))
        if self.payload is not None:
            payload = self.payload.copy()
            scene.play(payload.animate.move_to(self.envelope).scale(0.5))
            self.envelope.add(payload)

    def transmit(self, scene = None):
        if self.timestamp_idx is not None:
            self.tx_timestamp = MathTex(
                r't_%d' % self.timestamp_idx,
                color=self.txr.get_color()
            ).next_to(self.start_pt, RIGHT * self.timestamp_idx_side)
            scene.play(Write(self.tx_timestamp))
        animations = [
            GrowArrow(self.arrow),
            self.envelope.animate.move_to(self.rxr).shift(DOWN * MED_LARGE_BUFF),
        ]
        if self.payload is not None:
            payload = self.payload.copy()
            animation = (
                payload
                    .animate
                    .move_to(self.arrow)
                    .shift(DOWN * 0.2)
                    .scale(0.5)
            )
            animations.append(animation)
        scene.play(*animations)
        if self.timestamp_idx is not None:
            self.rx_timestamp = MathTex(
                r't_%d' % (self.timestamp_idx + 1),
                color=self.rxr.get_color()
            ).next_to(self.end_pt, LEFT * self.timestamp_idx_side)
            scene.play(Write(self.rx_timestamp))

    def destroy(self, scene):
        scene.play(ShrinkToCenter(self.envelope))

    def send(self, scene):
        self.create(scene)
        self.transmit(scene)
        self.destroy(scene)

class Node(Square):
    label: str

    def __init__(
            self,
            label: str,
            color: ParsableManimColor = WHITE,
    ):
        super().__init__(color=color)
        self.set_fill(color, opacity=0.6)
        self.label = label

    def create(self, scene):
        text = Text(self.label).move_to(self.get_center())
        scene.play(Create(self))
        scene.play(Write(text))
        self.add(text)

class PeerLinkDelayMeasurement(Scene):
    def construct(self):
        # self.next_section(skip_animations=True)
        Text.set_default(font_size = 12)

        tt = Node("timeTransmitter", color=GREEN).shift(LEFT * 3)
        tt.create(self)

        tr = Node("timeReciever", color=BLUE).shift(RIGHT * 3)
        tr.create(self)

        topology = Group(tt, tr)
        self.play(topology.animate.next_to(ORIGIN, UP, buff=1.5))
        self.play(
            Create(Line([0, 1, 0], [0, -3.5, 0], color=GREEN).shift(LEFT * 3)),
            Create(Line([0, 1, 0], [0, -3.5, 0], color=BLUE).shift(RIGHT * 3)),
        )

        time = 0.2
        pdelay_req = Transmission("pdelay_req", tr, tt, time, color=GOLD, timestamp_idx=1)
        pdelay_req.send(self)

        time += 2
        pdelay_resp = Transmission("pdelay_resp", tt, tr, time, color=MAROON, timestamp_idx=3, payload=pdelay_req.rx_timestamp.copy())
        pdelay_resp.send(self)

        time += 1
        pdelay_resp_follow_up = Transmission("pdelay_resp_follow_up", tt, tr, time, color=PURPLE, payload=pdelay_resp.tx_timestamp.copy())
        pdelay_resp_follow_up.send(self)

        sequence = Group(*self.mobjects)
        self.play(sequence.animate.next_to(config.left_side))

        t1 = MathTex(r"\operatorname{meanLinkDelay}", r" = {(t_4 - t_3) + (t_2 - t_1) \over 2}", font_size=36)
        t2 = MathTex(r" = {(t_4 - t_1) - (t_3 - t_2) \over 2}", font_size=36)
        t1.next_to(config.right_side, LEFT)
        t2.next_to(t1[1], DOWN)
        t1[1][2:4].set_color(BLUE)
        t1[1][5:7].set_color(GREEN)
        t1[1][10:12].set_color(GREEN)
        t1[1][13:15].set_color(BLUE)
        t2[0][2:4].set_color(BLUE)
        t2[0][5:7].set_color(BLUE)
        t2[0][10:12].set_color(GREEN)
        t2[0][13:15].set_color(GREEN)
        self.play(Write(t1))
        self.play(TransformFromCopy(t1[1], t2))
        self.wait(3)
