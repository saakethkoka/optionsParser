import pandas as pd
import re
import datetime as dt


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


    option_details = {
        "flag": "C", # C for call, P for put
        "ticker": "BBIG", # Ticker of the underlying (capitalized)
        "expiry": dt.date(2022, 5, 6), # Expiry date of the option
        "strike": 3, # Strike price of the option
    }

    return option_details


data = pd.read_csv("data.csv")
data.Expiry = pd.to_datetime(data.Expiry).dt.date


total_entries = len(data)
correct_entries = 0

for i in range(len(data)):
    option = parse_text(data["Text"][i])

    if(data["Flag"][i] == option["flag"]
            and data["Ticker"][i] == option["ticker"]
            and data["Expiry"][i] == option["expiry"]
            and data["Strike"][i] == option["strike"]):
        correct_entries += 1


accuracy = correct_entries*100 / total_entries
accuracy = round(accuracy, 2)

print("Accuracy: {}%".format(accuracy))