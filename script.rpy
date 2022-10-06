# 游戏的脚本可置于此文件中。
init python:
    def change_title(i=0):
        i=renpy.random.randint(0,2)
        if i==0:
            gui.main_menu_background = "gui/main_menu.png"
        elif i==1:
            gui.main_menu_background = "gui/title2.png"
        elif i==2:
            gui.main_menu_background = "gui/title3.png"
init python:
    def play_music(filename, channel='music', start=0, end=-1):
        c = renpy.audio.audio.get_channel(channel)
        file = renpy.audio.audio.load(filename)
        _filename = renpy.audio.audio.AudioData(b'...', filename)
        renpy.audio.renpysound.play(c.get_number(), file, _filename, start=start, end=end)
init python:

    class PongDisplayable(renpy.Displayable):

        def __init__(self):

            renpy.Displayable.__init__(self)


            # The sizes of some of the images.
            self.PADDLE_WIDTH = 12
            self.PADDLE_HEIGHT = 95
            self.PADDLE_X = 240
            self.BALL_WIDTH = 15
            self.BALL_HEIGHT = 15
            self.COURT_TOP = 193.5
            self.COURT_BOTTOM = 975


            # Some displayables we use.
            self.paddle = Solid("#ffffff", xsize=self.PADDLE_WIDTH, ysize=self.PADDLE_HEIGHT)
            self.ball = Solid("#ffffff", xsize=self.BALL_WIDTH, ysize=self.BALL_HEIGHT)

            # If the ball is stuck to the paddle.
            self.stuck = True

            # The positions of the two paddles.
            self.playery = (self.COURT_BOTTOM - self.COURT_TOP) / 2
            self.computery = self.playery

            # The speed of the computer.
            self.computerspeed = 380.0

            # The position, delta-position, and the speed of the
            # ball.
            self.bx = self.PADDLE_X + self.PADDLE_WIDTH + 10
            self.by = self.playery
            self.bdx = .5
            self.bdy = .5
            self.bspeed = 350.0

            # The time of the past render-frame.
            self.oldst = None

            # The winner.
            self.winner = None

        def visit(self):
            return [ self.paddle, self.ball ]

        # Recomputes the position of the ball, handles bounces, and
        # draws the screen.
        def render(self, width, height, st, at):

            # The Render object we'll be drawing into.
            r = renpy.Render(width, height)

            # Figure out the time elapsed since the previous frame.
            if self.oldst is None:
                self.oldst = st

            dtime = st - self.oldst
            self.oldst = st

            # Figure out where we want to move the ball to.
            speed = dtime * self.bspeed
            oldbx = self.bx

            if self.stuck:
                self.by = self.playery
            else:
                self.bx += self.bdx * speed
                self.by += self.bdy * speed

            # Move the computer's paddle. It wants to go to self.by, but
            # may be limited by it's speed limit.
            cspeed = self.computerspeed * dtime
            if abs(self.by - self.computery) <= cspeed:
                self.computery = self.by
            else:
                self.computery += cspeed * (self.by - self.computery) / abs(self.by - self.computery)

            # Handle bounces.

            # Bounce off of top.
            ball_top = self.COURT_TOP + self.BALL_HEIGHT / 2
            if self.by < ball_top:
                self.by = ball_top + (ball_top - self.by)
                self.bdy = -self.bdy

                if not self.stuck:
                    renpy.sound.play("pong_beep.opus", channel=0)

            # Bounce off bottom.
            ball_bot = self.COURT_BOTTOM - self.BALL_HEIGHT / 2
            if self.by > ball_bot:
                self.by = ball_bot - (self.by - ball_bot)
                self.bdy = -self.bdy

                if not self.stuck:
                    renpy.sound.play("pong_beep.opus", channel=0)

            # This draws a paddle, and checks for bounces.
            def paddle(px, py, hotside):

                # Render the paddle image. We give it an 800x600 area
                # to render into, knowing that images will render smaller.
                # (This isn't the case with all displayables. Solid, Frame,
                # and Fixed will expand to fill the space allotted.)
                # We also pass in st and at.
                pi = renpy.render(self.paddle, width, height, st, at)

                # renpy.render returns a Render object, which we can
                # blit to the Render we're making.
                r.blit(pi, (int(px), int(py - self.PADDLE_HEIGHT / 2)))

                if py - self.PADDLE_HEIGHT / 2 <= self.by <= py + self.PADDLE_HEIGHT / 2:

                    hit = False

                    if oldbx >= hotside >= self.bx:
                        self.bx = hotside + (hotside - self.bx)
                        self.bdx = -self.bdx
                        hit = True

                    elif oldbx <= hotside <= self.bx:
                        self.bx = hotside - (self.bx - hotside)
                        self.bdx = -self.bdx
                        hit = True

                    if hit:
                        renpy.sound.play("pong_boop.opus", channel=1)
                        self.bspeed *= 1.10

            # Draw the two paddles.
            paddle(self.PADDLE_X, self.playery, self.PADDLE_X + self.PADDLE_WIDTH)
            paddle(width - self.PADDLE_X - self.PADDLE_WIDTH, self.computery, width - self.PADDLE_X - self.PADDLE_WIDTH)

            # Draw the ball.
            ball = renpy.render(self.ball, width, height, st, at)
            r.blit(ball, (int(self.bx - self.BALL_WIDTH / 2),
                          int(self.by - self.BALL_HEIGHT / 2)))

            # Check for a winner.
            if self.bx < -50:
                self.winner = "eileen"

                # Needed to ensure that event is called, noticing
                # the winner.
                renpy.timeout(0)

            elif self.bx > width + 50:
                self.winner = "player"
                renpy.timeout(0)

            # Ask that we be re-rendered ASAP, so we can show the next
            # frame.
            renpy.redraw(self, 0)

            # Return the Render object.
            return r

        # Handles events.
        def event(self, ev, x, y, st):

            import pygame

            # Mousebutton down == start the game by setting stuck to
            # false.
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                self.stuck = False

                # Ensure the pong screen updates.
                renpy.restart_interaction()

            # Set the position of the player's paddle.
            y = max(y, self.COURT_TOP)
            y = min(y, self.COURT_BOTTOM)
            self.playery = y

            # If we have a winner, return him or her. Otherwise, ignore
            # the current event.
            if self.winner:
                return self.winner
            else:
                raise renpy.IgnoreEvent()
init:

    python:

        import math

        class Shaker(object):

            anchors = {
                'top' : 0.0,
                'center' : 0.5,
                'bottom' : 1.0,
                'left' : 0.0,
                'right' : 1.0,
                }

            def __init__(self, start, child, dist):
                if start is None:
                    start = child.get_placement()
                #
                self.start = [ self.anchors.get(i, i) for i in start ]  # central position
                self.dist = dist    # maximum distance, in pixels, from the starting point
                self.child = child

            def __call__(self, t, sizes):
                # Float to integer... turns floating point numbers to
                # integers.
                def fti(x, r):
                    if x is None:
                        x = 0
                    if isinstance(x, float):
                        return int(x * r)
                    else:
                        return x

                xpos, ypos, xanchor, yanchor = [ fti(a, b) for a, b in zip(self.start, sizes) ]

                xpos = xpos - xanchor
                ypos = ypos - yanchor

                nx = xpos + (1.0-t) * self.dist * (renpy.random.random()*2-1)
                ny = ypos + (1.0-t) * self.dist * (renpy.random.random()*2-1)

                return (int(nx), int(ny), 0, 0)

        def _Shake(start, time, child=None, dist=100.0, **properties):

            move = Shaker(start, child, dist=dist)

            return renpy.display.layout.Motion(move,
                          time,
                          child,
                          add_sizes=True,
                          **properties)

        Shake = renpy.curry(_Shake)
    #

#
init:
    $ sshake = Shake((0, 0, 0, 0), 1.0, dist=15)
init python:
    class MyValue:
        def __init__(self, init_value, min_value=0, max_value=100):
            self.value = 0
            self.min_value = min_value
            self.max_value = max_value
            self.add(init_value)

        def add(self, add_value):
            value = self.value + add_value
            if value <= self.min_value:
                self.value = self.min_value
            elif value >= self.max_value:
                self.value = self.max_value
            else:
                self.value = value

            return

init python:
    renpy.music.register_channel('music2')
image Dice:
    "images/dice_action_0.png"
    pause 0.08
    "images/dice_action_1.png"
    pause 0.08
    "images/dice_action_2.png"
    pause 0.08
    "images/dice_action_3.png"
    pause 0.08
    repeat
image Result1:
    "images/dice_[j].png"
image Result2:
    "images/dice_[k].png"
screen aaa:
    add "Dice" align (0.47,0.5)
    add "Dice" align (0.53,0.5)
screen ccc:
    add "Result1" align (0.47, 0.5)
    add "Result2" align (0.53, 0.5)
screen pong():

    default pong = PongDisplayable()

    add "bg pong field"

    add pong

    text _("玩家"):
        xpos 360
        xanchor 0.5
        ypos 25
        size 40

    text _("艾琳"):
        xpos (1920 - 360)
        xanchor 0.5
        ypos 25
        size 40

    if pong.stuck:
        text _("点击开始"):
            xalign 0.5
            ypos 50
            size 40
# 声明此游戏使用的角色。颜色参数可使角色姓名着色。
define config.main_menu_music = "audio/title1.mp3"
define flashbulb = Fade(0.2, 0.0, 0.8, color='#fff')
define circlewipe = ImageDissolve("imagedissolve circlewipe.png", 1.0, 8)
define d = Character("店员")
define dy = Character("导员")
define h = Character("毕涉")
define u = Character("??")
define g = Character("高姝")
define p = Character("彭哥")
define t = Character("李田所")
define m = Character("妈")
define s = Character("手机")
define f = Character("女生")
define f2 = Character("女生2")
define v = Character("副会长")
define l = Character("团长")
define lr = Character("路人")
define n = Character("娜娜")
define ns = Character("男生")
define st = Character("尸体")
define c = Character("陈语嫣")
define y = Character("医生")
default i=0
default j=0
default k=0
default mt=0.0
default escore=0
default pscore=0
default isg = False
default isn = False
default isc = False
default gdateflag = False
default ndateflag2 = False
default ndateflag3 = False
default ndateflag4 = False
default action1 = False
default count = 0
default week = 0
default day = 0
default tcount = 0
default route = 0
image sky_d = "sky_d.png"
image sky_s = "sky_s.png"
image sky_n = "sky_n.png"
image xm_d = "xm_d.png"
image g_idle = "g_idle.png"
image g_surprised = "g_surprised.png"
image g_verysurprised = "g_verysurprised.png"
image g_giggle = "g_giggle.png"
image st = "st.png"
image g_excited = "g_excited.png"
image g_angry = "g_angry.png"
image g_blush = "g_blush.png"
image g_ahem = "g_ahem.png"
image g_eating1 = "g_eating1.png"
# 游戏在此开始。
label play_pong:
    window hide  # Hide the window and  quick menu while in pong
    $ quick_menu = False
    call screen pong
    $ quick_menu = True
    window show
    if _return == "eileen":
        $escore+=1
        "你输了"
        "[pscore]：[escore]"
        jump pong_done
    else:
        $pscore+=1
        "恭喜你，你赢了"
        "[pscore]：[escore]"
        jump pong_done
label pong_done:
    if pscore==2 or escore==2:
        "游戏结束，比分[pscore]：[escore]"
        if pscore==2 and escore==0:
            $marks.add(-10)
            $stress.add(-30)
            "压力-30,学习成绩-10"
        elif pscore==2 and escore==1:
            $marks.add(-10)
            $stress.add(-20)
            "压力-20,学习成绩-10"
        elif pscore==1 and escore==2:
            $marks.add(-10)
            "学习成绩-10"
        elif pscore==0 and escore==2:
            $marks.add(-10)
            $stress.add(10)
            "压力+10,学习成绩-10"
        jump timechange
    else:
        "下一局开始"
        jump play_pong
label start:
    $ marks = MyValue(0)
    $ stress = MyValue(0)
    $ love_points = MyValue(0)
    scene sky_d with fade
    stop music
    play sound "audio/cicada.mp3"
    "夏日还没有真正过去。"
    play music "audio/daily.mp3"
    "按理来说，九月不属于夏季，但头上自顾自散发着热量的太阳却丝毫没有要休息的意思。"
    h "热死了……"
    "我拖着巨大的行李箱，站在树莓大学门口。"
    stop sound fadeout 0.5
    scene xm_d with fade
    "看着校园里打扮各异的人们，我不禁有种奇妙的感觉。"
    "毕竟中小学都是对学生的着装发型之类的东西有要求的。"
    "如今失去了那些条条框框，我虽然自由了，却也一时难以习惯。"
    h "我真的成年了吗……"
    "法律上我确实成年了，心理上我却有些迷茫。"
    "就比如，当看见呼吁禁止未成年人玩游戏的律令时我会下意识地觉得不妙。"
    "但回过神来，才发现这已经和自己没什么关系了。"
    "简而言之，就是心理上还没有迈过成人的坎吧。"
    "虽然独立生活是没什么问题。"
    h "呃，报到处是在……"
    "我东张西望地不知道该往哪走。"
    voice "voice/g1.mp3"
    u "同学，请问你是新生吗？"
    voice sustain
    play sound poke
    "有人从背后碰了碰我的肩膀。"
    "我转过头去——"
    play music "audio/g.mp3" fadeout 1.0 fadein 1.0
    show g_idle with dissolve
    "是一位打扮成熟的漂亮姐姐。"
    h "……呃"
    "我好紧张。我本来就不怎么擅长和人交流，偏偏还碰见异性来找我搭话，那就更没辙了。"
    hide g_idle
    show g_surprised
    u "同学？"
    h "呃，我是新生，那个，我第一次，就是第一次上大学……"
    "完蛋。芭比Q了。为什么只有说出口才发现自己说错话了呢？"
    "结结巴巴的不说，什么叫第一次上大学？难道还要上第二次三次吗？？？"
    "现在就是非常后悔。我低下头去，不敢看对面人的表情。"
    hide g_surprised
    show g_giggle
    u "……噗"
    "她忍不住笑了。"
    hide g_giggle
    show g_idle
    u "你别那么紧张嘛！我又不会吃人。"
    "她说着，掏出自己的学生证给我看。"
    g "我是高你一届的学姐，我叫高姝，这次负责接待你们新生。"
    g "你以后有什么问题，就直接找我好啦！"
    hide g_idle
    show g_smile
    g "来，我们加一下微信。"
    "她的话里好像有什么魔力，反正就是让人不知不觉想要相信她。"
    "我掏出手机，乖乖和学姐加上了微信好友。"
    hide g_smile
    show g_idle
    g "我看看……你叫毕涉，那我就直接叫你名字啦！"
    h "……好。"
    scene xxgc with fade
    show g_smile
    g "那我先带你去报道，弄完了我再带你去看看食堂宿舍什么的。"
    h "好，谢谢学姐。"
    hide g_smile with dissolve
    "于是我跟着她踏进了学校大门。"
    "迎来了，我大学生活的第一天。"
    show dark with circlewipe
    hide dark with circlewipe
    "完成报到后。"
    show g_idle with dissolve
    g "好啦，现在手续就办完了。接下来你想先去哪里？食堂还是宿舍？"
    h "食堂吧。"
    hide g_idle
    show g_smile
    g "嗯，那我带你去我最喜欢的那个食堂吧！"
    g "有个窗口的黄焖鸡可好吃了，对了，你爱吃黄焖鸡吗？"
    h "还可以，只要不辣就行。"
    "我暗自松了一口气。没想到这个学姐还挺好相处的。和她交流不用我费多大功夫，她会一个接一个的地找话题跟我说，不给气氛变得尴尬的空隙。"
    scene st with fade
    play music2 "audio/stcrowd.mp3"
    "走进食堂，瞬间飘来一阵浓烈的食物香气。"
    show g_excited with dissolve:
        linear 0.25 xoffset 20
        linear 0.25 xoffset -20
        repeat
    play sound "audio/gshine.mp3"
    g "我们到了。你看那个就是黄焖鸡的窗口，很香对不对？"
    hide g_excited
    show g_surprised
    g "咦，不过为什么现在就这么香……"
    "学姐瞟了一眼食堂墙上的挂钟。"
    hide g_surprised
    show g_verysurprised:
        xzoom -1.0 yzoom 1.0
        pause 0.5
        xzoom 1.0 yzoom 1.0
        pause 0.5
        repeat
    play sound "audio/tsukomi.mp3"
    g "啊不好，都这个点了！"
    hide g_verysurprised
    show g_excited
    g "毕涉，你饿不饿？"
    h "……啊？"
    "突然被这么一问，我也懵了。"
    hide g_excited
    show g_excited:
        zoom 1.75
        xanchor 0.5 yanchor 0.5
        xpos 0.5 ypos 1.7
        linear 2.0 yoffset -1000
    "我本来想说不饿，但是学姐的眼神怎么看都写着“快说你饿了”几个字。"
    h "呃，那我也饿了。"
    hide g_excited
    show g_angry
    g "“也”是什么意思嘛！不要小看学姐，学姐的胃是很强的！"
    play sound "audio/ghungry.mp3"
    "咕~~~~~~"
    hide g_angry
    show g_verysurprised:
        linear 0.25 xoffset 20
        linear 0.25 xoffset -20
        repeat
    "学姐的胃很强（指诚实）。我努力憋着笑，导致自己的表情拧成了一团。"
    hide g_verysurprised
    show g_blush
    play music "audio/funny.mp3" fadeout 0.5 fadein 0.5
    g "咳咳。（清嗓子）"
    hide g_blush
    show g_excited
    g "既然你也饿了，不如我们就在这里一起吃饭吧。"
    h "可是我才拿到学生卡，里面没钱——"
    hide g_excited
    show g_excited:
        zoom 1.75
        xanchor 0.5 yanchor 0.5
        xpos 0.5 ypos 0.7
    g "没事，学姐请你！就当安利我最爱的黄焖鸡了！"
    "看来学姐已经擅自决定了吃什么。"
    "我们两人各自端着一份黄焖鸡饭和一瓶果汁，找了张桌子坐下。"
    hide g_excited
    show g_eating1 with dissolve
    g "（嚼嚼嚼）太好吃了，我能吃一辈子。"
    h "那倒不至于。（小声）"
    "学姐开心地扫荡着自己的黄焖鸡饭，完全无视了我的吐槽。"
    show g_eating2
    g "大学食堂可比我高中食堂好吃多了。"
    hide g_eating2
    show g_eating3
    play music "audio/g.mp3" fadeout 0.5 fadein 0.5
    g "对了，我高中是西区从大附中，你呢？"
    "她看似不经意地问道。"
    h "我是东区会文中学毕业的……诶不对，学姐怎么直接开始问中学了，不应该先问我老家是哪的吗？"
    g "听口音就知道了呀，你这口音绝对是老胡同串子了。"
    h "哦哦。"
    hide g_eating3
    show g_eating2
    "我惊讶于她的观察力。学姐这种会来事的人，一定人缘很好吧。"
    "我从小就不善人际关系，基本不会主动和别人交往。"
    "看着这样的学姐，我不由得产生出一个想法——"
    h "“好羡慕啊。”"
    hide g_eating2
    hide g_eating1
    show g_surprised
    g "嗯？"
    "糟了，我怎么说出来了！"
    h "呃没有，就是，这个，我觉得学姐好会和人交流，呃，我很羡慕……"
    "我开始语无伦次地解释。"
    hide g_surprised
    show g_giggle
    "学姐却笑了。"
    g "你不用紧张啊，哈哈哈哈，你说话好好玩。"
    hide g_giggle
    show g_smile
    g "其实你也可以更外向一点呀！"
    h "我可能不行吧，因为我从小就是这个性子……"
    g "你别不信，其实我呀——"
    hide g_smile
    show g_upclose with dissolve
    "学姐突然神神秘秘地凑近我的耳朵。"
    "她身上的香味飘了过来。"
    g "我高中的时候可自闭了呢！都是上大学后才变成现在这样的。"
    "自闭？这个开朗的学姐？"
    hide g_upclose
    show g_idle
    g "真的真的，我当时上大学的时候就想，一定要改变自己。"
    g "不是为了别的什么，我只是想证明我也能做到，我也有改变自己的能力。"
    h "……"
    hide g_idle
    show g_smile
    g "所以你要是愿意，你也肯定能改变的。"
    play sound "audio/gshine.mp3"
    g "当然这也要看你自己啦！总之，有问题就问我吧。"
    "学姐笑眯眯地说。"
    h "（我真的可以做到么……）"
    stop music2 fadeout 1.0
    scene tour with fade
    "吃完饭后，学姐又带我去参观了一下别的地方，像什么教学楼，图书馆，操场之类的。"
    "然后就送我回宿舍了。"
    scene ss_d with fade
    show g_idle with dissolve
    g "明天就要上课了，你可别迟到啊。"
    g "要是挂科了，之后补考或者重修很麻烦的。"
    h "嗯，谢谢学姐。"
    hide g_idle with dissolve
    "虽然很累，但第一天就能认识一个好相处的学姐真是太好了。"
    "不过，我又很快担忧起来。"
    "不知道我的室友是什么样的人呢？"
    play sound"audio/opendoor.mp3"
    scene ssroom with fade
    "我推开了宿舍大门——"
    stop music
    play sound "audio/cheer.mp3"
    u "Surprise——！"
    stop sound
    show ts:
        zoom 1.75
        xoffset -500 yoffset -300
    "？？？"
    hide ts
    show ts with dissolve
    play music "audio/ts.mp3"
    "一个肤色偏黑的寸头男突然出现在门口，吓了我一大跳。"
    play sound "audio/yarimasune.mp3"
    t "你好！我是李田所！"
    h "呃……你好，请问你几岁？"
    "虽然不太礼貌，但我还是问出口了。"
    "要问为什么，那就是他实在长得不太像我的同龄人。"
    play sound "audio/24astudent.mp3"
    t "24岁。是学生！"
    h "住宿舍的除了学生还能有什么人。"
    "我忍不住对这个第一次见面的室友吐槽道。"
    play sound "audio/yarimasune.mp3"
    t "身高170，体重74公斤。"
    "可是我没问啊。"
    t "有什么关系，以后我们都是室友了，互相了解了解不是应该的嘛。"
    "虽然我一直在吐槽他，但用不了多久，我们就熟悉了起来。"
    "还一起去澡堂洗了澡。"
    hide ts
    stop music
    play sound "audio/footsteps.mp3"
    show dark with circlewipe
    hide dark with circlewipe
    stop sound
    play music "audio/zzz.mp3"
    "晚上，我躺在自己的床上思考人生。"
    "李田所的呼噜声已经响了一个小时，但我还没有睡着的意思。"
    h "（像学姐那样，改变自己……）"
    h "（就凭我能行吗……）"
    show g_memory with flashbulb
    g "我只是想证明我也能做到，我也有改变自己的能力。"
    hide g_memory with flashbulb
    play music "audio/hdetermined.mp3"
    h "！！"
    h "不对。我要去做。我一定也行的。"
    h "我也要证明我有那个能力。"
    "我想起小时候自己被其他孩子欺负的场景——"
    h "（我一定要改变自己！让那些欺负过我的人——）"
    play sound "audio/hdenden.mp3"
    h"都吃屎去吧！！！！！"
    stop music
    play sound "audio/hghg.mp3"
    t "呼噜~呼噜~哼？？？（被惊醒）哼啊~哼哼~"
    play music "audio/zzz.mp3"
    "不好，不小心说出了内心话，好像把室友吵醒了。"
    "总之，还是快睡吧。"
    "我一定要拿到好成绩，还要交好多朋友，度过有意义的四年！"
    "我在心里暗暗发誓。"
    show dark with circlewipe
    scene js_s with circlewipe
    play music "audio/stable.mp3"
    "上完了一天的课，我脑子晕乎乎的转不过来。"
    "找学姐借笔记吧……"
    play sound "audio/typing.wav"
    "我点开微信，快速敲打着键盘。"
    show biji1 with dissolve
    play sound "audio/message.mp3"
    h "“学姐，请问可不可以借我高数上的笔记？”"
    play sound "audio/message.mp3"
    "很快，学姐的回复就发了过来。"
    hide biji1
    show biji2
    g "“等我做完学生会的工作就给你拿”"
    play sound "audio/message.mp3"
    hide biji2
    show biji3
    play sound "audio/message.mp3"
    g "“要不你来女生宿舍这边找我吧，我给你拿下楼”"
    "女生宿舍吗……总觉得靠近那块地方很不好意思。"
    "但是，我这可是为了学习。是正当的！嗯。"
    hide biji3
    show biji4
    play sound "audio/message.mp3"
    h "“好的，请问那我大概多久过去比较合适”"
    hide biji4
    show biji5
    play sound "audio/message.mp3"
    g "“你说话不用这么毕恭毕敬的啦，都是同龄人，轻松一点才好嘛（=w=）”"
    hide biji5
    show biji6
    play sound "audio/message.mp3"
    g "“那就半小时后见（‘▽<）”"
    hide biji6
    show biji7
    play sound "audio/message.mp3"
    h "“okk（' w '）”"
    "我学着学姐的样子发了个颜文字过去。"
    "回宿舍休息一会再去好了。"
    scene ssroom with fade
    play sound "audio/wechatmessage.mp3"
    "刚回到宿舍，手机的提示音却再度响了起来。"
    show mama1 with dissolve
    m "“儿子，大学生活怎么样？还习惯吗？”"
    play sound "audio/message.mp3"
    hide mama1
    show mama2
    m "“爸爸妈妈虽然不能回去陪你，但我们的心是跟你在一起的。”"
    play sound "audio/message.mp3"
    hide mama2
    show mama3
    m "“对了，你还记不记得娜娜？小时候你俩经常一块玩的。”"
    play sound "audio/message.mp3"
    hide mama3
    show mama4
    m "“我和你爸爸这次调到俄罗斯了。十一放假你要不要来这边？你可以去她们家玩。”"
    play music "audio/title.mp3"
    h "是妈妈啊……"
    "我的家虽然在本地，但父母因为工作原因常年滞留在海外。"
    "他们不在的时候，每次回到家，迎接我的只有寂静的一片黑暗。"
    "所以我早就习惯一个人生活了。"
    "不过偶尔，还是会感到孤独。"
    "虽然父母也经常给我发微信，打电话，但又怎么比得过真正在我身边呢？"
    "小时候，我还能哭着撒娇求他们不要走。"
    "但现在，随着年龄的增长，我失去了那样做的资格。"
    "所以不过是寂寞时，做些别的事来转移注意力罢了。"
    "我真正想要的，果然还是来自他人的关怀。"
    "要看得见摸得着的那种。"
    "隔着网络的关心又有什么用？就算说的再好听，也只是冷冰冰的数据。"
    play sound "audio/message.mp3"
    hide mama4
    show mama5
    h "“我没事，不用管我。我也不想去别人家。”"
    play sound "audio/message.mp3"
    hide mama5
    show mama6
    m "“别这么说嘛。爸爸妈妈是在关心你啊！”"
    play sound "audio/message.mp3"
    hide mama6
    show mama7
    m "“而且娜娜好像挺想见你一面的，你好好想想吧。”"
    "娜娜。我的发小。我小时候最好的朋友。"
    "也是……我的初恋。"
    "我曾经以为，我们会要好一辈子。"
    "但她初中的时候，和全家人一起回了她爸爸的祖国俄罗斯。"
    "并没有提前告诉我。"
    "就像我的父母要离开我去工作的时候，特意等我睡着了再出门一样。"
    "大家都是骗子。"
    "我的初恋早就结束了。我也以为自己早就忘了她。"
    "但听到“她想见我”的时候，心脏不知为何还是一颤。"
    h "……"
    "如果我之后见到她的话，我该说些什么呢？"
    "怪她为什么不辞而别？说我以前喜欢过她？问她过得好不好？"
    "蠢死了。"
    h "（总之先找个理由推掉吧。）"
    menu :
        h "“我去不了。因为——”"
        "“我加入了学生会，工作很忙”":
            jump groute
        "“我和室友约好了去他老家玩”":
            jump alt1
    return
image tour:
    "images/js_d.png" with dissolve
    pause 1.0
    "images/cc_d.png" with dissolve
    pause 1.0
    "images/tsg.png" with dissolve
    pause 1.0
    "images/st_d.jpg" with dissolve
    pause 1.0
    repeat
label alt1:
    play music "audio/ts.mp3"
    h "（对了，室友……）"
    play sound "audio/typing.wav"
    h "（就用这个理由搪塞过去吧。）"
    play sound "audio/message.mp3"
    h "“其实室友跟我关系不错，他叫我十一跟他去老家玩。”"
    play sound "audio/message.mp3"
    h "“所以实在没时间过去那边。”"
    "母亲马上发来了消息。"
    play sound "audio/message.mp3"
    hide mama7
    show sy1
    m "“这么快就交到朋友啦！真不错，妈妈为你骄傲！”"
    "还有一个大拇指表情包。"
    play sound "audio/message.mp3"
    hide sy1
    show sy2
    m "“那到时候你要多少钱就跟妈妈说，去别人家记得要带点礼物……”"
    play sound "audio/message.mp3"
    hide sy2
    show sy3
    m "“对了，你室友老家是哪儿的啊？”"
    "是啥来着……昨天晚上他好像说过。"
    play sound "audio/message.mp3"
    hide sy3
    show sy4
    h "“下北泽。”"
    play sound "audio/message.mp3"
    hide sy4
    show sy5
    m "“没听说过。到时候你多拍几张照片啊。”"
    play sound "audio/message.mp3"
    hide sy5
    show sy6
    h "“知道了。”"
    play sound "audio/wechatskype.mp3"
    hide sy6
    show sy7
    "我本以为对话到此就该结束了，没想到母亲直接打了视频电话过来。"
    "我不太情愿地接了起来。"
    "视频那头的母亲笑眯眯的。"
    m "儿子，你室友在吗，妈想跟他说两句。"
    h "说什么呀，他不——"
    hide sy7
    show ts with dissolve:
        xpos 0.5
        linear 1.0 xoffset -960
    play sound "audio/jingju.wav"
    t "大王回营啊~！（模仿京剧）"
    "完犊子。这个时候最不该出现的人出现了。"
    hide ts
    show ts:
        zoom 1.75
        xoffset -500 yoffset -300
    t "干什么呢毕涉？"
    "他凑过来探头探脑地看我的手机。"
    m "你就是圆圆，哦不毕涉的室友李同学吧？"
    hide ts
    show ts
    play sound "audio/yarimasune.mp3"
    t "诶我就是，阿姨好阿姨好！"
    m "你好你好。我听毕涉说你很照顾他呀？谢谢你啊。"
    t "没有阿姨，我俩是室友嘛，应该的应该的。"
    "出现了，太极拳式对话。我不爱跟人说话的其中一个原因就是这个，总要说些麻烦又没什么实际意义的社交辞令。"
    m "不好意思啊，我和他爸爸都常年在国外，巴拉巴拉……"
    t "您们工作辛苦了，巴拉巴拉……"
    "他们聊得不亦乐乎。真不知道还要说多久。"
    "不知道过了多长时间。"
    t "嗯嗯好的阿姨，再见！"
    play sound "audio/hangup.mp3"
    "终于挂电话了。"
    t "毕涉。"
    h "干嘛。"
    t "听说你十一要来我家玩啊？"
    "惨了。我妈告诉他了。"
    h "这个就是糊弄我妈的，你别放心上。"
    hide ts
    show ts:
        linear 0.25 xoffset 20
        linear 0.25 xoffset -20
        repeat
    t "不要这么冷淡嘛，你假戏真做不就行了。"
    t "我家很大的，你玩累了就直接睡，没关系的。"
    t "哦我家阳台也很大，我平时喜欢在阳台晒日光浴，你到时候也试试吧。"
    "他说得眉飞色舞，好像真的很欢迎我一样。"
    h "知道了知道了。"
    "虽然嘴上没什么，我心里却也有淡淡的喜悦。"
    "如果这样的关系能被称为“朋友”的话，那我还是第一次交到同性好友。"
    stop music
    $count=0
    $route = 0
    jump daily0
    return
label groute:
    play music "audio/gevent.mp3"
    h "（对了，学姐就是学生会的，而且她说工作很忙……）"
    play sound "audio/typing.wav"
    h "（就用这个理由搪塞过去吧。）"
    play sound "audio/message.mp3"
    hide mama7
    show xsh
    h "“其实我进学生会了，工作很多很忙，而且我们十一要组织团建的。”"
    play sound "audio/message.mp3"
    h "“所以实在没时间过去那边。”"
    hide xsh
    "过了一会儿……"
    "母亲才发来消息。"
    play sound "audio/wechatmessage.mp3"
    show xsh2
    m "“进学生会啦？那好，那好，要多跟别人交流啊！”"
    play sound "audio/message.mp3"
    hide xsh2
    show xsh3
    m "“妈妈真为你开心。那你们到时候就好好玩吧，最好多交几个朋友，说不定你还能找到女朋友呢！”"
    play sound "audio/message.mp3"
    hide xsh3
    show xsh4
    m "“——对了，学习也不能放松啊！”"
    "她很高兴。很难说是因为儿子做了学生干部还是因为儿子愿意和别人交流了。"
    "虽然，这只是儿子的一个借口罢了。"
    play sound "audio/message.mp3"
    hide xsh4
    show xsh5
    h "“知道了。我还要找学姐借笔记，就先不聊了。”"
    play sound "audio/message.mp3"
    hide xsh5
    show xsh6
    m "“好，去吧！”"
    "末了，母亲还发来一个“加油”的表情。"
    h "唉……"
    "虽然夸下海口说自己加入了学生会，但我其实连学生会到底是干什么的都不清楚。"
    "越想越烦，还是赶紧去找学姐吧。"
    play sound "audio/footsteps.mp3"
    scene ss_n with fade
    "女生宿舍前。"
    "我等了一会，学姐才穿着睡衣下楼来。"
    show g_pjidle with dissolve
    play music "audio/g.mp3"
    g "不好意思呀，让你久等了。"
    "她把一个厚厚的笔记本交到我手里。"
    h "没有，谢谢学姐。"
    g "怎么感觉你还是有点拘谨啊，不用客气的。"
    g "批了一晚上社团申请表，累死了。"
    g "或许是想活跃气氛，学姐说着，松了松自己的胳膊。"
    h "学生会的工作很累吗？"
    g "就还好吧，只是开学的时候累一点而已。"
    g "像要处理社团活动啊，给新生写学校生活指南，团委党委推送什么的。"
    hide g_pjidle
    show g_pjsurprised
    g "对了，说到这个，你有没有想过加入社团？"
    "她笑吟吟地看着我。"
    h "呃，还没有。我们学校都有什么社团啊？"
    hide g_pjsurprised
    show g_face
    g "什么都有，体育文学语言动漫……哦，还有我们学生会，负责管社团。"
    "学姐调皮地笑了笑。"
    h "嗯？可是我听说社团是社联管的。"
    hide g_face
    show g_pjidle
    g "我们学校的社联属于学生会分部啦，都是为学生服务，学校就直接把这俩合并了。"
    h "哦哦。"
    h "所以学姐才会负责批申请表啊。"
    hide g_pjidle
    show g_pjsurprised
    g "对呀。那，你有没有感兴趣的？"
    "就在我们聊着社团的时候，冷不丁从学姐背后钻出来一个女生。"
    play music "audio/funny.mp3"
    hide g_pjsurprised
    show g_pjsurprised:
        xpos -0.25
    show nvsheng with dissolve:
        xpos 0.6
        ypos 0.2
        zoom 1.9
        pause 0.4
        linear 0.1 yoffset 10
        linear 0.1 yoffset -10
        linear 0.1 yoffset 10
        linear 0.1 yoffset -10
    f "姝姝，行啊你。跟男朋友在宿舍门口依依不舍呢？"
    "听见“男朋友”一词，我的脸上瞬间烧了起来。"
    h "呃，这……"
    "我向学姐投去求助的眼神，内心却莫名跃动不已。"
    hide g_pjsurprised
    show g_pjidle:
        xpos -0.25
        linear 0.1 yoffset 10
        linear 0.1 yoffset -10
        linear 0.1 yoffset 10
        linear 0.1 yoffset -10
    hide nvsheng
    show nvsheng:
        xpos 0.6
        ypos 0.2
        zoom 1.9
    g "（笑着）干嘛，你吃醋啊？"
    "学姐明显是在打趣，但我脑子里已经一片空白了。"
    "她没有否认。"
    "这是什么？是学姐对我有好感的意思？是说我们有发展的可能性？"
    "不是吧，不要太自我感觉良好了。"
    "但是，但是，但是……"
    "我恐怕对学姐是有好感的。对这个，在第一天就帮助我，请我吃饭，还鼓励我改变的热心大姐姐。"
    "如果能和这样的人做朋友，我是求之不得的。"
    "自从小时候和娜娜分别之后，我再没有过交心的人。"
    "据说刚出壳的小鸡会把见到的第一个动物当成自己的妈妈。我会不会，也是因为这样才下意识地依赖着学姐呢？"
    hide g_pjidle
    show g_pjidle:
        xpos -0.25
    hide nvsheng
    show nvsheng:
        xpos 0.6
        ypos 0.2
        zoom 1.9
        linear 0.1 yoffset 10
        linear 0.1 yoffset -10
        linear 0.1 yoffset 10
        linear 0.1 yoffset -10
    f "咦，他怎么脸红了——哦~"
    hide nvsheng
    show nvsheng:
        xpos 0.6
        ypos 0.2
        zoom 2.0
        linear 0.2 zoom 2.2
        linear 0.2 yoffset -50
        linear 0.2 yoffset 50
        linear 0.2 yoffset -50
        linear 0.2 yoffset 50
    "女生兴许是看出了什么，又转到我身边，拍拍我的肩。"
    f "加油啊！男孩子还是主动一点的好！"
    hide nvsheng with dissolve
    "说完，她蹦蹦跳跳上楼去了。"
    hide g_pjidle
    show g_moved with dissolve
    "只留下我和学姐，还有也许是粉红色的空气。"
    play music "audio/gevent.mp3"
    h "……学姐。"
    "我抬起头，直视她的眼睛，才发现她竟然也有微微的脸红。"
    hide g_moved
    show g_pjsurprised
    g "——嗯？哦，哦，你说吧。"
    hide g_pjsurprised
    show g_pjidle
    h "我能不能加入学生会？"
    "虽然我对学姐有好感，但要说恋爱，我觉得现在的我是不配的。"
    "但我仍然希望接近她，也许因为这是长大后，第一次有人这么关怀我。"
    "我真心想进学生会。不仅是因为自己对母亲夸下海口，也是因为我确实想为学姐做点什么。"
    h  "我想帮上学姐的忙，能不能告诉我怎么加入学生会？"
    hide g_pjidle
    show g_pjsurprised
    g "欸？啊，当然可以啊。我拿张表给你，你填完给我就行。"
    "说完，学姐像是掩盖害羞一样转过身。"
    hide g_pjsurprised
    show g_pjidle
    g "你稍微等我一会，好吗？"
    h "好。"
    hide g_pjidle with dissolve
    "她进了宿舍，过了一会又拿着表回来了。"
    show g_pjidle with dissolve
    "她把表递给我。"
    g "虽然你说要帮我我挺高兴的，但最好还是依你自己的兴趣决定。"
    h "不止想帮你，其实我还有私心。"
    hide g_pjidle
    show g_pjsurprised
    g "什么私心？"
    h "我想通过学生会的工作改变自己……学姐不是说过，我想改变就能改变吗。"
    "她看起来吃了一惊。"
    hide g_pjsurprised
    show g_face
    g "这样啊……那就祝你成功了！"
    "随即调皮地眨了眨眼睛。"

    g "要是觉得工作无聊，可不许赖我！"
    h "放心吧，那肯定不会的。"
    hide g_face
    show g_pjsurprised
    g "那就，晚安？"
    h "嗯，晚安。"
    "我转身刚迈出一步，学姐又在背后说道。"
    hide g_pjsurprised
    show g_moved
    g "……不管怎么样，谢谢你说想帮我。"
    $count=0
    $route=1
    jump daily1
    return
screen status:
    tag menu
    frame:
        align(1.0,0)
        xysize(300,200)
        hbox:
            spacing 10
            vbox:
                text "学习成绩: [marks.value]"
                text "压力值: [stress.value]"
                text "好感度：[love_points.value]"
                textbutton "退出":
                    action Hide("status")

label chooseroute:
    if route==0:
        call screen map_day0 with fade
    elif route==1:
        call screen map_day1 with fade
    elif route==2:
        call screen map_day2 with fade
    elif route==3:
        call screen map_day3 with fade
    elif route==4:
        call screen map_day0 with fade
    else:
        return
label timechange:
    if tcount==1:
        scene sky_m with fade
        "中午了，该做什么呢？"
        $tcount+=1
        if route==0:
            call screen map_noon0 with fade
        elif route==1:
            call screen map_noon1 with fade
        elif route==2:
            call screen map_noon2 with fade
        elif route==3:
            call screen map_noon3 with fade
        elif route==4:
            call screen map_noon0 with fade
        else:
            return
    elif tcount==2:
        scene sky_s with fade
        "下午了，该做什么呢？"
        $tcount+=1
        if route==0:
            call screen map_afternoon0 with fade
        elif route==1:
            call screen map_afternoon1 with fade
        elif route==2:
            call screen map_afternoon2 with fade
        elif route==3:
            call screen map_afternoon3 with fade
        elif route==4:
            call screen map_afternoon0 with fade
        else:
            return
    elif tcount==3:
        scene sky_n with fade
        "晚上了，该做什么呢？"
        $tcount+=1
        if route==0:
            call screen map_night0 with fade
        elif route==1:
            call screen map_night1 with fade
        elif route==2:
            call screen map_night2 with fade
        elif route==3:
            call screen map_night3 with fade
        elif route==4:
            call screen map_night0 with fade
        else:
            return
    elif tcount==4:
        scene sky_n with fade
        "今天就到这里，睡觉吧。"
        if day==5:
            jump weekend
        else:
            if route==0:
                jump daily0
            elif route==1:
                if count<=20:
                    jump daily1
                elif count>20 and count<=40:
                    jump daily2
            elif route==2:
                jump daily3
            elif route==4:
                jump daily0
label daily0:
    if stress.value==100:
        jump overstress
    $count+=1
    $tcount=1
    if count<=5:
        $week=1
        $day=count
    elif count<=10:
        $week=2
        $day=count-5
    elif count<=15:
        $week=3
        $day=count-10
    elif count<=20:
        $week=4
        $day=count-15
    elif count>30 and count<=35:
        $week=7
        $day=count-30
    elif count<=40:
        $week=8
        $day=count-35
    elif count<=45:
        $week=9
        $day=count-40
    elif count<=50:
        $week=10
        $day=count-45
    scene sky_d with fade
    play music "audio/daily.mp3"
    "今天是第[week]周第[day]天"
    "新的一天开始了，该做什么好呢？"
    jump chooseroute
label daily1:
    if stress.value==100:
        jump overstress
    $count+=1
    $tcount=1
    if count<=5:
        $week=1
        $day=count
    elif count<=10:
        $week=2
        $day=count-5
    elif count<=15:
        $week=3
        $day=count-10
    elif count<=20:
        $week=4
        $day=count-15
    scene sky_d with fade
    play music "audio/daily.mp3"
    "今天是第[week]周第[day]天"
    "新的一天开始了，该做什么好呢？"
    jump chooseroute
label overstress:
    scene stress with fade
    stop music
    play music"audio/NE.mp3"
    "最近总是状态不好。"
    "什么也不想干，翘了课，也不想吃饭，在床上能躺一整天。"
    "学校发现我的异常状况后联系了家长。"
    "父母连忙请假回国带我去看医生。"
    "结果显示我由于压力过大患上了焦虑症。"
    "父母为我办理了休学，让我好好养病。"
    "等我康复了回到学校，一定能过上规划合理的生活吧。"
    "等我康复了……"
    show over with dissolve
    "{b}GAME OVER{/b}"
    $renpy.full_restart()
screen map_day0:
    imagemap:
        idle "buttons.png"
        ground "smap.png"
        hover "buttons_dark.png"
        #pos(100,100)
        xpos 0
        ypos 0
        hotspot(1000,200,500,300) action [Hide("map_day0"),Jump("room")]   #宿舍
        hotspot(760,550,500,300) action [Hide("map_day0"),Jump("classroom")]  #教学楼
        hotspot(760,750,500,300) action [Hide("map_day0"),Jump("library")]   #图书馆
        hotspot(100,800,500,300) action [Hide("map_day0"),Jump("field")]  #操场
        hotspot(1250,550,500,300) action [Hide("map_day0"),Jump("canteen")]  #食堂
screen map_noon0:
    imagemap:
        idle "buttons.png"
        ground "smap.png"
        hover "buttons_dark.png"
        #pos(100,100)
        xpos 0
        ypos 0
        hotspot(1000,200,500,300) action [Hide("map_noon0"),Jump("room")]   #宿舍
        hotspot(760,550,500,300) action [Hide("map_noon0"),Jump("classroom")]  #教学楼
        hotspot(760,750,500,300) action [Hide("map_noon0"),Jump("library")]   #图书馆
        hotspot(100,800,500,300) action [Hide("map_noon0"),Jump("field")]  #操场
        hotspot(1250,550,500,300) action [Hide("map_noon0"),Jump("canteen")]  #食堂
screen map_afternoon0:
    imagemap:
        idle "buttons.png"
        ground "smap.png"
        hover "buttons_dark.png"
        #pos(100,100)
        xpos 0
        ypos 0
        hotspot(1000,200,500,300) action [Hide("map_afternoon0"),Jump("room")]   #宿舍
        hotspot(760,550,500,300) action [Hide("map_afternoon0"),Jump("classroom")]  #教学楼
        hotspot(760,750,500,300) action [Hide("map_afternoon0"),Jump("library")]   #图书馆
        hotspot(100,800,500,300) action [Hide("map_afternoon0"),Jump("field")]  #操场
        hotspot(1250,550,500,300) action [Hide("map_afternoon0"),Jump("canteen")]  #食堂
screen map_night0:
    imagemap:
        idle "buttons.png"
        ground "smap.png"
        hover "buttons_dark.png"
        #pos(100,100)
        xpos 0
        ypos 0
        hotspot(1000,200,500,300) action [Hide("map_night0"),Jump("room")]   #宿舍
        hotspot(760,550,500,300) action [Hide("map_night0"),Jump("classroom")]  #教学楼
        hotspot(760,750,500,300) action [Hide("map_night0"),Jump("library")]   #图书馆
        hotspot(100,800,500,300) action [Hide("map_night0"),Jump("field")]  #操场
        hotspot(1250,550,500,300) action [Hide("map_night0"),Jump("canteen")]  #食堂
screen map_day1:
    imagemap:
        idle "gbuttons.png"
        ground "smap.png"
        hover "gbuttons_dark.png"
        #pos(100,100)
        xpos 0
        ypos 0
        hotspot(1000,200,500,300) action [Hide("map_day1"),Jump("room")]   #宿舍
        hotspot(760,550,500,300) action [Hide("map_day1"),Jump("classroom")]  #教学楼
        hotspot(760,750,500,300) action [Hide("map_day1"),Jump("library")]   #图书馆
        hotspot(100,800,500,300) action [Hide("map_day1"),Jump("field")]  #操场
        hotspot(1250,550,500,300) action [Hide("map_day1"),Jump("canteen")]  #食堂
        hotspot(1300,250,500,300) action [Hide("map_day1"),Jump("studentunion")]  #学生会
screen map_noon1:
    imagemap:
        idle "gbuttons.png"
        ground "smap.png"
        hover "gbuttons_dark.png"
        #pos(100,100)
        xpos 0
        ypos 0
        hotspot(1000,200,500,300) action [Hide("map_noon1"),Jump("room")]   #宿舍
        hotspot(760,550,500,300) action [Hide("map_noon1"),Jump("classroom")]  #教学楼
        hotspot(760,750,500,300) action [Hide("map_noon1"),Jump("library")]   #图书馆
        hotspot(100,800,500,300) action [Hide("map_noon1"),Jump("field")]  #操场
        hotspot(1250,550,500,300) action [Hide("map_noon1"),Jump("canteen")]  #食堂
        hotspot(1300,250,500,300) action [Hide("map_noon1"),Jump("studentunion")]  #学生会
screen map_afternoon1:
    imagemap:
        idle "gbuttons.png"
        ground "smap.png"
        hover "gbuttons_dark.png"
        #pos(100,100)
        xpos 0
        ypos 0
        hotspot(1000,200,500,300) action [Hide("map_afternoon1"),Jump("room")]   #宿舍
        hotspot(760,550,500,300) action [Hide("map_afternoon1"),Jump("classroom")]  #教学楼
        hotspot(760,750,500,300) action [Hide("map_afternoon1"),Jump("library")]   #图书馆
        hotspot(100,800,500,300) action [Hide("map_afternoon1"),Jump("field")]  #操场
        hotspot(1250,550,500,300) action [Hide("map_afternoon1"),Jump("canteen")]  #食堂
        hotspot(1300,250,500,300) action [Hide("map_afternoon1"),Jump("studentunion")]  #学生会
screen map_night1:
    imagemap:
        idle "gbuttons.png"
        ground "smap.png"
        hover "gbuttons_dark.png"
        #pos(100,100)
        xpos 0
        ypos 0
        hotspot(1000,200,500,300) action [Hide("map_night1"),Jump("room")]   #宿舍
        hotspot(760,550,500,300) action [Hide("map_night1"),Jump("classroom")]  #教学楼
        hotspot(760,750,500,300) action [Hide("map_night1"),Jump("library")]   #图书馆
        hotspot(100,800,500,300) action [Hide("map_night1"),Jump("field")]  #操场
        hotspot(1250,550,500,300) action [Hide("map_night1"),Jump("canteen")]  #食堂
        hotspot(1300,250,500,300) action [Hide("map_night1"),Jump("studentunion")]  #学生会
screen map_day2:
    imagemap:
        idle "cbuttons.png"
        ground "smap.png"
        hover "cbuttons_dark.png"
        #pos(100,100)
        xpos 0
        ypos 0
        hotspot(1000,200,500,300) action [Hide("map_day2"),Jump("room")]   #宿舍
        hotspot(760,550,500,300) action [Hide("map_day2"),Jump("classroom")]  #教学楼
        hotspot(760,750,500,300) action [Hide("map_day2"),Jump("library")]   #图书馆
        hotspot(100,800,500,300) action [Hide("map_day2"),Jump("field")]  #操场
        hotspot(1250,550,500,300) action [Hide("map_day2"),Jump("canteen")]  #食堂
        hotspot(1300,250,500,300) action [Hide("map_day1"),Jump("concert")]  #合唱团
screen map_noon2:
    imagemap:
        idle "cbuttons.png"
        ground "smap.png"
        hover "cbuttons_dark.png"
        #pos(100,100)
        xpos 0
        ypos 0
        hotspot(1000,200,500,300) action [Hide("map_noon2"),Jump("room")]   #宿舍
        hotspot(760,550,500,300) action [Hide("map_noon2"),Jump("classroom")]  #教学楼
        hotspot(760,750,500,300) action [Hide("map_noon2"),Jump("library")]   #图书馆
        hotspot(100,800,500,300) action [Hide("map_noon2"),Jump("field")]  #操场
        hotspot(1250,550,500,300) action [Hide("map_noon2"),Jump("canteen")]  #食堂
        hotspot(1300,250,500,300) action [Hide("map_noon2"),Jump("concert")]  #合唱团
screen map_afternoon2:
    imagemap:
        idle "cbuttons.png"
        ground "smap.png"
        hover "cbuttons_dark.png"
        #pos(100,100)
        xpos 0
        ypos 0
        hotspot(1000,200,500,300) action [Hide("map_afternoon2"),Jump("room")]   #宿舍
        hotspot(760,550,500,300) action [Hide("map_afternoon2"),Jump("classroom")]  #教学楼
        hotspot(760,750,500,300) action [Hide("map_afternoon2"),Jump("library")]   #图书馆
        hotspot(100,800,500,300) action [Hide("map_afternoon2"),Jump("field")]  #操场
        hotspot(1250,550,500,300) action [Hide("map_afternoon2"),Jump("canteen")]  #食堂
        hotspot(1300,250,500,300) action [Hide("map_afternoon2"),Jump("concert")]  #合唱团
screen map_night2:
    imagemap:
        idle "cbuttons.png"
        ground "smap.png"
        hover "cbuttons_dark.png"
        #pos(100,100)
        xpos 0
        ypos 0
        hotspot(1000,200,500,300) action [Hide("map_night2"),Jump("room")]   #宿舍
        hotspot(760,550,500,300) action [Hide("map_night2"),Jump("classroom")]  #教学楼
        hotspot(760,750,500,300) action [Hide("map_night2"),Jump("library")]   #图书馆
        hotspot(100,800,500,300) action [Hide("map_night2"),Jump("field")]  #操场
        hotspot(1250,550,500,300) action [Hide("map_night2"),Jump("canteen")]  #食堂
        hotspot(1300,250,500,300) action [Hide("map_night2"),Jump("concert")]  #合唱团
label room:
    scene ssroom with fade
    menu:
        "学习":
            jump study_room
        "玩游戏":
            jump game_room
        "休息":
            jump rest_room
label game_room:
    "开始玩游戏"
    jump play_pong
label study_room:
    "你在宿舍认真学习了一段时间"
    $marks.add(10)
    $stress.add(10)
    "学习成绩+10，压力+10"
    jump timechange
label rest_room:
    $i=renpy.random.randint(0,11)
    if i==0:
        jump rest_room0
    elif i==1:
        jump rest_room1
    elif i==2:
        jump rest_room2
    elif i==3:
        jump rest_room3
    elif i==4:
        jump rest_room4
    elif i==5:
        jump rest_room5
    elif i==6:
        jump rest_room6
    elif i==7:
        jump rest_room7
    elif i==8:
        jump rest_room8
    elif i==9:
        jump rest_room9
    elif i==10:
        jump rest_room10
    elif i==11:
        jump rest_room11
    return
label rest_room0:
    "隔壁宿舍举办了女装大会，你大为震惊但是觉得很好笑，压力-10"
    $stress.add(-10)
    jump timechange
label rest_room1:
    "玩手游抽卡出货，压力-20"
    $stress.add(-20)
    jump timechange
label rest_room2:
    "玩手游抽卡沉船，压力+20"
    $stress.add(20)
    jump timechange
label rest_room3:
    "做了挂科的噩梦，醒了之后发誓要好好学习，成绩+2 压力+10"
    $stress.add(10)
    $marks.add(2)
    jump timechange
label rest_room4:
    "室友请你喝家乡特产红茶，你喝了之后昏睡到第二天中午，错过了上课时间，成绩-10"
    $marks.add(-10)
    $count+=1
    $tcount=2
    jump timechange
label rest_room5:
    "隔壁宿舍的学霸给你辅导了功课，成绩+10 压力-10"
    $stress.add(-10)
    $marks.add(10)
    jump timechange
label rest_room6:
    "隔壁宿舍的学霸穿着女装给你辅导了功课，成绩- 压力-"
    $stress.add(-10)
    $marks.add(-10)
    jump timechange
label rest_room7:
    "和室友一起学习，成绩+10"
    $marks.add(10)
    jump timechange
label rest_room8:
    "和室友一起打游戏成功吃鸡，压力-10"
    $stress.add(-10)
    jump timechange
label rest_room9:
    "去上厕所时发现有人拉屎不冲水，压力+10"
    $stress.add(10)
    jump timechange
label rest_room10:
    "隔壁宿舍聚会喝酒吵到你休息了，压力+20"
    $stress.add(20)
    jump timechange
label rest_room11:
    "你和室友聊天的时候偶然间悟到了一些知识点，学习成绩+20"
    $marks.add(20)
    jump timechange
label classroom:
    if tcount==1 and tcount==2:
        scene js_d with fade
    elif tcount==3:
        scene js_s with fade
    elif tcount==4:
        scene jxl_n with fade
    $i=renpy.random.randint(0,11)
    if i==0:
        jump classroom0
    elif i==1:
        jump classroom1
    elif i==2:
        jump classroom2
    elif i==3:
        jump classroom3
    elif i==4:
        jump classroom4
    elif i==5:
        jump classroom5
    elif i==6:
        jump classroom6
    elif i==7:
        jump classroom7
    elif i==8:
        jump classroom8
    elif i==9:
        jump classroom9
    elif i==10:
        jump classroom10
    elif i==11:
        jump classroom11
    return
label classroom0:
    "上课时认真听讲，学习成绩+10，压力+10"
    $marks.add(10)
    $stress.add(10)
    jump timechange
label classroom1:
    "无意中捡到了一本高数秘籍，读后觉得自己的学力大大提高，成绩+30"
    $marks.add(30)
    jump timechange
label classroom2:
    "忘了预习了，老师讲的东西全都没听懂，成绩-5"
    $marks.add(-5)
    jump timechange
label classroom3:
    "上课时走神了，成绩-10"
    $marks.add(-10)
    jump timechange
label classroom4:
    "上课的时候被窗外的小鸟吸引了目光，成绩-10 压力-10"
    $marks.add(-10)
    $stress.add(-10)
    jump timechange
label classroom5:
    "老师教的东西自己预习了，无所畏惧，学习成绩+10"
    $marks.add(10)
    jump timechange
label classroom6:
    "老师教的东西都会，趴下睡会儿，压力-20"
    $stress.add(-20)
    jump timechange
label classroom7:
    "上课的时候有猫猫闯入课堂，成绩+10 压力-10"
    $stress.add(-10)
    $marks.add(10)
    jump timechange
label classroom8:
    "后排的同学不知道在干什么，时不时发出恶心的笑声，成绩+5 压力+5"
    $stress.add(5)
    $marks.add(5)
    jump timechange
label classroom9:
    "老师讲得太难了，听不懂，成绩+2 压力+10"
    $stress.add(10)
    $marks.add(2)
    jump timechange
label classroom10:
    "老师讲得东西你完全听明白了，成绩+20 压力-10"
    $marks.add(10)
    $stress.add(-10)
    jump timechange
label classroom11:
    "上课的时候，坐在前面的同学散发出没有洗澡的味道，导致无法专心听课，成绩-10 压力+10"
    $marks.add(-10)
    $stress.add(10)
    jump timechange
label library:
    scene tsg with fade
    $i=renpy.random.randint(0,1)
    if i==0:
        jump library0
    elif i==1:
        jump library1
label library0:
    "一个人在图书馆学习了一段时间，学习成绩+5"
    $marks.add(+5)
    jump timechange
label library1:
    "遇到了认识的同学一起学习，学习成绩+10"
    $marks.add(10)
    jump timechange
label field:
    if tcount==1 and tcount==2:
        scene cc_d with fade
    elif tcount==3:
        scene cc_s with fade
    elif tcount==4:
        scene cc_n with fade
    $i=renpy.random.randint(1,3)
    if i==1:
        jump field1
    elif i==2:
        jump field2
    elif i==3:
        jump field3
    return
label field1:
    "锻炼成功，压力-5"
    $stress.add(-5)
    jump timechange
label field2:
    "锻炼大成功，压力-10"
    $stress.add(-10)
    jump timechange
label field3:
    "锻炼极大成功，压力-20"
    $stress.add(-20)
    jump timechange
label canteen:
    if tcount==1 and tcount==2:
        scene st_d with fade
    elif tcount==3:
        scene st_s with fade
    elif tcount==4:
        scene st_n with fade
    $i=renpy.random.randint(0,3)
    if i==0:
        jump canteen0
    elif i==1:
        jump canteen1
    elif i==2:
        jump canteen2
    elif i==3:
        jump canteen3
    elif i==4:
        jump canteen4
    elif i==5:
        jump canteen5
    elif i==6:
        jump canteen6
    elif i==7:
        jump canteen7
    elif i==8:
        jump canteen8
    elif i==9:
        jump canteen9
    elif i==10:
        jump canteen10
    elif i==11:
        jump canteen11
    elif i==12:
        jump canteen12
    elif i==13:
        jump canteen13
    elif i==14:
        jump canteen14
    elif i==15:
        jump canteen15
    return
label canteen0:
    "今天吃到了火龙果炒肉，实在是太奇葩了，压力+10"
    $stress.add(10)
    jump timechange
label canteen1:
    "今天吃到了拔丝黄瓜，有点怪，压力+5"
    $stress.add(5)
    jump timechange
label canteen2:
    "今天吃到了红烧胖大海，好怪，压力+5"
    $stress.add(5)
    jump timechange
label canteen3:
    "今天吃到了油炸辣白菜，好怪，压力+3"
    $stress.add(3)
    jump timechange
label canteen4:
    "今天吃到了糖醋猪乳头，好怪，压力+3"
    $stress.add(3)
    jump timechange
label canteen5:
    "买了一屉包子，咬了一口发现是咸鱼馅的，压力+5"
    $stress.add(20)
    jump timechange
label canteen6:
    "买了一屉包子，皮薄馅大很好吃，压力-10"
    $stress.add(-10)
    jump timechange
label canteen7:
    "买了一屉包子，但是里面没有馅，压力+10"
    $stress.add(10)
    jump timechange
label canteen8:
    "今天吃到了红烧排骨，很好吃，压力-10"
    $stress.add(-10)
    jump timechange
label canteen9:
    "今天吃到了喜欢的干拌面，很好吃，压力-20"
    $stress.add(-20)
    jump timechange
label canteen10:
    "今天吃到了喜欢的牛肉汤粉，很好吃，压力-20"
    $stress.add(-20)
    jump timechange
label canteen11:
    "今天吃到了回锅肉，很好吃，压力-5"
    $stress.add(-5)
    jump timechange
label canteen12:
    "今天吃到了黑椒牛柳，很好吃，压力-5"
    $stress.add(-5)
    jump timechange
label canteen13:
    "今天吃到了汤罐面，很好吃，压力-5"
    $stress.add(-5)
    jump timechange
label canteen14:
    "今天吃到了黄焖鸡，很好吃，压力-5"
    $stress.add(-5)
    jump timechange
label canteen15:
    "今天吃到了北京烤鸭套餐，很好吃，压力-10"
    $stress.add(-10)
    jump timechange
label studentunion:
    if tcount==1 and tcount==2:
        scene xsh_d with fade
    elif tcount==3 and tcount==4:
        scene xsh_s with fade
    $i=renpy.random.randint(0,3)
    if i==0:
        jump studentunion0
    elif i==1:
        jump studentunion1
    elif i==2:
        jump studentunion2
    elif i==3:
        jump studentunion3
label studentunion0:
    "在学生会处理表格，工作了一段时间，好感度+5，压力+5"
    $love_points.add(+5)
    $stress.add(5)
    jump timechange
label studentunion1:
    "和高姝一起工作，好感度+10，压力-5"
    $love_points.add(10)
    $stress.add(-5)
    jump timechange
label studentunion2:
    "在学生会室里休息了一会儿，压力-5"
    $stress.add(5)
    jump timechange
label studentunion3:
    "和学生会的人聊天，压力-5"
    $stress.add(-5)
    jump timechange
label studentunion4:
    "在学生会摸鱼打游戏，压力-10"
    $stress.add(-10)
    jump timechange
label studentunion5:
    "在高姝工作的时候偷偷在本子上画她的侧脸，被她发现了，好感度+5"
    $love_points.add(5)
    jump timechange
label studentunion6:
    "被高姝拉过来一起摸鱼，好感度+10，压力-10"
    $love_points.add(10)
    $stress.add(-10)
    jump timechange
label weekend:
    play music "audio/stable.mp3"
    scene ssroom with fade
    menu:
        "周末了，该干什么呢？"
        "宿舍":
            jump weekend_room
        "回家":
            jump weekend_home
        "和高姝约会" if isg:
            jump gdate
        "和娜娜约会" if isn:

            jump ndate
label gdate:
    if gdateflag==False:
        jump gdate1
    elif gdateflag==True:
        jump gdate2
label gdate1:
    $gdateflag = True
    scene beach with fade
    play music "audio/date.mp3"
    show g_b1 with dissolve
    play music2 "audio/beach.mp3"
    g "大——海——呀——"
    "小长假，我和学姐来到了海边玩。"
    "学姐兴奋地对着海面大喊。"
    h "一般来说不是爬山的时候才会这样吗？"
    hide g_b1
    show g_b2
    g "不要在意这些细节，开心就好~"
    hide g_b2
    show g_b7
    g "你也来试试？能发泄压力哦。"
    h "好吧。"
    h "啊——啊——"
    "我也对着大海叫了起来。"
    "压力-"
    "哇，居然真的轻松了不少！"
    hide g_b7
    show g_b3
    g "怎么样？"
    h "还挺有效的，我再试试。"
    menu:
        h "喊什么好呢？"
        "姝姝我爱你":
            jump gdate1_1
        "世界毁灭吧":
            jump gdate1_2
label gdate1_1:
    h "姝姝我爱你——"
    "我用尽力气喊了一嗓子。"
    hide g_b3
    show g_b5
    g "哇！哇！别乱喊！"
    "学姐一下羞红了脸。"
    h "明明是你先让我喊的呀，喊什么是我的自由吧。"
    "我对她坏笑。"
    hide g_b5
    show g_b6
    g "笨、笨蛋！不理你了！"
    h "啊你看那边在卖烤鱿鱼。"
    hide g_b6
    show g_b7
    g "咦？哪里哪里？"
    h "噗。"
    "如何哄学姐：买好吃的给她。"
    "成功率：100%%"
    "我拉着学姐（已经忘了不理我）往烤鱿鱼的小摊那边走去。"
    $love_points.add(15)
    jump gdate1end
label gdate1_2:
    h "世界毁灭吧——"
    "我随便喊道。"
    stop music
    stop  music2
    show destruction with dissolve
    play sound "audio/boom.mp3"
    "轰！！！！！" with sshake
    "山崩地裂，世界毁灭了。"
    hide destruction with dissolve
    play music "audio/date.mp3"
    play music2 "audio/beach.mp3"
    "当然是不可能的。"
    "但是为了减轻压力，就允许我在脑子里模拟一下世界毁灭的景象吧。"
    hide g_b3
    show g_b4
    g "嗅嗅。"
    hide g_b4
    show g_b7
    g "啊，果然是烤鱿鱼！"
    g "我们去吃那个嘛！"
    "学姐的雷达发现了目标。"
    h "嗯嗯嗯。"
    "我随便应付着，脑子里还在想象世界毁灭后的景象。"
    "于是我被学姐拖着往烤鱿鱼的小摊那边去了。"
    $stress.add(-15)
    jump gdate1end
label gdate1end:
    scene gsea1 with fade
    "吃完烤鱿鱼，我们又下水玩了一会。"
    "玩累了，学姐就像坐船那样躺在了我们租来的泳圈上，随着波浪漂浮。"
    "而我则望着这幅景象，久久移不开眼睛。"
    scene beach_s with dissolve
    "不知不觉间，学姐已经来到我身边坐下了。"
    "原来太阳要下山了啊。"
    show g_b3 with dissolve
    play music "audio/stable.mp3"
    g "在想什么？"
    h "我在想，要是以后也能这么开心就好了。"
    g "那肯定不能啊。"
    h "啊？"
    "她的回答出乎我意料。"
    show gsea with dissolve
    play sound"audio/gshine.mp3"
    g "因为我会让你比现在还要开心一百倍。"
    "她说着，朝我wink了一下，一副“交给姐姐吧”的表情。"
    "怎么说呢。太可靠了。"
    "真是担心我以后会不会被她养成废人。"
    stop music fadeout 0.5
    stop music2 fadeout 1.0
    if count<40:
        jump daily2
    elif count==40:
        jump gendcheck

label gdate2:
    "你和高姝约会了，好感度+10"
    $love_points.add(10)
    if count<40:
        jump daily2
    elif count==40:
        jump gendcheck

label weekend_room:
    "在宿舍度过了劳逸结合的周末，学习成绩+10，压力-5"
    $marks.add(10)
    $stress.add(-5)
    if route==0:
        if count==20:
            jump concertstart
        else:
            jump daily0
    elif route==1:
        if count<20:
            jump daily1
        elif count==20:
            jump gpropose
        elif count>20 and count<40:
            jump daily2
        elif count==40:
            jump gendcheck
    elif route==2:
        if count<30:
            jump daily3
        elif count==30:
            jump concertevent
    elif route==4:
        if count<50:
            jump daily0
        elif count==50:
            jump nendcheck

label weekend_home:
    scene hroom_d with fade
    "周末回家休息，压力-20"
    $stress.add(-20)
    if route==0:
        if count==20:
            jump concertstart
        else:
            jump daily0
    elif route==1:
        if count<20:
            jump daily1
        elif count==20:
            jump gpropose
        elif count>20 and count<40:
            jump daily2
        elif count==40:
            jump gendcheck
    elif route==2:
        if count<30:
            jump daily3
        elif count==30:
            jump concertevent
    elif route==4:
        if count<50:
            jump daily0
        elif count==50:
            jump nendcheck
label concertstart:
    stop music
    scene jxl_s with fade
    play music "audio/stable.mp3"
    "这天傍晚，我在学校的小广场附近散步。"
    h "好闲啊……嗯？"
    show nansheng1 with dissolve:
        xpos 0.25
        ypos 0.3
    "只见那边的长椅上坐着一个抱吉他的同学。"
    "我不由得停下来，好奇地看着他摆弄手中的琴。"
    "他熟练地调完音，随即弹奏起来。"
    stop music fadeout 0.5
    $ play_music('audio/song.mp3')
    "♪——"
    h "！"
    h "（这是我中学时最喜欢听的歌。）"
    "而且他弹得好好。"
    "我充满感动地倾听着。"
    $ pos = renpy.music.get_pos()
    $ renpy.music.stop()
    $ play_music('audio/song_vocal.mp3', start=pos)
    h "♪~"
    "糟了，我怎么唱出来了。"
    "不过广场上人这么少，应该没有人听见吧？"
    "而且还有吉他声为我掩护。"
    "哎，管它呢。"
    "我很久没唱过歌了，虽然我其实还挺有天赋的。"
    "中学时，我一直在学校的银帆合唱团担任男高音。"
    "好不容易有这个机会，我唱两句又不会碍着别人。"
    h "♬~♪~"
    "于是我跟着唱完了整首歌"
    "唱歌让我感觉很自由，很快乐。"
    "上课的劳累都被一扫而空。"
    "一曲完了，我还陶醉在刚刚的音乐里。"
    "直到——"
    show fushezhang with dissolve:
        xalign 0.5 yalign 0.9
        zoom 1.6
    play sound "audio/futuanzhang.mp3"
    ns "太好听了吧！！！！！"
    stop music fadeout 1.0
    play music "audio/funny.mp3"
    h "？！"
    ns "你唱歌真的好好听啊，简直就是天籁！"
    "突然蹦出一个戴帽子的男生，对着我就是一顿夸。"
    h "呃……谢谢？"
    ns "我们以后一起唱好不好，一起唱！"
    "怎么就快进到一起唱了。"
    ns "哦对，我是咱们学校合唱团的副团长。"
    play sound "audio/cheer.mp3"
    ns "恭喜你，你被录取了！"
    stop sound
    h "这个……（我还没说要加入好吧……）"
    "或许看我好像不是很想加入的样子，男生一下凑了上来。"
    "甚至还可怜巴巴地望着我。"
    ns "不要这样嘛同学，先了解了解啊！"
    ns "银帆合唱团，带你月入三百万，来了就是赚到！"
    h "听起来完全就是可疑组织好吧！"
    "嗯？"
    "银帆合唱团？"
    h "等等……银帆？"
    h "大学里也有银帆的么？"
    h "我高中就是银帆的。"
    ns "什么！"
    ns "那你有合唱的经验是吗，那太好了！"
    ns "嘿嘿嘿抓到一个不用训练马上就能唱的。"
    "虽然我还没有确定要加入，但听到银帆的名字，就有点怀念起来。"
    h "能不能带我去合唱团看看？"
    ns "！！！"
    ns "好啊好啊，我们现在就去！"
    scene yyjs_s with fade
    "他带着我来到了学生服务楼五层的排练室。"
    h "哇……"
    "这个排练室比高中可大多了。"
    show sz with dissolve:
        xalign 0.5 yalign 0.5
        zoom 1.5
    "里面有一些正在练声的人，还有一个看起来是指挥的女生。"
    hide sz
    show sz2 with dissolve:
        xalign 0.25
        yalign 0.9
        zoom 1.75
    f "哟，带人来了？"
    show fushezhang with dissolve:
        xalign 0.75
        yalign 0.9
        zoom 1.6
    ns "嗯嗯，找到个好苗子。他以前也呆过银帆。"
    f "有多好？让我也听听。"
    f "正好我们在排《一剪梅》。"
    "女生转向我。"
    f "同学，你会唱吗？"
    h "呃，会的。"
    "这首歌高中时也排过，所以我能唱。"
    "怎么回事啊，难道所有的银帆都喜欢排一样的曲子吗？"
    hide sz2
    show sz:
        xalign 0.25 yalign 0.6
        zoom 1.5
    f "好，那麻烦你唱两句吧。"
    h "♪~"
    "女生的眼神忽地亮了起来。"
    f "可以啊这个。"
    f "同学，你站到男高里面去试试。"
    "虽然有点不好意思，但我照做了。"
    f "那我们走一遍试试。"
    "♬~♪~"
    "我站在队里，心潮澎湃。"
    "多久没有和他人一起唱过了呢？"
    "现在，这种感觉让我非常眷恋。"
    "这样的话，加入合唱团也不赖吧。"
    "反正读大学总要找点事做啊。"
    "一曲完毕。"
    "拉我进来的男生已经一脸陶醉。"
    ns "怎么样？"
    f "挺好的。"
    ns "我就说嘛！"
    "他对着我竖起大拇指。"
    ns "恭喜你，你被录取了！"
    "但是我真的还没说自己要加入。"
    "不过，也挺好的，不是吗？"
    "如此这般，我（被动地）正式成为了学校银帆合唱团的一员。"
    $route=2
    jump daily3
label daily3:
    if stress.value==100:
        jump overstress
    $count+=1
    $tcount=1
    if count<=25:
        $week=5
        $day=count-20
    elif count<=30:
        $week=6
        $day=count-25
    if count<=30:
        scene sky_d with fade
        play music "audio/daily.mp3"
        "今天是第[week]周第[day]天"
        "新的一天开始了，该做什么好呢？"
        jump chooseroute
    elif count>30:
        jump concertevent
label concert:
    if tcount==1 and tcount==2:
        scene yyjs_d with fade
    elif tcount==3:
        scene yyjs_s with fade
    elif tcount==4:
        scene yyjs_n with fade
    "和团员们一起排练，压力-10"
    $stress.add(-10)
    jump timechange
image takeclass:
    "images/jxl.png" with dissolve
    pause 0.75
    "images/zl_d.png" with dissolve
    pause 0.75
    "images/js_d.png" with dissolve
image findg:
    "images/xxgc.png" with dissolve
    pause 0.75
    "images/b201201.png" with dissolve
    pause 0.75
    "images/zl_s.png" with dissolve
label gpropose:
    scene xsh_d with fade
    play music "audio/stable.mp3"
    "加入学生会已经两个月了。"
    "可能是学姐在背后帮忙的关系，我顺理成章被分到了她所在的社联部。"
    "主要工作就是帮学姐处理社团活动申请表，还有帮忙写宣传活动的推送。"
    "虽说工作不是很累，但同时还要兼顾学习生活，有时就有些繁忙。"
    "好在学姐一直都很照顾我。"
    "而且有了学生会这个接点，我和学姐的关系也变得越发亲近。"
    "午饭时间，学生会室。"
    play sound "audio/chickensoup.mp3"
    p "哈哈哈哈哈哈哈哈哈哈哈，鸡汤来咯！"
    show g_idle with dissolve
    g "3Q，谢啦彭哥~"
    p "不谢，大家都来吃吧。"
    "书记彭哥拿着一屋子人的饭进来，招呼还在埋头批报表的我们吃饭。"
    show g_idle at right with dissolve
    play sound "audio/chickensoup2.mp3"
    p "（吸溜吸溜）这喝汤多是一件美事啊~"
    hide g_idle
    show g_smile at right
    stop sound
    g "（吸溜吸溜）啊，我记得你爱吃香菇对不对，我的给你。"
    h "（吸溜吸溜）嗯？！"
    "学姐很自然地从自己碗里夹起香菇放到我碗里。"
    "她也不是第一次这样了。"
    "总觉得学姐……在不知有意还是无意地做出这种亲密举动。"
    "对我来说当然是值得开心的事。"
    "在一起处理学生会事务的过程中，我更加了解她了。"
    "而越了解她，也就越喜欢她。"
    "我也是正值青春的男生，自然也很憧憬恋爱。"
    "就在我第n次在梦里见到学姐的身姿后，我意识到我其实是喜欢学姐的。"
    "是那种想在一起的喜欢。"
    "所以我自然对她的一举一动都格外关注。"
    "既然能做出这种举动，那是不是就说明她起码是不反感我的？"
    "最好还有点小喜欢。这样发展下去，我就可以顺理成章地向学姐表白，然后……"
    hide g_smile
    show g_poke with fade
    play sound "audio/poke.mp3"
    g "怎么了，想什么呢？"
    "学姐戳了戳我的脸。"
    h "（惊）"
    h "没什么，只是在发呆。"
    "我尽可能自然地回答道。"
    play sound "audio/poke.mp3"
    g "完了，孩子天天批报表批傻了。"
    hide g_poke
    show g_idle
    g "那吃完饭歇会吧。你下午有课吗？"
    h "有一节。"
    g "那你先去上课，弄完了回来找我吧。"
    hide g_idle
    show g_surprised
    g "学校后门新开了家奶茶店，我请你喝奶茶。"
    h "好。"
    p "又约会啊，感情真好。"
    "就彭哥这种社交牛逼症重度患者，想让他放过任何一个调侃的机会是不可能的。"
    hide g_surprised
    show g_smile
    g "对对对，约会了，那剩下的表就交给彭哥了。"
    "学姐居然接着他的话，顺便把工作推给了他。"
    hide g_smile
    stop music
    p "小心副会吃醋。"
    "我收拾餐具的手顿在了那里。"
    play music "audio/gevent.mp3"
    "副会长，传说中的人物。"
    "概括一下就是高富帅且现充。像那种爽文男主。"
    "似乎在别的学生会成员眼里，他和学姐就是金童玉女天生一对。"
    "甚至还有真情实感嗑他俩的cp粉。"
    "证据就是，偶尔在学生会公众号的文章底下会有人留言，比如“今天副会高姝结婚了吗”。"
    "我也向学姐求证过流言的真实性，但学姐都是说“副会怎么可能喜欢我嘛”，打着哈哈过去了。"
    "总之，先去上课吧。"
    scene takeclass with fade
    "……"

    scene zl_d with fade
    play sound "audio/footsteps.mp3"
    "下课后，我飞奔着冲向学生会室。"
    scene findg with dissolve
    "马上就能见到学姐了。"
    play sound "audio/pant.wav"
    h "呼哧……呼哧……"
    "我在学生会室门口喘着气。"
    "还是等呼吸平稳了再进去吧。我可不想被学姐看见喘粗气的样子。"
    "此时，里面传来说话声。"
    stop music
    g "副会，怎么了？"
    "看来副会在里面。"
    v "高姝，我真的不明白。"
    v "我到底哪里不好？"
    g "没有啊！你很好。"
    v "那你为什么不愿意和我在一起？"
    play sound "audio/gulp.mp3"
    h "！！！"
    "我悄悄贴近了门缝。"
    g "呃，该怎么说呢……就是我没有那个意思吧。"
    v "你没有那个意思？"
    v "那你为什么要对我好？"
    g "你冷静一下。"
    v "你给我带饭，还请我喝饮料，还跟我一起学习。"
    g "这只是很正常的朋友之间的行为啊！"
    v "学生会合影的时候我找你单独照双人照你也没拒绝。"
    g "我也和别人一起照了呀。"
    v "眼神不会骗人。你其实喜欢我的，对不对？"
    v "其他成员不也觉得我们很配吗。为什么我们就不可以在一起试试？"
    g "你真的误会了。"
    g "对我来说，你只是一个好朋友。我不想破坏我们之间的友情。"
    v "……"
    play music "audio/rejection.mp3"
    "我的胃里翻江倒海。"
    "学姐拒绝了我的“情敌”副会长。"
    "本来应该是高兴的事，但为什么，我会觉得这么苦涩呢？"
    "是了，是因为拒绝的原因。"
    "学姐说，他误会了。"
    "误会了什么？误会了学姐对他的好是喜欢他的表现。"
    "他以为自己是特别的那个人，结果实际上她对谁都一样。"
    "学姐只是单纯的人好而已。只是关心普通朋友而已。"
    "我又何尝不是一样？"
    "难道学姐就没有给我带过饭，请我喝过饮料，和我一起学过习吗？"
    "我所感受到的温柔，可能对人家来说真的没什么 特别的意义。"
    "学姐说不定，对我也是当成普通朋友看待。"
    "而我却擅自喜欢上了她。"
    v "……我好像一个小丑啊。"
    "如果我抢先副会一步向学姐表白的话，可能现在站在她面前狼狈不堪，像个小丑的就是我了。"
    "我可能也是小丑，而且刚刚才发现。"
    "果然像我这样的人是注定得不到幸福的吗。"
    "我决定要加入学生会时，是为了帮上学姐。也是为了让自己有机会改变，成长为配得上她的人。"
    "但是，配不配得上和人家喜不喜欢你根本就是两码事。"
    "我这才醒悟过来，自己的恋情可能一开始就不该萌生。"
    "人家连那个公认受欢迎的副会长都看不上，能看上你？"
    "好丢脸，好后悔，好想马上死掉。"
    menu:
        "我——"
        "“但我还是想要相信学姐”":
            jump isgroute
        "放弃吧":
            jump ne1
    return
label isgroute:
    "但我所有的负面情绪后隐藏着的些微希望仍然没有消失。"
    play music "audio/gge.mp3"
    h "（我自己先打退堂鼓怎么行……）"
    "是的，学姐又没有当面拒绝我。"
    "我是害怕，害怕自己和副会一样一厢情愿。"
    "但是，也只是害怕而已。"
    "是，我知道。我长得一般，人也内向，是没有什么优势。"
    "但我怎么能还没有迈出一步就放弃呢？"
    "我还没有亲口对学姐说我喜欢她。"
    "我还没有感谢她一直照顾我。"
    "不管结果是什么，就算我遭到更直接的拒绝也好，我想要自己堂堂正正说出自己的感情。"
    "因为已经和学姐约好要改变了。"
    scene dark with fade
    play sound "audio/footsteps.mp3"
    "学生会的门有要开的趋势，我连忙跑到楼梯后，装作刚上来的样子。"
    scene zl_s with fade
    play sound "audio/closedoor.mp3"
    queue sound "audio/footsteps.mp3"
    "副会出去了。"
    "我和他擦身而过，往学生会室走去。"
    "如同打开猫箱前的薛定谔。"
    play sound "audio/opendoor.mp3"
    scene xsh_s with fade
    show g_moody with dissolve
    g "你回来啦。"
    "学姐看起来心情不是很好。"
    "可能是因为失去了一位朋友吧。"
    "我不觉得学姐或者副会中的任何一人有错。"
    "只能说，感情就是这样无奈的东西。"
    h "学姐，去喝奶茶吧。"
    g "嗯。"
    scene cafe with fade
    play sound "audio/chimes.wav"
    "我们出了校门，来到奶茶店。"
    show g_surprised with dissolve
    h "学姐你要什么？"
    g "大杯金桔柠檬吧。"
    h "大杯金桔柠檬，少冰少糖，再来大杯双拼奶茶少冰半糖。"
    hide g_surprised
    show g_blush
    g "你怎么记得我要少冰少糖啊。"
    h "学姐不也记得我爱吃香菇吗。"
    "说着，我掏出手机付了钱。"
    g "欸，不是说好我请你吗。"
    h "我请吧。"
    play music "audio/gevent.mp3"
    h "毕竟，我接下来可能要说一些学姐不想听的话。"
    hide g_blush
    show g_upclose
    g "！"
    "我能感到气氛在极速地变化。"
    "学姐的不安，疑惑，还有我的紧张。"
    hide g_upclose
    show g_worried
    g "那么，你要说……"
    "我深吸一口气。"
    h "学姐，我喜欢你。"
    hide g_worried
    h "虽然你可能只拿我当弟弟看，但我还是要说。"
    h "我想，起码要为自己的感情勇敢站出来一次。"
    h "教会我，鼓励我改变的人就是你。"
    h "真的很谢谢你一直那么照顾我。"
    h "就算学姐不会选择我，我也衷心希望你有一天能找到属于自己的幸福。"
    h "我说完了。"
    "我说出来了，我做到了，我直面了自己没有逃避。"
    "所以，指引我改变的人啊。"
    stop music
    "请你，为我不成熟的恋情画上句号。"
    "一阵沉默。"
    g "……为什么"
    hide g_blush
    show g_angry1
    play music "audio/gpropose.mp3"
    g "为什么要说得好像认定我会拒绝一样啊！"
    h "？！"
    hide g_angry1
    show g_blush
    "我看着学姐，她也看着我。"
    "她的脸红红的。"
    voice "voice/g2.mp3"
    g "所以……你有没有想过一种可能，"
    hide g_blush
    show g_blush2
    voice "voice/g3.mp3"
    g "就是我也喜欢你呢？"
    h "？？？"
    "我不敢相信自己的耳朵。"
    "明明我想出了一百种她拒绝我时会说的话。"
    "脑内演练过一千次如何应对拒绝后潇洒退场。"
    "表白前更是拿出了一万分的勇气。"
    "但是我独独没想过这个回答。只是这一句话，就让这些准备工作瞬间烟消云散。"
    h "你的意思是……"
    g "我的回答是yes。"
    g "我想听你说你的问题是什么？"
    h "……学姐可不可以做我的女朋友？"
    hide g_blush2
    show g_upclose1
    g "当然可以。"
    play sound "audio/putdowncup.mp3"
    d "您的奶茶好了。"
    d "唉，上个班都要吃狗粮。"
    hide g_upclose1
    show g_verysurprised:
        xzoom -1.0 yzoom 1.0
        pause 0.5
        xzoom 1.0 yzoom 1.0
        pause 0.5
        repeat
    "店员的调侃让学姐有点不好意思。"
    g "嗯，那，我们要不去哪走走？"
    h "好。都听学姐的。"
    hide g_verysurprised
    show g_worried
    g "既然已经确定关系了，你要不要直接叫我名字？"
    h "！！"
    h "嗯……都听姝姝的。"
    hide g_worried
    show g_smile
    "我和学姐相视而笑，走出奶茶店，开始了我们交往后的第一次约会。"
    stop music fadeout 0.5
    $isg = True
    $count=20
    $route=1
    jump daily2
label daily2:
    if stress.value==100:
        jump overstress
    $count+=1
    $tcount=1
    if count<=25:
        $week=5
        $day=count-20
    elif count<=30:
        $week=6
        $day=count-25
    elif count<=35:
        $week=7
        $day=count-30
    elif count<=40:
        $week=8
        $day=count-35
    if count<=40:
        scene sky_d with fade
        play music "audio/daily.mp3"
        "今天是第[week]周第[day]天"
        "新的一天开始了，该做什么好呢？"
        jump chooseroute
label gendcheck:
    if love_points.value>50 and marks.value>=70:
        jump gge
    elif love_points.value<=50 and marks.value>=70:
        jump gne
    elif love_points.value>50 and marks.value<70:
        jump gbe1
    elif love_points.value<=50 and marks.value<70:
        jump gbe2
image timepasses:
    "images/b204000.png" with dissolve
    pause 0.75
    "images/b204001.png" with dissolve
    pause 0.75
    "images/b204023.png" with dissolve
    pause 0.75
    "images/b204033.png" with dissolve
    pause 0.75
    "images/b204002.png" with dissolve
label gge:
    scene timepasses with fade
    play music "audio/gge.mp3"
    "四年的时光，很快就过去了。"
    "我一直保持着优异的学习成绩。"
    "当然，情感方面也无懈可击。"
    "多亏有了学姐陪在我身边，如今的我早已成为了全方面发展的“现充”。"
    "成了以前的自己想都不敢想的那种人。"
    "真想感谢当初勇敢踏出表白一步的自己。"
    scene b204000 with fade
    "今天是保研结果公示的日子。"
    h "（果然！）"
    play sound "audio/cheer.mp3"
    "果然不出我所料。我成功得到了保研本校的名额。"
    stop sound
    "这样就可以继续做学姐的学弟了。"
    "要问为什么，那就是学姐先我一年保研到了本校。"
    "我决定给学姐一个惊喜，所以并没有马上打电话报喜。"
    "而是等到周末约会的时候。"
    scene gy_d with fade
    play sound "audio/footsteps.mp3"
    show g_ge1 with dissolve:
        xalign 0.1
        parallel:
            linear 1.0 zoom 1.85
        parallel:
            linear 0.1 yoffset 10
            linear 0.1 yoffset -10
            linear 0.1 yoffset 10
            linear 0.1 yoffset -10
            linear 0.1 yoffset 10
            linear 0.1 yoffset -10
            linear 0.1 yoffset 10
            linear 0.1 yoffset -10
            linear 0.1 yoffset 10
            linear 0.1 yoffset -10
        parallel:
            linear 1.0 xoffset -550
    g "（一路小跑）不好意思我来晚啦。"
    stop sound
    h "没事。"
    "她来到我身边，很自然地牵起了我的手。"
    hide g_ge1
    show g_ge2
    g "怎么了？怎么一脸深沉？"
    g "难道是……"
    "苦着一张脸就是为了吓她一跳。"
    "我已经迫不及待想看见学姐惊讶的表情了。"
    h "是的，就是你想的那样。"
    "说完，我装模作样地长叹一口气。"
    g "……"
    stop music fadeout 1.0
    "学姐似乎是思考了一会怎么安慰我。"
    hide g_ge2
    show g_ge3
    g "没事的，不管怎么样，我都会陪着你。"
    g "不行咱就另找出路，三百六十行行行出状元嘛。"
    "看着她真诚的样子，反而让我有点羞愧了。"
    "还是赶紧告诉她真相吧。"
    play music "audio/nge.mp3"
    h "我……保研啦！"
    "我紧紧抱住了面前的女朋友。"
    hide g_ge3
    show g_ge4
    g "……"
    "她愣住了。"
    hide g_ge4
    show g_ge5:
        linear 0.1 xoffset 10
        linear 0.1 xoffset -10
        repeat
    voice "voice/g4.mp3"
    g "……你你你你你！！"
    voice "voice/g5.mp3"
    g "你怎么耍我呀！！"
    hide g_ge5
    show g_ge6:
        linear 0.1 xoffset 10
        linear 0.1 xoffset -10
        repeat
    play music2 "audio/bonk.mp3"
    g "这大骗子，打死你，打死你……"
    g "学姐涨红了脸，轻轻捶打着我的胸口。"
    h "哈哈哈哈哈哈哈。这么容易就被骗到，是不是不相信你男朋友的能力啊？"
    g "我当然相信啦！但是你居然！故意吓我！"
    stop music2
    hide g_ge6
    show g_ge5
    "学姐嘟着嘴。"
    "那个成熟冷静的学姐，在恋人的面前也会像小女孩一样撒娇。"
    "真是越看越可爱。"
    g "再也不理你了。"
    h "真的？"
    g "真的。"
    h "请你吃大份黄焖鸡加鸡爪煲。"
    hide g_ge5
    show g_ge7
    play sound "audio/gshine.mp3"
    g "（双眼放光）真的吗？！"
    h "噗嗤。"
    "好搞定度：十分（满分五分）。"
    hide g_ge7
    show g_ge8
    g "！！！"
    "学姐反应过来了。"
    hide g_ge8
    show g_ge9:
        linear 0.1 xoffset 10
        linear 0.1 xoffset -10
        repeat
    play music2 "audio/bonk.mp3"
    g "你笑我！啊啊啊啊啊！！！"
    "她想要挣脱我的怀抱，但我怎么会放手呢。"
    "这一辈子都不会放手了。"
    stop music2
    h "姝姝，我做到了。"
    hide g_ge9
    show g_ge10
    g "嗯。"
    "我把她抱得更紧。"
    h "我现在是不是成功改变了？"
    hide g_ge10
    show g_ge11
    g "傻瓜……"
    g "从你下定决心改变的那一刻，就离成功不远了呀。"
    h "要是没有你，我肯定做不到的。"
    h "所以呢，我要送你这个礼物。"
    h "我现在应该有把它送给你的资格。"
    h "你愿意……接受吗？"
    hide g_ge11
    show g_ge4
    g "什么？黄焖鸡加鸡爪煲还有一份炒蟹吗？"
    h "……不要在重要的时候装傻好吗。"
    hide g_ge4
    show g_ge11
    g "这是对你刚刚故意吓我的回礼。"
    hide g_ge11
    show g_ge10
    "我掏出了用这几年攒的奖学金买下的小盒。"
    "一枚戒指安安静静地躺在中央。"
    h "姝姝，我们订婚吧。"
    h "等读完研，就结婚。"
    h "你的回答还会是yes吗？"
    show g_ge10:
        zoom 1.0
        linear 0.5 zoom 0.8
    "学姐退后两步，深吸一口气。"
    "然后直直扑了过来，用亲吻代替了回答。"
    hide g_ge10
    show g_ge10:
        xalign 0.5 yalign 1.0
        zoom 0.8
        linear 0.5 zoom 1.5
    scene g_kiss with flashbulb
    g "我的回答……永远都是yes。"
    stop music fadeout 0.5
    "{b}GOOD END{/b}"
    $renpy.full_restart()
label gne:
    scene train with fade
    play music "audio/NE.mp3"
    "四年的时光，很快就过去了。"
    "我一直保持着优异的学习成绩。"
    "但是和学姐已经分手很久了。"
    "是她先提的分手，理由是我不够关心她。"
    "说不难过是不可能的。"
    "但我也无力改变什么，而且也已经过去了。"
    "我考上了另一个城市重点大学的研究生，今天就要启程。"
    "我坐在火车上，陷入了浅浅的睡眠。"
    show gbe with fade
    "梦里，一个穿着成熟的女孩子前来迎接第一天踏入大学校门的我。"
    "啊，是你……这次，我……"
    "不会再……"
    hide gbe
    show gbe_blurry with dissolve
    "留下遗憾……"
    "{b}NEUTRAL END{/b}"
    $renpy.full_restart()
label gbe1:
    stop music
    scene apt_m with fade
    play sound "audio/clock.mp3"
    "醒来的时候，已经十二点了。"
    stop sound
    h "哈欠~"
    "我打着哈欠起身，准备随便弄点吃的。"
    "毕涉，今年二十三岁，现在是自由职业者。"
    "换句话说就是没工作。"
    "没办法，在大学成绩不好，勉强混了个学位证。"
    "找工作的时候人家一看简历都摇头。"
    "但是还好，还有学姐陪在我身边。"
    "为了照顾我，学姐放弃了保研，找了份工作。"
    "而我现在住在学姐的公寓里，每天过着家庭主夫般的生活。"
    "我给学姐发微信。"
    play sound "audio/typing.wav"
    queue sound "audio/message.mp3"
    h "“晚上回来吃吗？”"
    play sound "audio/message.mp3"
    g "“嗯嗯，给我留点就行，今天加班回得晚。”"
    play sound "audio/message.mp3"
    h "“好。”"
    "得到了她的答复，我开始思考晚上的菜单。"
    "说真的，我一点都不擅长做饭。"
    "以前一个人在家也是点外卖而已。"
    "但现在，我没有了父母给的生活费，每个月只能靠学姐的工资过日子。"
    "点外卖是不可能的，只能节约点自己做饭。"
    "不过学姐一次都没说过我做的饭难吃。"
    "肯定是工作太忙，已经没空思考饭菜是否可口了吧。"
    scene apt_s with dissolve
    "下午六点，我做好了晚饭。"
    "是简单的青菜肉丝面。"
    "我唯一能拿出手的菜。"
    "我看了看表，发觉学姐回家还要三个小时，再加上坐车一小时。"
    "那就是晚上十点了。"
    play sound "audio/controller.mp3"
    "没办法，一边玩游戏一边等吧。"
    scene apt_e with dissolve
    play sound "audio/opendoor.mp3"
    "结果直到十一点多，学姐才到家。"
    show g_be1 with dissolve
    h "今天怎么这么晚？"
    g "嗯……路上堵车。"
    "她的眼圈是黑夹杂着红。"
    "但我并没看出什么。"
    "我把面热了热，两个人开始吃过了时间的晚饭。"
    "……"
    scene gne with fade
    play music "audio/gbe.mp3"
    "明天也没什么要做的事。无非是一点家务，再做点吃的等学姐回来罢了。"
    "身边的学姐在高强度的工作下日益憔悴。"
    "这样的日子能持续多久呢？"
    "我不敢细想，唯有闭眼睡觉。"
    "{b}BAD END{/b}"
    $renpy.full_restart()
label gbe2:
    stop music
    scene apt_m with fade
    play sound "audio/clock.mp3"
    "醒来的时候，已经十二点了。"
    stop sound
    h "哈欠~"
    "我打着哈欠起身，准备随便弄点吃的。"
    "毕涉，今年二十三岁，现在是自由职业者。"
    "换句话说就是没工作。"
    "没办法，在大学成绩不好，勉强混了个学位证。"
    "找工作的时候人家一看简历都摇头。"
    "但是还好，还有学姐陪在我身边。"
    "为了照顾我，学姐放弃了保研，找了份工作。"
    "而我现在住在学姐的公寓里，每天过着混吃等死的生活。"
    "我给学姐发微信。"
    play sound "audio/typing.wav"
    queue sound "audio/message.mp3"
    h "“晚上回来吃吗？”"
    "过去了很久，她都没有回复。"
    "一定是工作太忙。"
    "算了，反正闲着也是闲着，我开始思考晚上的菜单。"
    "说真的，我一点都不擅长做饭。"
    "以前一个人在家也是点外卖而已。"
    "但现在，我没有了父母给的生活费，每个月只能靠学姐的工资过日子。"
    "点外卖是不可能的，只能节约点自己做饭。"
    "不过学姐一次都没说过我做的饭难吃。"
    "肯定是工作太忙，已经没空思考饭菜是否可口了吧。"
    scene apt_s with dissolve
    "下午六点，我做好了晚饭。"
    "是简单的青菜肉丝面。"
    "我唯一能拿出手的菜。"
    "我看了看表，发觉学姐回家还要三个小时，再加上坐车一小时。"
    "那就是晚上十点了。"
    "太久了，我还是自己先吃吧。"
    scene apt_e with dissolve
    play sound "audio/opendoor.mp3"
    "结果直到十一点多，学姐才到家。"
    show g_be1 with dissolve
    h "今天怎么这么晚？"
    g "……。"
    "她的眼圈是黑夹杂着红。"
    h "我给你留了碗面条，你热热吃吧。"
    hide g_be1
    show g_be2
    stop music
    g "我有话要说。"
    "她先一步叫住了意欲回房睡觉的我。"
    h "咋了？"
    g "坐下说吧。"
    "她示意我坐到餐桌旁。"
    hide g_be2
    show g_be1
    play music "audio/gbe.mp3"
    g "其实……我妈今天给我打电话了。"
    g "我们聊了很多……"
    hide g_be1
    show g_be2
    g "就是我也觉得不能再这样下去了。"
    voice "voice/g6.mp3"
    g "我们分手吧。"
    voice sustain
    "我 们 分 手 吧。"
    h "……啊？"
    "我不是没想过这个可能性。"
    "但是为什么会来得如此之快。"
    hide g_be2
    show g_be4
    g "我真的，真的……要撑不住了……"
    "她哭了。"
    "怎么会？为什么？"
    "学姐不应该是强大又骄傲的吗？"
    "所以我可以躲在她的身后什么都不用做。"
    "明明之前一直都是这样过来的，为什么现在却要抛下我？"
    hide g_be4
    show g_be3
    g "我查出了急性心肌梗死。"
    g "你知道吗？你不知道。"
    hide g_be3
    show g_be5
    g "因为你其实并没有很关心我。"
    h "我……"
    hide g_be5
    show g_be6
    g "就这样吧，我妈妈一会就来接我。"
    g "这间房子的租期就到月底为止，你也准备准备回自己家吧。"
    hide g_be6 with dissolve
    "说完，她便进卧室开始收拾东西。"
    "只剩我呆站在原地。"
    scene apt_n with dissolve
    "为什么？为什么？"
    "如果我多关心她一点，如果我有工作的话……"
    "是不是，就不用走到今天的地步呢……"
    "我的人生到底是哪里开始出错的呢？"
    stop music fadeout 0.5
    "{b}BAD END{/b}"
    $renpy.full_restart()
label ne1:
    scene zl_s with fade
    play music "audio/gbe.mp3"
    "好害怕，好害怕，好害怕。"
    scene jxl_s with dissolve
    "害怕被拒绝，害怕被疏远，害怕悲剧重演。"
    scene ss_s with dissolve
    "我的感情一开始就是错的，所以……"
    scene ssroom with dissolve
    "所以就让我亲手把它掐死在摇篮里吧。"
    scene dark with fade
    "为了不被学姐疏远，只能我自己选择疏远她了。"
    "逃避吧，逃避吧，逃避吧。"
    "因为，一直以来不都是这么过来的吗？"
    "……"
    scene yt with fade
    "我以学业为由退出了学生会。"
    "也不再联系学姐了。"
    "今后，我决定一如既往地，孤身一人走下去。"
    "我一个人也能行的。"
    "我不需要人际关系，也不需要和他人的接点。"
    "……"
    play music "audio/NE.mp3"
    scene train with fade
    "四年后。"
    "我成功考上了某所著名大学的研究生。"
    show gbe with fade
    "但偶尔还是会梦见自己第一天踏进大学校门时，那个来迎接我的热心学姐的身影。"
    "现在她又在哪里，在做什么呢？"
    "我不可能知道了。"
    "如果那时我没有选择逃避的话，是不是会有不一样的结局？"
    "但那也永远只是“如果”而已了。"
    scene dark with fade
    stop music fadeout 0.5
    "{b}NEUTRAL END{/b}"
    $renpy.full_restart()
##学姐线完
##合唱队事件开始
label concertevent:
    stop music
    scene b201201 with fade
    play music "audio/title.mp3"
    "合唱团的训练非常严格。"
    "尤其是大赛快要到了的这个时候。"
    "我们从平时两天一练改成了一天一练。"
    "然后每次还多加了一个小时。"
    "“我们银帆可是树莓大学的面子，一定要在这次比赛中拿到好名次。”"
    "团长是这么说的。"
    "甚至为了增加效率，特地请了专业的老师过来指导。"
    h "唉……"
    "我最近状态不好。"
    "有时候甚至因为紧张而唱破音。"
    "团长当然是不允许这种情况的。"
    "她说，到时候上场我是离话筒最近的人之一。"
    "一旦不小心失误，就会被放大到全场都听得见。"
    "我当然也不想在那么多人面前出丑。"
    "于是只好等到合唱团练习结束后，自己一个人偷偷找地方练习。"
    "我常去的地方是4栋13层。"
    "那里很少有人上自习，自然也没人投诉我扰民。"
    "而且楼层高，也不怕被外面来往的学生听见。"
    "13层的教室多是用来当活动室用的，所以隔音效果也很不错。"
    stop music
    play sound "audio/footsteps.mp3"
    scene darkroom with fade
    "于是乎，我今晚也来到这里偷偷练习。"
    h "吸——呼——"
    play sound "audio/slam_suspension.flac"
    "我做了一次深呼吸，刚要开口唱歌，却听见旁边教室传来“咚”一声巨响。" with sshake
    h "？？？"
    play music "audio/badfeeling.mp3"
    "怎么回事？按理说这个时候应该没人在啊？"
    "我忽然，有种不好的预感。"
    menu:
        "那么，我要——"
        "去看看情况":
            jump inv
        "别管了，快回宿舍吧":
            jump goback
label inv:
    scene darkhall with fade
    play sound "audio/heartbeat.mp3"
    "扑通、扑通、扑通……"
    "我不知为何心跳得特别快。"
    "说不上来为什么，但我就是有种很不好的预感。"
    "此刻除了我练歌的教室外，别的教室都是一片漆黑。"
    "走廊上只有昏暗的灯光。"
    "我来到刚刚从中传出响声的教室前，轻轻推门——"
    "但是门不知为何反锁着。"
    $j=renpy.random.randint(1,6)
    $k=renpy.random.randint(1,6)
    $sum=j+k
    if sum>=6:
        $action1=True
    show screen aaa
    "开始roll点"
    hide screen aaa
    show screen ccc
    "roll点结果：[sum]"
    hide screen ccc
    menu:
        "我——"
        "撞开" if action1:
            jump deadbody
        "放弃":
            jump goback
image fangda:
    "darkhall.png"
    zoom 1.0
    parallel:
        linear 3.0 xoffset 240 yoffset 300
    parallel:
        linear 0.1 zoom 1.1
        pause .2
        linear 0.1 zoom 1.2
        pause .2
        linear 0.1 zoom 1.3
        pause .2
        linear 0.1 zoom 1.4
        pause .2
        linear 0.1 zoom 1.5
        pause .2
        linear 0.1 zoom 1.6
        pause .2
        linear 0.1 zoom 1.7
        pause .2
        linear 0.1 zoom 1.8
        pause .2
        linear 0.1 zoom 1.9
        pause .2
        linear 0.1 zoom 2.0
label deadbody:
    stop music
    "我突然浑身充满了力量，有种自己能撞开这扇门的感觉。"
    "而且，我必须这么做。"
    "我退后两步，摆好姿势。"
    show fangda
    play sound footsteps
    "然后，向前冲去。"
    hide darkhall
    show dark
    play sound "audio/bang.mp3"
    "咣！！！" with sshake
    "门被我强行撞开了。"
    "木屑散落一地。"
    show darkroom with fade
    play music "audio/badfeeling.mp3"
    h "……"
    "里面果然一片漆黑。"
    "隐隐约约还似乎有点说不上来的臭味。"
    "是有人把吃的放这里坏了么？"
    play sound "audio/switch.mp3"
    "我尝试开灯，却没用。难道灯坏了？"
    h "有人吗？"
    show flashlight:
        xpos -0.2
        pause .5
        linear 1.0 xpos 0.2
        pause .5
        linear 1.0 xpos -0.2
        repeat
    "没有人回答。我只好打开手机的手电筒功能。"
    "天花板上原本有灯的地方空空荡荡。"
    h "是灯管掉下来了？"
    play sound "audio/footstep.mp3"
    "我往灯管掉下的地方走去，想看看情况。"
    play sound "audio/footstep.mp3"
    "但我每走近一步，腐臭味就更加浓烈。"
    play sound "audio/footstep.mp3"
    "有这么巧……灯管正好掉在坏掉的食物旁边？"
    play sound "audio/heartbeat.mp3"
    "我能清晰听见自己越来越响的心跳声。"
    stop sound
    play music "audio/heartbeat_faster.mp3"
    "穿过桌椅，我看见的是"
    "{color=#f00}{b}我 看 见 的 是{/b}{/color}" with sshake
    hide flashlight
    play sound "audio/corpsediscovery.wav"
    show shiti
    "{color=#f00}死死死死死死死死死死死死死死死死死死死死死死死死死死死死死死死死死
    死死死死死死死死死死死死死死死死死死死死死死死死死死死死死死死死死
    死死死死死死死死死死死死死死死死死死死死死死死死死死死死死死死死死
    死死死死死死死死死死死死死死死死死死死死死死死死死死死死死死死死死{/color}"
    play music "audio/corpseinv.mp3"
    "{color=#f00}{b}死 人{/b}{/color}"
    play sound "audio/earringing.mp3"
    h "呜呕！！！！呕！！！咳！！！！"
    "我干呕起来。"
    $j=renpy.random.randint(1,6)
    $k=renpy.random.randint(1,6)
    $sum=j+k
    show screen aaa
    "开始roll点"
    hide screen aaa
    show screen ccc
    "roll点结果：[sum]"
    hide screen ccc
    if sum>=6:
        jump evidence
    else:
        jump sanoff
    hide shiti
label sanoff:
    stop music
    h "{color=#f00}啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊！！！！！！！！{/color}" with sshake
    scene dark with fade
    play sound "audio/down.ogg"
    "在失去意识前，我发出了这辈子最响，音调最高还没有破音的尖叫。"
    play sound "audio/earringing.mp3"
    "……"
    scene hospital with fade
    play sound "audio/pulse.wav"
    "我在医院醒来。"
    "医生说，由于受到刺激，我可能需要住一段时间院静养。"
    "父母也赶了回国照顾我。"
    "他们给我办理了休学手续，叫我安心养着，好了再说。"
    "我其实没觉得自己有多大问题，就是那天晚上看见的尸体不知为何总出现在我身边。"
    show sanend with dissolve
    play music "audio/BE.mp3"
    show ghost with dissolve:
        anchor (0.5, 0)
        around (960, 300)
        angle 0
        radius 300
        linear 1.0 angle 60
        linear 1.0 angle 0
        linear 1.0 angle -60
        linear 1.0 angle 0
        repeat
    "真奇怪，一般的尸体应该是不会动的啊？"
    play sound "audio/enteringscene.wav"
    st "是的，但我不是一般的尸体。"
    h "哦哦。"
    st "我们做朋友吧。"
    h "好啊。"
    "虽然一开始我也觉得有点接受不了，但看多了就习惯了。"
    "其实尸体只是外表吓人而已，他的性格还是挺好的。"
    "而且看起来他非常想和我交朋友。"
    "在病房里待着真的很无趣，还好有这个朋友陪在我身边。"
    "以后也和他好好相处吧。"
    "不知道什么时候能把他介绍给父母认识呢？"
    show san with dissolve
    "{b}GAME OVER{/b}"
    stop sound
    $renpy.full_restart()
label evidence:

    "这是，这是……千真万确的尸体。"
    "虽然我也希望是自己看错了，但这凸得像金鱼一样，充满血丝的眼球；"
    "长长伸出的发白舌头；"
    "体表上不自然膨起的血管；"
    "无一不在向我述说着事实。"
    "我强行忍住了想放声大叫的冲动。"
    h "（怎么办，怎么办……要报警吗，要叫120吗）"
    h "（不对，人都死了，还叫120有什么用……）"
    "怎么会这样……"
    "教室里为什么会有尸体……"
    "仔细一看，尸体的手里紧紧攥着一张纸条。"
    "我费了好大劲才把它掏出来。"
    show note at truecenter with dissolve
    "只见上面写着："
    "“永别了这个世界我再也忍不了xxx导师对我的性侵行为了”"
    h "……"
    "如果这是这个人写的话，那就是说他是个研究生，因遭受导师性侵自杀了的意思吧。"
    "怎么会……"
    "对了，我要赶紧找人来才行！！"
    play sound "audio/snap.mp3"
    queue sound "audio/snap.mp3"
    "我颤抖着拍了两张尸体的照片，以及字条的内容，逃也似地跑出教室下楼去。"
    jump afterinv
label afterinv:
    play sound "audio/footsteps.mp3"
    scene sanend with fade
    "之后的事情，我记得不是太清楚。"
    "不过应该是找保安说了尸体的事，就交给保安处理了。"
    "我不知道自己当晚是怎么合的眼。"
    "只有纸条上的内容和尸体凄惨的死状一直在我脑内来回旋转。"
    show dark with circlewipe
    scene ssroom with circlewipe
    stop music
    "第二天晚上。"
    show ts with dissolve
    t "我去，你看看这个！"
    show statement at truecenter with dissolve
    "田所硬把他的手机凑到我面前。"
    h "怎么了。"
    t "你看我们学校公众号发的声明。"
    t "说是有个研究生因为情感问题在4栋自杀了！"
    t "昨天晚上发现的，唉，真是太惨了……"
    hide statement
    "等等。昨天？4栋自杀的研究生？"
    "而且，情 感 问 题？"
    h "放屁！" with sshake
    "我脱口而出。"
    t "啊？说什么呢？"
    h "就是我发现的，我昨天在4栋练歌！"
    h "那个人手里有张纸条，说是因为被导师性侵才会自杀的！"
    h "为什么要说成是情感问题，明明就是那个导师的错！" with sshake
    t "……你别逗我。"
    h "我说的是真的，我还拍了照片。"
    "说着，我翻出昨天的照片给他看。"
    t "妈耶……"
    "他倒抽一口凉气，半天没说话。"
    play sound "audio/dong.mp3"
    h "学校这是要干什么，掩盖问题吗？！" with sshake
    t "毕涉，你冷静一点，我们也做不了什么呀。"
    h "那难道就看着那个害死人的导师什么处分都没有吗？"
    menu:
        "对了——"
        "我有证据啊":
            jump share_inv
        "多一事不如少一事":
            jump ne2
label share_inv:
    "我发了朋友圈述说我所看到的真相，配图是尸体和他手里的字条。"
    show dark with circlewipe
    scene js_d with circlewipe
    play music "audio/rejection.mp3"
    "第二天醒来，我仍然没有胃口，便没吃早餐直接去了教室等着上课。"
    "毕竟昨天才看见过那副场景。"
    "怎么可能马上恢复食欲。"
    "鲜明的记忆在我脑内复苏，害得我差点干呕出来。"
    "为了平复心情，我打开了手机。"
    show pyq2 with dissolve
    "一看朋友圈，有很多人给我点赞。"
    "果然我发出来是有意义的。"
    "今日不站出来为他发声，明天受害的将会是我们自己。"
    "……"
    jump reject
label goback:
    scene ssroom with fade
    play music "audio/rejection.mp3"
    "我回到了宿舍。"
    "田所正在玩游戏。"
    show ts with dissolve
    t "回来了。咦，你脸色怎么不好。"
    h "啊？"
    "我这才发现自己出了一身冷汗。"
    h "我也不知道，是不是太累了。"
    t "那早点睡好了。"
    h "好。"
    hide ts with dissolve
    "我没想太多，便和田所互道晚安后上床睡了。"
    "……"
    "第二天晚上。"
    show ts with dissolve
    t "我去，你看看这个！"
    "田所硬把他的手机凑到我面前。"
    h "怎么了怎么了，没出大事不要来烦我。"
    "我习惯了田所的一惊一乍，他连食堂换菜了都能拿出来说一说。"
    t "不是，真出事了！"
    h "除了食堂，还能有什……"
    hide ts
    show ts:
        zoom 1.75
        xoffset -500 yoffset -300
    t "我们学校死人了！！！！" with sshake
    h "啊？！！"
    "死人了？谁？怎么死的？在哪里？"
    h "什么情况？"
    hide ts
    show ts
    t "就在4栋，听说昨天晚上发现的 ！"
    h "4栋？这……"
    t "死的是个研究生，男的，被导师强奸了想不开自杀了。"
    h "你听谁说的？"
    t "就，我社团群里说的。"
    t "说是昨天晚上保安去巡楼发现了，死得可惨了。"
    t "给你看聊天记录，不过你可别说出去啊，学校不让。"
    "昨天晚上，4栋，我听见的巨响……"
    "难道是……"
    h "呕！" with sshake
    "我被自己的想象激得干呕一声。"
    t "没事吧？"
    h "我昨天晚上就在4栋练歌……"
    t "……"
    "他不说话了，可能他也想到了什么。"
    t "不过还真够惨的……"
    t "居然被导师……"
    h "现在考研卷成这样，好不容易考上了却遇见这种烂导师，换我我也崩溃。"
    menu:
        "我越想越气，"
        "在朋友圈发表自己的看法":
            jump share_notinv
        "还是算了":
            jump ne2
label share_notinv:
    "我发了一条朋友圈抨击该导师，然后心满意足地睡下了。"
    scene st_d with fade
    play music "audio/n_memory.mp3"
    "第二天醒来，我一如既往地到食堂吃过早餐后进教室等着上课。"
    show pyq1 with dissolve
    "在等待的时候，我掏出手机看了看朋友圈。"
    "有很多人给我点赞。"
    "果然大家跟我的想法是一样的吧。"
    "今日不站出来为他发声，明天受害的将会是我们自己。"
    "不过，田所给我评论说“快删掉”。"
    "我做的明明是为了正义……"
    "我不会删的。"
    "……"
    jump reject
label reject:
    scene ssroom with fade
    stop music
    "中午，我接到了辅导员的电话，说是让我去办公室一趟。"
    h "（这时候找我干什么？难道是因为朋友圈……）"
    scene gs_d with fade
    play music "audio/ne.mp3"
    "事实证明，我的直觉很准。"
    "一进办公室，就有几个老师围上来把我一顿批评。"
    show dy with dissolve:
        xalign 0.5 yalign 0.9
        zoom 1.5
    dy "你这样给学校声誉造成了很不好的影响，知道吗，嗯？"
    h "……但是"
    dy "没有但是！你赶紧把朋友圈删了，并且以后也不准再发相关内容了！"
    dy "不然学校这边也只有给你处分了。"
    dy "不要拿自己的前途开玩笑，懂吗？！"
    "……"
    "如此这般地，我被迫删除了那条朋友圈，他们才放我走。"
    hide dy
    scene zl_d with fade

    "为什么会变成这样呢？"
    "像辅导员说的一样，是我的错吗？"
    "我给学校抹黑了？"
    "但是，真正抹黑的人难道不是那名对学生犯罪的导师吗？"
    "加害者置身事外，为受害者发声的人却要受到处分。"
    "这不合理。"
    "下午上课的时候，我也一直在想这件事。"
    scene st_s with fade
    stop music
    "终于放学了。"
    "虽然我实在没什么心情吃饭，但为了一会合唱团训练，还是吃一点吧。"
    "我来到食堂，点了一份牛肉米线，就近找了个位置坐下。"
    play sound "audio/wechatmessage.mp3"
    "就在我等待米线做好的时候，手机突然传出收到新消息的提示音。"
    show text1 with dissolve
    h "（娜娜？）"
    "怎么是她？"
    "她明明应该不怎么用微信的吧。"
    "她那么小就去了国外，用的肯定是国外流行的app。"
    play sound "audio/typing.wav"
    "就连这个微信号都是我父母调到俄罗斯后，和她们家联系了，她才创建的新号。"
    play sound "audio/message.mp3"
    h "“怎么了”"
    "我回复道。"
    hide text1
    show text2
    play sound "audio/message.mp3"
    n "“你朋友圈删了，你遇到事我以为”"
    play sound "audio/typing.wav"
    h "（语法好奇怪啊。但是毕竟她也没有语言环境，能看懂就行吧。）"
    play sound "audio/message.mp3"
    hide text2
    show text3
    h "“没事”"
    "为什么娜娜会突然跳出来关心我。"
    "要是换做小时候，我肯定开始跟她诉苦了。"
    "但是很可惜，我已经从初恋情结中走出来了。"
    "已经决定要放下了。"
    hide text3
    show text4
    play sound "audio/message.mp3"
    n "“骗人”"
    "她的回复好直接。"
    "算了，不要跟娜娜说了。"
    "还是快点吃完饭去合唱团吧。"
    play sound "audio/typing.wav"
    "现在，也只有那里能让我安心了。"
    hide text4
    show text5
    play sound "audio/message.mp3"
    h "“我吃饭了，先不说了。”"
    hide text5 with dissolve
    "然后，我就关掉微信，以最快的速度吃完米线，向合唱团训练的教室走去。"
    scene yyjs_s with fade
    "进了排练室，不知为何有很多双眼睛齐刷刷朝我盯来。"
    play music "audio/whisper.mp3"
    "还有几个人在小声议论。"
    show sz2 with dissolve:
        xalign 0.5
        yalign 0.9
        zoom 1.75
    "团长看见我来了，脸上的表情有些僵硬。"
    "我正要站进队里去，又被叫住了。"
    l "毕涉，过来一下。"
    h "哦。"
    "团长示意我跟她出去。"
    stop music
    scene zl_s with fade
    show sz2 with dissolve:
        xalign 0.5
        yalign 0.9
        zoom 1.75
    h "怎么了？如果是副歌最后那段高音的话，我会努力练好的。"
    l "不是这个问题。"
    l "就是，嗯……"
    l "你发那条朋友圈，我看见了。"
    l "后来你删了对吧。"
    h "是校领导要求我删的。"
    l "我知道。"
    play music "audio/outcome.mp3"
    l "但是现在就是校文艺部下指令了。"
    "我心里“咯噔”一下。"
    l "所以……校方现在就是希望你自愿退出。"
    h "为什么。"
    l "我理解你的感受，不过如果你不选择自己退出的话，文艺部就要把这个通告发出去了。"
    "说着，她把手机里的文件照片给我看。"
    "通告的内容是因我毁坏学校声誉勒令我退团，上面还盖着文艺部的红印章。"
    "格外的刺眼。"
    l "我想，你自愿退出的话会体面一些。"
    h "……"
    h "那大赛怎么办？"
    "我好像一条在岸上垂死挣扎的鱼。"
    l "这个你不用管。我们有代替的人选。"
    h "……"
    h "就是赶我走的意思呗。"
    l "话不要说得这么难听，我也是不想这样才和你谈的。"
    h "还不都是一样，反正都是走。"
    h "自己滚和别人让你滚结果有什么不同吗？"
    "我越说越气，最后大笑三声。"
    h "哈哈，好！我退出！"
    play sound "audio/footsteps.mp3"
    "说完，我转身就走。"
    scene dark with fade
    stop sound
    play sound "audio/sigh.mp3"
    "但背后，却传来了团长松了一口气的声音。"
    jump lowpoint
label ne2:
    h "（是啊，冷静下来想想，我有什么把这事抖出去的必要呢。）"
    "多一事不如少一事。"
    "先不说别的，就算我在朋友圈发了这件事，也没有人会感谢我。"
    "而且死者为大，也不要过多追究人家的隐私比较好吧。"
    "我一边说服着自己，一边退出了发朋友圈的界面。"
    h "（没错，这样的选择才是正确的吧……）"
    "……"
    play music "audio/cpropose.mp3"
    scene yyjs_d with fade
    "四年后。"
    "我顺利于树莓大学毕业了。"
    "期间，我所在的银帆合唱团成功在各类大赛中获奖。"
    "算是留下了一段美好的回忆吧。"
    "毕业典礼结束后，我望着平常合唱团排曲子的教室，久久移不开眼睛。"
    "虽然很不舍，但是也不得不迈向人生的下一步了。"
    "再见了，所有的合唱团回忆。"
    "前方又会是什么在等着我呢？"
    "{b}NEUTRAL END{/b}"
    $renpy.full_restart()
label lowpoint:
    scene dark with fade
    play music "audio/gevent.mp3"
    "我如同僵尸般游荡着。"
    scene dt_d with fade
    "不知不觉，我坐上了地铁，随着列车绕了树莓市一圈，"
    scene dt_s with dissolve
    "一圈，"
    scene dt_n with dissolve
    "再一圈。"
    scene station with dissolve
    "直到这趟车今天最后一次抵达树莓大学站，我才浑浑噩噩地走出车厢，随着人流回到地面上。"
    scene lx_n with fade
    "感觉什么都思考不了。"
    "好后悔随便加入了合唱团。"
    "好恨这种处罚敢于说出真相的人的风气。"
    "更恨的是被夸了两句就再次选择信任别人的自己。"
    scene xm_n with dissolve
    "烂透了，烂透了。"
    "要处分我，大可以直接发通知。"
    "什么时候这种学生组织的活动也成了打压人的工具？"
    "我以为这里能承载我的归属感。"
    "结果呢？退团不是因为我唱得不好，而是校方施压。"
    scene ss_n with dissolve
    "我脚步不稳地踏进宿舍楼时，已经是第二天了。"
    "宿管大爷让我填完晚归理由就放我走了，并没问什么。"
    "可能他也看见我脸色不太好。"
    play sound"audio/opendoor.mp3"
    scene ssroom with fade
    "我拉开宿舍的门。"
    "灯还亮着，田所还没睡。"
    show ts with dissolve
    t "你去哪里了，我给你打那么多电话都不接。"
    "电话？是吗？"
    "我极其缓慢地掏出手机一看，果然。"
    "114个未接电话占满了我的消息通知栏。"
    t "吓死我了，还以为你出啥事了。"
    h "……"
    "我想开口，却发现嗓子干涩无比。"
    t "毕涉，你脸色怎么这样。"
    t "唉，你那朋友圈，是不是学校让你删的？"
    "我点了点头。"
    t "你就是太冲动了，我当时还想劝你别发来着……"
    h "那难道就眼睁睁看着这件事不了了之吗？"
    t "你别激动啊，我是说有更好的办法。"
    t "你看，你发朋友圈是实名的，如果有心人要举报你，那是一举报一个准。"
    t "要是你找那种记者呀什么的，就匿名采访说出实情，"
    t "不至于百分百学校不知道是你说的，但也不会这么快就被找到不是。"
    h "……"
    t "所以具体处分是什么，不让你评优了还是？"
    h "没有，是合唱团。"
    "我把下午合唱团团长说的话一五一十告诉了他。"
    t "这不是故意恶心人吗。"
    "我一口气说了太多话，现在有点头晕。"
    "田所看出了我的不适，便提议到阳台去透透气。"
    scene yt with fade
    h "唉……"
    show ts with dissolve
    t "事已至此，你只能先调整好自己的心态了。"
    "我又叹了一口气，没说话。"
    t "对了，要不我们周末出去玩，把不开心的事都忘掉好不好？"
    h "没心情。"
    t "就是为了让你有心情才出去的嘛。"
    "几个推拉回合下来，我还是没拗过他。"
    "……"
    show dark with circlewipe
    scene mall with circlewipe
    play music "audio/stable.mp3"
    "周末。田所带着我东逛西逛。"
    scene gaybar with fade
    play music "audio/gaybar.mp3"
    "到了晚上，我们去了一间外表很低调的酒吧。"
    show ts with dissolve
    t "你去过酒吧没有？"
    h "没，感觉不是我这种人该去的。"
    t "你看看你，又来了。"
    t "别想太多，这里一会有乐队演奏，你就权当放松心情吧。"
    "其实我不太习惯酒吧的氛围，但碍于田所的好意，还是待会吧。"
    "我坐在吧台前喝一杯朗姆可乐。"
    "不知为何，来这里的都是男人。"
    "是什么失意男人的秘密聚会吗，算了不管了。"
    play sound "audio/gaybarcheer.wav"
    play music "audio/ymca.mp3"
    scene gaybar2 with dissolve
    "奇异的音乐响起，一大群人开心地跳起舞来。"
    stop sound
    scene gaybar with dissolve
    show ts with dissolve
    t "走，咱们也去！"
    h "我不会跳啊。"
    t "这有什么的，瞎扭就行了！"
    "兴许是氛围，兴许是酒精作用，或者兴许是我对田所的信任。"
    scene gaybar2 with fade
    "我站起来，跟田所一起加入了狂欢的人群中。"
    show ts with dissolve:
        linear 0.9 xoffset 50
        linear 0.9 xoffset -50
        repeat
    t "（扭动）快看我自创的摆手开脚舞！"
    h "（扭动）哈哈哈哈哈哈哈哈好搞笑。"
    t "你感觉怎么样？"
    h "好像真的有点开心。"
    t "对吧！我觉得你需要一个发泄口！"
    show blurry behind ts with dissolve
    h "（酒精有点上头）嗯嗯。"
    stop music
    scene station with fade
    play music "audio/npropose.mp3"
    "我和田所畅快地瞎跳了一番，便准备回家了。"
    show ts with dissolve
    t "那我就回学校了，你回家小心点啊！"
    h "好。"
    t "有什么事随时找我说，因为我们是哥们嘛！"
    "……谢谢。"
    "哥们。奇特的称呼。"
    "我从来没有把一个同龄的友人称为“哥们”过。"
    "可能更多是因为关系没有好到那种地步。"
    "……"
    scene hroom_d with fade
    "总之，我失去了对学校活动的兴趣。"
    "教室，食堂，宿舍，每天三点一线地生活着。"
    "父母知道了我退团的前因后果，也只能无力地安慰我几句。"
    "就这样，过去了一年。"
    scene dark with fade
    scene xxgc with fade

    "新学期，这天我吃完午饭正要回宿舍。"
    "忽然发现食堂前的小广场上摆起了很多摊子。"
    "一看，每个摊子上都挂着不同社团的名称。"
    h "原来是招新啊。"
    "大一的时候，我因为加入了合唱团，对社团集体招新并没上过心。"
    "也没有去注意过。"
    show nvsheng with dissolve:
        xpos 0.6
        ypos 0.2
        zoom 1.9
    f "要不去看看吧？"
    h "（去看了又能怎么样。）"
    "我可不想再来一次合唱团的经历了。"
    f "我看街舞社就挺好的。"
    show nvsheng2 with dissolve:
        xpos 0.2
        ypos 0.2
        xzoom -1.9 yzoom 1.9
    f2 "嗯嗯，那我们去看看。"
    "……人家根本没和我说话。"
    hide nvsheng with dissolve
    hide nvsheng2 with dissolve
    "算了。"
    "不过要回宿舍就必须穿过那些摊位。"
    menu:
        "怎么办呢？"
        "去看看吧":
            jump isc
        "还是算了":
            jump isn
image nzoom:
    "n_idle.png"
    zoom 1.0
    linear 0.1 zoom 1.1
image nzoom1:
    "n_happy.png"
    zoom 1.1
image nzoom2:
    "n_happy.png"
    zoom 1.0
    linear 0.1 zoom 1.1
label isn:
    "我实在很难对学校里的集体活动产生什么信心了。"
    "赶紧走吧。"
    scene lx_s with fade
    "于是，又一周平平淡淡地过去了。"
    "我下了地铁，朝小区里走去。"
    stop music
    show nana1 with fade
    "但就在楼下——"
    play music "audio/n.mp3" fadein 1.0 fadeout 1.0
    hide nana1
    show nana1:
        zoom 3.3
        xalign 0.68 yalign 0.7
        linear 2.0 yoffset 850
    "我看见了，似曾相识的身影。"
    "虽然已经过去了十多年。"
    "但只有这个人，我不会认错。"
    play sound "audio/heartbeat.mp3"
    "心脏在高鸣着。"
    hide nana1 with dissolve
    h "——娜娜？"
    "她也发现了我。"
    show n_idle with dissolve
    "便像小鹿一样朝我奔过来。"
    hide n_idle
    show n_happy
    voice "voice/n1_1.mp3"
    n "圆圆！"
    voice "voice/n1_2.mp3"
    n "你回来啦！"
    stop sound
    with flashbulb
    with sshake

    "然后就是一个大大的拥抱。"
    "我的脑子转不过来了。"
    "为什么？娜娜为什么会在这里？"
    "难道这是我的幻觉？"
    "是我到了现在仍然没有放下她而出现的幻想吗？"
    h "你掐我一下。"
    hide n_happy
    show n_puzzled
    n "？？"
    "她一脸惊讶地伸出手，捏了一下我的脸。"
    h "你是真人吗？"
    n "难道还能是假人吗？"
    h "可是你为什么会在这里，而且中文还说得很好。"
    hide n_puzzled
    show n_idle
    n "我是过来当交换生的呀。"
    hide n_idle
    show n_happy
    n "为了申请学校的交换项目，我叫妈妈帮我恶补了一年中文呢！"
    "她很骄傲地掏出学生证给我看。"
    "派森大学 机械工程学院 安娜·陀思妥耶夫斯卡娅"
    "娜娜的全名这么复杂的吗？"
    "我从小就只叫她娜娜，完全不知道她的姓。"
    hide n_happy
    show n_pout
    n "其实我还有中间名，但是校方说名字再长就写不下了。"
    "她像小时候那样嘟起了嘴。"
    h "那你……"
    "我还想问，却不知道说什么了。"
    "为什么要在我失意的时候出现呢"
    "不想让她看见我现在这副样子。"
    "曾经的初恋已经长成了一个优秀的大人。"
    "甚至能成功申请到公费留学。"
    "而我却只是被一个又一个生活的打击推来搡去的失败者。"
    "见我不说话了，她上来拉我的手。"
    hide n_pout
    show nzoom
    n "走吧，到我家去。"
    h "你……为什么不回去住学校的宿舍。"
    hide nzoom
    show nzoom1
    n "当然是为了跟你待在一起呀！"
    "她无视了我的抗拒，反而直球说出了一些容易让人误会的话。"
    h "（不能当真不能当真……）"
    "我闭上眼睛，努力让自己的心跳平静下来。"
    "……"
    scene kt_s with fade
    play music "audio/stable.mp3"
    "好久没有进去过的娜娜家。"
    "还是像我记忆里那样熟悉。"
    show n_brag with dissolve
    n "怎么样，是不是很干净？"
    n "我昨天回来打扫了好久！"
    "她神气地叉起了腰。"
    h "是是是。"
    n "那，夸我。"
    hide n_brag
    show n_brag:
        xalign 0.65
        zoom 1.7
    "她凑过来，看起来想被我摸头的样子。"
    "就像小时候那样。"
    menu:
        "……"
        "摸摸":
            jump ytouch
        "不摸":
            jump ntouch
label ytouch:
    $love_points.add(10)
    hide n_brag
    show n_brag:
        xalign 0.65
        zoom 1.7
        linear 0.2 xoffset 20
        linear 0.2 xoffset -20
        repeat
    play music2 "audio/poke.mp3"
    "我无奈地揉了揉她的脑袋。"
    n "嘿嘿。"
    "娜娜满足地享受着抚摸。"
    "要是她有尾巴的话，现在应该已经摇起来了吧。"
    stop music2
    jump npropose
label ntouch:
    h "话说，你为什么要申请国内的大学？"
    "我强行转移了话题。"
    hide n_brag
    show n_idle
    h "派森大学的这个专业也不是特别厉害啊。"
    n "因为你在这里啊！"
    hide n_idle
    show n_upset
    n "你都不知道我有多担心你。"
    h "……"
    jump npropose
label npropose:
    scene kt_n with fade
    show n_idle with dissolve
    n "好了，你饿不饿？我去做饭。"
    h "呃，我就不用……"
    hide n_idle
    show n_puzzled
    n "但以前我们不是经常一起吃饭的吗？"
    h "以前是以前。"
    hide n_puzzled
    show n_idle
    n "现在和以前又没什么区别。"
    hide n_idle
    show n_bigeyes2
    n "我买了好多菜，一个人吃不完的。你就留下来好不好嘛？"
    hide n_bigeyes2
    show n_bigeyes1
    h "……好吧。"
    "被小狗一样的眼神盯着，实在是难以说出拒绝。"
    hide n_bigeyes1
    show n_happy
    n "好耶！那你等会，饭做好了叫你。"
    stop music
    hide n_happy with dissolve
    play music2 "voice/n7.mp3"
    "说完，她就开开心心穿上围裙，开始从冰箱里拿食材。"
    "我坐在了沙发上。"
    play music "audio/chopvegetables.mp3"
    "娜娜哼着歌，把洗好的菜放到案板上切碎。"
    "不知道她要做什么菜？"
    "我不禁想，如果我和娜娜在一起了，应该每天都能看到这副场景吧。"
    stop music
    play sound "audio/stove.mp3"
    "等等。说好的放下了呢。"
    play sound "audio/chaocai.mp3"
    "我不会再喜欢上她了。"
    "至少在弄清楚小时候她为什么一声不吭地消失了之前都不会。"
    "就在我发呆的时候，一口炖锅已经架在了灶上。"
    play sound "audio/boil.mp3"
    "里面的汤“咕嘟咕嘟”地响着。"
    n "还有二十分钟就能吃啦~"
    "她用汤勺在锅里搅动着，偶尔舀一点尝尝味道，偶尔往里加些调料。"
    "身影像极了以前她爸爸给年幼的我们俩做饭吃的样子。"
    "……在我的印象中，娜娜一直都是那个不擅长动手实践的小女孩。"
    "但看来，她已经成长改变了。"
    "那我呢？我成长了吗？"
    "恐怕没有。如果我真的成长了，又怎么会处理不好学校和合唱团那些破事。"
    "不知道为什么，我暗暗地有些嫉妒娜娜。"
    "明明在她走之后，我就决定要放下她，放下过去的一切，独立前行在人生道路上的。"
    stop music2
    stop sound
    scene dark with fade
    play music "audio/n_memory.mp3"
    "过去，我曾经喜欢过她，而且我觉得她也是喜欢我的。"
    "我们约好长大了要结婚，"
    "要一直在一起。"
    "那时我们每天都一起玩耍，一起上下学，去对方家里吃饭睡觉，亲密得好像一家人。"
    "我天真地以为这种日子会一直持续下去。"
    scene n_memory with fade
    "某天放学途中，我和娜娜路过学校旁的文具店。"
    show neckalace at truecenter with dissolve
    "她看中了一条项链，现在想来应该就是铁做的廉价小饰品。"
    hide neckalace
    show nlily1 with dissolve
    n "哇，这个好漂亮啊~~~"
    "娜娜在自己的口袋里摸了半天，只掏出两元零花钱。"
    hide nlily1
    show nlily3
    n "买不起欸，算了，咱们走吧！"
    hide nlily3 with dissolve
    "虽然我们没有多做停留，但回家的路上，她一直眉飞色舞地向我描述着那条项链有多么好看。"
    show nlily2 with dissolve
    n "等我长大了和你结婚的时候，就戴和那条一模一样的项链！"
    h "嗯！"
    hide nlily2 with dissolve
    "看来她是真的很想要。"
    "我的零花钱也没有多少，但只要我不吃零食不买玩具，攒一攒还是有的。"
    "想让喜欢的人开心。"
    "等她过生日了，我就给她写贺卡，再把项链也装进去。"
    "我等不及要看她收到项链有多惊喜了。"
    scene nhouse_memory with fade
    "于是在她过生日的前一天，我花了好长时间写贺卡。"
    "大意就是表达了一下我对她的喜欢以及要一直在一起的愿望。"
    "然后，把贺卡放进装着项链的盒子里，趁着晚上偷偷放到她家门口。"
    "当晚，我美滋滋地躺在床上想象第二天娜娜的反应。"
    scene airplane_memory with fade
    "但第二天，等来的却是她空荡荡的座位和老师说她出国了的消息。"
    "我全心全意信任着，喜欢着的人就这么突然地从我身边消失了。"
    "甚至连“再见”都没说。"
    "自那以后，我就开始抵触和人交流了。"
    scene kt_n with fade
    play music "audio/npropose.mp3"
    n "做好了，来吃吧！"
    "发小变成熟的声音把我拉回了现实。"
    scene kt_b with dissolve
    "她把热气腾腾的汤锅端到桌上，给我们一人盛了一大碗。"
    h "是什么菜？"
    "对于少下厨房的我来说，只闻得出很香，却不知道具体是什么。"
    show n_idle with dissolve
    n "炖牛肉。我爸教我的。"
    "是了，小时候，她爸爸也经常做炖牛肉给我们吃。"
    "我舀了一勺牛肉放进嘴里。"
    hide n_idle
    show n_determined
    n "好吃吧？是不是很好吃？"
    "娜娜好像一只叼回飞盘等待夸奖的小狗。"
    h "嗯，很好吃。"
    hide n_determined
    show n_brag
    n "哼哼，不愧是我！"
    "……虽然外表和能力都成长了，但性格还是没变。"
    hide n_brag
    show n_idle
    n "对了对了，你不吃胡萝卜对不对，我特意没给你盛。"
    h "是啊，真亏你还记得。"
    hide n_idle
    show n_happy
    n "我当然记得啊！"
    n "只要是关于你的，我都记得。"
    "她的话又让我一阵酸涩。"
    "那为什么不辞而别？"
    "不要再说这种好像把我放在心上一样的话了。我会误会的。"
    "如果你再一次从我身边离去的话，我又该怎么办呢？！"
    "把话说明白吧。"
    "即使，即使可能这下就做不成朋友了，"
    "我也想要一个答案。"
    scene cf_n with fade
    "吃完饭后，我帮着她把锅碗收拾了。"
    show n_stretch with dissolve:
        xalign 0.5 yalign 0.5
        linear 0.1 xoffset 10
        linear 0.1 xoffset -10
        linear 0.1 xoffset 10
        linear 0.1 xoffset -10
        linear 0.1 xoffset 10
        linear 0.1 xoffset -10
        linear 0.1 xoffset 10
        linear 0.1 xoffset -10
        linear 0.1 xoffset 10
        linear 0.1 xoffset -10
        linear 0.1 xoffset 10
        linear 0.1 xoffset -10
    n "嗯~~好累！"
    "她伸了一个大大的懒腰。"
    hide n_stretch
    show n_idle
    n "接下来干什么好呢？要一起学习？玩游戏还是看电影？"
    h "娜娜。"
    "我出声打断了她。"
    h "我有事要问你。"
    hide n_idle
    show n_puzzled
    n "怎么了？"
    n "坐下说吧。"
    scene kt_n with dissolve
    stop music
    "我们坐到了沙发上。"
    "加油啊。如果现在不问个清楚的话，这件事恐怕会成为我一辈子过不去的坎。"
    show n_bigeyes1 with dissolve
    play music"audio/title.mp3"
    h "就是，你当时出国的时候……"
    h "为什么没有告诉我？"
    "声音在颤抖。"
    n "……"
    "她沉默了一会才开口。"
    n "其实，我直到第二天早上起床才知道我们要走。"
    n "我爸告诉我，半夜他收到联系，说是爷爷去世了。"
    n "必须马上赶回圣彼得堡。"
    hide n_bigeyes1
    show n_bigeyes2
    n "我当时就想跟你说的！你相信我！"
    n "但是我去敲你家门的时候，你已经去上学了，叔叔阿姨也上班去了……"
    hide n_bigeyes2
    show n_bigeyes1
    n "对不起，真的对不起……"
    n "我到了爷爷那边之后一直想给你写信，但是当时俄语不好，完全没法寄信……"
    n "我打过电话，结果你们家的座机号好像也换了……"
    hide n_bigeyes1
    show n_neckalace:
        xalign 0.5
    n "只有这个陪着我……"
    "她说着，拨了一下自己颈上的项链。"
    "……项链？"
    n "这些年，我一次都没取下来过。"
    "她捻起项链上的那个爱心。"
    n "圆圆，对不起……"
    h "为什么，"
    play music "audio/rejection.mp3"
    hide n_neckalace
    show n_bigeyes1
    h "为什么突然消失又突然回来啊！！！"
    "人的崩溃往往只需要一瞬间。"
    "我无法控制地大喊起来，想要把积攒了十几年的情感一并宣泄而出。"
    h "是你先丢下我的！"
    h "那又为什么要在我努力忘记你的时候回来啊？！"
    h "你觉得道个歉我就原谅你了吗？！"
    h "你知不知道我有多难过？！"
    h "回来了就算了，为什么还表现得这么亲热啊？！"
    h "我跟你已经不是什么最好的朋友了！！！"
    "我几乎咆哮着，"
    h "呜……呜呜呜……"
    h "现在这样，要让我怎么放下……"
    hide n_bigeyes1
    show hcry with dissolve
    "我嚎啕大哭。"
    "最遗憾的不是告别，而是连告别都来不及。"
    hide hcry with dissolve
    hide n_neckalace
    show n_cry:
        linear 0.1 xoffset 10
        linear 0.1 xoffset -10
        linear 0.1 xoffset 10
        linear 0.1 xoffset -10
        pause 1.0
        repeat
    n "但是你不也没有联系我吗，而且放假也不去找我……"
    "娜娜也开始哭了。"
    n "明明我从来没有忘记过你……我心里最好的朋友那个位置一直是留给你的……"
    n "为什么好不容易又联系上了却不理我，呜呜……"
    h "最好的朋友，谁要跟你当朋友……"
    h "我是喜欢你的啊……"
    n "呜……明明是我比较喜欢你……"
    h "你又骗我……呜呜呜……"
    n "谁会跟不喜欢的人说长大了要跟他结婚啊？！"
    n "圆圆是笨蛋，不理你了！"
    h "你才是笨蛋！"
    scene dark with fade
    stop music
    "然后，我们像小学生吵架那样互骂对方是笨蛋，"
    "直到两个人都没力气了才停下。"
    scene kt_n with fade
    show n_bigeyes1 with dissolve
    n "……圆圆。"
    h "干嘛？"
    n "其实我这次是为了你才回来的。"
    n "你去年发的那个朋友圈，还有学校的事……"
    n "阿姨已经都告诉我了。"
    hide n_bigeyes1
    show n_cry
    n "我真的好担心，但是你又不肯跟我说。"
    hide n_cry
    show n_bigeyes1
    n "所以我只能申请来这边留学了……"
    hide n_bigeyes1
    show n_bigeyes2
    n "你记不记得小时候我被别的男生欺负，都是你站出来救我？"
    hide n_bigeyes2
    show n_bigeyes1
    n "现在轮到我来救你了。"
    h "……娜娜是笨蛋。干嘛救我这种人。"
    hide n_bigeyes1
    show n_upset
    n "那又怎么了，我乐意！"
    hide n_upset
    show n_idle
    n "话说，我们小时候约好的，"
    n "要一直在一起，还算数吗？"
    h "不算了。"
    h "你没守约，要交违约金十亿元。"
    "我故意没好气地说道。"
    hide n_idle
    show n_bigeyes2
    play music "audio/npropose.mp3"
    n "怎么办呢，我没有那么多。"
    hide n_bigeyes2
    show n_bigeyes1
    n "只能用我以后的人生来抵债了。"
    h "你说啥？"
    hide n_bigeyes1
    show n_bigeyes2
    voice "voice/n2.mp3"
    n "就是说，我们从现在开始再也不分开了，好不好？"
    "真是服了这个女人。"
    "为什么老是能让我精准破防呢。"
    h "说的不算，拉钩。"
    hide n_bigeyes2
    show n_idle
    n "好。"
    n "拉钩上吊，一百年不许变……"
    show dark with fade
    "我们拉起了钩。"
    "就像很久以前，曾经的我们所做的那样。"
    hide dark with fade
    h "其实你能一直戴着那条项链，我挺开心的。"
    hide n_idle
    show n_upset
    n "那你刚刚还对我那么凶。"
    h "……抱歉。"
    n "你要怎么赔我？"
    h "但我身上啥都没有，怎么赔？"
    scene n_kiss1 with flashbulb
    play music "audio/n.mp3"
    n "不是还有这个吗？"
    show n_kiss2
    "在我反应过来之前，"
    "她就印上了我的唇。"
    scene dark with fade
    "唉。"
    "看来我说了十几年的放下是白费功夫了。"
    "……"
    $isn = True
    $route=4
    jump daily0

label ndate:
    if count==35:
        jump ndate1
    elif count>=40 and count<=50:
        $i=renpy.random.randint(2,4)
        if i==2:
            jump ndate2
        elif i==3:
            jump ndate3
        elif i==4:
            jump ndate4

label ndate1:
    play music "audio/amusementpark.mp3"
    scene yly_d with fade
    "和娜娜正式确认关系后的第一次约会。"
    "地点在树莓欢乐谷。"
    "小时候，我们最期待的就是过生日可以去这种游乐园。"
    "不仅有过山车摩天轮，还有冰淇淋烤肠爆米花。"
    "充满了小孩会喜欢的东西。"
    h "不过，为什么是欢乐谷？"
    show n_dfist with dissolve
    n "那当然是因为我们分开的时候就是我的生日啊。"
    hide n_dfist
    show n_dburning
    n "我要把这十几年全都补回来！"
    "好吧好吧。"
    "她今天穿了新衣服，头发也特意打理了一番。"
    "根据我昨天学习了半夜的恋爱小贴士，这种时候应该夸夸她。"
    "我用尽毕生所学，努力寻找赞美的词。"
    h "你今天真……"
    hide n_dburning
    show n_dpuzzled
    n "？（看着我）"
    h "……真好看。"
    "啊啊啊啊我刚想好的一千二百字夸夸小作文呢？！"
    "被她的蓝眼睛注视着，就一下子忘得干干净净了。"
    hide n_dpuzzled
    show n_dpout
    n "只有今天好看吗？嗯？"
    "糟糕。"
    h "呃、这、当然不是，你天天都好看……"
    "我急得语无伦次。"
    hide n_dpout
    show n_dfist
    n "哈哈哈哈别紧张嘛~咱们还跟以前一样相处就好了。"
    hide n_dfist
    show n_dbye
    n "虽然我也很喜欢你紧张的样子~~~"
    "她凑到我的耳边说话，呼出的气息吹到我的脸上。"
    "感觉自己的脸一下就烧起来了。"
    "可怜的我，被娜娜玩弄在股掌之中。"
    hide n_dbye with dissolve
    "……"
    "树莓欢乐谷。"
    "由于是周末，里面挤满了带小孩的家长，以及像我们一样来约会的情侣。"
    show n_dsmile with dissolve
    n "我们先坐海盗船吧！"
    h "好啊。"
    hide n_dsmile
    show n_dhappy
    "她还是老样子，一上来先玩自己最喜欢的。"
    hide n_dhappy
    show n_didle
    n "那你先在这排着，我出去一下。"
    menu:
        "自己排队":
            jump hqueue
        "让娜娜排队":
            jump nqueue
label nqueue:
    h "还是你先排着吧，我先出去一下。"
    hide n_didle
    show n_dlips
    n "诶——————"
    hide n_dlips with dissolve
    "虽然有些对不起娜娜，但是我突发奇想，觉得应该给她整个惊喜。"
    "毕竟总是被她拿捏，想反将她一军嘛。"
    "我来到了小吃摊周围，想找点吃的买给她。"
    show nvsheng with dissolve:
        xpos 0.2
        ypos 0.3
        zoom 1.5
        linear 1.0 xoffset 200
    show nansheng2 with dissolve:
        xpos 0.6
        ypos 0.3
        zoom 1.5
    f "来，张嘴~"
    hide nansheng2
    show nansheng2:
        xpos 0.6
        ypos 0.3
        zoom 1.5
        linear 1.0 xoffset -200
    ns "啊~"
    "正愁想不到买啥呢，偶然看到一对情侣在互喂冰激凌。"
    h "就这个了。"
    hide nvsheng
    hide nansheng2
    "拿定主意后，我去买了两支冰激凌，回去找娜娜。"
    h "我回来啦~"
    show n_dpout with dissolve
    n "真是的，到底去哪里——"
    hide n_dpout
    show n_dexcited
    n "哇，冰激凌耶，给我的吗？"
    h "当然了。"
    h "来，张嘴~"
    "我把香草味的那支递到她嘴边。"
    hide n_dexcited
    show n_dicesmile2
    n "啊~"
    n "好吃~"
    n "你也来吃。"
    "她把咬过的冰激凌递给了我，我咬了一口后还给了她。"
    n "果然还是喜欢香草味呢~"
    h "是啊，我又不是什么都不记得。"
    hide n_dicesmile2
    show n_dicesmile1
    n "圆圆也有贴心的一面嘛。"
    h "哼，我咋就不能贴心啊。"
    hide n_dicesmile1 with dissolve
    "还没等我反应过来，娜娜的嘴唇已经和我的贴在了一起"
    with flashbulb
    "然后她退后几步，头扭向一边。"
    show n_dfist
    n "……"
    n "这是奖励。"
    hide n_dfist
    show n_dcold
    "为了掩饰自己的害羞，娜娜咬了一大口自己那支香草冰淇淋。"
    n "啊！！！"
    n "冰到牙了！！"
    "……我的女朋友好可爱。"
    "……"
    $love_points.add(15)
    jump ndate1end
label hqueue:
    h "……行。"
    play sound"audio/footsteps.mp3"
    hide n_didle with dissolve
    "虽然排队是我该做的，但娜娜突然把我一个人留在这里走了，我心里还是有点不高兴。"
    show nvsheng with dissolve:
        xpos 0.2
        ypos 0.3
        zoom 1.5
        linear 1.0 xoffset 200
    show nansheng2 with dissolve:
        xpos 0.6
        ypos 0.3
        zoom 1.5
    f "来，张嘴~"
    hide nansheng2
    show nansheng2:
        xpos 0.6
        ypos 0.3
        zoom 1.5
        linear 1.0 xoffset -200
    ns "啊~"
    "排在我前面的一对情侣正在亲热地互喂零食。"
    "真好啊，我也想要。"
    "可恶的娜娜，到底干什么去了。"
    hide nvsheng
    hide nansheng2
    play sound"audio/footsteps.mp3"
    show n_dice with dissolve
    n "我回来了~"
    h "怎么这么久——"
    "我才抱怨到一半，忽然注意到她手上拿的东西。"
    "是两支冰淇淋。"
    hide n_dice
    show n_diceupclose
    n "来，啊~"
    "她笑眯眯地把巧克力味的那支递到我嘴边。"
    h "啊~"
    h "好吃。"
    hide n_diceupclose
    show n_dicesmile1
    n "真的吗？我也尝尝。"
    "然后她毫不在意地就着我咬下的缺口咬了一口，又把冰淇淋递到我手上。"
    hide n_dicesmile1
    show n_dicesmile2
    n "真的耶！还是那个味道。"
    h "所以，你刚刚就是去买冰淇淋了吗？"
    hide n_dicesmile2
    show n_dicesmile1
    n "对呀！你从小不就爱吃这里的冰淇淋嘛！"
    "看来我误会她了……"
    hide n_dicesmile1
    show n_dicesmile2
    play sound"audio/gshine.mp3"
    n "怎么样，我是不是很贴心！"
    "如果现在手上没有冰淇淋的话，她一定会叉腰的吧。"
    h "嗯，娜娜最贴心了"
    hide n_dicesmile2
    show n_diceupclose
    voice "voice/n3.mp3"
    n "那，给我奖励……"
    voice sustain
    "她嘟了嘟嘴示意我。"
    h "……"
    hide n_diceupclose
    show n_diceupclose:
        xalign 0.5 yalign 0.5
        zoom 1.0
        linear 1.0 zoom 1.5
    "我慢慢靠近她……"
    lr "咳咳。"
    hide n_diceupclose
    show n_diceupclose
    n "啊不好，还在排队呢。"
    n "走吧！"
    "被路人这么一提醒，我和她都怪不好意思的。"
    hide n_diceupclose
    show n_dcold
    "为了掩饰自己的害羞，娜娜咬了一大口自己那支香草冰淇淋。"
    n "啊！！！"
    n "冰到牙了！！"
    "……我的女朋友好可爱。"
    "……"
    jump ndate1end
label ndate1end:
    play music "audio/stable.mp3"
    scene yly_n with fade
    "我们一直玩到晚上，欢乐谷的灯光亮起，夜景十分好看。"
    "真开心。"
    "和自己喜欢的人一起去欢乐谷玩居然会这么开心。"
    "就像回到了无忧无虑的小时候。"
    "我盯着远处摩天轮上一闪一闪的霓虹灯发呆。"
    show n_dsmile with dissolve
    n "我们要不要拍照留念一下？"
    hide n_dsmile
    show n_dhappy
    n "来笑一个~"
    play sound "audio/snap.mp3"
    show n_dphoto1 with flashbulb
    "娜娜打开了自拍app，举着剪刀手对着镜头摆姿势,拍了一张。"
    n "你过来一点嘛，不然我挡着你拍不到了。"
    hide n_dphoto1
    show n_dphoto2
    "说着，她硬是搭着我的肩膀，还把我的手往她腰上揽。"
    play sound "audio/heartbeat.mp3"
    "心跳得好快啊，不会被她听见吧？"
    stop sound
    n "看镜头，笑一下~"
    h "这样吗？"
    hide n_dphoto2
    show n_dphoto4
    "我努力地挤出笑容。"
    play sound "audio/snap.mp3"
    with flashbulb
    "咔嚓。"
    hide n_dphoto4 with dissolve
    h "让我看看。"
    "我探头一看——"
    show n_dphoto5 with dissolve
    "照片上的我在傻笑，娜娜在一旁举着剪刀手做鬼脸。"
    "然后，她还用了什么滤镜，在我俩的脸上画了胡须，头上画了猫耳。"
    h "……"
    "为什么只有我在傻笑啊？！"
    n "是不是很可爱？"
    h "但是只有我一个人在笑，看起来好尴尬。"
    h "还有这个猫耳，我要怎么发给家长看啊啊啊啊？"
    hide n_dphoto5 with dissolve
    n "但是我喜欢这张耶。那要不我们再拍一张？"
    h "拍什么样的？"
    n "两个人一起傻笑的。"
    "所以为什么就认定我只会傻笑啊？？？？"
    n "一，二，茄子！"
    play sound "audio/snap.mp3"
    show n_dphoto3 with flashbulb
    "咔嚓。"
    "画面上的两人勾肩搭背，脸上是大大的笑容。"
    "不管谁看了，都会觉得这是一对笨蛋情侣吧。"
    hide n_dphoto3 with dissolve
    hide n_dhappy
    show n_dsmile
    n "发给你吧。"
    hide n_dsmile
    show n_dhappy
    n "这张要不要加猫耳？"
    h "千万别！"
    hide n_dhappy with dissolve
    "但我还是偷偷把这两张照片设成了手机壁纸。"
    "当然这是后话了。"
    if count<50:
        jump daily0
    elif count==50:
        jump nendcheck

label ndate2:
    if ndateflag2==True:
        jump ndate
    scene mall with fade
    "商场。"
    "娜娜带着我到处逛服装店。"
    "忽然她停下来转身看我，大喊："
    show n_happy with dissolve
    n "ударная проверка(突击测试)！"
    h "？？？？？？"
    "突然发什么神经。"
    hide n_happy
    show n_determined
    play sound "audio/quiz.mp3"
    n "还记得我的全名是什么吗？"
    h "啊啊？"
    hide n_determined
    show n_determined:
        zoom 1.0
        parallel:
            linear 0.1 zoom 1.4
        parallel:
            linear 0.1 xpos -0.25 ypos -0.2
        parallel:
            linear 0.1 xoffset 10
            linear 0.1 xoffset -10
            repeat
    menu:
        n "还 记 得 吗 ？"#脸逼近，抖动
        "“安娜·陀思妥耶夫斯卡娅”":
            jump ndate2y
        "“娜塔莎·奎恩·爽·孙笑川斯基”":
            jump ndate2n
label ndate2y:
    hide n_determined
    show n_happy
    play sound "audio/right.mp3"
    n "宾果~"
    n "给你奖励的亲亲。"
    n "啾~~~~"
    $ndateflag2 = True
    $love_points.add(15)
    if count<50:
        jump daily0
    elif count==50:
        jump nendcheck

label ndate2n:
    hide n_determined
    show n_sus
    play sound "audio/wrong.mp3"
    n "连这个都不记得还好意思当人家男朋友。"
    hide n_sus
    show n_upset
    n "圆圆是笨蛋！"
    $ndateflag2 = True
    if count<50:
        jump daily0
    elif count==50:
        jump nendcheck

label ndate3:
    if ndateflag3==True:
        jump ndate
    scene hroom_d with fade
    "家。"
    "我在疯狂学习，马上就要考试了。"
    play sound"audio/bell.wav"
    "就在这时，门铃响了。"
    "打开门一看，没有人。"
    "不过地上有个盒子，上面塞着个纸条。"
    "上面写道："
    n "“最近咱们都忙着学习，偶然想起有爸爸托运过来的土特产，拿来给你尝尝。————娜娜”"
    "果然她也要考试了啊，忙得连个面都不露一下。"
    "我把盒子拿了进来，拆开，发现里面有个黑乎乎的东西。"
    "它散发着一股面包的香气，但是硬度堪比中秋节月饼。"
    h "(这该不是传说中的大列巴......吧.......)"
    menu:
        h "(怎么办好呢......)"
        "吃掉":
            jump ndate3y
        "不吃":
            jump ndate3n

label ndate3y:
    "我一遍感受着板砖一样的硬度，一遍一口接一口地吃完了。"
    "然后发现后槽牙传来一股剧痛，果然是牙碎了吗。"
    scene xxgc with fade
    "周日，返校后，娜娜跑过来找我。"
    show n_idle with dissolve
    n "圆圆圆圆，你收到我的礼物了吗？"
    h "收到了（嘶）。"
    hide n_idle
    show n_sus
    n "真的吗？不要骗我。"
    h "这就是证据。"
    "我指了指肿起来的半边脸。"
    hide n_sus
    show n_bigeyes2
    n "呀，不会把牙吃坏了吧，我寻思老家那边的人吃着没事啊....."
    hide n_bigeyes2
    show n_idle
    n "不过你能喜欢我送的东西真是太好了，下次给你吃点不伤牙的东西吧。"
    h "嗯。（欲哭无泪）"
    $ndateflag3 = True
    $love_points.add(15)
    $stress.add(10)
    if count<50:
        jump daily0
    elif count==50:
        jump nendcheck

label ndate3n:
    "还是算了吧，把牙吃坏了怎么办。"
    "我默默地把它收到了门口，这个硬度防身应该不错。"
    scene xxgc with fade
    "周日，返校后，娜娜跑过来找我。"
    show n_idle with dissolve
    n "圆圆圆圆，你收到我的礼物了吗？"
    h "收到了"
    n "吃掉了吗？"
    menu:
        "撒谎":
            jump ndate3end1
        "说实话":
            jump ndate3end2

label ndate3end1:
    h "吃了。"
    hide n_idle
    show n_sus
    n "真的吗？"
    h "真的。"
    hide n_sus
    show n_happy
    n "太好了，下一次让爸爸多给你送点。"
    "？？？？？"
    h "呃......替我谢谢叔叔......"
    "完了啊，以后不吃不行了啊......"
    $ndateflag3 = True
    $stress.add(10)
    if count<50:
        jump daily0
    elif count==50:
        jump nendcheck

label ndate3end2:
    h "没吃。"
    hide n_idle
    show n_upset
    n "为什么嘛？"
    h "这么硬的东西怎么嚼得动嘛，跟中秋节月饼有一拼了都。"
    hide n_upset
    show n_puzzled
    n "但是老家那边的人吃着没问题啊。"
    h "人和人的体质是不能相提并论的....."
    hide n_puzzled
    show n_bigeyes1
    n "知道了嘛，下次给你买点不那么硬的东西吃。"
    n "还好你没有瞎说，要不然早晚吃坏了牙。"
    h "唉....."
    "我松了口气。"
    $ndateflag3 = True
    $love_points.add(10)
    if count<50:
        jump daily0
    elif count==50:
        jump nendcheck


label ndate4:
    if ndateflag4==True:
        jump ndate
    scene pool with fade
    "和娜娜一起去了新开的水上乐园。"
    show n_p1 with dissolve:
        pause 0.4
        linear 0.1 yoffset -10
        linear 0.1 yoffset 10
    n "怎么样，好看吧~"
    h "好看啊。"
    "好看是好看，就是我有点不太好意思。"
    hide n_p1
    show n_p2
    n "好了，下水前我们来热身。"
    $ renpy.movie_cutscene("audio/n_warmup.webm")
    "说着，娜娜站在池子边开始做热身动作。"
    n "圆圆也来嘛！"
    n "不要等到在水里抽筋了才后悔哟~"
    menu:
        "听她的":
            jump ndate4y
        "不听她的":
            jump ndate4n
label ndate4y:
    h "知道了。"
    hide warmup
    "我跟着娜娜做完了整套热身才下水。"
    "我们比赛游泳，玩得很开心。"
    $ndateflag4 = True
    $love_points.add(15)
    if count<50:
        jump daily0
    elif count==50:
        jump nendcheck
label ndate4n:
    h "我才不做。"
    hide warmup
    hide n_p2
    show n_p3
    n "为什么嘛！万一抽筋了怎么办！"
    "我没听她的，径直跳进了水里。"
    "但是，就在之后和娜娜的游泳比赛中……"
    "我游到一半，小腿肚子就抽筋了。"
    "不管怎么扑腾都没用。"
    scene water with fade
    h "？！咕噜咕噜咕噜……"
    "我沉了下去。"
    n "啊啊啊啊啊圆圆！！！！"
    "意识有点朦胧。"
    "虽然最后被娜娜救了起来，但我还是呛了好大几口水，差点被送医院。"
    $ndateflag4 = True
    $stress.add(10)
    if count<50:
        jump daily0
    elif count==50:
        jump nendcheck
label nendcheck:
    if love_points.value>=50:
        jump nge
    elif love_points.value<50:
        jump nbe
label nge:
    scene n_wedding with fade
    play music "audio/wedding.mp3"
    "时光飞逝。"
    "昔日骄傲的小女孩，我的青梅竹马，"
    "如今正穿着婚纱站在我面前。"
    "说不上来的感动。"
    "我们正在娜娜的家乡圣彼得堡的一个教堂里。"
    "虽然在国内已经办过一次喜酒了，"
    "不过这次主要是为了让她父亲那边的亲朋好友参与。"
    "而且，娜娜自己其实也很期待在教堂里举行婚礼。"
    "神父叽里呱啦地说着俄语。"
    "虽然听不懂，但我能理解这是婚礼誓词。"
    scene n_weddingbg with dissolve
    show n_w1 with dissolve
    voice "voice/n4.mp3"
    n "他问你愿不愿意一辈子和我在一起，爱我，关心我。"
    "娜娜充当了翻译。"
    n "愿意的话就说Да。"
    "她笑盈盈地等着我的回答。"
    "娜娜太狡猾了，只告诉我肯定的回答，"
    "哪有我选择的余地。"
    "可惜她不知道，我还有这一招。"
    h "但是，我拒绝！"
    hide n_w1
    show n_w2
    n "？？？"
    "我早就预料到她会是这个反应，于是接着说。"
    h "一辈子太短了，要一千辈子，一万辈子，"
    h "一直一直在一起，我才答应。"
    hide n_w2
    show n_w3
    "娜娜呆了一下，随即泛起了泪花。"
    h "别哭啊，大喜的日子哭什么……"
    "我手忙脚乱地想安慰她，她却抢先扑进了我怀里。"
    hide n_w3
    show n_w4
    voice "voice/n5.mp3"
    n "那就说好了，要一千辈子，一万辈子，永远在一起！"
    voice sustain
    "周围的人虽然听不懂我们的交流，但也从氛围中感受到了什么，"
    play sound "audio/pachi.mp3"
    "纷纷站起来祝贺我们。"
    "执子之手，与子偕老。"
    "这一定是对我，对她也是，最好的结局。"
    stop sound
    "{b}GOOD END{/b}"
    $renpy.full_restart()
label nbe:
    stop music
    show dark with circlewipe
    scene nbe with circlewipe
    "致我永远的爱人毕涉："
    "你还记得我们第一次约会的地方吗？"
    "树莓欢乐谷，现在仍在营业。"
    "那里承载了好多我们的回忆。"
    "不管是小时候还是交往后，我们都经常去那里玩。"
    "你最爱吃那里的巧克力冰淇淋，我给你带过来了。"
    "我昨天去那里买的，还拍了照片。"
    "就像我们第一次约会那样。"
    "你想我的时候，就看看照片吧。"
    play music "audio/nbe.mp3"
    "从你突发心脏病走后，已经过了十年。"
    "我好想你。"
    "还想和你一起去玩，和你一起看电影，吃饭，和你去各种各样的地方。"
    "不想去也没关系，在家里待着什么都不做也没关系，"
    "只要身边有你就很好了。"
    "你会不会已经忘记我了呢？"
    voice "voice/n6.mp3"
    "我不会忘记你的，过去没有，以后也不会。"
    voice sustain
    "你送我的项链，我到现在还戴着。"
    "告诉你一个小秘密。"
    "我柜子里的婚纱，是我外婆送给妈妈，她又送给我的。"
    "真想让你看看我穿婚纱的样子。"
    "不过，我这辈子应该都没机会穿了吧。"
    "你在那里一定很孤单对不对？"
    "我现在还要赡养父母，所以暂时抽不开身。"
    "等到了时候，我就会去见你的。"
    "要等我哦。"
    "я буду любить тебя вечно."
    "你的，"
    "安娜·毕（原谅我这么写）"
    "{b}BAD END{/b}"
    $renpy.full_restart()
label isc:
    "随便看看吧，又不会掉块肉。"
    "我随意张望着。"
    "有在发传单的，有靠唱歌跳舞什么吸引人的，还有……"
    h "吃饭社又是什么鬼。"
    "有三个人正在桌前开开心心地吃饭，头上的棚子挂着一个横幅：吃饭社。"
    "就在我百思不得其解的时候——"
    "咚！"
    "我被某种不知名的冲击撞倒在地。"
    h "艹……"
    "感觉遇到这种突发状况时，中国人都会下意识甩出一句国骂。"
    u "啊疼……"
    "我才看清还有个人跟我一样坐在地上。"
    "是个穿着JK制服的女生。"
    "不知道刚刚到底发生了什么，还是问问她吧。"
    h "同学，你还好吗？"
    "我爬起来，拍了拍自己身上的灰尘。"
    f "……"
    "她好像想说什么，但最终只是摇了摇头。"
    f "嘶——"
    "疼痛让她皱起了眉头。"
    h "你膝盖流血了。"
    "我指着她的膝盖。"
    f "啊这个，那个……对、对不起……"
    h "？？？"
    "为什么突然道歉了。我好像没有说什么重话吧？"
    h "算了，先起来吧，地上脏。"
    "我试图伸手拉她。"
    "她迟疑了一下，还是接住了我的手，借力站了起来。"
    f "谢谢……"
    "她很不好意思地拍打着自己衣服上的灰尘。"
    h "没事，你还是快去校医院处理一下吧。"
    "说完，我打算转身离去。"
    "但身后却传来了她微弱的声音。"
    f "呃，我不知道在哪里……"
    "新生？"
    "好吧，那只好帮人帮到底了。"
    "我又朝她转了过去。"
    h "那，我带你去吧。"
    "女生露出了很不可思议的表情。"
    f "对、对不起！你听见了？"
    "怎么感觉比我还社恐。"
    h "你不是说你不知道校医院在哪吗。"
    f "嗯，那是我在自言自语……"
    f "我不是有意要麻烦你的……"
    "她不好意思地低下了头。"
    h "不麻烦，走吧走吧。"
    "我毕涉今天又做了一件好事，啊，好为自己骄傲。"
    "我带她来到校医院，教她怎么挂号，然后陪她在医院走廊里坐着等叫号。"
    "先说好，这不是在把妹，而是我还没搞清楚刚刚谁撞的我，要问问她。"
    h "话说刚刚到底怎么回事？"
    f "就是，有个人突然冲过来……"
    h "然后就把我俩都撞了？"
    f "（点头点头）"
    "唔，有点可爱，好像小动物。"
    h "那你认识那个人吗？"
    f "（摇头摇头）"
    h "唉，感觉是找不到人了。"
    h "话说你是新生？"
    f "……嗯。我是QQ捏捏难学到咩噗语专业的。"
    h "？？？什么语？"
    f "……QQ捏捏难学到咩噗语。"
    "她重复了一遍，但我还是怀疑自己的耳朵。"
    "有这种语言的吗？？"
    "世界还真大啊。"
    h "好吧。"
    "我也不知道该说些什么了，于是掏出手机玩起了游戏。"
    s "指挥官，欢迎回来~有没有想人家？"
    "惨了，我忘了关声音。"
    "画面上的纸片人摆着可爱的姿势，用撒娇的语气大声叫我指挥官。"
    "啊啊啊啊啊社死了。"
    f "？？？"
    "空气一度十分安静。"
    "完了，要被当成恶心死宅了。"
    "女生飞快地朝我这边瞟了一眼。"
    "不、不是你想的那样啊啊啊啊！！！！"
    f "咦，这个不是新出的SSR吗？！"
    "只见她的眼睛“嗖”一下亮了起来。"
    f "你也玩这个呀！"
    f "我也在玩，但是周围都没有人跟我聊这个。"
    "她掏出手机，打开了自己的游戏界面。"
    f "我昨天氪了三单都没抽出来，气死了。"
    "这个人是那种，聊到兴趣爱好的时候话会变得很多的那种类型吗？"
    "反差还真大。"
    h "呃是啊，你怎么氪了那么多，上头毁一生啊。"
    f "因为她真的好可爱，是我老婆！！话说你怎么抽出来的，我好羡慕呜呜。"
    h "就是每日免费送的单抽……"
    f "为什么那么欧啊啊啊啊——"
    f "啊。"
    "她好像意识到自己过于兴奋了，又一下缩了回去。"
    h "咳咳。"
    "为了不让她尴尬，善良的我就来找点话说吧。"
    h "话说回来，我还没自我介绍，我叫毕涉，计算机大二的。"
    f "嗯……那就是学长了……"
    "她红着脸点点头。"
    c "我是陈语嫣……今年大一，刚满18……"
    c "真不好意思，还让学长陪我来医院……"
    h "没事，应该的。"
    c "话说学长……有什么推荐的社团吗？"
    "社团啊。我大一的时候根本没去看过别的社团，恐怕也不能提供什么意见。"
    h "你就想想，自己有什么兴趣？"
    c "嗯……我喜欢动漫……"
    c "我刚刚拿了一张动漫社的传单，上面说今晚有迎新晚会，"
    c "但我不知道这个楼在哪里……"
    c "而且也不太敢自己一个人去……"
    c "其实我有点社恐，很害怕和陌生人说话……"
    "这个我早看出来了。"
    "闲着也是闲着，不如晚上我带她去好了。"
    "反正我对动漫社也有点兴趣。"
    h "我也有点想去看看，那我晚上跟你一起去吧。"
    c "真、真的吗？！"
    "她好像很开心。"
    h "话说，你不是害怕跟陌生人说话吗，可我感觉还好啊。"
    c "那是因为学长不算陌生人了……"
    c "学长是大学里第一个帮助我的人……"
    c "而且还陪我聊手游，还愿意带我去社团……"
    "她天真地笑了起来。"
    "她这么信任我，怎么感觉像那种刚出壳的小鸡，会把第一眼看的生物当成妈妈。"
    "啊，不过我可不是男妈妈。"
    y "下一个！"
    h "医生叫你了。"
    c "嗯，那我去包扎了。"
    "处理完伤口，她又回到我旁边。"
    c "那我们加一下微信吗？"
    h "好。到点了我去女生宿舍楼下找你？"
    c "嗯，好。"
    "晚饭后。"
    "看着差不多该到点了，我准备出发去找学妹。"
    h "……唔。"
    "突然发现自己的衣服上有点油渍。"
    "要不要换一套呢？"
    menu:
        "换一套吧":
            jump ychange
        "算了":
            jump nchange

label ychange:
    "换一套吧。"
    "怎么说，穿着带油渍的衣服去见人都太邋遢了。"
    "况且还是个刚认识不到一天的学妹。"
    "身为前辈的尊严不允许我摆烂。"
    "我换了一套干净衣服，朝女生宿舍走去。"
    $love_points.add(10)
    jump st

label nchange:
    "换个锤子，一点油渍而已。"
    "还是赶快出发吧。"
    "我直接朝女生宿舍走去。"
    jump st

label st:
    c "学长！"
    "看来她早就等在楼下了。"
    h "噗。"
    "虽然这种时候不该笑的，但她看见我就跑过来的样子，"
    "真的很像站起来的北极兔那张动图。"
    c "？？？怎么了？"
    h "没什么，就是，我想起……高兴的事情（噗）"
    "未完待续"
    $renpy.full_restart()
