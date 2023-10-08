from cryptography.fernet import Fernet
import tkinter as tk
from tkinter import messagebox
import pyperclip
import sqlite3
import keyboard
import customtkinter

# Функция для загрузки ключа шифрования из базы данных
def load_key():
    try:
        conn = sqlite3.connect('passwords.db')
        cursor = conn.cursor()
        cursor.execute("SELECT key FROM encryption_key")
        key = cursor.fetchone()[0]
        conn.close()
        return key
    except sqlite3.Error:
        messagebox.showerror("Ошибка", "Не удалось загрузить ключ шифрования из базы данных.")

# Функция для шифрования текста
def encrypt_text(text, key):
    fernet = Fernet(key)
    encrypted_text = fernet.encrypt(text.encode())
    return encrypted_text

# Функция для дешифрования текста
def decrypt_text(encrypted_text, key):
    fernet = Fernet(key)
    decrypted_text = fernet.decrypt(encrypted_text)
    return decrypted_text.decode()

# Функция для сохранения пароля в базу данных
def save_password():
    site = site_entry.get()
    email = email_entry.get()
    password = password_entry.get()

    # Проверка наличия записи с таким же названием сайта/приложения
    if check_site_exists(site):
        messagebox.showinfo("Ошибка", f"Запись для сайта/приложения '{site}' уже существует")
    else:
        # Шифрование пароля
        key = load_key()
        encrypted_password = encrypt_text(password, key)

        # Сохранение пароля в базу данных
        try:
            conn = sqlite3.connect('passwords.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO password_entries VALUES (?, ?, ?)", (site, email, encrypted_password))
            conn.commit()
            conn.close()
        except sqlite3.Error:
            messagebox.showerror("Ошибка", "Не удалось сохранить пароль в базе данных.")

        messagebox.showinfo("Сохранение пароля", "Пароль успешно сохранен!")

# Функция для получения информации о пароле
def get_password():
    site = site_entry.get()

    # Получение информации о пароле из базы данных
    try:
        conn = sqlite3.connect('passwords.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM password_entries WHERE site=?", (site,))
        password_info = cursor.fetchone()
        conn.close()

        if password_info:
            email = password_info[1]
            encrypted_password = password_info[2]

            # Дешифрование пароля
            key = load_key()
            decrypted_password = decrypt_text(encrypted_password, key)

            # Вывод информации о пароле в поля Entry
            email_entry.delete(0, tk.END)
            email_entry.insert(0, email)

            password_entry.delete(0, tk.END)
            password_entry.insert(0, decrypted_password)
        else:
            messagebox.showinfo("Ошибка", f"Запись для сайта/приложения '{site}' не найдена.")
    except sqlite3.Error:
        messagebox.showerror("Ошибка", "Не удалось получить информацию о пароле из базы данных.")

# Функция для редактирования информации о пароле
def edit_password():
    site = site_entry.get()

    # Получение информации о пароле из базы данных
    try:
        conn = sqlite3.connect('passwords.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM password_entries WHERE site=?", (site,))
        password_info = cursor.fetchone()
        conn.close()

        if password_info:
            email = email_entry.get()
            password = password_entry.get()

            # Шифрование пароля
            key = load_key()
            encrypted_password = encrypt_text(password, key)

            # Обновление информации о пароле в базе данных
            try:
                conn = sqlite3.connect('passwords.db')
                cursor = conn.cursor()
                cursor.execute("UPDATE password_entries SET email=?, password=? WHERE site=?", (email, encrypted_password, site))
                conn.commit()
                conn.close()
            except sqlite3.Error:
                messagebox.showerror("Ошибка", "Не удалось обновить информацию о пароле в базе данных.")

            messagebox.showinfo("Редактирование информации", "Информация успешно отредактирована")
        else:
            messagebox.showinfo("Редактирование информации", f"Запись для сайта/приложения '{site}' не найдена")
    except sqlite3.Error:
        messagebox.showerror("Ошибка", "Не удалось получить информацию о пароле из базы данных.")

# Функция для очистки всех полей
def clear_all_fields():
    site_entry.delete(0, tk.END)
    email_entry.delete(0, tk.END)
    password_entry.delete(0, tk.END)

# Функция для вывода всех записей
def show_all_passwords():
    try:
        conn = sqlite3.connect('passwords.db')
        cursor = conn.cursor()
        cursor.execute("SELECT site FROM password_entries")
        password_sites = cursor.fetchall()
        conn.close()

        sites = [site[0] for site in password_sites]

        messagebox.showinfo("Список сайтов/приложений", "\n".join(sites))
    except sqlite3.Error:
        messagebox.showerror("Ошибка", "Не удалось получить список сайтов/приложений из базы данных.")

# Функция для проверки наличия записи с заданным названием сайта/приложения
def check_site_exists(site):
    try:
        conn = sqlite3.connect('passwords.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM password_entries WHERE site=?", (site,))
        count = cursor.fetchone()[0]
        conn.close()
        return count > 0
    except sqlite3.Error:
        messagebox.showerror("Ошибка", "Не удалось проверить наличие записи в базе данных.")

# Функция для копирования текста в буфер обмена
def copy_text():
    widget = root.focus_get()
    if isinstance(widget, tk.Entry):
        text = widget.selection_get()
        pyperclip.copy(text)

# Функция для вставки текста из буфера обмена
def paste_text():
    widget = root.focus_get()
    if isinstance(widget, tk.Entry):
        text = pyperclip.paste()
        widget.delete(0, tk.END)
        widget.insert(tk.END, text)

# Создание главного окна
root = customtkinter.CTk()
root.title("PassKeeper")
root.iconbitmap('key.ico')

# Создание метки и поля для ввода названия сайта/приложения
site_label = customtkinter.CTkLabel(root, text="Название сайта/приложения:", font=("Arial", 16))
site_label.grid(row=0, column=0, sticky="w", padx=25)
site_entry = customtkinter.CTkEntry(root, font=("Arial", 16))
site_entry.grid(row=0, column=1, padx=25)

# Создание метки и поля для ввода email/логина
email_label = customtkinter.CTkLabel(root, text="Email/Логин:", font=("Arial", 16))
email_label.grid(row=1, column=0, sticky="w", padx=25)
email_entry = customtkinter.CTkEntry(root, font=("Arial", 16))
email_entry.grid(row=1, column=1, padx=25)

# Создание метки и поля для ввода пароля
password_label = customtkinter.CTkLabel(root, text="Пароль:", font=("Arial", 16))
password_label.grid(row=2, column=0, sticky="w", padx=25)
password_entry = customtkinter.CTkEntry(root, font=("Arial", 16))
password_entry.grid(row=2, column=1, padx=25)

# Создание кнопок для сохранения, получения, редактирования, очистки полей и вывода списка
save_button = customtkinter.CTkButton(root, text="Сохранить", command=save_password, font=("Arial", 16))
save_button.grid(row=3, column=0, pady=10)

get_button = customtkinter.CTkButton(root, text="Получить", command=get_password, font=("Arial", 16))
get_button.grid(row=3, column=1, pady=10)

edit_button = customtkinter.CTkButton(root, text="Редактировать", command=edit_password, font=("Arial", 16))
edit_button.grid(row=4, column=0, pady=10)

clear_all_button = customtkinter.CTkButton(root, text="Очистить", command=clear_all_fields, font=("Arial", 16))
clear_all_button.grid(row=4, column=1, pady=10)

show_all_button = customtkinter.CTkButton(root, text="Вывести список", command=show_all_passwords, font=("Arial", 16))
show_all_button.grid(row=5, column=0, pady=10)

# Функция для проверки наличия записи с заданным названием сайта/приложения
def check_site_exists(site):
    try:
        conn = sqlite3.connect('passwords.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM password_entries WHERE site=?", (site,))
        count = cursor.fetchone()[0]
        conn.close()
        return count > 0
    except sqlite3.Error:
        messagebox.showerror("Ошибка", "Не удалось проверить наличие записи в базе данных.")

# Функция для обработки события нажатия клавиш
def on_key_press(event):
    if keyboard.is_pressed("Ctrl+C") or keyboard.is_pressed("Ctrl+С"):
        copy_text()
    elif keyboard.is_pressed("Ctrl+V") or keyboard.is_pressed("Ctrl+В"):
        paste_text()

# Привязка обработчика событий к главному окну
root.bind("<Key>", on_key_press)

# Создание таблицы для хранения паролей в базе данных
try:
    conn = sqlite3.connect('passwords.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS password_entries
                      (site text, email text, password text)''')
    conn.commit()
    conn.close()
except sqlite3.Error:
    messagebox.showerror("Ошибка", "Не удалось создать таблицу в базе данных.")

# Создание таблицы для хранения ключа шифрования в базе данных
try:
    conn = sqlite3.connect('passwords.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS encryption_key
                      (key text)''')
    conn.commit()

    # Генерация ключа шифрования и сохранение его в базе данных (если ключа нет)
    cursor.execute("SELECT COUNT(*) FROM encryption_key")
    count = cursor.fetchone()[0]
    if count == 0:
        key = Fernet.generate_key()
        cursor.execute("INSERT INTO encryption_key VALUES (?)", (key,))
        conn.commit()
    conn.close()
except sqlite3.Error:
    messagebox.showerror("Ошибка", "Не удалось создать таблицу для ключа шифрования в базе данных.")

# Запуск основного цикла обработки событий
root.mainloop()
