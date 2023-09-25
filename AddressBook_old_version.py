from collections import UserDict
import re
from datetime import date, timedelta
import typing as t

from DigiDuckBook.abc_book import AbstractData


class Field:
    """
    Parent class representing a field used in the record of the address book.
    """

    def __init__(self, value: str) -> None:
        self.value = value

    def __valid_value(self, value) -> None:
        if not isinstance(value, str):
            raise TypeError(f'Value {value} is not valid. It must be a string')

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value: str, validation: t.Callable | None = None) -> None:
        self.__valid_value(value)
        if validation is not None:
            value = validation(value)
        self._value = value

    def __str__(self) -> str:
        return f"{self.value}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(value={self.value})"

    def __eq__(self, val):  # ==
        if isinstance(val, self.__class__):  # можно и через if hasattr(val, 'value'):
            val = val.value
        return self.value == val


class Name(Field):
    """
    Class representing the name field in a record of the address book.
    """

    def __valid_name(self, value) -> str:
        if not (len(value) > 2):
            raise ValueError(f'Name "{value}" is too short!')
        return value

    @Field.value.setter  # переопределяем сеттер родительского класса
    def value(self, value: str) -> None:
        Field.value.fset(self, value, self.__valid_name)


class Phone(Field):
    """
    Class representing the phone field in a record of the address book.
    """

    def __valid_phone(self, value) -> str:
        """
        Validate and format a phone number string.

        Args:
            value (str): The input phone number string to be validated.
        Returns:
            str: The validated and formatted phone number in the "+380xxxxxxxxx" format.
        Raises:
            ValueError: If the input value is not in the correct format.
        Example:
            valid_phone = __valid_phone("+380 (67) 123-45-67")
        """
        value = re.sub(r'[ \(\)\-]', '', value)
        phone_pattern = re.compile(r'\+380\d{9}|380\d{9}|80\d{9}|0\d{9}')
        if re.fullmatch(phone_pattern, value) is None:
            raise ValueError(f'Value {value} is not in correct format! Enter phone in format "+380xx3456789"')
        return f"+380{value[-9:]}"

    @Field.value.setter  # переопределяем сеттер родительского класса
    def value(self, value: str) -> None:
        Field.value.fset(self, value, self.__valid_phone)


class Email(Field):
    """
    Class representing the email field in a record of the address book.
    """

    def __valid_email(self, value: str) -> str:
        """
        Validate the correct format of email in the input email string.
        Valid format of email: (username)@(domainname).(top-leveldomain).
        Args:
            value (str): The input email string.
        Raises:
            ValueError: If the input email string is not in a valid format.
        Returns:
            str: The valid email string.
        """
        email_pattern = re.compile(r'[a-zA-Z]{1}[\S.]+@[a-zA-Z]+\.[a-zA-Z]{2,}')
        # або r"[a-zA-Z0-9._ %-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2, }"
        if re.fullmatch(email_pattern, value) is None:
            raise ValueError(
                f'Value {value} is not in correct format! Enter it in format "email prefix @ email domain"')
        return value

    @Field.value.setter
    def value(self, value: str) -> None:
        Field.value.fset(self, value, self.__valid_email)


class Birthday(Field):
    """
    Class representing the birthday field in a record of the address book.
    The date is stored in ISO 8601 format.
    """

    def __valid_date(self, value: str) -> str:
        """
        Input date string to a valid ISO-formatted date.
        Args:
            value (str): The input date string.
        Raises:
            ValueError: If the input date string is not in a valid date format(ISO).
        Returns:
            str: The valid ISO-formatted date string.
        """
        try:
            b_day = date.fromisoformat(value)
        except ValueError:
            raise ValueError(f'Birthday {value} is not correct format! for example "2023-12-30"')
        if b_day.year > date.today().year:
            raise ValueError(f'{value} -  you from the future?')
        return value

    @Field.value.setter
    def value(self, value: str) -> None:
        Field.value.fset(self, value, self.__valid_date)

    def get_date(self) -> date:
        return date.fromisoformat(self.value)


class Address(Field):
    """
    Class representing the address field in a record of the address book.
    """

    def __valid_address(self, value: str) -> str:
        """
        Validate the length of address in the input address string.
        Args:
            value (str): The input address string.
        Raises:
            ValueError: If the input address string exceeds the allowed length.
        Returns:
            str: The valid address string.
        """
        if value.isspace():
            raise ValueError(f'Address "{value}" is not in correct format!')
        if not (5 <= len(value) <= 50):
            raise ValueError(
                f'Address "{value}" is not in correct format! It must contain from 5 to 50 characters')
        return value

    @Field.value.setter
    def value(self, value: str) -> None:
        Field.value.fset(self, value, self.__valid_address)


class Record:
    """
    Class representing a record in an address book.

    Attributes:
        name (Name): The name of the contact.
        phones (list): A list of phone numbers associated with the contact.
        email (Email): The email of the contact.
        birthday (Birthday): The birthday of the contact.
        address (Address): The address of the contact.
    """

    def __init__(
            self,
            name: Name | str,
            phones: list[Phone] | list[str] = [],
            email: Email | str | None = None,
            birthday: Birthday | str | None = None,
            address: Address | str | None = None,
    ) -> None:

        self.name = self._name(name)
        self.phones = [self._phone(phone) for phone in phones]
        self.email = None if email is None else self._email(email)
        self.birthday = None if birthday is None else self._birthday(birthday)
        self.address = None if address is None else self._address(address)

    def _name(self, name: str | Name) -> Name:
        if not isinstance(name, Name):
            name = Name(name)
        return name

    def _phone(self, phone: str | Phone) -> Phone:
        if not isinstance(phone, Phone):
            phone = Phone(phone)
        return phone

    def _email(self, email: str | Email) -> Email:
        if not isinstance(email, Email):
            email = Email(email)
        return email

    def _birthday(self, birthday: str | Birthday) -> Birthday:
        if not isinstance(birthday, Birthday):
            birthday = Birthday(birthday)
        return birthday

    def _address(self, address: str | Address) -> Address:
        if not isinstance(address, Address):
            address = Address(address)
        return address

    def add_phone(self, phone: Phone | str) -> None:
        """
        Add a new phone number to the list of phone numbers for the contact.
        Args:
            phone (Phone) or try valid Str: The phone number to be added to the contact.
        Returns:
            None: This method does not return any value.
        """
        if phone in self.phones:
            raise ValueError("this phone number has already been added")

        phone = self._phone(phone)
        self.phones.append(phone)

    def remove_phone(self, phone: Phone | str) -> None:
        """
        Remove a phone number from the list of phone numbers for the contact.

        Args:
            phone (Phone) or try valid Str: The phone number to be removed from the contact.
        Raises:
            ValueError: If the phone number is not found in the contact's list of phone numbers.
        Returns:
            None: This method does not return any value.
        """
        phone = self._phone(phone)  # єту строку может после райза?
        if phone not in self.phones:
            raise ValueError(f"The phone '{phone}' is not in this record.")
        self.phones.remove(phone)

    def change_phone(self, old_phone: Phone | str, new_phone: Phone | str) -> None:
        """
        Change a phone number in the list of phone numbers for the contact.

        Args:
            old_phone (Phone)  or try valid Str: The existing phone number to be replaced.
            new_phone (Phone)  or try valid Str: The new phone number to replace the existing one.
        Raises:
            ValueError: If the old phone number is not found in the contact's list of phone numbers.
            ValueError: If the new phone number is already in contact's list of phone numbers.
        """

        if (old_phone := self._phone(old_phone)) not in self.phones:
            raise ValueError(
                f"The phone '{old_phone}' is not in this record '{self.name}'."
            )
        if (new_phone := self._phone(new_phone)) in self.phones:
            raise ValueError(
                f"The phone '{new_phone}' already in record '{self.name}'."
            )
        inx = self.phones.index(old_phone)
        self.phones[inx] = new_phone

    def change_email(self, email: Email) -> None:
        self.email = self._email(email)

    def change_birthday(self, birthday: Birthday) -> None:
        self.birthday = self._birthday(birthday)

    def days_to_birthday(self) -> int:
        """
        Calculate the number of days remaining until the contact's next birthday.

        Returns:
            int: The number of days remaining until the contact's next birthday.
        Raises:
            KeyError: If the contact does not have a birthday set.
        """
        if self.birthday == None:
            raise KeyError(f"No birthday set for the contact {self.name}.")

        today = date.today()
        try:
            bday = self.birthday.get_date().replace(
                year=today.year
            )  # дата др в этом году
            if (
                    today > bday
            ):  # если др уже прошло берем дату следующего(в следующем году)
                bday = bday.replace(year=today.year + 1)
            return (bday - today).days
        except ValueError:  # исключение для високосной дати 1го дня уууу-02-29
            exept_temp = Record(
                self.name, [], today.replace(month=2, day=28).isoformat()
            )
            return exept_temp.days_to_birthday() + 1

    def change_address(self, address: Address) -> None:
        self.address = self._address(address)

    def __str__(self) -> str:
        # вывод телефонов с новой строки и табуляцией
        birthday_str = f'birthday: {self.birthday or "Empty"}'
        email_str = f'email: {self.email or "Empty"}'
        address_str = f'address: {self.address or "Empty"}'
        phones_str = ", ".join([str(ph) for ph in self.phones])
        return (
            f'<Record>:\n\tname: {self.name}\n'
            f'\tphones: {phones_str or "Empty"}\n'
            f'\t{email_str}\n'
            f'\t{birthday_str}\n'
            f'\t{address_str}\n'
        )

    def __repr__(self) -> str:
        # __repr__ используется для того что бы показать как создается екземпляр
        # т.е. если выполнить эту строку в repl python будет создан такой же екземпляр,
        # конечно, при условии , что все необходимые классы тоже импортированы
        # repl python
        # (встроенная в пайтон среда выполенния, которую можно вызвать просто выполнив команду python)
        return (
            f"Record(name={self.name!r}, "
            f'phones=[{", ".join([ph.__repr__() for ph in self.phones])}, '
            f'email={self.email!r}, '
            f'birthday={self.birthday!r},'
            f'address={self.address!r})'
        )

    def to_dict(self) -> dict[str, dict[str, list[str] | str | None]]:
        phones = [str(phone) for phone in self.phones]
        email = None if self.email is None else str(self.email)
        birthday = None if self.birthday is None else str(self.birthday)
        address = None if self.address is None else str(self.address)

        return {
            str(self.name): {
                "phones": phones,
                "email": email,
                "birthday": birthday,
                "address": address,
            },
        }


class AddressBook(UserDict, AbstractData):
    """
    A class representing an address book, which is a dictionary
    with record names as keys and record objects as values.
    """

    def add_record(self, record: Record) -> None:
        """
        Add a record to the address book.

        Args:
            record (Record): The record object to be added.
        Raises:
            TypeError: If the given object is not an instance of the Record class.
        """
        self[record.name.value] = record  # отрабативает __setitem__

    def __getitem__(self, key: str) -> Record:
        """
        Retrieve a record from the address book by its name.

        Args:
            key (str): The name of the record to retrieve.
        Returns:
            Record: The record object corresponding to the given name.
        Raises:
            KeyError: If the provided name is not found in the address book.
        """
        record = self.data.get(key)
        if record is None:
            raise KeyError(f"This name {key} isn't in Address Book")
        return record

    def __setitem__(self, key: str, val: Record) -> None:
        """
        Add or update a record in the address book.

        Args:
            key (str): The name of the record.
            val (Record): The record object to be added or updated.
        Raises:
            TypeError: If the given value is not an instance of the Record class.
            KeyError: If the provided name is already present in the address book.
        """
        if not isinstance(val, Record):
            raise TypeError("Record must be an instance of the Record class.")
        if key in self.data:
            raise KeyError(f"This name '{key}' is already in contacts")
        self.data[key] = val

    def __delaitem__(self, key: str) -> None:
        """
        Delete a record from the address book by its name.

        Args:
            key (str): The name of the record to delete.
        Raises:
            KeyError: If the provided name is not found in the address book.
        """
        if not isinstance(key, str):
            raise KeyError("Value must be string")
        if key not in self.data:
            raise KeyError(f"Can't delete contact {key} isn't in Address Book")
        del self.data[key]

    def groups_days_to_bd(self, input_days: str) -> list[Record]:
        """

        Display list of users which birthday is a given number of days from the current date

        Returns:
            list of records

        """
        if not input_days.isdigit():
            raise ValueError(f"Not valid days {input_days}, please input num")
        current_date = date.today()
        time_delta = timedelta(days=int(input_days))
        last_date = current_date + time_delta
        list_records = []

        for record in self.data.values():
            birthday: date = record.birthday.get_date()
            birthday = birthday.replace(year=current_date.year)

            if (current_date <= birthday <= last_date):
                list_records.append(record)
        return list_records

    def to_dict(self) -> dict:
        """
        Convert the address book to a dictionary.

        Returns:
            dict: A dictionary representing the address book.
        """
        res_dict = {}
        for record in self.data.values():
            res_dict.update(record.to_dict())
        return res_dict

    def from_dict(self, data_json: dict) -> None:
        """
        Load data from a dictionary into the address book.

        Args:
            data_json (dict): A dictionary containing data for the address book.
        Raises:
            TypeError: If the provided data is not a dictionary.
        """
        if not isinstance(data_json, dict):
            raise TypeError("this is not dict")

        for name, record in data_json.items():
            self.add_record(
                Record(name=name,
                       phones=record['phones'],
                       email=record['email'],
                       birthday=record['birthday'],
                       address=record['address']),
            )

    def __str__(self) -> str:
        return "\n".join([str(r) for r in self.values()])

    def output_all_data(self) -> str:
        return "\n".join([str(record)[9] for record in self.values()])

    def search(self, search_word: str) -> list[Record]:
        """
        Search for records containing the given search word.

        Args:
            search_word (str): The word to search in the address book.

        Returns:
            list[Record] or []: list with found records.
        """
        search_list = []
        for record in self.data.values():
            str_val_record = (f'{record.name}'
                              f'{" ".join([str(ph) for ph in record.phones])}'
                              f'{record.email}'
                              f'{record.birthday}'
                              f'{record.address}'
                              )
            if search_word.lower() in str_val_record.lower():
                search_list.append(record)
        return search_list

    def iterator(self, item_number: int) -> t.Generator[Record, int, None]:
        """
        Iterate through the records in the address book and yield groups of records.

        Args:
            item_number (int) > 0: The number of records to be yielded at a time.

        Yields:
            List[Record]: A list containing a group of records.

        Notes:
            If the given item_number is greater than the total number of records in the address book,
            all records will be yielded in one group.

        """
        if item_number <= 0:
            raise ValueError("Item number must be greater than 0.")
        elif item_number > len(
                self.data
        ):  # если количство виводов(за раз) больше чем количество записей
            item_number = len(self.data)  # виводим все

        list_records = []
        for counter, record in enumerate(self.data.values(), 1):
            list_records.append(record)
            if (not counter % item_number) or counter == len(self.data):
                yield list_records
                list_records = []


if __name__ == "__main__":
    pass