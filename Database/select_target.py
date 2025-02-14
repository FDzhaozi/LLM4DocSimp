import sqlite3


def query_word(db_name, word):
    # 连接到数据库
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()

    # 查询数据
    cursor.execute('SELECT * FROM words WHERE word = ?', (word,))
    result = cursor.fetchone()

    # 关闭连接
    connection.close()

    # 如果找到结果，返回字典
    if result:
        return {
            "word": result[0],
            "oldword": result[1],
            "strokes": result[2],
            "pinyin": result[3],
            "radicals": result[4],
            "explanation": result[5],
            "more": result[6]
        }
    else:
        return None


def query_ci(db_name, ci):
    # 连接到数据库
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()

    # 查询数据
    cursor.execute('SELECT * FROM cis WHERE ci = ?', (ci,))
    result = cursor.fetchone()

    # 关闭连接
    connection.close()

    # 如果找到结果，返回字典
    if result:
        return {
            "ci": result[0],
            "explanation": result[1]
        }
    else:
        return None


def query_level(db_name, ci):
    # 连接到数据库
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()

    # 查询数据
    cursor.execute('SELECT * FROM levels WHERE word = ?', (ci,))
    result = cursor.fetchone()

    # 关闭连接
    connection.close()

    # 如果找到结果，返回字典
    if result:
        return {
            "word": result[0],
            "level": result[1]
        }
    else:
        return None

def query_idiom(db_name, word):
    # 连接到数据库
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()

    # 查询数据
    cursor.execute('SELECT * FROM idioms WHERE word = ?', (word,))
    result = cursor.fetchone()

    # 关闭连接
    connection.close()

    # 如果找到结果，返回字典
    if result:
        return {
            "word": result[0],
            "derivation": result[1],
            "example": result[2],
            "explanation": result[3],
            "pinyin": result[4],
            "abbreviation": result[5]
        }
    else:
        return None


def query_abbre(db_name, abbre):
    # 连接到数据库
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()

    # 查询数据
    cursor.execute('SELECT * FROM abbres WHERE abbreviation = ?', (abbre,))
    result = cursor.fetchone()

    # 关闭连接
    connection.close()

    # 如果找到结果，返回字典
    if result:
        return {
            "abbreviation": result[0],
            "full_form": result[1]
        }
    else:
        return None


def query_freq(db_name, ch_char):
    # 连接到数据库
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()

    # 查询数据
    cursor.execute('SELECT * FROM freq WHERE ch_char = ?', (ch_char,))
    result = cursor.fetchone()

    # 关闭连接
    connection.close()

    # 如果找到结果，返回字典
    if result:
        return {
            "ch_char": result[0],
            "char_freq": result[1]
        }
    else:
        return None


def query_word_freq(db_name, word):
    # 连接到数据库
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()

    # 查询数据
    cursor.execute('SELECT * FROM word_freq WHERE bigram = ?', (word,))
    result = cursor.fetchone()

    # 关闭连接
    connection.close()

    # 如果找到结果，返回字典
    if result:
        return {
            "bigram": result[0],
            "freq": result[1]
        }
    else:
        return None


def insert_into_sims(db_name, word, sim_value):
    # 连接到数据库
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()

    # 插入数据
    cursor.execute('INSERT INTO sims VALUES (?, ?)', (word, sim_value))
    print('插入一条相似度数据！')

    # 提交更改
    connection.commit()

    # 关闭连接
    connection.close()


def query_sims(db_name, word):
    # 连接到数据库
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()

    # 查询数据
    cursor.execute('SELECT * FROM sims WHERE word = ?', (word,))
    result = cursor.fetchone()

    # 关闭连接
    connection.close()

    # 如果找到结果，返回字典
    if result:
        return {
            "word": result[0],
            "sim_value": result[1]
        }
    else:
        return None

if __name__ == '__main__':
    # db_name = r'./DBs/words.db'
    # result = query_word(db_name, '叱')
    # print(result)

    # db_name = r'./DBs/cis.db'
    # result = query_ci(db_name, '舆情')
    # print(result)

    # db_name = r'./DBs/idioms.db'
    # result = query_idiom(db_name, '完璧归赵')
    # print(result)

    # db_name = r'./DBs/abbres.db'
    # result = query_abbre(db_name, '婉拒')
    # print(result)

    # db_name = r'./DBs/freq.db'
    # result = query_freq(db_name, '人')
    # print(result)
    # result = query_freq(db_name, '耄')
    # print(result)

    # db_name = r'./DBs/levels.db'
    # result = query_level(db_name, '激烈')
    # print(result)

    db_name = r'./DBs/sims.db'
    # insert_into_sims(db_name, '方登朝', 1.62)
    result = query_sims(db_name, '弯弓')
    print(result)
    print(result['sim_value'])
    print(type(result['sim_value']))

    # db_name = r'./DBs/word_freq.db'
    # result = query_word_freq(db_name, '犀利')
    # print(result)


