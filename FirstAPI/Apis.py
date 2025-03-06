import sqlite3
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys  # Interações com o teclado
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
import time

def login_to_erp(username, password):
    """
    Logs into the ERP system using the provided username and password.
    """
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--headless")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--remote-debugging-port=9222")

    service = Service('/usr/local/bin/chromedriver')

    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get("https://intranet.epema.com.br/portal/#/")
        driver.implicitly_wait(5)
        print("Página carregada:", driver.title)

        usuario = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "rr1_padm086Login-0"))
        )
        usuario.send_keys(username)

        senha = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "rr1_padm086Senha-0"))
        )
        senha.send_keys(password)
        senha.send_keys(Keys.RETURN)

        print("Login realizado com sucesso!")
        return driver

    except Exception as e:
        print("Erro ao fazer login:", e)
        return None


def navigate_to_service_queue(driver):
    """
    Navigate to the service queue tab in the ERP system.
    """
    try:
        service_queue_tab = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.LINK_TEXT, "Fila de Ordens de Serviço"))
        )
        service_queue_tab.click()
        print("Navegou para a aba Fila de Ordens de Serviço")
    except Exception as e:
        print(f"Erro ao navegar para a aba Fila de Ordens de Serviço: {e}")


def extract_service_queue_data(driver):
    """
    Extract data from the service queue tab.
    """
    try:
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "r-datagrid-data")))

        data_rows = driver.find_elements(By.CLASS_NAME, "r-datagrid-data")

        extracted_data = []
        for row in data_rows:
            row_data = row.text.splitlines()
            extracted_data.append(row_data)

        print("Extração de dados bem-sucedida.")
        return extracted_data

    except Exception as e:
        print(f"Erro ao extrair dados: {e}")
        return None


def save_data_to_db(data, db_name="erp_data.db"):
    """
    Saves the extracted data to an SQLite database.

    Args:
        data (list): The data to be saved.
        db_name (str): The name of the database file.
    """
    if data is None:
        print("No data to save.")
        return
    conn = None # Added conn to finally scope
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS service_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                col1 TEXT,
                col2 TEXT,
                col3 TEXT,
                col4 TEXT,
                col5 TEXT
            )
        ''')

        for row in data:
            if len(row) == 5:
                cursor.execute("INSERT INTO service_queue (col1, col2, col3, col4, col5) VALUES (?, ?, ?, ?, ?)", row)
            elif len(row) == 4:
                cursor.execute("INSERT INTO service_queue (col1, col2, col3, col4) VALUES (?, ?, ?, ?)", row)
            elif len(row) == 3:
                cursor.execute("INSERT INTO service_queue (col1, col2, col3) VALUES (?, ?, ?)", row)
            elif len(row) == 2:
                cursor.execute("INSERT INTO service_queue (col1, col2) VALUES (?, ?)", row)
            elif len(row) == 1:
                cursor.execute("INSERT INTO service_queue (col1) VALUES (?)", row)

        conn.commit()
        print(f"Data successfully saved to {db_name}")

    except Exception as e:
        print(f"Error saving data to database: {e}")

    finally:
        if conn:
            conn.close()


def main():
    username = "8832"
    password = "101203"
    driver = None # Added driver to finally scope

    try:
        driver = login_to_erp(username, password)

        if driver:
            time.sleep(10)
            navigate_to_service_queue(driver)
            extracted_data = extract_service_queue_data(driver)
            save_data_to_db(extracted_data)
    except Exception as e:
        print(f"An error occurred in main: {e}")
    finally:
      if driver:
        driver.quit()

if __name__ == "__main__":
    main()
