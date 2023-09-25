from collections import UserDict
from abc import ABC, abstractmethod
import re
from datetime import date, timedelta
import typing as t

from DigiDuckBook.abc_book import AbstractData

# abstract base class that defines the common properties and methods for all field types, including the validation logic
# Each specific field type (Name, Phone, Email, Birthday, Address) inherits from AbstractField and provides its own validation logic by implementing the _validate method
# each class has a single responsibility: representing a specific field type and validating its value

class AbstractField(ABC):
    def __init__(self, value: str) -> None:
        self._value = None
        self.value = value

    @property
    def value(self) -> str:
        return self._value

    @value.setter
    def value(self, value: str) -> None:
        self._validate(value)
        self._value = value

    @abstractmethod
    def _validate(selfself, value: str) -> None:
        pass

    def __str__(self) -> str:
        return f"{self.value}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(value={self.value})"

    def __eq__(self, val):  # ==
        if isinstance(val, self.__class__):
            val = val.value
        return self.value == val


class Name(AbstractField):
    def __validate(self, value: str) -> None:
        if not (len(value) > 2):
            raise ValueError(f'Name "{value}" is too short!')

class Phone(AbstractField):
    def _validate(self, value: str) -> None:
        value = re.sub(r'[ \(\)\-]', '', value)
        phone_pattern = re.compile(r'\+380\d{9}|380\d{9}|80\d{9}|0\d{9}')
        if re.fullmatch(phone_pattern, value) is None:
            raise ValueError(f'Value {value} is not in correct format! Enter phone in format "+380xx3456789"')
        return f"+380{value[-9:]}"

class Email(AbstractField):
    def _validate(self, value: str) -> None:
        email_pattern = re.compile(r'[a-zA-Z]{1}[\S.]+@[a-zA-Z]+\.[a-zA-Z]{2,}')
        if re.fullmatch(email_pattern, value) is None:
            raise ValueError(
                f'Value {value} is not in correct format! Enter it in format "email prefix @ email domain"')

class Birthday(AbstractField):
    def _validate(self, value: str) -> None:
        try:
            b_day = date.fromisoformat(value)
        except ValueError:
            raise ValueError(f'Birthday {value} is not correct format! for example "2023-12-30"')
        if b_day.year > date.today().year:
            raise ValueError(f'{value} -  you from the future?')

    def get_date(self) -> date:
        return date.fromisoformat(self.value)


class Address(AbstractField):
    def _validate(self, value: str) -> None:
        if value.isspace():
            raise ValueError(f'Address "{value}" is not in correct format!')
        if not (5 <= len(value) <= 50):
            raise ValueError(
                f'Address "{value}" is not in correct format! It must contain from 5 to 50 characters')


class Record: #validation and conversion of field values are already handled by the respective field classes.
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

    def add_phone(self, phone: Phone | str) -> None:
        if phone in self.phones:
            raise ValueError("this phone number has already been added")

        phone = self._phone(phone)
        self.phones.append(phone)

    def remove_phone(self, phone: Phone | str) -> None:
        phone = self._phone(phone)
        if phone not in self.phones:
            raise ValueError(f"The phone '{phone}' is not in this record.")
        self.phones.remove(phone)

    def change_phone(self, old_phone: Phone | str, new_phone: Phone | str) -> None:
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
        if self.birthday == None:
            raise KeyError(f"No birthday set for the contact {self.name}.")

        today = date.today()
        try:
            bday = self.birthday.get_date().replace(year=today.year)
            if (today > bday):
                bday = bday.replace(year=today.year + 1)
            return (bday - today).days

        except ValueError:
            exept_temp = Record(self.name, [], today.replace(month=2, day=28).isoformat())
            return exept_temp.days_to_birthday() + 1

    def change_address(self, address: Address) -> None:
        self.address = self._address(address)

    def __str__(self) -> str:

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
    def add_record(self, record: Record) -> None:
        self[record.name.value] = record

    def __getitem__(self, key: str) -> Record:
        record = self.data.get(key)
        if record is None:
            raise KeyError(f"This name {key} isn't in Address Book")
        return record

    def __setitem__(self, key: str, val: Record) -> None:
        if not isinstance(val, Record):
            raise TypeError("Record must be an instance of the Record class.")
        if key in self.data:
            raise KeyError(f"This name '{key}' is already in contacts")
        self.data[key] = val

    def __delitem__(self, key: str) -> None:
        if not isinstance(key, str):
            raise KeyError("Value must be a string")
        if key not in self.data:
            raise KeyError(f"Can't delete contact {key} isn't in Address Book")
        del self.data[key]

    def groups_days_to_bd(self, input_days: str) -> list[Record]:
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
        res_dict = {}
        for record in self.data.values():
            res_dict.update(record.to_dict())
        return res_dict

    def from_dict(self, data_json: dict) -> None:
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
        if item_number <= 0:
            raise ValueError("Item number must be greater than 0.")
        elif item_number > len(self.data):
            item_number = len(self.data)

        list_records = []
        for counter, record in enumerate(self.data.values(), 1):
            list_records.append(record)
            if (not counter % item_number) or counter == len(self.data):
                yield list_records
                list_records = []


if __name__ == "__main__":
    pass