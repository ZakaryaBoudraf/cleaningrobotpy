import time
from time import sleep
from unittest import TestCase
from unittest.mock import Mock, patch, call

from mock import GPIO
from mock.ibs import IBS
from src.cleaning_robot import CleaningRobot


class TestCleaningRobot(TestCase):

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
        mock_led.assert_has_calls(calls)
        self.assertFalse(system.cleaning_system_on)
        self.assertTrue(system.recharge_led_on)

    @patch.object(IBS, "get_charge_left")
    @patch.object(GPIO, "output")
    def test_manage_cleaning_system_recharge_led_turns_off_and_cleaning_system_on_if_battery_high(self, mock_led: Mock, mock_ibs: Mock):
        system = CleaningRobot()
        mock_ibs.return_value = 11

        system.manage_cleaning_system()

        calls = [call(system.CLEANING_SYSTEM_PIN, True), call(system.RECHARGE_LED_PIN, False)]
        mock_led.assert_has_calls(calls)
        self.assertTrue(system.cleaning_system_on)
        self.assertFalse(system.recharge_led_on)

    @patch.object(IBS, "get_charge_left")
    @patch.object(CleaningRobot, "activate_wheel_motor")
    def test_execute_command_move_forward(self, mock_activate_wheel_motor: Mock, mock_ibs: Mock):
        mock_ibs.return_value = 11
        system = CleaningRobot()
        system.pos_x = 1
        system.pos_y = 1
        system.heading = "E"

        status = system.execute_command("f")
        mock_activate_wheel_motor.assert_called_once()
        self.assertEqual(status,"(2,1,E)")

    @patch.object(IBS, "get_charge_left")
    @patch.object(CleaningRobot, "activate_rotation_motor")
    def test_execute_command_turn_right(self, mock_activate_rotation_motor: Mock, mock_ibs: Mock):
        mock_ibs.return_value = 11
        system = CleaningRobot()
        system.pos_x = 1
        system.pos_y = 2
        system.heading = "N"

        status = system.execute_command("r")
        mock_activate_rotation_motor.assert_called_once()
        self.assertEqual(status,"(1,2,E)")

    @patch.object(IBS, "get_charge_left")
    @patch.object(CleaningRobot, "activate_rotation_motor")
    def test_execute_command_turn_left(self, mock_activate_rotation_motor: Mock, mock_ibs: Mock):
        mock_ibs.return_value = 11
        system = CleaningRobot()
        system.pos_x = 1
        system.pos_y = 2
        system.heading = "E"

        status = system.execute_command("l")
        mock_activate_rotation_motor.assert_called_once()
        self.assertEqual(status,"(1,2,N)")

    @patch.object(GPIO, "input")
    def test_obstacle_found_is_true(self, mock_infrared_sensor: Mock):
        mock_infrared_sensor.return_value = True
        system = CleaningRobot()
        self.assertTrue(system.obstacle_found())

    @patch.object(GPIO, "input")
    def test_obstacle_found_is_false(self, mock_infrared_sensor: Mock):
        mock_infrared_sensor.return_value = False
        system = CleaningRobot()
        self.assertFalse(system.obstacle_found())

    @patch.object(IBS, "get_charge_left")
    @patch.object(GPIO, "input")
    def test_execute_command_forward_when_obstacle_found(self, mock_infrared_sensor: Mock, mock_ibs: Mock):
        mock_ibs.return_value = 11
        mock_infrared_sensor.return_value = True
        system = CleaningRobot()
        system.pos_x = 1
        system.pos_y = 1
        system.heading = "N"

        status = system.execute_command("f")
        self.assertEqual(status,"(1,1,N)(1,2)")

    @patch.object(IBS, "get_charge_left")
    @patch.object(GPIO, "input")
    def test_execute_command_forward_when_no_obstacle_found(self, mock_infrared_sensor: Mock, mock_ibs: Mock):
        mock_ibs.return_value = 11
        mock_infrared_sensor.return_value = False
        system = CleaningRobot()
        system.pos_x = 1
        system.pos_y = 1
        system.heading = "N"

        status = system.execute_command("f")
        self.assertEqual(status,"(1,2,N)")

    @patch.object(IBS, "get_charge_left")
    @patch.object(GPIO, "output")
    def test_execute_command_if_battery_is_low(self, mock_led: Mock, mock_ibs: Mock):
        mock_ibs.return_value = 10
        system = CleaningRobot()
        system.pos_x = 1
        system.pos_y = 1
        system.heading = "N"

        status = system.execute_command("f")

        calls = [call(system.CLEANING_SYSTEM_PIN, False), call(system.RECHARGE_LED_PIN, True)]
        mock_led.assert_has_calls(calls)
        self.assertEqual(status, "!(1,1,N)")

    @patch.object(GPIO, "output")
    @patch("time.sleep")
    def test_activate_uv_light(self, mock_sleep: Mock, mock_uv_light: Mock):
        system = CleaningRobot()

        system.activate_uv_light()

        mock_uv_light.assert_any_call(system.UV_LIGHT_PIN, True)

        mock_uv_light.assert_any_call(system.UV_LIGHT_PIN, False)

        self.assertTrue(mock_sleep.called)
        mock_sleep.assert_called_with(30)

    @patch.object(IBS, "get_charge_left")
    @patch.object(CleaningRobot, "activate_uv_light")
    def test_uv_light_activation_on_movement(self, mock_activate_uv_light: Mock, mock_ibs: Mock):
        mock_ibs.return_value = 11
        system = CleaningRobot()
        system.pos_x = 1
        system.pos_y = 1
        system.heading = "N"

        system.execute_command("f")

        mock_activate_uv_light.assert_called_once()

        self.assertEqual(system.pos_x, 1)
        self.assertEqual(system.pos_y, 2)
        self.assertEqual(system.heading, "N")