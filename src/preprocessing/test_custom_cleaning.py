import argparse
import time
from custom_cleaning import Custom_Cleaner


# execute
parser = argparse.ArgumentParser(description="testing-custom-cleaning-module")
parser.add_argument("--inp-text", type=str, help="input text", required=True)
args = parser.parse_args()
inp_text = args.inp_text
start = time.time()
cust_cleaner = Custom_Cleaner()
cleaned_text = cust_cleaner.fit_transform(inp_text)
print("time taken: %0.4f" %(time.time()-start))
print(cleaned_text)
