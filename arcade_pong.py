"""
Starting Template

Once you have learned how to use classes, you can begin your program with this
template.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.starting_template
"""
import random
import arcade

SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
SCREEN_TITLE = "Pong"

MAXSPEED = 20

PADDLE_SCALE = 0.35
BALL_SCALE = 0.75


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

        if self.change_x > MAXSPEED :
            self.change_x = MAXSPEED

        if self.change_x < -MAXSPEED :
            self.change_x = -MAXSPEED

        if self.change_y > MAXSPEED :
            self.change_y = MAXSPEED

        if self.change_y < -MAXSPEED :
            self.change_y = -MAXSPEED

        if self.change_x < -20 :
            self.change_x = -20

        if self.left < 0 :
            self.left = 0
            self.change_x *= -1

        if self.bottom < 0 :
            self.bottom = 0
            self.change_y *= -1
            
        if self.right > SCREEN_WIDTH :
            self.right = SCREEN_WIDTH
            self.change_x *= -1

        if self.top > SCREEN_HEIGHT :
            self.top = SCREEN_HEIGHT
            self.change_y *= -1


def make_ball() :
    """
    Function to make a new, random ball.
    """
    ball = Ball()

    # starting position on screen
    ball.center_x = random.randrange(int(ball.width), SCREEN_WIDTH - int(ball.width))
    ball.center_y = random.randrange(int(ball.height), SCREEN_HEIGHT - int(ball.height))

    # speed and direction
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
        self.paddle_list = None
        self.ball_list = None

    def setup(self):
        # Create your sprites and sprite lists here

        # paddles !
        self.paddle_list = arcade.SpriteList()

        for n in range(3) :
            paddle = Paddle(center_y=25)
            paddle.center_x = SCREEN_WIDTH // 3 * n + SCREEN_WIDTH // 6
            paddle.change_x = random.randrange(-5,5)
            self.paddle_list.append(paddle)

        for n in range(3) :
            paddle = Paddle(center_y=SCREEN_HEIGHT - 25)
            paddle.center_x = SCREEN_WIDTH // 3 * n + SCREEN_WIDTH // 6
            paddle.change_x = random.randrange(-5,5)
            self.paddle_list.append(paddle)

        # new ball !
        self.ball_list = arcade.SpriteList()
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

        output = f"{self.ball_list[0].change_x:.02f} {self.ball_list[0].change_y:.02f}"
        arcade.draw_text(output, 10, 20, arcade.color.CHARTREUSE, 14)

    def update(self, delta_time):
        """
        All the logic to move, and the game logic goes here.
        Normally, you'll call update() on the sprite lists that
        need it.
        """
        self.paddle_list.update()
        
        for ball in self.ball_list :
            paddles_hit = arcade.check_for_collision_with_list(ball, self.paddle_list)
            for paddle in paddles_hit :
                # a revoir
                if ball.change_y > 0 :
                    ball.top = paddle.bottom - MAXSPEED
                elif ball.change_y < 0 :
                    ball.bottom = paddle.top + MAXSPEED
            if len(paddles_hit) > 0 :
                ball.change_y *= -1.01
                ball.change_x *= 1.01

        self.ball_list.update()

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
