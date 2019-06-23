"""
Starting Template

Once you have learned how to use classes, you can begin your program with this
template.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.starting_template
"""

import time
import argparse
import logging
import random
import arcade

from pong.detector import Detector

# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
SCREEN_TITLE = "Pong"

BOUNCE_FACTOR = 1.05
MAXSPEED = 30
SERVICE_SPEED = 3, 7

MATCH_WIN = 11
GAME_OVER_WAIT = 2
DETECTOR_WAIT = 1.5

PADDLE_SCALE = 0.2
BALL_SCALE = 0.6

# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------

class Ball(arcade.Sprite) :
    """
    Class to keep track of a ball's location and motion vector
    """
    def __init__(self) :
        super().__init__('images/ball.png', scale=BALL_SCALE)

    def update(self) :
        """
        Limit ball speed to MAXSPEED
        Bounce on lateral walls
        """
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
    ball.change_x = random.randrange(*SERVICE_SPEED)
    ball.change_y = random.randrange(*SERVICE_SPEED)

    return ball

# ------------------------------------------------------------------------------

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

# ------------------------------------------------------------------------------

class PongGame(arcade.Window):
    """
    Main application class.

    NOTE: Go ahead and delete the methods you don't need.
    If you do need a method, delete the 'pass' and replace it
    with your own code. Don't leave 'pass' in this program.
    """

    def __init__(self, options):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        self.set_viewport(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT)

        arcade.set_background_color(arcade.color.CATALINA_BLUE)

        # keep options
        self.options = options

        # fullscreen start ?
        self.start_fullscreen = options.fullscreen

        # declare sprite lists
        self.paddle_list = None
        self.ball_list = None

        # game variables
        self.human_paddles = []
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
        logging.debug('setup new game')

        # game state variables
        self.ball_lost = False
        self.score_top = 0
        self.score_bottom = 0

        # human controlled paddles list
        self.human_paddles = []

        # setup move detector
        self.detector = Detector(
            self.options.source,
            self.options.algo,
            nZones=self.options.nZones,
            yZone=self.options.yZone,
            wZone=self.options.wZone,
            hZone=self.options.hZone
        )
        self.detector.width = SCREEN_WIDTH
        self.detector.height = SCREEN_HEIGHT
        self.detector.init_zones()
        
        # setup the paddles !
        self.paddle_list = arcade.SpriteList()

        # human paddles
        for n in range(self.options.nZones) :
            paddle = Paddle(center_y=25)
            paddle.center_x = SCREEN_WIDTH // 3 * n + SCREEN_WIDTH // 6
            self.human_paddles.append(paddle)
            self.paddle_list.append(paddle)

        # automatic paddles
        for n in range(3) :
            paddle = Paddle(center_y=SCREEN_HEIGHT - 25)
            paddle.center_x = SCREEN_HEIGHT // 3 * n + SCREEN_HEIGHT // 6
            paddle.change_x = random.randrange(-5,5)
            self.paddle_list.append(paddle)

        # setup a new ball !
        self.new_ball()

        # start detector
        self.detector.start()
        time.sleep(DETECTOR_WAIT)
        # synchro (to do : add condition instead timing)

        self.game_over = False

        # a fix to pass window front of others
        self.set_visible(True)
        self.set_viewport(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT)

        logging.debug('setup done')

    def gameover(self) :
        """
        Cleanup the game before starting it again
        """
        logging.debug('gameover')

        # clean paddles
        for paddle in self.paddle_list :
            paddle.kill()
        self.paddle_list = None

        # clean balls
        for ball in self.ball_list :
            ball.kill()
        self.ball_list = None

        # time for users to aknowledge Game Over
        # to do : a Real and independant Game Over Mode
        time.sleep(GAME_OVER_WAIT)

        # stop detector
        self.detector.terminate()
        self.detector.join()
        self.detector = None

        logging.debug('gameover done')

    def new_ball(self) :
        """
        Create a fresh new ball
        """
        logging.debug('new ball')
        self.ball_list = arcade.SpriteList()
        for n in range(1) :
            ball = make_ball()
            self.ball_list.append(ball)
        self.ball_lost = False

    def switch_fullscreen(self) :
        """
        Manage fullscreen switch and adapt the viewport
        """
        self.set_fullscreen(not self.fullscreen)
        self.set_viewport(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT)

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

        # some feedback on the screen : the scores
        output = f"""{self.score_bottom:2d}"""
        arcade.draw_text(output, 10, SCREEN_HEIGHT//6, arcade.color.WHITE, 28)
        output = f"""{self.score_top:2d}"""
        arcade.draw_text(output, 10, SCREEN_HEIGHT//1.33, arcade.color.WHITE, 28)

        # game over display
        if self.game_over :
            output = """GAME OVER"""
            arcade.draw_text(output, SCREEN_WIDTH//3.25, SCREEN_HEIGHT//2, arcade.color.RED, 40)

    def update(self, delta_time):
        """
        All the logic to move, and the game logic goes here.
        Normally, you'll call update() on the sprite lists that
        need it.
        """

        # first time fix : do we have to start the game fullscreen ?
        if self.start_fullscreen :
            self.switch_fullscreen()
            self.start_fullscreen = False

        # game is over, start a new one
        if self.game_over :
            logging.debug('game over during update')
            self.gameover()
            self.setup()
            return

        # the ball is lost, get a new one
        if self.ball_lost :
            self.new_ball()

        # query the move detector to control player paddle moves
        for n, paddle in enumerate(self.human_paddles) :
            paddle.center_x = self.detector.center_x(n)

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
        # switch fullscreen / windowed
        if key == arcade.key.F :
            self.switch_fullscreen()

        # reset game
        elif key == arcade.key.R :
            self.game_over = True

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

# ------------------------------------------------------------------------------

def parse_args() :
    """
    Choose source and algo for tracking
    """
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
        '-n', '--nZones',
        type=int,
        choices=range(1,4),
        default=1,
        help='Number of zones (ie: paddles)'
    )
    parser.add_argument(
        '-Y', '--yZone',
        type=int,
        default=58,
        help='top coord for each zone'
    )
    parser.add_argument(
        '-W', '--wZone',
        type=int,
        default=130,
        help='width of each tracking zone'
    )
    parser.add_argument(
        '-H', '--hZone',
        type=int,
        default=400,
        help='height of each tracking zone'
    )
    parser.add_argument(
        '--screen',
        type=screen,
        default='640x480'
    )
    parser.add_argument(
        '-f', '--fullscreen',
        action='store_true',
        help='Start game fullscreen'
    )
    args = parser.parse_args()

    # adjust arguments
    # convert source to int if contains only decimal digits
    if args.source.isdecimal() :
        args.source = int(args.source)
    logging.debug(args)
    return args

# ------------------------------------------------------------------------------

def main():
    """ Main method """
    global SCREEN_WIDTH, SCREEN_HEIGHT

    logging.basicConfig(
        level=logging.DEBUG,
        format='(%(threadName)-10s) %(message)s'
    )
    logging.debug('start main')
    
    args = parse_args()
    SCREEN_WIDTH, SCREEN_HEIGHT = args.screen
    game = PongGame(options=args)
    game.setup()
    arcade.run()


# ------------------------------------------------------------------------------

if __name__ == "__main__":
    main()
