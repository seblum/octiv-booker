import logging
import os
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Optional, Tuple, NamedTuple
from dataclasses import dataclass
from .src.slotbooker.utils.xpaths import XPath
from .src.slotbooker.utils.alerts import AlertErrorHandler


@dataclass
class BookingEntry:
    """Represents a single booking entry."""

    time: str
    class_name: str
    waiting_list: bool = False

    @classmethod
    def from_dict(cls, data: dict) -> "BookingEntry":
        """Create BookingEntry from dictionary."""
        return cls(
            time=data.get("time", ""),
            class_name=data.get("class", ""),
            waiting_list=data.get("wl", False),
        )


@dataclass
class BookingSlot:
    """Represents an available booking slot."""

    xpath: str
    class_name: str
    time: str


class BookingResult(NamedTuple):
    """Result of a booking operation."""

    success: bool
    class_name: str
    time_slot: str
    message: str = ""


class ClassBookingError(Exception):
    """Custom exception for booking-related errors."""

    pass


class ClassBooker:
    """Handles class booking operations with improved error handling and structure."""

    def __init__(self, selenium_manager, day: str):
        self.selenium_manager = selenium_manager
        self.day = day
        self.booking_information = {"bookings": []}

    def book_classes(self, class_dict: Dict, enter_class: bool = True) -> BookingResult:
        """
        Book or cancel classes based on provided booking information.

        Args:
            class_dict: Dictionary containing booking information for different days
            enter_class: True for booking, False for cancelling

        Returns:
            BookingResult with success status and details
        """
        action = "Booking" if enter_class else "Cancelling"
        logging.info(f"{action} classes for {self.day}...")

        try:
            # Get booking entries for the specified day
            day_entries = class_dict.get(self.day, [])
            if not day_entries:
                return BookingResult(False, "", "", f"No entries found for {self.day}")

            booking_entries = [BookingEntry.from_dict(entry) for entry in day_entries]

            # Check for 'None' class entries
            if any(entry.class_name == "None" for entry in booking_entries):
                logging.info("No class set for this day.")
                return BookingResult(False, "", "", "No class set for this day")

            # Get available booking slots
            available_slots = self._get_available_booking_slots(
                booking_entries, enter_class
            )
            if not available_slots:
                logging.info("No classes found overall for this day.")
                return BookingResult(False, "", "", "No available classes found")

            # Process each booking entry
            for entry in booking_entries:
                result = self._process_booking_entry(
                    entry, available_slots, enter_class
                )
                if result.success:
                    return result

            return BookingResult(False, "", "", "No successful bookings made")

        except Exception as e:
            logging.error(f"Error during {action.lower()}: {str(e)}")
            return BookingResult(False, "", "", f"Booking failed: {str(e)}")

    def _get_available_booking_slots(
        self, booking_entries: List[BookingEntry], enter_class: bool
    ) -> Dict[str, Dict[str, BookingSlot]]:
        """
        Get all available booking slots for the specified classes.

        Returns:
            Dictionary mapping class_name -> time_slot -> BookingSlot
        """
        try:
            # Wait for booking section to load
            self.selenium_manager.wait_for_element(xpath=XPath.booking_section_head())
            slot_elements = self.selenium_manager.find_elements(
                xpath=XPath.booking_section_head()
            )

            if not slot_elements:
                logging.warning("No booking slot elements found")
                return {}

            # Get unique class names to look for
            target_classes = {entry.class_name for entry in booking_entries}
            logging.info(f"Looking for classes: {target_classes}")

            return self._parse_booking_slots(slot_elements, target_classes, enter_class)

        except Exception as e:
            logging.error(f"Error getting available slots: {str(e)}")
            return {}

    def _parse_booking_slots(
        self, slot_elements: List, target_classes: set, enter_class: bool
    ) -> Dict[str, Dict[str, BookingSlot]]:
        """Parse slot elements to extract available booking slots."""
        slots_dict = defaultdict(dict)

        for slot_index, element in enumerate(slot_elements, start=1):
            try:
                class_name = self._get_slot_class_name(slot_index, enter_class)
                if not class_name or class_name not in target_classes:
                    continue

                time_slot = self._get_slot_time(slot_index, enter_class)
                if not time_slot:
                    continue

                button_xpath = self._get_slot_button_xpath(slot_index, enter_class)

                slot = BookingSlot(
                    xpath=button_xpath, class_name=class_name, time=time_slot
                )

                slots_dict[class_name][time_slot] = slot
                logging.info(f"Found slot - Time: {time_slot}, Class: {class_name}")

            except Exception as e:
                logging.debug(f"Error parsing slot {slot_index}: {str(e)}")
                continue

        return slots_dict

    def _get_slot_class_name(self, slot_index: int, enter_class: bool) -> Optional[str]:
        """Get class name for a specific slot."""
        try:
            return self.selenium_manager.get_element_text(
                xpath=XPath.bounding_box_label(
                    slot_index=slot_index, enter_class=enter_class
                )
            )
        except Exception:
            return None

    def _get_slot_time(self, slot_index: int, enter_class: bool) -> Optional[str]:
        """Get time slot for a specific slot."""
        try:
            return self.selenium_manager.get_element_text(
                xpath=XPath.bounding_box_time(
                    slot_index=slot_index, enter_class=enter_class
                )
            )
        except Exception:
            return None

    def _get_slot_button_xpath(self, slot_index: int, enter_class: bool) -> str:
        """Get button xpath for a specific slot."""
        return (
            XPath.enter_slot(slot=slot_index)
            if enter_class
            else XPath.cancel_slot(slot=slot_index)
        )

    def _process_booking_entry(
        self,
        entry: BookingEntry,
        available_slots: Dict[str, Dict[str, BookingSlot]],
        enter_class: bool,
    ) -> BookingResult:
        """Process a single booking entry."""
        logging.info(f"Processing {entry.class_name} at {entry.time}...")

        # Add to booking information
        self.booking_information["bookings"].append(
            {"time": entry.time, "class": entry.class_name}
        )

        # Check if the requested slot is available
        if entry.class_name not in available_slots:
            message = f"Class '{entry.class_name}' not available on {self.day}"
            logging.info(message)
            return BookingResult(False, entry.class_name, entry.time, message)

        if entry.time not in available_slots[entry.class_name]:
            message = f"Class '{entry.class_name}' not available at {entry.time} on {self.day}"
            logging.info(message)
            return BookingResult(False, entry.class_name, entry.time, message)

        # Attempt to book the slot
        slot = available_slots[entry.class_name][entry.time]
        return self._execute_booking(slot, entry, enter_class)

    def _execute_booking(
        self, slot: BookingSlot, entry: BookingEntry, enter_class: bool
    ) -> BookingResult:
        """Execute the actual booking process."""
        action = "Booking" if enter_class else "Cancelling"
        logging.info(f"{action} {entry.class_name} at {entry.time}")

        try:
            # Wait for execution time if specified
            self._wait_for_execution_time()

            # Execute the booking click
            execution_start = datetime.now()
            element = self.selenium_manager.find_element(xpath=slot.xpath)
            self.selenium_manager.execute_script(
                "arguments[0].click();", element=element
            )
            execution_end = datetime.now()

            execution_time = (execution_end - execution_start).total_seconds()
            logging.info(
                f"Executed at {execution_end.time()}, took {execution_time:.3f}s"
            )

            # Handle any alerts or errors
            if self._handle_booking_response(entry.waiting_list):
                return BookingResult(
                    False, entry.class_name, entry.time, "Booking failed due to error"
                )

            logging.info(f"Successfully {action.lower()} {entry.class_name}")
            return BookingResult(
                True, entry.class_name, entry.time, f"{action} successful"
            )

        except Exception as e:
            error_msg = f"Error during {action.lower()}: {str(e)}"
            logging.error(error_msg)
            return BookingResult(False, entry.class_name, entry.time, error_msg)

    def _wait_for_execution_time(self) -> None:
        """Wait until the specified execution time."""
        execution_time = os.environ.get("EXECUTION_BOOKING_TIME", "00:00:00.000000")
        if execution_time == "00:00:00.000000":
            return  # No waiting required

        logging.info(f"Waiting for execution time: {execution_time}")

        while True:
            current_time = datetime.now().time().strftime("%H:%M:%S.%f")
            if current_time >= execution_time:
                logging.info(f"Execution time reached: {current_time}")
                break

    def _handle_booking_response(self, prioritize_waiting_list: bool) -> bool:
        """
        Handle the response after attempting to book a class.

        Returns:
            True if booking should be stopped due to error, False otherwise
        """
        try:
            return AlertErrorHandler.check_booking_alert(
                selenium_manager=self.selenium_manager,
                waiting_list=prioritize_waiting_list,
            )
        except Exception as e:
            logging.error(f"Error handling booking response: {str(e)}")
            return True  # Stop on error

    # Helper function to maintain compatibility with existing code
    def stop_booking_process(self) -> bool:
        """Helper function for stopping booking process."""
        self.selenium_manager.close_driver()
        return True


# Example usage and integration
class ImprovedBookingManager:
    """Main manager class that uses the improved ClassBooker."""

    def __init__(self, selenium_manager):
        self.selenium_manager = selenium_manager

    def book_class(
        self, class_dict: dict, enter_class: bool = True
    ) -> Tuple[bool, str, str]:
        """
        Compatibility method that matches the original interface.

        Returns:
            Tuple of (success, class_name, time_slot)
        """
        # Assuming we have a way to determine the current day
        current_day = self._get_current_day()  # This would need to be implemented

        booker = ClassBooker(self.selenium_manager, current_day)
        result = booker.book_classes(class_dict, enter_class)

        return result.success, result.class_name, result.time_slot

    def _get_current_day(self) -> str:
        """Get the current day - this would need to be implemented based on your logic."""
        # This should return the day string that matches your class_dict keys
        return "monday"  # placeholder
