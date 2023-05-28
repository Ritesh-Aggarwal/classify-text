#!/usr/bin/env python
import requests
import csv
import re
from bs4 import BeautifulSoup
from bs4 import SoupStrainer

f = csv.writer(open('data_stackoveflow_2.csv', 'w'))
f.writerow(['URL', 'Text', 'Code Start Indices (Inc)', 'Code End indices (Exc)'])
url_index_counter = 53903512
url = "https://stackoverflow.com/questions/"
no_error_code = 200
data_written_to_file = 0

post_contents = SoupStrainer('div', class_ = "post-text")

regex = re.compile("<code>((.*?(\\n).*?)*.*?)</code>")#("<code>((.*)(\\n)*)*(.*?)</code>")#"<code>(.*?)<\/code>")

for i in range (0, 1000):
	num = url_index_counter + i
	url_read = url + str(num)
	print("Reading from URL : ", url_read)
	page = requests.get(url_read)
	
	# check if page exists	
	if(page.status_code != no_error_code):
		print ("Error")		
		continue
	
	soup = BeautifulSoup(page.text, 'html.parser')
	question_contents = soup.find_all(post_contents)

	# to remove all blockquotes as they don't give correct code tags!	
	for blockquote in soup("blockquote"):
    		blockquote.decompose()
	
	## regex to get the code tagged text
	for ques in question_contents:
		print("---------")
		print(ques.contents)
		print("---------")
		for html_text in ques.contents:
			html_text = str(html_text)
			
			start = 0
			post_content_clean = ""
            label = 5
            
			## list to store all the starting and ending indices of the post
			code_range_start_list = []
			code_range_end_list = []
			if(len(html_text)<3):
				continue

			# Remove bottom links
			#last_links = BeautifulSoup(html_text, 'html.parser').find('blockquote')
			#last_links.decompose()
			#print(html_text)
			for m in regex.finditer(html_text):
				print ("MATCH START : ", m.start())
				print ("MATCHED LENGTH : " , len(m.group()))
				print ("MATCHED GROUP : " , m.group())
				

				string_code = str(m.group())
				string_text = html_text[start:m.start()]
			
				## update for next starting index
				start = m.start() + len(m.group())

				clean_code_without_html = BeautifulSoup(string_code, 'html.parser').get_text();
				clean_text_without_html = BeautifulSoup(string_text, 'html.parser').get_text();
			
				post_content_clean = post_content_clean + (clean_text_without_html)
				code_start_index = len(post_content_clean) #inclusive

				code_end_index = code_start_index + len(clean_code_without_html) #exclusive
				post_content_clean = post_content_clean + (clean_code_without_html)
			
				code_range_start_list.append(code_start_index)
				code_range_end_list.append(code_end_index)
			
			#parsing the remaining text
			string_text = html_text[start:]
			clean_text_without_html = BeautifulSoup(string_text, 'html.parser').get_text();
			post_content_clean = post_content_clean + (clean_text_without_html)
			print("FINAL CONTENT ------> ", post_content_clean, " : ", label)
			if(len(post_content_clean)>3):
                if(len(code_range_start_list) == 0):
                    label = 0
                elif (len(code_range_start_list)==1 and code_range_start_list[0]==0 and
                      code_range_end_list[0] == len(post_content_clean)):
                    label = 2
                else:
                    label = 1
				f.writerow([url_read, post_content_clean, code_range_start_list, code_range_end_list, label])
				data_written_to_file = data_written_to_file + 1
	
	#print(question_contents[0].get_text())
	if (data_written_to_file > 5000):
		break

print("Pages read : ", data_written_to_file)
