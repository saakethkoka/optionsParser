import pandas as pd
import re
import datetime as dt

MONTHS_DICT = {
    "JANUARY": 1, "FEBRUARY": 2, "MARCH": 3, "APRIL": 4, "MAY": 5, "JUNE": 6, "JULY": 7, "AUGUST": 8, "SEPTEMBER": 9,
    "OCTOBER": 10, "NOVEMBER": 11, "DECEMBER": 12, "JAN": 1, "FEB": 2, "MAR": 3, "APR": 4, "JUN": 6, "JUL": 7, "AUG": 8,
    "SEP": 9, "OCT": 10, "NOV": 11, "DEC": 12
}




def remove_emojis(text):
    emoj = re.compile("["
                      u"\U0001F600-\U0001F64F"  # emoticons
                      u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                      u"\U0001F680-\U0001F6FF"  # transport & map symbols
                      u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                      u"\U00002500-\U00002BEF"  # chinese char
                      u"\U00002702-\U000027B0"
                      u"\U00002702-\U000027B0"
                      u"\U000024C2-\U0001F251"
                      u"\U0001f926-\U0001f937"
                      u"\U00010000-\U0010ffff"
                      u"\u2640-\u2642"
                      u"\u2600-\u2B55"
                      u"\u200d"
                      u"\u23cf"
                      u"\u23e9"
                      u"\u231a"
                      u"\ufe0f"  # dingbats
                      u"\u3030"
                      "]+", re.UNICODE)
    return re.sub(emoj, '', text)


def clean_text(text):
    text = text.replace('\n', ' ')
    text = text.replace('\r', ' ')
    text = text.replace('\t', ' ')
    text = text.strip()
    text = remove_emojis(text)
    return text


def parse_text(text, ticker=None):
    text = clean_text(text)
    # TODO: Add logic to create an option_details dictionary formatted like the one bellow:
    word_list = text.split()
    option_details = {
        "flag": None,
        "ticker": None,  # Ticker of the underlying (capitalized)
        "expiry": None,  # Expiry date of the option
        "strike": None,  # Strike price of the option
    }

    for i in range(len(word_list)):
        # Looking for a ticker first:
        if word_list[i][0] == '$':
            if word_list[i][1].isalpha():
                ticker = word_list[i][1:].upper()
                if not ticker[-1].isalpha():
                    ticker = ticker[:-1]
                option_details['ticker'] = ticker
                # When a ticker is found:
                while i < len(word_list)-1:
                    i += 1
                    # Looking for a flag:
                    if word_list[i].upper() == 'PUT' or word_list[i].upper() == 'PUTS' or word_list[i].upper() == 'P':
                        option_details['flag'] = 'P'
                    elif word_list[i].upper() == 'CALL' or word_list[i].upper() == 'CALLS' or word_list[i].upper() == 'C':
                        option_details['flag'] = 'C'
                    # Looking for a strike price (given that one has not been found yet):
                    # The strike price typically comes soon after the ticker
                    elif word_list[i][0] == '$' and option_details["strike"] is None:
                        option_details["strike"] = float(word_list[i][1:])
                    # Looking for an expiry date:
                    elif option_details["expiry"] is None:
                        # The expiry date typically comes soon after the ticker
                        if word_list[i][:3].upper() == "EXP":
                            if "/" in word_list[i+1]:
                                dates = word_list[i+1].split("/")
                                month = int(dates[0])
                                day = int(dates[1])
                                year = 2022  # TODO: better way to find year but should be fine for now
                                option_details["expiry"] = dt.date(year, month, day)
                            elif word_list[i+1] in MONTHS_DICT and word_list[i+2].isnumeric():
                                month = MONTHS_DICT[word_list[i+1]]
                                day = int(word_list[i+2])
                                year = 2022  # TODO: better way to find year but should be fine for now
                                option_details["expiry"] = dt.date(year, month, day)

    return option_details


data = pd.read_csv("data.csv")
data.Expiry = pd.to_datetime(data.Expiry).dt.date


total_entries = len(data)
correct_entries = 0
unfinished_entries = 0

for i in range(len(data)):
    option = parse_text(data["Text"][i])

    if(option["ticker"] is None or option["expiry"] is None or option["strike"] is None or option["flag"] is None):
        print(option)
        continue

    if(data["Flag"][i] == option["flag"]
            and data["Ticker"][i] == option["ticker"]
            and data["Expiry"][i] == option["expiry"]
            and data["Strike"][i] == option["strike"]):
        correct_entries += 1
    else:
        print("Incorrect entry:")
        print("Expected:")
        print("Flag:", data["Flag"][i])
        print("Ticker:", data["Ticker"][i])
        print("Expiry:", data["Expiry"][i])
        print("Strike:", data["Strike"][i])
        print("Got:")
        print("Flag:", option["flag"])
        print("Ticker:", option["ticker"])
        print("Expiry:", option["expiry"])
        print("Strike:", option["strike"])


accuracy = correct_entries*100 / total_entries
accuracy = round(accuracy, 2)

print("Accuracy: {}%".format(accuracy))
print("Unfinished entries: {}".format(unfinished_entries))