from random import randrange
import sqlite3


class BankAccount:
    iin = '400000'  # issuer_identification_number

    def __init__(self):
        self.card_number = None
        self.card_pin = None
        self.create_db()
        self.main()

    @staticmethod
    def create_db():
        conn = sqlite3.connect('card.s3db')
        cur = conn.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS card('
                    '   id INTEGER PRIMARY KEY AUTOINCREMENT,'
                    '   number TEXT NOT NULL,'
                    '   pin TEXT NOT NULL,'
                    '   balance INTEGER DEFAULT 0);')
        conn.commit()
        conn.close()

    @staticmethod
    def main_menu():
        choice = input('1. Create an account\n2. Log into account\n0. Exit')
        return int(choice)

    @staticmethod
    def user_menu():
        print("1. Balance\n2. Add income\n3. Do transfer")
        print("4. Close account\n5. Log out\n0. Exit")
        choice = input()
        return int(choice)

    @staticmethod
    def sql_insert(card, pin):
        conn = sqlite3.connect('card.s3db')
        cur = conn.cursor()
        cur.execute(
            f'INSERT INTO'
            f'  card(number, pin)'
            f'VALUES'
            f'  ("{card}", "{pin}")'
        )
        conn.commit()
        conn.close()

    @staticmethod
    def sql_credentials(card, pin):
        value = (card, pin)
        conn = sqlite3.connect('card.s3db')
        cur = conn.cursor()
        cur.execute(
            'SELECT number FROM card WHERE number = ? AND pin = ?', value
        )
        result = cur.fetchone()
        conn.commit()
        conn.close()
        return True if result else False

    @staticmethod
    def sql_balance(card_number):
        value = (card_number,)
        conn = sqlite3.connect('card.s3db')
        cur = conn.cursor()
        cur.execute(
            'SELECT balance FROM card WHERE number = ?', value
        )
        balance = cur.fetchone()
        conn.commit()
        conn.close()
        return balance[0]

    @staticmethod
    def luhn(card_number):
        luhn_sum = 0
        for index, num in enumerate(card_number):
            if index % 2 == 0:
                if int(num) * 2 > 9:
                    luhn_sum += int(num) * 2 - 9
                else:
                    luhn_sum += int(num) * 2
            else:
                luhn_sum += int(num)
        return luhn_sum

    @staticmethod
    def display():
        conn = sqlite3.connect('card.s3db')
        cur = conn.cursor()
        for row in cur.execute('SELECT * FROM card'):
            print(row)
        conn.close()

    @staticmethod
    def delete(card_number):
        conn = sqlite3.connect('card.s3db')
        cur = conn.cursor()
        cur.execute(
            f'DELETE FROM card WHERE number = {card_number}')
        conn.commit()
        conn.close()
        print('The account has been closed!')

    def create_account(self):
        card_number = self.generate_card_number()
        card_pin = self.generate_pin()
        self.sql_insert(self.card_number, self.card_pin)
        print('Your card has been created')
        print(f'Your card number:\n{card_number}')
        print(f'Your card PIN:\n{card_pin}')

    def generate_card_number(self):
        number = ''
        for num in range(9):
            number += str(randrange(10))
        partial_number = (self.iin + number)
        new_card_number = (partial_number +
                           self.generate_checksum(partial_number))
        self.card_number = new_card_number
        return new_card_number

    def generate_checksum(self, card_number):
        luhn_sum = self.luhn(card_number)
        if luhn_sum % 10 > 0:
            return str(10 - (self.luhn(card_number) % 10))
        else:
            return '0'

    def generate_pin(self):
        new_card_pin = ''
        for num in range(4):
            new_card_pin += str(randrange(10))
        self.card_pin = new_card_pin
        return new_card_pin

    def log_into_account(self):
        print('Enter your card number: ')
        username = str(input())
        print('Enter your PIN: ')
        password = str(input())
        if self.sql_credentials(username, password):
            print('You have successfully logged in!')
            return username
        else:
            print('Wrong card number or PIN!')
            return False

    def add_income(self, card_number, income_value):
        balance = self.sql_balance(card_number)
        sum_value = int(balance) + int(income_value)
        conn = sqlite3.connect('card.s3db')
        cur = conn.cursor()
        cur.execute(
            f'UPDATE card SET balance = {sum_value} '
            f'WHERE number = {card_number}'
        )
        print('Income was added!')
        conn.commit()
        conn.close()

    def transfer(self, card_number, acceptor_card_number):
        conn = sqlite3.connect('card.s3db')
        cur = conn.cursor()
        cards_data = []
        for row in cur.execute('SELECT number FROM card'):
            cards_data.append(row[0])
        luhn_sum = self.luhn(acceptor_card_number)
        if luhn_sum % 10 > 0:
            print("Probably you made a mistake in the card number. Please try again!")
        else:
            if acceptor_card_number not in cards_data:
                print("Such a card does not exist.")
            else:
                transfer_value = input('Enter how much money you want to transfer:')
                owner_balance = self.sql_balance(card_number)
                new_owner_balance = int(owner_balance) - int(transfer_value)
                acceptor_balance = self.sql_balance(acceptor_card_number)
                new_acceptor_balance = int(acceptor_balance) + int(transfer_value)

                if int(transfer_value) > int(owner_balance):
                    print('Not enough money!')
                elif card_number == acceptor_card_number:
                    print("You can't transfer money to the same account!")
                else:
                    cur.execute(
                        f'UPDATE card SET balance = {new_owner_balance} '
                        f'WHERE number = {card_number}'
                    )
                    cur.execute(
                        f'UPDATE card SET balance = {new_acceptor_balance} '
                        f'WHERE number = {acceptor_card_number}'
                    )
                    print('Success!')
        conn.commit()
        conn.close()

    def main(self):
        while True:
            choice1 = self.main_menu()
            if choice1 == 1:
                self.create_account()
            elif choice1 == 2:
                logged_user = self.log_into_account()
                while logged_user:
                    choice2 = self.user_menu()
                    if choice2 == 1:
                        print(self.sql_balance(logged_user))
                    elif choice2 == 2:
                        self.add_income(logged_user, input('Enter income:'))
                    elif choice2 == 3:
                        print('Transfer')
                        self.transfer(logged_user, input('Enter card number:'))
                    elif choice2 == 4:
                        self.delete(logged_user)
                        break
                    elif choice2 == 5:
                        print('You have successfully logged out!')
                        break
                    else:
                        print('Bye!')
                        # self.display()
                        exit()
            else:
                print('Bye!')
                # self.display()
                exit()


new = BankAccount()
