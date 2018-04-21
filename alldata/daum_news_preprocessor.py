import sys
import re

"""Use for preprocessing daum news data when you wnat to get only the titles and the body"""

try:
	var = sys.argv[1]
	fp = open(var, 'r', encoding='utf-8')
except:
	print("Usage: python daum_news_preprocessor [news file]")
	exit()

articles = fp.read().split('\n')

preprocessed_articles = ''
sentence_num = 0

WEB_URL_REGEX = r"""(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@)))"""


for article in articles:
	if len(article.split("|$|")) != 6:
		continue

	article_body = article.split("|$|")[2]
	if "◆" in article_body or "▲" in article_body:
		print("weird char")
		continue
	article_title = article.split("|$|")[1]

	article_body = re.sub(r'[\w\.-]+@[\w\.-]+', '', article_body)
	article_body = re.sub(r'■', '', article_body)
	article_body = re.sub(r'●', '', article_body)
	article_body = re.sub(r'#', '', article_body)
	article_body = re.sub(r'…', '.', article_body)
	article_body = re.sub(WEB_URL_REGEX, '', article_body)

	sentences = re.split('\.|\?|\!', article_body)
	sentences = sentences[0:len(sentences)-1]

	article_body = ''
	for sentence in sentences:
#print("sentence: ", sentence, "\n")

		if 'ⓒ' in sentence or '/' in sentence or '▶' in sentence or '〓' in sentence or '|' in sentence or '★' in sentence or '☆' in sentence or '=' in sentence or "사진제공" in sentence or "tvm" in sentence:
			continue

		sentence_num += 1

		sentence = re.sub(r'\[.*?\]', '', sentence)
		sentence = re.sub(r'\(.*?\)', '', sentence)
		sentence = re.sub(r'\【.*?\】', '', sentence)
		sentence = re.sub(r'\<.*?\>', '', sentence)
		sentence = re.sub(' +', ' ', sentence)
		article_body += sentence + '.'

#	preprocessed_articles += re.sub(r'[\w\.-]+@', '', article_body)
#	preprocessed_articles += re.sub(r'@+[\w\.-]', '', article_body)
	preprocessed_articles += article_body + "\n"
	print(article_body)


preprocessed_fp = open("preprocessed_" + var, 'w', encoding='utf-8')
preprocessed_fp.write(preprocessed_articles)
preprocessed_fp.close()
