import re
import datetime
import syslog

#   message[0] # timestamp "%Y.%m.%d"
#   message[1] # timestamp "%H:%M"
#   message[2] # type
#   message[3] # severity
#   message[4] # set the uptime
#   message[5] # set the message
#   message[6] # set the full message

def parse_syslog_message(message) -> list[str]:

	#message = '<30>Jan 19 17:00:00 [kern.uptime.filer:info]:   5:00pm up  4 days,  5:39 241578229 NFS ops, 4430 CIFS ops, 0 HTTP ops, 0 FCP ops, 0 iSCSI ops'
	#message = '<29>Jan 15 20:25:12 [asup.smtp.sent:notice]: System Notification mail sent: System Notification from filer (USER_TRIGGERED (do)) INFO'

	# the regex creates groups based on ontap 7 standard syslog messages
	the_regex: str = r'<.+>(.+?(?=.\[))..(.+?(?=.\:).).(.*?)(\]:\s+)(\D)?(?(5)(.*$)|.+(up)(\s*)(.+?(?=,))(.+?(?=:).\d*.)(.*))'

	target: list[str] = ['' for x in range(0, 11)]	# initaialize array, we need 12 elements 
	final:  list[str] = ['' for x in range(0, 7)]	# initialize final array, we need 8 elements

	# create a regex grouped response, we expect max 12 groups (0-11)
	m = re.search(the_regex, message)

	# if there is a regex result
	if m:
		for x in range(0, 11):
			if m.group(x) is not None:
				target[x] = str(m.group(x))
			# otherweise fill ist with an empty string

	#	m.group(0)		# full message
	#	m.group(1)		# timestamp
	#	m.group(2)		# short
	#	m.group(3)		# severity 
	#	m.group(4)		# not of interest
	#	m.group(5)		# if 7 is empty, message = 5+6
	#	m.group(6)		# if 7 is empty, message = 5+6
	#	m.group(7)		# empty or the word 'up'
	#	m.group(8)		# not of interest
	#	m.group(9)		# number of days (5 days)
	#	m.group(10)		# not of interest
	#	m.group(11)		# final message

	#	final[0]		# timestamp "%Y.%m.%d" | raw timestamp in case of an error
	#	final[1]		# timestamp "%H:%M"    | empty
	#	final[2]		# short
	#	final[3]		# severity
	#	final[4]		# uptime               | empty
	#	final[5]		# message
	#	final[6]		# full message

	# add year: Jan 19 17:00:00 --> 2023 Jan 19 17:00:00
	target[1] = str(datetime.datetime.now().year) + ' ' + target[1]

	# there can be cases that strptime fails and would kill the program
	# but the string causing the issue is not printed therefore using try/except
	try:
		t = datetime.datetime.strptime(target[1], "%Y %b %d %H:%M:%S")
		final[0] = t.strftime("%Y.%m.%d")					# timestamp "%Y.%m.%d"
		final[1] = t.strftime("%H:%M")						# timestamp "%H:%M"
	except:
		t = target[1]
		syslog.syslog(f'Unidentifyable time string: {t}') 	# log the failed string for further investigation
		final[0] = t										# raw timestamp in case of an error
		final[1] = ""										# keep empty
		if len(target[11]) == 0:							# if the message is empty
			t = datetime.datetime.now().strftime("%Y.%m.%d %H:%M:%S")
			target[11] = (f'Syslog Parse Error at: {t}')	# prefill it with an error and timestamp

	# print for testing
	# for i in range(1, len(target)):
	#	print(i, target[i])

	final[2] = target[2]					# short
	final[3] = target[3]					# severity

	if len(target[7]) == 0:
		final[5] = target[5] + target[6]	# set the message
	else:
		final[4] = target[9]				# set the uptime 
		final[5] = target[11]				# set the message

	# construct a full message based on the regex outcome
	# special care on the uptime as it can be empty, avoid double whitespace
	utptime = final[4] + ' '
	if utptime.isspace():
		ut = ''
	final[6] = final[0] + ' ' + final[1] + ' ' + final[2] + ' ' + final[3] + ' ' +  utptime + final[5]

	# remove the first entry (full message), not necessary
	#final = final[1:]

	# print for testing
	#for i in range(0, len(final)):
	#	print(i, final[i])

	return final
