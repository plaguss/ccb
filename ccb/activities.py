"""
Classes offered by the gym.
When defined, the methods let you sign up for one in case there
is a vacancy.
"""

import typing
import selenium.webdriver.remote.webelement as we
import warnings
import logging


# Set default message from config to be info, and prettier format:
logging.basicConfig(format='%(asctime)s --> %(levelname)s: %(message)s', level=logging.INFO)


class Reservation:
    """
    Processes the 'Reservas' elements.
    Number of places in a given Activity.

    Parameters
    ----------
    reserva : str
        Element representing the number of places in a given activity.
        Its structure is (<PLACES_LEFT>/<TOTAL_PLACES>)

    Methods
    -------
    is_free

    Attributes
    ----------
    places
    total

    Examples
    --------
    >>> reserva = '(13/15)'
    >>> reserv = Reservation(reserva)
    >>> reserv.is_free()
    True
    """
    def __init__(self, reserva: str) -> None:
        self._reserva = reserva
        places, total = reserva[1:-1].split('/')
        self.places = places
        self.total = total

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, str(self))

    def __str__(self):
        return self._reserva

    @property
    def places(self) -> int:
        """Contains the number of places on a given activity. """
        return self._places

    @places.setter
    def places(self, plc: str):
        self._places = int(plc)

    @property
    def total(self) -> int:
        """Contains the total number of places on a given activity. """
        return self._total

    @total.setter
    def total(self, tot: str):
        self._total = int(tot)

    def is_free(self) -> bool:
        """Returns True if places < total, false otherwise.

        Returns
        -------
        free : bool
            Checks whether is place in a given activity.
        """
        return self.places < self.total


class Hour:
    """Simple Hour format to represent a class.
    Allows different operations between them to check if
    a reservation deserves taking a place or not.

    Parameters
    ----------
    h : str
        String representing an hour of the format hh:mm, i.e. 20:30.

    Examples
    --------
    >>> h = '11:30'
    >>> hour = Hour(h)
    >>> h2 = '13:30'
    >>> hour2 = Hour(h2)
    >>> hour == hour2
    False
    >>> hour <= hour2
    True
    >>> hour >= hour2
    """
    def __init__(self, h: str) -> None:
        self._h = h
        hour, minutes = h.split(':')
        self.hour = hour
        self.minutes = minutes

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, str(self))

    def __str__(self):
        return self._h

    @property
    def hour(self) -> int:
        return self._hour

    @hour.setter
    def hour(self, hr: str) -> None:
        self._hour = int(hr)

    @property
    def minutes(self) -> int:
        return self._minutes

    @minutes.setter
    def minutes(self, mins: str) -> None:
        self._minutes = int(mins)

    def __eq__(self, other: 'Hour') -> bool:
        if not isinstance(other, Hour):
            raise ValueError('{} must be an Hour instance.'.format(other))

        if self.hour == other.hour:
            return self.minutes == other.minutes
        else:
            return False

    def __le__(self, other: 'Hour') -> bool:
        if not isinstance(other, Hour):
            raise ValueError('{} must be an Hour instance.'.format(other))

        if self.hour <= other.hour:
            return True
        else:
            if self.hour == other.hour:
                return self.minutes <= other.minutes

    def __lt__(self, other: 'Hour') -> bool:
        if not isinstance(other, Hour):
            raise ValueError('{} must be an Hour instance.'.format(other))

        if self.hour < other.hour:
            return True
        else:
            if self.hour == other.hour:
                return self.minutes < other.minutes

    def __ge__(self, other: 'Hour') -> bool:
        return not self <= other

    def __gt__(self, other: 'Hour') -> bool:
        return not self < other


class Schedule:
    """Contains the class to deal with the hours a given class takes place.

    Parameters
    ----------
    sch : str
        Represents the hour of the class as a string. i.e. '11:00 - 13:00'

    Examples
    --------
    >>> sch = '11:00 - 13:00'
    >>> schedule = Schedule(sch)
    >>> schedule.start
    Hour(11:00)

    >>> hour = Hour('11:30')
    >>> hour2 = Hour('16:00')
    >>> hour in schedule
    True
    >>> hour2 in schedule
    False
    """
    def __init__(self, sch: str) -> None:
        self._sch = sch
        start, end = sch.split(' - ')
        self.start = start
        self.end = end

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, str(self))

    def __str__(self):
        return self._sch

    def __contains__(self, item: Hour) -> bool:
        return self.start < item < self.end

    @property
    def start(self) -> Hour:
        """Start hour. """
        return self._start

    @start.setter
    def start(self, strt: str) -> None:
        self._start = Hour(strt)

    @property
    def end(self) -> Hour:
        """End hour. """
        return self._end

    @end.setter
    def end(self, end_: str) -> None:
        self._end = Hour(end_)


class ButtonIcon:
    """
    Reference for plus/minus icons of a button.
    A PLUS button appears when there is a vacancy, a
    MINUS button appears when you are already signed
    for a class, checking it would leave the reservation.
    """
    PLUS = 'PLUS'
    MINUS = 'MINUS'


class Button:
    """
    Element of selenium representing the button to be pressed to book a class.

    TODO:
        determinar si un botón es glyphicon-minus para NO clickar.
    """
    def __init__(
            self, element: typing.Union[we.WebElement, str],
            driver: "WebDriver",
            icon: typing.Union[str, None] = None,
    ) -> None:
        if isinstance(element, str):
            self._enabled = False
            self._icon = icon
        else:  # Properly defined button.
            self.element = element
            self._enabled = True
            self.icon = icon
        self.driver = driver

    def __repr__(self):
        if self.icon is not None:
            icon = self.icon
        else:
            icon = ''
        return "{}({} - {})".format(self.__class__.__name__, self.is_enabled(), icon)

    def is_enabled(self) -> bool:
        """Check whether a button can be checked or not. """
        return self._enabled

    @property
    def element(self) -> typing.Union[we.WebElement, None]:
        """WebElement containing the element to be clicked. Or None if could not be found. """
        return self._element

    @element.setter
    def element(self, el: we.WebElement) -> None:
        self._element = el

    @property
    def icon(self) -> typing.Union[str, None]:
        """WebElement containing the element to be clicked. Or None if could not be found. """
        return self._icon

    @icon.setter
    def icon(self, ico: str) -> None:
        if 'plus' in ico:
            ico_ = ButtonIcon.PLUS
        else:
            ico_ = ButtonIcon.MINUS
        self._icon = ico_

    def click(self) -> None:
        """Clicks the button, then registering to a class. """
        if self.is_enabled():
            try:
                self.element.click()
                logging.info("Class booked!")
            except:
                logging.info("The button could not be clicked, trying to execute the element.")
                self.driver.execute_script("arguments[0].click();", self.element)
            finally:
                logging.info("Could not book the class")

        else:
            warnings.warn('The Button cannot be clicked.')


class Activities:
    CROSSFIT = 'Crossfit'
    OPEN_BOX = 'Open Box'
    WEIGHTLIFTING = 'Halterofília'
    CALISTHENICS = 'Calisteni'


class Activity:
    """
    TODO: Definir completamente activity.
    """
    def __init__(
            self,
            schedule: typing.Union[Schedule, None] = None,
            reservation: typing.Union[Reservation, None] = None,
            button: typing.Union[Button, None] = None
    ) -> None:
        self.schedule = schedule
        self.reservation = reservation
        self.button = button

    def __repr__(self):
        return '{}({}, {})'.format(self.__class__.__name__, self.schedule, self.reservation)

    def __str__(self):
        return self.__repr__()

    def book(self) -> bool:
        """Returns True if there was space and the class could be registered,
        False otherwise.
        """
        # Check for space
        if self.reservation.is_free():
            self.button.click()
            logging.info('Class registered: {}'.format(self))
            check = True
        else:
            logging.info('No space at the moment')
            check = False

        return check

    @property
    def name(self) -> str:
        raise NotImplementedError


class OpenBox(Activity):
    """Activity subclass for an OpenBox activity. """
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    @property
    def name(self) -> str:
        return Activities.OPEN_BOX


class Crossfit(Activity):
    """Activity subclass for a Crossfit class. """
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    @property
    def name(self) -> str:
        return Activities.CROSSFIT


class Calisthenics(Activity):
    """Activity subclass for a Calisthenics class. """
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    @property
    def name(self) -> str:
        return Activities.CALISTHENICS


class Weightlifting(Activity):
    """Activity subclass for a Weightlifting class. """
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    @property
    def name(self) -> str:
        return Activities.WEIGHTLIFTING
