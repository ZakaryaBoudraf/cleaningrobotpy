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

    @patch.object(IBS, "get_charge_left")
    @patch.object(GPIO, "output")
    def test_manage_cleaning_system_led_turns_on_and_cleaning_system_off_if_battery_low(self, mock_led: Mock, mock_ibs: Mock):
        system = CleaningRobot()
        mock_ibs.return_value = 10

        system.manage_cleaning_system()

        calls = [call(system.CLEANING_SYSTEM_PIN, False), call(system.RECHARGE_LED_PIN, True)]
        mock_led.assert_has_calls(calls, any_order=False)
        self.assertFalse(system.cleaning_system_on)
        self.assertTrue(system.recharge_led_on)

    @patch.object(IBS, "get_charge_left")
    @patch.object(GPIO, "output")
    def test_manage_cleaning_system_recharge_led_turns_off_and_cleaning_system_on_if_battery_high(self, mock_led: Mock, mock_ibs: Mock):
        system = CleaningRobot()
        mock_ibs.return_value = 11

        system.manage_cleaning_system()

        calls = [call(system.CLEANING_SYSTEM_PIN, True), call(system.RECHARGE_LED_PIN, False)]
        mock_led.assert_has_calls(calls, any_order=False)
        self.assertTrue(system.cleaning_system_on)
        self.assertFalse(system.recharge_led_on)

    @patch.object(CleaningRobot, "activate_wheel_motor")
    def test_execute_command_move_forward(self, mock_activate_wheel_motor: Mock):
        system = CleaningRobot()
        system.pos_x = 1
        system.pos_y = 1
        system.heading = "N"

        status = system.execute_command("f")
        mock_activate_wheel_motor.assert_called_once()
        self.assertEqual(status,"(1,2,N)")
