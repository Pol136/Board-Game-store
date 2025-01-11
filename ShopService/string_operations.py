def write_string_to_file(filename, text_string):
    try:
        with open(filename, 'w', encoding='utf-8') as file: # 'w' перезапишет файл
            file.write(text_string)
    except Exception as e:
        print(f"Ошибка при записи в файл: {e}")


def read_string_from_file(filename):
       try:
           with open(filename, 'r', encoding='utf-8') as file:
                file_content = file.read()
           return file_content
       except FileNotFoundError:
           return None
       except Exception as e:
            return None
