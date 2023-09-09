"""
SRT-TS Transcript Software
AI's transcription is not perfect and hence must be proofread by a human transcriber
who needs AI's accuracy in fetching names, places and orgs.
AI Whisper Large-CPP prefers AUDIO in m4a-format

TODO: Add a GUI for SRT file input, tags for relabeling entries, treeview etc...
"""


def main():
	filename = "tagged_TPPart3_126268_137.srt"
	inputfilename = "./input/" + filename
	outputfilename = "./output/" + filename
	content_in_single_line = clean_SRT_and_combine_all_texts_in_one(inputfilename)
	outputfilename = relabel_speakers_in_clean_SRT_txt(content_in_single_line, outputfilename)
	print("File created: " + outputfilename)
	

def relabel_speakers_in_clean_SRT_txt(content_in_single_line, outputfilename):
	# Dictionary of tags to be re-labeled:
	tags_dict = {  # \n for Single-spaced, \n\n for Double-spaced
		'dd1': '\n\nMan 1:',
		'dd2': '\n\nMan 2:',
		'dd3': '\n\nMan 3:',
		'dd4': '\n\nMan 4:',
		'ff1': '\n\nWoman 1:',
		'ff2': '\n\nWoman 2:',
		'ff3': '\n\nWoman 3:',
		'ff4': '\n\nWoman 4:',
		'vd1': '\n\n[video playback]',
		'vd2': '\n\n[video playback ends]',
		'vv1': '\n\n[voice 1 in video]',
		'vv2': '\n\n[voice 2 in video]',
		'vm1': '\n\n[man in video]',
		'vm2': '\n\n[man 2 in video]',
		'vw1': '\n\n[woman in video]',
		'vw2': '\n\n[woman 2 in video]',
		'vi1': '\n\n[indistinct talking in video]',
		'tv1': '\n\n[TV]',
		'bc1': '\n\n[background conversations]',
		'bg1': '\n\n[background sounds only]',
		'bn1': '\n\n[background noise]',
		'it1': '\n\n[indistinct talking]',
		'ct1': '[crosstalk]',
		'fo1': '[foreign word]',
		'fo2': '[foreign words]',
		'in1': '[inaudible]',
		'in2': '[inaudible]',  # For two consecutive in1 but unique timestamps
		'in3': '\n\n[indiscernible]',
		'la1': '[laughter]',
		'la2': '\n\n[laughter]',  # For group laughter
		'pa1': '[pause]',
		'pa2': '\n\n[pause]',
		'si1': '[silence]',
		'si2': '\n\n[silence]',
		'si3': '\n\n[silence]',  # For two consecutive si2 but unique timestamps
		'br1': '\n\n',
		'en1': '\n\n[END]',
	}
	
	new_content_relabeled_speakers = [[]]
	for each_line in content_in_single_line:
		new_content_relabeled_speakers.append(each_line.split())
	time_tag = current_tag = previous_tag = new_label = ''
	for index_of_each_list in range(len(new_content_relabeled_speakers)):
		for index_of_per_string in range(len(new_content_relabeled_speakers[index_of_each_list])):
			# Re-group each string with spaces and a new line at their end:
			if index_of_per_string < len(new_content_relabeled_speakers[index_of_each_list]):
				string_value_of_second_index \
					= new_content_relabeled_speakers[index_of_each_list][index_of_per_string] \
					= new_content_relabeled_speakers[index_of_each_list][index_of_per_string] + ' '
			else:
				string_value_of_second_index \
				= new_content_relabeled_speakers[index_of_each_list][index_of_per_string] \
				= new_content_relabeled_speakers[index_of_each_list][index_of_per_string] + '\n'
			# Check if it's a time code (format: t12-t12345) or tag code (present in tags dictionary)
			if timestamp(string_value_of_second_index) != '':
				# If it is not empty because it is a time tag, then empty it as it will be added later.
				time_tag = timestamp(string_value_of_second_index)
				new_content_relabeled_speakers[index_of_each_list][index_of_per_string] = ''
			# Else if it is a tag code (present in tags dictionary)
			else:
				# Slices the FIRST THREE bytes in each string and place them in tag_code
				tag_code = string_value_of_second_index[0:3]
				the_rest_of_string = string_value_of_second_index[3:]
				if '[?]' in tag_code and time_tag != '':
					# Combine [(1:43:00)] and [?] into [1:43:00 ?]
					time_extracted = time_tag[2:-2]
					new_label = '[' + time_extracted + ' ?]'
					time_tag = ''
					new_content_relabeled_speakers[index_of_each_list][index_of_per_string] \
						= new_label + the_rest_of_string
				elif '. ' == tag_code[0:2] and (' ' or '\n') in new_content_relabeled_speakers[index_of_each_list-1][-1]:
					new_content_relabeled_speakers[index_of_each_list][index_of_per_string].replace('. ', '')
					new_content_relabeled_speakers[index_of_each_list-1][-1].replace('\n', '.')
					new_content_relabeled_speakers[index_of_each_list-1][-1].replace(' ', '.')
				elif 'br1' in tag_code:
					new_label = tags_dict[tag_code]
					new_content_relabeled_speakers[index_of_each_list][index_of_per_string] \
						= new_label + the_rest_of_string
				elif tag_code in tags_dict.keys():
					current_tag = tag_code
					if previous_tag == '':
						# If it's the first time, remove \n\n
						new_label = tags_dict[current_tag]
						if '\n\n' in new_label[:2] and time_tag != '':
							new_label = new_label.replace('\n\n', time_tag + ' ')
							time_tag = ''
						else: new_label = new_label.replace('\n\n', time_tag + '')
					elif previous_tag != current_tag:
						# If it's a different tag_code
						new_label = tags_dict[current_tag]
					else:
						# with the same tag_code, empty just the code
						new_label = ''
					if new_label[0:2] == '\n\n' and time_tag != '':
						# Insert timestamp at the beginning just after \n\n:
						new_label = new_label.replace('\n\n', '\n\n' + time_tag + ' ')
						time_tag = ''
					elif '[inaudible]' in new_label and time_tag != '':
						# Combine [(1:43:00)] and [inaudible] into [1:43:00 inaudible]
						time_extracted = time_tag[2:-2]
						new_label = new_label.replace('[inaudible]', '[' + time_extracted + ' inaudible]')
						time_tag = ''
					
					previous_tag = current_tag
					new_content_relabeled_speakers[index_of_each_list][index_of_per_string] \
						= new_label + the_rest_of_string
			# Make sure there is no extra space between strings:
			if '  ' in new_content_relabeled_speakers[index_of_each_list]:
				new_content_relabeled_speakers[index_of_each_list] \
					= new_content_relabeled_speakers[index_of_each_list].replace('  ', ' ')
	outputfilename = outputfilename.replace(outputfilename[-4:], '_trimmed.txt')
	with open(outputfilename, 'w') as f:
		for each_list in new_content_relabeled_speakers:
			for each_string in each_list:
				f.write(each_string)
	return outputfilename


def clean_SRT_and_combine_all_texts_in_one(inputfilename):
    print("Cleaning the SRT file and combining all texts in one line...")
    with open(inputfilename, 'r') as f:
        content = f.readlines()
    content_in_single_line = ['']
    content[0] = content[1] = ''
    for each_line in content:
        new_line = ''
        line_has_alpha_or_punctuation = False
        for byte in each_line: # Remove lines without alpha bytes and...
            new_line = new_line + byte
            if byte.isalpha() or (byte in ',.?' and ':' not in each_line):
                line_has_alpha_or_punctuation = True  # ... combine all lines in one that is...
        if line_has_alpha_or_punctuation:				# ... not like: 00:00:05,650 --> 00:00:11,000
            content_in_single_line.append(new_line)
    return content_in_single_line


def timestamp(string_value='t143'):
	# t124 = 01:24, t1143 = 11:43 ---> Sample format
	timestamp_string = ''
	count_digits = 0
	if string_value != '':  # If it's not empty:
		if string_value[0] == 't' and string_value[1:3].isdigit():
			for item in string_value:  # How many digits are there?
				if item.isdigit(): count_digits += 1
			if count_digits == 2:
				timestamp_string = '[(0:' + string_value[1:3] + ')]'
			elif count_digits == 3:
				timestamp_string = '[(' + string_value[1] + ':' + string_value[2:4] + ')]'
			elif count_digits == 4:
				timestamp_string = '[(' + string_value[1:3] + ':' + string_value[3:5] + ')]'
			elif count_digits == 5:
				timestamp_string = '[(' + string_value[1] + ':' + string_value[2:4] + ':' + string_value[4:6] + ')]'
	return timestamp_string
	
	
if __name__ == "__main__":	
	run_program = 'y'
	while run_program.lower() != 'q':
		main()
		run_program = input("\nPress 'q' to EXIT PROGRAM or other keys to continue: ")
