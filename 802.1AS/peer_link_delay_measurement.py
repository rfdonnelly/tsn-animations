from manim import *

class LabeledArrow(Arrow):
    def __init__(
        self,
        label: str,
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

class Envelope(Rectangle):
    def __init__(
        self,
        color: ParsableManimColor = WHITE,
        *args,
        **kwargs,
    ) -> None:
        size = MED_SMALL_BUFF

        super().__init__(*args, height=size, width=size*1.5, color=color, **kwargs)

        self.add(Line(start=self.get_corner(UL), end=self.get_center(), color=color))
        self.add(Line(start=self.get_center(), end=self.get_corner(UR), color=color))

class PeerLinkDelayMeasurement(Scene):
    def construct(self):
        Text.set_default(font_size = 12)

        tt = (
            Square(color=GREEN)
                .set_fill(GREEN, opacity=0.6)
                .add(Text("timeTransmitter"))
                .shift(LEFT * 3)
        )
        tr = (
            Square(color=BLUE)
                .set_fill(BLUE, opacity=0.6)
                .add(Text("timeReceiver"))
                .shift(RIGHT * 3)
        )
        self.play(Create(tt))
        self.play(Create(tr))

        topology = Group(tt, tr)
        self.play(topology.animate.next_to(ORIGIN, UP, buff=1.5))
        self.play(
            Create(Line([0, 1, 0], [0, -3.5, 0], color=GREEN).shift(LEFT * 3)),
            Create(Line([0, 1, 0], [0, -3.5, 0], color=BLUE).shift(RIGHT * 3)),
        )

        def transmit(label, tx, rx, time, color=WHITE):
            start = tx.get_bottom() + DOWN * (MED_LARGE_BUFF + time)
            end = rx.get_bottom() + DOWN * (MED_LARGE_BUFF + time + 1)

            arrow = LabeledArrow(label, start=start, end=end, color=color)
            envelope = Envelope(color=color).move_to(tx).shift(DOWN * MED_LARGE_BUFF)
            self.play(Succession(
                GrowFromCenter(envelope),
                AnimationGroup(
                    GrowArrow(arrow),
                    envelope.animate.move_to(rx).shift(DOWN * MED_LARGE_BUFF),
                ),
                ShrinkToCenter(envelope)
            ))

        time = 0.2
        transmit("pdelay_req", tr, tt, time, color=GOLD)
        time += 2
        transmit("pdelay_resp", tt, tr, time, color=MAROON)
        time += 1
        transmit("pdelay_resp_follow_up", tt, tr, time, color=PURPLE)

        self.wait(3)
