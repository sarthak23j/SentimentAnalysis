import llama_cpp as llama
import pandas as pd
import torch # type: ignore
from sklearn.model_selection import train_test_split
from transformers import AutoModelForSequenceClassification, AutoTokenizer, Trainer, TrainingArguments
from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments
from peft import LoraConfig, get_peft_model
from datasets import Dataset

# Load data
df = pd.read_csv("imdb_data.csv")

# Format data for LLaMA (convert numerical labels to text)
df["sentiment_text"] = df["sentiment"].map({0: "Negative", 1: "Positive"})
dataset = Dataset.from_pandas(df)

# Load tokenizer and model
model_name = "NousResearch/Llama-3-7b-chat-hf"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name, device_map="auto", torch_dtype=torch.float16)

# Apply LoRA for efficient training
peft_config = LoraConfig(r=8, lora_alpha=32, target_modules=["q_proj", "v_proj"], lora_dropout=0.1, bias="none", task_type="CAUSAL_LM")
model = get_peft_model(model, peft_config)

# Tokenize dataset
def tokenize_function(examples):
    return tokenizer(examples["review"], truncation=True, padding="max_length", max_length=256)

dataset = dataset.map(tokenize_function, batched=True)

# Training arguments
training_args = TrainingArguments(
    output_dir="./fine_tuned_llama",
    per_device_train_batch_size=4,
    per_device_eval_batch_size=4,
    evaluation_strategy="epoch",
    num_train_epochs=3,
    logging_dir="./logs",
    save_strategy="epoch",
    fp16=True
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset,
)

# Train the model
trainer.train()

# Save model
model.save_pretrained("fine_tuned_llama")
tokenizer.save_pretrained("fine_tuned_llama")



# Load datasets
imdb_data = pd.read_csv("imdb_data.csv")
flipkart_data = pd.read_csv("flipkart_data.csv")

# Combine datasets
df = pd.concat([imdb_data, flipkart_data], ignore_index=True)

# Preprocessing: Keep only relevant columns
df = df[['review', 'sentiment']]
df = df.dropna()  # Remove missing values

# Convert text labels to numerical values
label_map = {"positive": 2, "neutral": 1, "negative": 0}
df["sentiment"] = df["sentiment"].map(llama)
df["sentiment"] = df["sentiment"].map(label_map)

# Split into training and testing sets
train_texts, val_texts, train_labels, val_labels = train_test_split(
    df["review"], df["sentiment"], test_size=0.2, random_state=42
)

# Load tokenizer and model
model_name = "NousResearch/Llama-2-7b-chat-hf"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=3)

# Tokenize the dataset
train_encodings = tokenizer(list(train_texts), truncation=True, padding=True, max_length=512)
val_encodings = tokenizer(list(val_texts), truncation=True, padding=True, max_length=512)

class SentimentDataset(torch.utils.data.Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        return {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}, torch.tensor(self.labels[idx])

train_dataset = SentimentDataset(train_encodings, train_labels.tolist())
val_dataset = SentimentDataset(val_encodings, val_labels.tolist())

training_args = TrainingArguments(
    output_dir="./results",
    evaluation_strategy="epoch",
    per_device_train_batch_size=2,
    per_device_eval_batch_size=2,
    num_train_epochs=3,
    save_strategy="epoch",
    logging_dir="./logs",
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
)

# Train the model
trainer.train()

# Save the fine-tuned model
model.save_pretrained("fine_tuned_llama")
tokenizer.save_pretrained("fine_tuned_llama")
