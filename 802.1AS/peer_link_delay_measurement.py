from manim import *
from typing import Optional

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
        size = MED_SMALL_BUFF

        super().__init__(*args, height=size, width=size*1.5, color=color, **kwargs)

        self.add(Line(start=self.get_corner(UL), end=self.get_center(), color=color))
        self.add(Line(start=self.get_center(), end=self.get_corner(UR), color=color))

class PeerLinkDelayMeasurement(Scene):
    def construct(self):
        # self.next_section(skip_animations=True)
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

        def time_to_points(relative_to, time):
            return relative_to.get_bottom() + DOWN * (MED_LARGE_BUFF + time)

        def transmit(label, tx, rx, time, color=WHITE, ts_idx: Optional[int] = None, payload=None):
            start = time_to_points(tx, time)
            end = time_to_points(rx, time + 1)
            ts_idx_size = 1 if tx.get_x() > 0 else -1
            timestamps = []

            arrow = LabeledArrow(label, bottom_label=payload, start=start, end=end, color=color)
            envelope = Envelope(color=color).move_to(tx).shift(DOWN * MED_LARGE_BUFF)
            self.play(GrowFromCenter(envelope))
            if payload is not None:
                self.play(payload.set_color(color).animate.move_to(envelope).scale(0.5))
                self.remove(payload)
            if ts_idx is not None:
                ts = MathTex(r't_%d' % ts_idx, color=tx.get_color()).next_to(start, RIGHT * ts_idx_size)
                timestamps.append(ts)
                self.play(Write(ts))
            self.play(
                GrowArrow(arrow),
                envelope.animate.move_to(rx).shift(DOWN * MED_LARGE_BUFF),
            )
            if ts_idx is not None:
                ts = MathTex(r't_%d' % (ts_idx + 1), color=rx.get_color()).next_to(end, LEFT * ts_idx_size)
                timestamps.append(ts)
                self.play(Write(ts))
            self.play(ShrinkToCenter(envelope))
            return timestamps

        time = 0.2
        timestamps = transmit("pdelay_req", tr, tt, time, color=GOLD, ts_idx=1)

        time += 2
        timestamps = transmit("pdelay_resp", tt, tr, time, color=MAROON, ts_idx=3, payload=timestamps[1].copy())

        time += 1
        transmit("pdelay_resp_follow_up", tt, tr, time, color=PURPLE, payload=timestamps[0].copy())

        sequence = Group(*self.mobjects)
        self.play(sequence.animate.next_to(config.left_side))

        self.next_section()
        eqn = MathTex(r'\operatorname{meanLinkDelay} = \frac{(t_4 - t_3) + (t_2 - t_1)}{2}', font_size=36)
        eqn[0][15:17].set_color(BLUE)
        eqn[0][18:20].set_color(GREEN)
        eqn[0][23:25].set_color(GREEN)
        eqn[0][26:28].set_color(BLUE)
        eqn.next_to(config.right_side, LEFT)
        self.play(Write(eqn))
        self.wait(3)
