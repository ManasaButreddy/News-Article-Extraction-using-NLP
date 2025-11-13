import pandas as pd
#import torch
from transformers import T5Tokenizer, T5ForConditionalGeneration
from datetime import date
import time
import boto3

# Load the T5 model and tokenizer
model_name = 't5-small'
model = T5ForConditionalGeneration.from_pretrained(model_name, cache_dir="D:/Manasa/huggingface_cache/")
tokenizer = T5Tokenizer.from_pretrained(model_name, cache_dir="D:/Manasa/huggingface_cache/")

current_date = date.today()
current_date
cd = current_date.strftime("%d%m%Y")
file_today = 'StarArticles{}.csv'.format(time.strftime("%d%m%Y"))
# Read the input data
df = pd.read_csv(file_today)
#df = pd.read_csv(r'D:/NewsArticleNLP/articles07112023.csv')
df_content = pd.DataFrame(df["Content"])

# Add T5 prefix for text summarization
df_content["Content"] = "summarize: " + df_content["Content"].astype(str)

# Tokenize the articles
tokenized_text = tokenizer.batch_encode_plus(
    df_content["Content"].tolist(),
    return_tensors='pt',
    padding='longest',  # Pad to the length of the longest article
    truncation=True,
    max_length=512  # Adjust as per your model's maximum input length
)

# Generate summaries using batch processing
batch_size = 25  # Adjust batch size as per your system's memory constraints
input_ids = tokenized_text['input_ids']
attention_mask = tokenized_text['attention_mask']
num_articles = len(df_content)

summaries = []
for i in range(0, num_articles, batch_size):
    start_idx = i
    end_idx = min(i + batch_size, num_articles)

    batch_input_ids = input_ids[start_idx:end_idx]
    batch_attention_mask = attention_mask[start_idx:end_idx]

#    set_seed(40)

    # Generate summaries for the current batch
    batch_summaries = model.generate(
        input_ids=batch_input_ids,
        attention_mask=batch_attention_mask,
        num_beams=3, #Beam search reduces the risk of missing hidden high probability word sequences
        no_repeat_ngram_size=2, #no n-gram appears twice
        min_length=30,
        max_length=100,
        early_stopping=True
    )

    # Decode the summaries
    decoded_summaries = tokenizer.batch_decode(batch_summaries, skip_special_tokens=True)
    summaries.extend(decoded_summaries)

# Update the DataFrame with the summaries
df["Summarized text"] = summaries

# save dataframe df to csv file
df.to_csv("StarArticles_summary{}.csv".format(time.strftime("%d%m%Y")), index=False)

# Function to upload output file to Amazon S3 bucket
def upload_to_s3():
    s3 = boto3.resource(service_name='s3',
                        region_name='us-east-2',
                        aws_access_key_id='AKIAR6JTQT3GS77CI6AW',
                        aws_secret_access_key='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')

    for bucket in s3.buckets.all():
        print(bucket.name)

    
    s3.Bucket('nlpnewsarticlebucket').upload_file(Filename='StarArticles_summary{}.csv'.format(cd),
                                                  Key='StarArticles_summary{}.csv'.format(cd))

# Upload the output file to Amazon S3 bucket
upload_to_s3()
