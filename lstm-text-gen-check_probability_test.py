import codecs
from bs4 import BeautifulSoup
from keras.models import Sequential
from keras.layers import Dense, Activation, Dropout
from keras.layers import LSTM
from keras.optimizers import RMSprop
from keras.utils.data_utils import get_file
import numpy as np
import random, sys

import hgtk

import os
import sqlite3

if not os.path.exists("data"):
	print("No directory \"data\"")
	exit()

conn = sqlite3.connect("phoneme_db.db")
cur = conn.cursor()

sql_create_phoneme_table = """CREATE TABLE IF NOT EXISTS phoneme (
								id integer PRIMARY KEY, 
								decomposed text, 
								year integer, 
								month text
							);"""
cur.execute(sql_create_phoneme_table)

files = [f for f in os.listdir("data") if os.path.isfile(os.path.join("data", f))]

#fp = codecs.open("./daumnews2017.txt", "r", encoding="utf-8")
#soup = BeautifulSoup(fp, "html.parser")
#body = soup.select_one("body")
#text = fp.read()

#make news id	
month_vec = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
newsstr = ''
for fi in files:
	filedate = fi.split('_')[3]
	year = int(filedate[0:4])
	month = int(filedate[4:6])
	month_vec[month - 1] = 1
	
	fp = open("./data/" + fi, 'r', encoding='utf-8')
	newsstr += fp.read()
	fp.close()
	text = newsstr

cur.execute('''SELECT * FROM phoneme WHERE year=? AND month=?''',
				(year, str(month_vec),)
			)
rows = cur.fetchall()

conn.commit()

print("year: ", year)
print("month: ", month_vec)

#if news id is not in phoneme	
if len(rows) is 0:
	text_decomposed = hgtk.text.decompose(text)
	#save text and decomposed
	cur.execute('''INSERT INTO phoneme(decomposed, year, month)
					VALUES(?, ?, ?)''',
					(text_decomposed, year, str(month_vec))
	)
	conn.commit()
else:
	text_decomposed = rows[0][1]

cur.close()
conn.close()


text = text_decomposed

consonant = ['ㄱ', 'ㄴ', 'ㄷ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅅ', 'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ', 'ㄲ', 'ㄸ', 'ㅃ', 'ㅆ', 'ㅉ']

#fp = codecs.open("./BEXX0003.txt", "r", encoding="utf-16")
#soup = BeautifulSoup(fp, "html.parser")
#body = soup.select_one("body")
#text = body.getText() + " "
print('코퍼스의 길이: ', len(text))


# 문자를 하나하나 읽어 들이고 ID 붙이기
chars = sorted(list(set(text)))
print('사용되고 있는 문자의 수:', len(chars))
char_indices = dict((c, i) for i, c in enumerate(chars)) # 문자 → ID
indices_char = dict((i, c) for i, c in enumerate(chars)) # ID → 문자
# 텍스트를 maxlen개의 문자로 자르고 다음에 오는 문자 등록하기

seed = hgtk.text.decompose("나는 밥을 먹었다. ")

maxlen = len(seed)
step = 12
sentences = []
next_chars = []

for i in range(0, len(text) - maxlen, step):
	sentences.append(text[i: i + maxlen])
	next_chars.append(text[i + maxlen])

print('학습할 구문의 수:', len(sentences))
print('텍스트를 ID 벡터로 변환합니다...')

X = np.zeros((len(sentences), maxlen, len(chars)), dtype=np.bool)
y = np.zeros((len(sentences), len(chars)), dtype=np.bool)
for i, sentence in enumerate(sentences):
	for t, char in enumerate(sentence):
		X[i, t, char_indices[char]] = 1
	y[i, char_indices[next_chars[i]]] = 1

# 모델 구축하기(LSTM)
print('모델을 구축합니다...')
model = Sequential()
model.add(LSTM(128, input_shape=(maxlen, len(chars))))
model.add(Dense(len(chars)))
model.add(Activation('softmax'))
optimizer = RMSprop(lr=0.01)
model.compile(loss='categorical_crossentropy', optimizer=optimizer)

# 후보를 배열에서 꺼내기
def sample(preds, temperature=1.0):
	preds = np.asarray(preds).astype('float64')
	preds = np.log(preds) / temperature
	exp_preds = np.exp(preds)
	preds = exp_preds / np.sum(exp_preds)
	probas = np.random.multinomial(1, preds, 1)
	sortd = np.argsort(probas)[0][::-1]
	return sortd[0:20]

# 학습시키고 텍스트 생성하기 반복

print()
print('-' * 50)

model.fit(X, y, batch_size=128, nb_epoch=1, verbose=1) # 

# 임의의 시작 텍스트 선택하기
start_index = random.randint(0, len(text) - maxlen - 1)

print()
print('--- 다양성 = ', )

generated = ''
sentence = seed #text[start_index: start_index + maxlen]
generated += sentence
print('--- 시드 = "' + sentence + '"')
sys.stdout.write(generated)

# 시드를 기반으로 텍스트 자동 생성
for i in range(1600):
	x = np.zeros((1, maxlen, len(chars)))
	for t, char in enumerate(sentence):
		x[0, t, char_indices[char]] = 1.

	# 다음에 올 문자를 예측하기
	preds = model.predict(x, verbose=0)[0]
	next_indice = sample(preds)

	collection = []
	for index in next_indice:
		collection.append((indices_char[index], preds[index]))
	print(collection)

	if sentence[len(sentence)-1] == ' ' or sentence[len(sentence)-1] == 'ᴥ':
		breakflag = False
		for char, proba in collection:
			if char in consonant:
				next_char = char
				breakflag = True
				break
		
		if breakflag is False:
			next_index = collection[0][0]
			#next_char = indices_char[next_index]

	else:
		next_char = collection[0][0]
		

	# 출력하기
	generated += next_char
	sentence = sentence[1:] + next_char
	#sys.stdout.write(next_char)
	sys.stdout.flush()

print(generated)
print()


