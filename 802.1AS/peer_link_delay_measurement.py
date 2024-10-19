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
            print("%s %f" % (label, self.get_angle()))
            if self.get_angle() < -PI/2:
                return self.get_angle() - PI
            else:
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
        line = DoubleArrow(start=tt.get_right(), end=tr.get_left())
        self.play(Create(tt), Create(tr), GrowArrow(line))


        topology = Group(tt, tr, line)
        self.play(topology.animate.next_to(ORIGIN, UP, buff=1.5))

        def seqline(start, color=WHITE):
            return Line(start, start + DOWN * 4.5, color=color)

        tt_line = seqline(tt.get_bottom() + DOWN * 0.5, color=GREEN)
        tr_line = seqline(tr.get_bottom() + DOWN * 0.5, color=BLUE)
        self.play(Create(tt_line), Create(tr_line))

        def tr_to_tt(text, start, end, color=WHITE):
            arrow = LabeledArrow(text, start=start, end=end, color=color)
            msg = Envelope(color=color).move_to(tr).shift(UP * MED_LARGE_BUFF)
            self.play(Succession(
                GrowFromCenter(msg),
                AnimationGroup(
                    GrowArrow(arrow),
                    msg.animate.move_to(tt).shift(UP * MED_LARGE_BUFF)
                ),
                ShrinkToCenter(msg),
            ))

        def tt_to_tr(text, start, end, color=WHITE):
            arrow = LabeledArrow(text, start=start, end=end, color=color)
            msg = Envelope(color=color).move_to(tt).shift(UP * MED_LARGE_BUFF)
            self.play(Succession(
                GrowFromCenter(msg),
                AnimationGroup(
                    GrowArrow(arrow),
                    msg.animate.move_to(tr).shift(UP * MED_LARGE_BUFF)
                ),
                ShrinkToCenter(msg),
            ))

        tr_pos = tr_line.get_start() + DOWN * 0.2
        tt_pos = tt_line.get_start() + DOWN * 1.2
        tr_to_tt("pdelay_req", tr_pos, tt_pos, color=GOLD)

        tt_pos += DOWN
        tr_pos += DOWN * 3
        tt_to_tr("pdelay_resp", tt_pos, tr_pos, color=MAROON)

        tt_pos += DOWN
        tr_pos += DOWN
        tt_to_tr("pdelay_resp_follow_up", tt_pos, tr_pos, color=PURPLE)

        self.wait(3)
