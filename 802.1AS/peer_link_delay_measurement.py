from manim import *

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
        
        def message(start, end, color=WHITE):
            msg_size = 0.3
            msg = Rectangle(height = msg_size, width = msg_size * 1.5, color=color)
            (
                msg
                    .add(Line(start=msg.get_corner(UL), end=msg.get_center(), color=color))
                    .add(Line(start=msg.get_center(), end=msg.get_corner(UR), color=color))
                    .move_to(start).shift(UP * 0.5)
            )
            return {
                'create': GrowFromCenter(msg),
                'transmit': msg.animate.move_to(end).shift(UP * 0.5),
                'consume': ShrinkToCenter(msg),
            }

        def tr_to_tt(text, start, end, color=WHITE):
            line = Arrow(start=start, end=end, color=color)
            line.add(
                Text(text, color=color)
                    .rotate(line.get_angle() - PI)
                    .move_to(line)
                    .shift(UP * 0.3)
            )
            msg = message(tr, tt, color=color)
            self.play(Succession(
                msg['create'],
                AnimationGroup(
                    GrowArrow(line),
                    msg['transmit']
                ),
                msg['consume']
            ))
            
        def tt_to_tr(text, start, end, color=WHITE):
            # line = Arrow(start=start, end=end, color=color)
            line = LabeledArrow(Text(text, color=color), start=start, end=end, color=color)
            msg = message(tt, tr, color=color)
            self.play(Succession(
                msg['create'],
                AnimationGroup(
                    GrowArrow(line),
                    msg['transmit']
                ),
                msg['consume']
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