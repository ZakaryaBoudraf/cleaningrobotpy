from unittest import TestCase
from unittest.mock import Mock, patch, call

from mock import GPIO
from mock.ibs import IBS
from src.cleaning_robot import CleaningRobot


class TestCleaningRobot(TestCase):

    @patch.object(GPIO, "input")
    def test_something(self, mock_object: Mock):
        # This is an example of test where I want to mock the GPIO.input() function
        pass

    def test_initialize_robot(self):
        system = CleaningRobot()
        system.initialize_robot()
        self.assertEqual(system.pos_x,0)
        self.assertEqual(system.pos_y,0)
        self.assertEqual(system.heading,"N")

    def test_robot_status(self):
        system = CleaningRobot()
        system.pos_x = 3
        system.pos_y = 2
        system.heading = "E"
        status = system.robot_status()
        self.assertEqual(status,"(3,2,E)")