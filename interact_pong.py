"""
Starting Template

Once you have learned how to use classes, you can begin your program with this
template.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.starting_template
"""
import random
import arcade

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
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

class Detector :

    def __init__(self) :
        self.cam = cv.VideoCapture(0, cv.CAP_DSHOW)
        self.win = WindowManager('capture', self.onKeypress)
        self.win.createWindow()
        self.cap = CaptureManager(self.cam, self.win, True)
        self.proc = TrackingProcessor()
        self.frameno = 0
        self.rect = (275, 58, 133, 404)
        
    def onKeypress(self, keycode) :
        pass

    def update(self) :
        if self.win.isCreated :
            # enter frame and capture
            self.cap.enterFrame()
            frame = self.cap.frame
            self.frameno += 1

            # process to detection
            frame = self.proc.apply(frame, self)

            # exit frame and process events
            self.cap.exitFrame()
            self.win.processEvents()
        

class TrackingProcessor(FrameProcessor) :

    def params(self, **kwargs) :
        self.tracker = cv.TrackerMOSSE_create()
        
    def apply(self, frame, context) :
        if context.frameno == 1 :
            roi = context.rect
            ok = self.tracker.init(frame, roi)
            return frame

        success, rect = self.tracker.update(frame)
        if success :
            x, y, w, h = (int(v) for v in rect)
            context.rect = (x, y, w, h)
            cv.rectangle(frame, (x, y), (x+w, y+h), (0,255,0), 2)
        
        return frame


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
        if self.left < 0 or self.right > SCREEN_WIDTH :
            self.change_x *= -1


class MyGame(arcade.Window):
    """
    Main application class.

    NOTE: Go ahead and delete the methods you don't need.
    If you do need a method, delete the 'pass' and replace it
    with your own code. Don't leave 'pass' in this program.
    """

    def __init__(self, width, height, title):
        super().__init__(width, height, title)

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
        self.detector = Detector()
        
        # setup the paddles !
        self.paddle_list = arcade.SpriteList()

        for n in range(1) :
            paddle = Paddle(center_y=25)
            paddle.center_x = SCREEN_WIDTH // 3 * n + SCREEN_WIDTH // 6
            paddle.change_x = random.randrange(-5,5)
            self.paddle_list.append(paddle)

        for n in range(3) :
            paddle = Paddle(center_y=SCREEN_HEIGHT - 25)
            paddle.center_x = SCREEN_WIDTH // 3 * n + SCREEN_WIDTH // 6
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

        output = f"haut : {self.score_top:02d}\nbas : {self.score_bottom:02d}"
        arcade.draw_text(output, 10, 20, arcade.color.RED, 14)

    def update(self, delta_time):
        """
        All the logic to move, and the game logic goes here.
        Normally, you'll call update() on the sprite lists that
        need it.
        """

        # use move detector to control player paddle moves
        self.detector.update()
        self.my_paddle.center_x = SCREEN_WIDTH - self.detector.rect[0]

        # game is over, start a new one
        if self.game_over :
            self.setup()
            return

        # the ball is lost, get a new one
        if self.ball_lost :
            self.new_ball()
            return

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
            if ball.top > SCREEN_HEIGHT :
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


def main():
    """ Main method """
    game = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()
