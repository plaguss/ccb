"""
Module automating crossfit registration.

chromedriver:
https://chromedriver.storage.googleapis.com/index.html?path=86.0.4240.22/

Esperar a que un elemento esté presente:
https://stackoverflow.com/questions/26566799/wait-until-page-is-loaded-with-selenium-webdriver-for-python
"""


import logging
import time
import datetime as dt
import typing
import os
import sys
import warnings
import json

import selenium.webdriver as wd
from selenium.webdriver.common.by import By
import selenium.webdriver.remote.webelement as we

# Set default message from config to be info, and prettier format:
logging.basicConfig(format='%(asctime)s --> %(levelname)s: %(message)s', level=logging.INFO)


up = os.path.dirname
here = up(up(os.path.abspath(__file__)))
if here not in sys.path:
    sys.path.append(here)


# from . import activities as act
import ccb.activities as act
# from ccb import activities as act

WAIT_FOR_CLOSE = 5  # Wait 5 seconds before closing the page.


# 1) acceso clientes:
URL = r'https://www.crossfitcostablanca.es/acceso-a-clientes/'
# 2) login:
LOGIN_URL = r'https://www.crossfitcostablanca.es/login.php'


CLASS_MAP = {
    'Open Box': act.Activities.OPEN_BOX,
    'Crossfit': act.Activities.CROSSFIT,
    'Calisthenics': act.Activities.CALISTHENICS,
    'Weightlifting': act.Activities.WEIGHTLIFTING
}


class ClassError(KeyError):
    def __init__(self, class_, message="Class not defined."):
        self.class_ = class_
        self.message = message + " Must be one of: {}.".format(list(CLASS_MAP.keys()))
        super().__init__(self.message)


class NoHoursError(ValueError):
    def __init__(self, message="No hours inserted or incorrect format."):
        # self.hours = hours
        self.message = message
        super().__init__(self.message)


class JsonConfig:
    """
    Sample config file:
    {
    "Username": "****",
    "Password": "****",
    "days": {
        "22/11/2020": {
            "11:00": ["Open Box", "Crossfit"]
        }
    }
    }

    Must contain 5 elements:
        - Username: string with the username. In general it should be
        your email account.
        - Password: string with the password.
        - wanted_classes: list with the classes you would like to attend.
        Must be one of Open Box, Crossfit, Calisthenics or Weightlifting.
        - wanted_hours: list with the hours you are interested to assist.
        Must be in format hh:mm.
        - wanted_days : list of days you are interested to check for the
        classes. Must be in format dd/mm/yyyy

    Parameters
    ----------
    path : str
        Full path to json config file.

    Examples
    --------
    >>> config = JsonConfig(CONFIG)
    >>> config.wanted_classes()
    ['Open Box', 'Crossfit']
    >>> config.wanted_days()
    [datetime.date(2020, 11, 22)]
    >>> config.wanted_hours()
    [Hour(11:00)]
    """
    def __init__(self, path: str) -> None:
        self._path = path
        self._data = None
        self._read_file()
        self._classes = []
        self._hours = []
        self._days = []

    def _read_file(self) -> None:
        """Parses the json config file and stores the info in _data attribute. """
        with open(self._path) as f:
            self._data = json.load(f)

    def _get_classes(self) -> None:
        """
        Parse the class string to one defined in Activities, which are present in
        the page.
        """
        for day in self._data["days"]:
            self._days.append(self._parse_day(day))
            for hour in self._data["days"][day]:
                self._hours.append(act.Hour(hour))
                for wanted_class in self._data["days"][day][hour]:
                    if wanted_class not in CLASS_MAP.keys():
                        raise ClassError(wanted_class)
                    activity = CLASS_MAP[wanted_class]
                    self._classes.append(activity)

    def submit_info(self) -> typing.Tuple[str, str]:
        """Returns a tuple with the username and password. """
        return self._data['Username'], self._data['Password']

    def wanted_classes(self) -> typing.List[act.Activities]:
        """Returns a list with classes defined as act.Activities. """
        if len(self._classes) == 0:
            self._get_classes()
        return self._classes

    def wanted_hours(self) -> typing.List[act.Hour]:
        """Hour objects to check for a place. """
        if len(self._hours) == 0:
            self._get_classes()

        if len(self._hours) == 0:
            raise NoHoursError()

        return self._hours

    def wanted_days(self) -> typing.List[dt.date]:
        """Days to check for a class, as a list of dt.date objects. """
        if len(self._days) == 0:
            self._get_classes()

        return self._days

    @staticmethod
    def _parse_day(day: str) -> dt.date:
        """Creates a dt.date object. """
        try:
            d, m, y = day.split('/')
            return dt.date(int(y), int(m), int(d))
        except ValueError:
            raise ValueError("Bad day format in 'wanted_days'. ")


class CCB:
    """Interact with Crossfit Costa Blanca web page.

    Parameters
    ----------
    webdriver_ : webdriver
        webdriver to use from selenium. Defaults to Chrome.
        Only one tested.

    Methods
    -------
    login_page
    set_username
    set_password
    submit

    """
    def __init__(self, webdriver_: str = 'chrome') -> None:
        self.driver = webdriver_

    @property
    def driver(self) -> wd.Chrome:
        """WebDriver object from selenium. Interactive web page object."""
        return self._driver

    @driver.setter
    def driver(self, drv: str) -> None:
        if drv.lower() == 'chrome':
            # Get the path to the chromedriver.exe of the project.
            driver_path = os.path.join(here, 'ccb', 'chromedriver.exe')
            logging.info(driver_path)

            # Set headless mode to avoid opening the browser
            options = wd.ChromeOptions()
            options.add_argument('headless')

            self._driver = wd.Chrome(driver_path)
            # self._driver = wd.Chrome(driver_path, options=options)
            self._driver.maximize_window()
        else:
            raise NotImplementedError(
                "Only tested for 'chrome', implement yourself other driver."
            )

    def login_page(self) -> None:
        """Enters to the login page. """
        self.driver.get(LOGIN_URL)
        logging.info('CCB accessed.')

    def set_username(self, user: str) -> None:
        """Sends the username to the page.

        Parameters
        ----------
        user : str
            Username
        """
        username = self.driver.find_element(By.NAME, 'Email')
        username.send_keys(user)
        logging.info('Username registered.')

    def set_password(self, passwd: str) -> None:
        """Sends the password to the page.

        Parameters
        ----------
        passwd : str
            Password
        """
        password = self.driver.find_element(By.NAME, 'passwd')
        password.send_keys(passwd)
        logging.info('Password registered.')

    def submit(self, username: str, password: str) -> None:
        """
        Sends Username and Password and press submit button.

        Parameters
        ----------
        username : str
            Username to be passed to set_username.
        password : str
            Password to be passed to set_username.

        Returns
        -------
        None
        """
        self.set_username(username)
        self.set_password(password)
        self.driver.find_element(By.CSS_SELECTOR, '.btn-primary').click()

    def get_day(self, day: dt.date) -> None:
        """Get the button of a given day, inserted as a datetime.date object.

        Extracts the day, passes it to str to find it, and pushes its button.

        Parameters
        ----------
        day : dt.date
            Day wanted to find.

        Examples
        --------
        >>> day = dt.date.today()
        >>> ccb.get_day(day)
        """
        strday = str(day.day)
        # Go to the end of the page.
        # This is done to be sure the last days in the calendar are
        # found in any type of screen.
        self._driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        day_button = self.driver.find_element(By.LINK_TEXT, strday)
        logging.info(day_button.get_attribute('href'))
        day_button.click()
        self._driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        logging.info('Day found: {}'.format(strday))

    def get_activities(self) -> typing.List[act.Activity]:
        """Loop over elements of the table. """
        # self.driver.find_element(By.CSS_SELECTOR, 'table-striped')
        tables = self.driver.find_elements(By.CLASS_NAME, 'table-striped')
        # There should be 2 tables, the first contains the days.
        # Clicking on a day displays the second table with the same class name,
        # containing the activities.
        table = tables[1]
        # logging.info('table found!')
        activities = []
        for i, row in enumerate(table.find_elements(By.CSS_SELECTOR, 'tr')):
            if i > 1:  # The first says the Activities of the day, the second the names of each column.
                row_elements = []
                cells = row.find_elements(By.TAG_NAME, 'td')
                if len(cells) > 4:
                    # FIXME: Define a proper way of controlling this.
                    # In this case we are already registered in a class, don't do anything yet
                    pass

                else:
                    for j, cell in enumerate(cells):
                        elem = self._parse_table_elem(j, cell)
                        row_elements.append(elem)
                    # Store as keyword arguments the information for the activities.
                    name = row_elements[1]
                    arguments = {'schedule': row_elements[0], 'reservation': row_elements[2], 'button': row_elements[3]}
                    activity = self._get_activity(arguments, name)
                    activities.append(activity)
                    # logging.info(activity)

        return activities

    # @staticmethod
    def _parse_table_elem(
            self, pos: int, cell: we.WebElement
    ) -> typing.Union[act.Schedule, act.Button, act.Reservation, str]:
        """Parses each element of the table to its corresponding object.

        Parameters
        ----------
        pos : int
            Element of a row in the table of activities.
        cell : we.WebElement
            Element obtained from Selenium with info to create a full
            object for the activities.

        Returns
        -------
        elem : Schedule, Button, Reservation or str
            Element parsed and transformed to its given class to
            simplify its interaction inside of an Activity.
        """
        if pos == 0:  # Horario
            elem = act.Schedule(cell.text)
        elif pos == 1:  # Actividad
            elem = cell.text
        elif pos == 2:  # Reservas
            elem = act.Reservation(cell.text)
        elif pos == 3:  # Reservar
            icon = None
            if len(cell.text) > 0:
                elem = cell.text
            else:
                elem = cell.find_element(By.CSS_SELECTOR, 'a')
                icon = cell.find_element_by_css_selector('span').get_attribute('class')
            elem = act.Button(elem, self.driver, icon=icon)
        else:
            raise ValueError('This element is not expected: {}'.format(cell))

        return elem

    @staticmethod
    def _get_activity(arguments: typing.Dict, name: str) -> act.Activity:
        """Get the corresponding activity by the parsed info.

        Parameters
        ----------
        arguments : dict
            Contains the dict with the names of the variables to instantiate
            a given activity, and the proper object as a value.
        name : str
            The parsed element indicating the type of activity.

        Returns
        -------
        activity : act.Activity
            Activity instantiated.
        """
        if name == act.Activities.OPEN_BOX:
            activity = act.OpenBox(**arguments)

        elif name == act.Activities.CROSSFIT:
            activity = act.Crossfit(**arguments)

        elif name == act.Activities.CALISTHENICS:
            activity = act.Calisthenics(**arguments)

        elif name == act.Activities.WEIGHTLIFTING:
            activity = act.Weightlifting(**arguments)

        else:
            activity = None
            warnings.warn('Activity unregistered: {}.'.format(activity))

        return activity

    def close_page(self) -> None:
        """Call at the end of the program to close the window.
        Has no effect on headless mode.
        """
        time.sleep(1)
        self.driver.close()

    def refresh(self) -> None:
        """To be called ro reload the tables, maybe? """
        self.driver.refresh()


if __name__ == '__main__':

    parent = os.path.dirname(os.path.abspath(__file__))
    CONFIG_PATH = os.path.join(parent, 'config.json')

    config_file = JsonConfig(CONFIG_PATH)
    logging.info('Config file read. ')
    ccb = CCB()
    # Get login page of San Vicente centre..
    ccb.login_page()

    # Wait 2 seconds in case the time is needed to load the page.
    time.sleep(2)

    # Get username and password to be sent.
    username, password = config_file.submit_info()
    ccb.submit(username, password)

    time.sleep(WAIT_FOR_CLOSE)
    # dia = TODAY + period(days=1)
    days = config_file.wanted_days()

    # TODO: Loop over the list of days. For the moment only one
    ccb.get_day(days[0])
    activities = ccb.get_activities()
    wanted_activities = config_file.wanted_classes()
    # TODO: Get the correct hour.
    wanted_hours = config_file.wanted_hours()
    wanted_hour = act.Hour('15:00')
    for activity in activities:
        if activity.name in wanted_activities:  # Check only in those selected.
            if wanted_hour in activity.schedule:  # Check for the hour.
                logging.info("Activity: {}".format(activity))
                is_booked = activity.book()
                logging.info("Are we registered? {}.".format(is_booked))

    # ccb.close_page()
