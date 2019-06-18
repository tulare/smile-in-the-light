"""
Starting Template

Once you have learned how to use classes, you can begin your program with this
template.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.starting_template
"""
import sys
import argparse
import random
import arcade

#SCREEN_WIDTH = 640
#SCREEN_HEIGHT = 480
SCREEN_TITLE = "Pong"

BOUNCE_FACTOR = 1.1
MAXSPEED = 30
MATCH_WIN = 11

PADDLE_SCALE = 0.2
BALL_SCALE = 0.6

import cv2 as cv
from ui.capture import CaptureManager
from ui.window import WindowManager
from processors.core import FrameProcessor
from processors.trackers import Tracker


class TrackingProcessor(FrameProcessor) :

    def __init__(self, algo) :
        self.algo = algo
        self.tracker = None
        self.tracked = False
        super().__init__()

    def params(self, **kwargs) :
        self.tracker = Tracker.create(self.algo)
        
    def apply(self, frame, context) :
        # init tracking on first frames
        if not self.tracked :
            self.tracked = self.tracker.init(frame, context.rect)
            return frame

        # update tracking on following frames
        success, rect = self.tracker.update(frame)
        if success :
            x, y, w, h = (int(v) for v in rect)
            context.rect = (x, y, w, h)
            cv.rectangle(frame, context.rect, (0,255,0), 2)
        else :
            cv.rectangle(frame, context.rect, (0,0,255), 2)
        
        return frame


class Detector :

    def __init__(self, source, algo, bbox) :

        # use DSHOW api for windows
        api = cv.CAP_ANY
        if isinstance(source, int) and sys.platform == 'win32' :
            api = cv.CAP_DSHOW

        self.cam = cv.VideoCapture(source, api)
        self.win = WindowManager('capture', self.onKeypress)
        self.win.createWindow()
        self.win.waitKeyDelay = 1
        self.cap = CaptureManager(self.cam, self.win, False)

        # screen
        self.cap.width = SCREEN_WIDTH
        self.cap.height = SCREEN_HEIGHT
        # to do : check if it works

        # initial rect for detection
        self.rect = bbox

        # processor
        self.proc = TrackingProcessor(algo)

    @property
    def frameno(self) :
        return self.cap.framesElapsed

    @property
    def width(self) :
        return self.cap.width

    @property
    def height(self) :
        return self.cap.height

    @property
    def algo(self) :
        return self.proc.algo

    @property
    def center_x(self) :
        """
        x coordinate of the self.rect center
        """
        return self.rect[0] + self.rect[1] // 2

    @property
    def center_y(self) :
        """
        y coordinate of the self.rect center
        """
        return self.rect[1] + self.rect[3] // 2
        
    def onKeypress(self, keycode) :

        if keycode == ord('-') :
            self.win.waitKeyDelay -= 1
        elif keycode == ord('+') :
            self.win.waitKeyDelay += 1

        if self.win.waitKeyDelay < 1 :
            self.win.waitKeyDelay = 1            


    def update(self) :
        # enter frame and capture
        self.cap.enterFrame()
        frame = self.cap.frame

        # horizontal mirror
        frame[:,::-1,:] = frame

        # process to detection
        frame = self.proc.apply(frame, self)

        # display feedback
        self.display_infos(frame)

        # exit frame and process events
        self.cap.exitFrame()

    def display_infos(self, frame) :
        text_info = '{} {}x{} @{:.0f}fps - {:2d}ms - {:4d}'.format(
            self.algo,
            self.width, self.height,
            self.cap.fpsEstimate,
            self.win.waitKeyDelay,
            self.frameno,
        )            
        cv.putText(
            frame,
            text=text_info,
            org=(15, 15),
            fontFace=cv.FONT_HERSHEY_SIMPLEX, fontScale=0.5,
            color=(0, 0, 0),
            thickness=1
        )    
        cv.putText(
            frame,
            text=text_info,
            org=(14, 14),
            fontFace=cv.FONT_HERSHEY_SIMPLEX, fontScale=0.5,
            color=(0, 215, 255),
            thickness=1
        )    

class Ball(arcade.Sprite) :
    """
    Class to keep track of a ball's location and motion vector
    """
    def __init__(self) :
        super().__init__('images/ball.png', scale=BALL_SCALE)

    def update(self) :
        # move the ball
        self.center_x += self.change_x
        self.center_y += self.change_y

        # limit ball speed to MAXSPEED
        if self.change_x > MAXSPEED :
            self.change_x = MAXSPEED

        if self.change_x < -MAXSPEED :
            self.change_x = -MAXSPEED

        if self.change_y > MAXSPEED :
            self.change_y = MAXSPEED

        if self.change_y < -MAXSPEED :
            self.change_y = -MAXSPEED

        # bounce on left wall (screen limit)
        if self.left < 0 :
            self.left = 0
            self.change_x *= -1

        # bounce on right wall (screen limit)
        if self.right > SCREEN_WIDTH :
            self.right = SCREEN_WIDTH
            self.change_x *= -1


def make_ball() :
    """
    Function to make a new, random ball.
    """
    ball = Ball()

    # starting position on screen
    ball.center_x = random.randrange(100, SCREEN_WIDTH - 100)
    ball.center_y = SCREEN_HEIGHT // 2

    # random speed and direction
    ball.change_x = random.randrange(5, 10)
    ball.change_y = random.randrange(5, 10)

    return ball


class Paddle(arcade.Sprite) :
    """
    Class to keep track of Paddles
    """
    def __init__(self, center_y=25) :
        super().__init__('images/paddle.png', scale=PADDLE_SCALE, center_y=center_y)
        self.change_x = 0
        self.change_y = 0

    def update(self) :
        # Move the paddle
        self.center_x += self.change_x
        self.center_y += self.change_y

        # keep them between lateral walls (screen limit)
        if self.left < 0 :
            self.change_x *= -1
            self.left = 0

        if self.right > SCREEN_WIDTH :
            self.change_x *= -1
            self.right = SCREEN_WIDTH


class PongGame(arcade.Window):
    """
    Main application class.

    NOTE: Go ahead and delete the methods you don't need.
    If you do need a method, delete the 'pass' and replace it
    with your own code. Don't leave 'pass' in this program.
    """

    def __init__(self, options):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        arcade.set_background_color(arcade.color.AMAZON)

        # If you have sprite lists, you should create them here,
        # and set them to None

        # sprite lists
        self.paddle_list = None
        self.ball_list = None

        # game variables
        self.score_top = 0 
        self.score_bottom = 0
        self.ball_lost = False
        self.game_over = False

        # options
        self.options = options

        # the move detector
        self.detector = None
        
    def setup(self):
        """
        Setup a new party
        """
        # Create your sprites and sprite lists here

        self.game_over = False
        self.score_top = 0
        self.score_bottom = 0

        # setup move detector
        self.detector = Detector(
            self.options.source,
            self.options.algo,
            self.options.bbox,
        )
        
        # setup the paddles !
        self.paddle_list = arcade.SpriteList()

        for n in range(1) :
            paddle = Paddle(center_y=25)
            paddle.center_x = self.width // 3 * n + self.width // 6
            paddle.change_x = random.randrange(-5,5)
            self.paddle_list.append(paddle)

        for n in range(3) :
            paddle = Paddle(center_y=self.height - 25)
            paddle.center_x = self.width // 3 * n + self.height // 6
            paddle.change_x = random.randrange(-5,5)
            self.paddle_list.append(paddle)

        # the player paddle controlled by move detector
        self.my_paddle = self.paddle_list[0]
        self.my_paddle.change_x = 0

        # setup a new ball !
        self.new_ball()


    def new_ball(self) :
        """
        Create a fresh new ball
        """

        self.ball_lost = False
        self.ball_list = arcade.SpriteList()
        for n in range(1) :
            ball = make_ball()
            self.ball_list.append(ball)

    def on_draw(self):
        """
        Render the screen.
        """

        # This command should happen before we start drawing. It will clear
        # the screen to the background color, and erase what we drew last frame.
        arcade.start_render()

        # Call draw() on all your sprite lists below
        self.paddle_list.draw()
        self.ball_list.draw()

        output = f"""{self.score_bottom:2d}"""
        arcade.draw_text(output, 10, self.height//6, arcade.color.BLUE, 28)
        output = f"""{self.score_top:2d}"""
        arcade.draw_text(output, 10, self.height//1.33, arcade.color.WHITE, 28)

    def update(self, delta_time):
        """
        All the logic to move, and the game logic goes here.
        Normally, you'll call update() on the sprite lists that
        need it.
        """

        # game is over, start a new one
        if self.game_over :
            self.setup()
            return

        # the ball is lost, get a new one
        if self.ball_lost :
            self.new_ball()
            return

        # use move detector to control player paddle moves
        self.detector.update()
        self.my_paddle.center_x = self.detector.center_x

        # manage paddles
        self.paddle_list.update()

        # manage the ball (move, left, rigth collision)
        self.ball_list.update()

        # manage ball collision 
        for ball in self.ball_list :

            # the ball is lost, update score
            if ball.bottom < 0 :
                self.ball_lost = True
                self.score_top += 1
            if ball.top > self.height :
                self.ball_lost = True
                self.score_bottom += 1

            # the ball hits some paddles
            paddles_hit = arcade.check_for_collision_with_list(ball, self.paddle_list)
            for paddle in paddles_hit :
                # logic to be reviewed here
                if ball.change_y > 0 :
                    ball.top = paddle.bottom - MAXSPEED
                elif ball.change_y < 0 :
                    ball.bottom = paddle.top + MAXSPEED
            if len(paddles_hit) > 0 :
                ball.change_y *= -BOUNCE_FACTOR
                ball.change_x *= BOUNCE_FACTOR

            # paddles hits some other ones
            # to do

        # winner and game over
        if self.score_bottom >= MATCH_WIN or self.score_top >= MATCH_WIN :
            self.game_over = True
        

    def on_key_press(self, key, key_modifiers):
        """
        Called whenever a key on the keyboard is pressed.

        For a full list of keys, see:
        http://arcade.academy/arcade.key.html
        """
        pass

    def on_key_release(self, key, key_modifiers):
        """
        Called whenever the user lets off a previously pressed key.
        """
        pass

    def on_mouse_motion(self, x, y, delta_x, delta_y):
        """
        Called whenever the mouse moves.
        """
        pass

    def on_mouse_press(self, x, y, button, key_modifiers):
        """
        Called when the user presses a mouse button.
        """
        pass

    def on_mouse_release(self, x, y, button, key_modifiers):
        """
        Called when a user releases a mouse button.
        """
        pass

def parse_args() :
    """
    Choose source and algo for tracking
    """
    # argument type : bbox
    def bbox(s) :
        try :
            x, y, w, h = map(int, s.split(','))
            return x, y, w, h
        except :
            raise argparse.ArgumentTypeError("bbox must be x,y,w,h integers")

    # argument type : screen
    def screen(s) :
        try :
            w, h = map(int, s.split('x'))
            return w, h
        except :
            raise argparse.ArgumentTypeError("screen must WxH integers")
    
    # define parser for arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'source',
        nargs='?',
        default='0',
        help='device, url or file as video source'
    )
    parser.add_argument(
        '--algo',
        default='MOSSE',
        help='Algo for tracking : MOSSE(default), MEDIANFLOW, CSRT, KCF, MIL'
    )
    parser.add_argument(
        '--bbox',
        type=bbox,
        default='275,58,133,404'
    )
    parser.add_argument(
        '--screen',
        type=screen,
        default='640x480'
    )
    args = parser.parse_args()

    # adjust arguments
    # convert source to int if contains only decimal digits
    if args.source.isdecimal() :
        args.source = int(args.source)
    print(args)
    return args

def main():
    """ Main method """
    global SCREEN_WIDTH, SCREEN_HEIGHT
    
    args = parse_args()
    SCREEN_WIDTH, SCREEN_HEIGHT = args.screen
    game = PongGame(options=args)
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()
