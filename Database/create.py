import sqlite3
import json


def create_word_database(json_file, db_name):
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS words (
            word TEXT PRIMARY KEY,
            oldword TEXT,
            strokes TEXT,
            pinyin TEXT,
            radicals TEXT,
            explanation TEXT,
            more TEXT
        )
    ''')

    with open(json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)
        total = len(data)
        print(f'Inserting {total} records into database {db_name}')
        ignored = 0
        for index, item in enumerate(data, start=1):
            try:
                cursor.execute('''
                    INSERT INTO words (word, oldword, strokes, pinyin, radicals, explanation, more)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    item['word'],
                    item['oldword'],
                    item['strokes'],
                    item['pinyin'],
                    item['radicals'],
                    item['explanation'],
                    item['more']
                ))
            except sqlite3.IntegrityError:
                ignored += 1
            print(f'Processed {index}/{total} records', end='\r')

    connection.commit()
    connection.close()
    print(f'\nIgnored {ignored} duplicate records.')



def create_ci_database(json_file, db_name):
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cis (
            ci TEXT PRIMARY KEY,
            explanation TEXT
        )
    ''')

    with open(json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)
        total = len(data)
        print(f'Inserting {total} records into database {db_name}')
        ignored = 0
        for index, item in enumerate(data, start=1):
            try:
                cursor.execute('''
                    INSERT INTO cis (ci, explanation)
                    VALUES (?, ?)
                ''', (
                    item['ci'],
                    item['explanation']
                ))
            except sqlite3.IntegrityError:
                ignored += 1
            print(f'Processed {index}/{total} records', end='\r')

    connection.commit()
    connection.close()
    print(f'\nIgnored {ignored} duplicate records.')



def create_idiom_database(json_file, db_name):
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS idioms (
            word TEXT PRIMARY KEY,
            derivation TEXT,
            example TEXT,
            explanation TEXT,
            pinyin TEXT,
            abbreviation TEXT
        )
    ''')

    with open(json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)
        total = len(data)
        print(f'Inserting {total} records into database {db_name}')
        ignored = 0
        for index, item in enumerate(data, start=1):
            try:
                cursor.execute('''
                    INSERT INTO idioms (word, derivation, example, explanation, pinyin, abbreviation)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    item['word'],
                    item['derivation'],
                    item['example'],
                    item['explanation'],
                    item['pinyin'],
                    item['abbreviation']
                ))
            except sqlite3.IntegrityError:
                ignored += 1
            print(f'Processed {index}/{total} records', end='\r')

    connection.commit()
    connection.close()
    print(f'\nIgnored {ignored} duplicate records.')


def create_abbre_database(json_file, db_name):
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()

    cursor.execute('''
            CREATE TABLE IF NOT EXISTS abbres (
                abbreviation TEXT PRIMARY KEY,
                full_form TEXT
            )
        ''')

    with open(json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)
        total = len(data)
        print(f'Inserting {total} records into database {db_name}')
        ignored = 0
        for index, item in enumerate(data, start=1):
            try:
                cursor.execute('''
                        INSERT INTO abbres (abbreviation, full_form)
                        VALUES (?, ?)
                    ''', (
                    item['abbreviation'],
                    item['full_form']
                ))
            except sqlite3.IntegrityError:
                ignored += 1
            print(f'Processed {index}/{total} records', end='\r')

    connection.commit()
    connection.close()
    print(f'\nIgnored {ignored} duplicate records.')



def create_freq_database(json_file, db_name):
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()

    cursor.execute('''
            CREATE TABLE IF NOT EXISTS freq (
                ch_char TEXT PRIMARY KEY,
                char_freq TEXT
            )
        ''')

    with open(json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)
        total = len(data)
        print(f'Inserting {total} records into database {db_name}')
        ignored = 0
        for index, item in enumerate(data, start=1):
            try:
                cursor.execute('''
                        INSERT INTO freq (ch_char, char_freq)
                        VALUES (?, ?)
                    ''', (
                    item['汉字'],
                    item['累计频率(%)']
                ))
            except sqlite3.IntegrityError:
                ignored += 1
            print(f'Processed {index}/{total} records', end='\r')

    connection.commit()
    connection.close()
    print(f'\nIgnored {ignored} duplicate records.')


def create_word_freq_database(file_news, file_novels, db_name):
    # 创建数据库连接和游标
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()

    # 创建表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS word_freq (
            bigram TEXT PRIMARY KEY,
            freq INTEGER
        )
    ''')
    print(f'Created table word_freq in database {db_name}')
    # 读取文件并计算频率平均值
    bigram_freq = {}

    for file_name in [file_news, file_novels]:
        print(f'Reading file {file_name}')
        with open(file_name, 'r', encoding='utf-8') as file:
            line_num = 0
            for line in file:
                parts = line.strip().split('\t')
                # print(f'parts: {parts}')
                line_num += 1
                if len(parts) >= 3 and line_num > 2:
                    bigram = parts[1]
                    freq = int(parts[2])
                    bigram_freq[bigram] = [freq]
                    # print(f'bigram: {bigram}, freq: {freq}')

    print(f'Finished reading files. Total {len(bigram_freq)} bigrams.')

    # 插入数据到数据库
    ignored = 0
    for bigram in bigram_freq:
        try:
            cursor.execute('''
                INSERT INTO word_freq (bigram, freq)
                VALUES (?, ?)
            ''', (
                bigram,
                bigram_freq[bigram][0]
            ))
        except sqlite3.IntegrityError:
            ignored += 1

    # 提交事务并关闭连接
    connection.commit()
    connection.close()

    print(f'Finished processing. Ignored {ignored} duplicate records.')

def create_levels_database(json_file, db_name):
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()

    cursor.execute('''
            CREATE TABLE IF NOT EXISTS levels (
                word TEXT PRIMARY KEY,
                word_level TEXT
            )
        ''')

    with open(json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)
        total = len(data)
        print(f'Inserting {total} records into database {db_name}')
        ignored = 0
        for index, item in enumerate(data, start=1):
            try:
                cursor.execute('''
                        INSERT INTO levels (word, word_level)
                        VALUES (?, ?)
                    ''', (
                    item['idiom'],
                    item['level']
                ))
            except sqlite3.IntegrityError:
                ignored += 1
            print(f'Processed {index}/{total} records', end='\r')

    connection.commit()
    connection.close()
    print(f'\nIgnored {ignored} duplicate records.')



def create_levels_database(db_name):
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()

    cursor.execute('''
            CREATE TABLE IF NOT EXISTS sims (
                word TEXT PRIMARY KEY,
                similarity DOUBLE
            )
        ''')

    connection.commit()
    connection.close()


def print_database_info(db_name, table_name='words'):
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()

    cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
    count = cursor.fetchone()[0]

    print(f'\nDatabase {db_name} contains {count} records.')

    connection.close()




if __name__ == '__main__':

    # json_file = r"../Datasets/ref_tables/word.json"
    # db_name = r'./DBs/words.db'
    #
    # create_word_database(json_file, db_name)
    # print_database_info(db_name, 'words')

    # json_file = r"../Datasets/ref_tables/ci.json"
    # db_name = r'./DBs/cis.db'
    #
    # create_ci_database(json_file, db_name)
    # print_database_info(db_name, 'cis')

    # json_file = r"../Datasets/ref_tables/idiom.json"
    # db_name = r'./DBs/idioms.db'
    # create_idiom_database(json_file, db_name)
    # print_database_info(db_name, 'idioms')

    # json_file = r"../Datasets/ref_tables/abbre/abbres.json"
    # db_name = r'./DBs/abbres.db'
    # create_abbre_database(json_file, db_name)
    # print_database_info(db_name, 'abbres')

    # json_file = r"../Methods/HSK_standard/词频.json"
    # db_name = r'./DBs/freq.db'
    # create_freq_database(json_file, db_name)
    # print_database_info(db_name, 'freq')

    # json_file = r"../Methods/HSK_standard/词语.json"
    # db_name = r'./DBs/levels.db'
    # create_levels_database(json_file, db_name)
    # print_database_info(db_name, 'levels')

    db_name = r'./DBs/sims.db'
    create_levels_database(db_name)
    print_database_info(db_name, 'sims')

    # # 100
    # file_news = r"../Datasets/ref_tables/Bigram/Bigram (News) .txt"
    # file_novels = r"../Datasets/ref_tables/Bigram/Bigram (Novels).txt"
    # db_name = r'./DBs/word_freq.db'
    # create_word_freq_database(file_news, file_novels, db_name)
    # print_database_info(db_name, 'word_freq')






