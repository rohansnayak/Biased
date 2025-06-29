import json
import os
import numpy as np
from typing import List, Dict, Tuple
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, AutoModelForSequenceClassification, TrainingArguments, Trainer
from bias_model import PoliticalBiasAnalyzer

class BiasDataset(Dataset):
    def __init__(self, texts: List[str], labels: List[str], tokenizer, max_length: int = 512):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
        
        # Create label mapping
        self.label2id = {'Left': 0, 'Center': 1, 'Right': 2}
        self.id2label = {0: 'Left', 1: 'Center', 2: 'Right'}
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = str(self.texts[idx])
        label = self.labels[idx]
        
        encoding = self.tokenizer(
            text,
            truncation=True,
            padding='max_length',
            max_length=self.max_length,
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(self.label2id[label], dtype=torch.long)
        }

def create_training_data() -> Tuple[List[str], List[str]]:
    """Create training data with examples of biased articles"""
    
    training_data = [
        # Left-leaning examples
        {
            'text': 'The progressive movement continues to fight for economic justice and wealth redistribution. Universal healthcare is a fundamental human right that should be available to all Americans. Climate change represents an existential threat that requires immediate government action.',
            'label': 'Left'
        },
        {
            'text': 'Systemic racism persists in our institutions and must be addressed through comprehensive police reform. Black Lives Matter activists are leading the charge for racial justice. LGBTQ+ rights are human rights that deserve full protection under the law.',
            'label': 'Left'
        },
        {
            'text': 'The Green New Deal offers a bold vision for addressing climate change while creating millions of good-paying jobs. Renewable energy is the future, and we must transition away from fossil fuels immediately. Environmental justice communities deserve protection from pollution.',
            'label': 'Left'
        },
        {
            'text': 'Workers deserve a living wage and the right to organize unions. Corporate greed is destroying the middle class while executives reap record profits. We need progressive taxation to ensure the wealthy pay their fair share.',
            'label': 'Left'
        },
        
        # Right-leaning examples
        {
            'text': 'The free market is the most efficient way to allocate resources and create prosperity. Government regulation stifles innovation and economic growth. Tax cuts for businesses and individuals will stimulate the economy and create jobs.',
            'label': 'Right'
        },
        {
            'text': 'Traditional family values are the foundation of a strong society. Religious freedom must be protected from government overreach. The Second Amendment guarantees our right to bear arms for self-defense.',
            'label': 'Right'
        },
        {
            'text': 'Border security is essential for national security. Illegal immigration threatens American jobs and communities. Law and order policies are necessary to keep our streets safe.',
            'label': 'Right'
        },
        {
            'text': 'Climate change is a hoax perpetuated by liberal elites to justify government control. American energy independence through fossil fuels is crucial for national security. Environmental regulations are killing American jobs.',
            'label': 'Right'
        },
        
        # Center/neutral examples
        {
            'text': 'This bipartisan legislation represents a compromise that addresses concerns from both sides of the aisle. The data shows mixed results on the effectiveness of the policy. Further research is needed to determine the long-term impacts.',
            'label': 'Center'
        },
        {
            'text': 'The study presents a balanced analysis of the economic impacts, considering both positive and negative factors. Experts disagree on the best approach to this complex issue. More evidence is needed before drawing conclusions.',
            'label': 'Center'
        },
        {
            'text': 'This factual report presents the information without taking sides on the controversial issue. The analysis considers multiple perspectives and presents the data objectively. Readers can draw their own conclusions from the evidence presented.',
            'label': 'Center'
        }
    ]
    
    # Add more examples with loaded language
    loaded_examples = [
        {
            'text': 'The radical left socialist agenda threatens to destroy American capitalism and freedom. This outrageous proposal would bankrupt our nation and lead to economic disaster.',
            'label': 'Right'
        },
        {
            'text': 'The corrupt establishment continues to ignore the will of the people. These dishonest politicians are betraying American values and selling out to special interests.',
            'label': 'Right'
        },
        {
            'text': 'The courageous activists are fighting against systemic oppression and injustice. Their brave stand for equality and justice inspires millions around the world.',
            'label': 'Left'
        },
        {
            'text': 'The greedy corporations are exploiting workers and destroying the environment for profit. These selfish billionaires refuse to pay their fair share in taxes.',
            'label': 'Left'
        }
    ]
    
    training_data.extend(loaded_examples)
    
    texts = [item['text'] for item in training_data]
    labels = [item['label'] for item in training_data]
    
    return texts, labels

def evaluate_current_model(texts: List[str], labels: List[str]) -> Dict:
    """Evaluate the current rule-based model"""
    analyzer = PoliticalBiasAnalyzer()
    
    predictions = []
    for text in texts:
        _, label, _ = analyzer.classify_bias(text)
        predictions.append(label)
    
    accuracy = accuracy_score(labels, predictions)
    report = classification_report(labels, predictions, output_dict=True)
    
    return {
        'accuracy': accuracy,
        'classification_report': report,
        'predictions': predictions
    }

def train_transformer_model(texts: List[str], labels: List[str], model_name: str = 'distilbert-base-uncased'):
    """Train a transformer model for bias classification"""
    
    # Split data
    train_texts, val_texts, train_labels, val_labels = train_test_split(
        texts, labels, test_size=0.2, random_state=42, stratify=labels
    )
    
    # Initialize tokenizer and model
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(
        model_name, 
        num_labels=3,
        id2label={0: 'Left', 1: 'Center', 2: 'Right'},
        label2id={'Left': 0, 'Center': 1, 'Right': 2}
    )
    
    # Create datasets
    train_dataset = BiasDataset(train_texts, train_labels, tokenizer)
    val_dataset = BiasDataset(val_texts, val_labels, tokenizer)
    
    # Training arguments
    training_args = TrainingArguments(
        output_dir='./bias_model_checkpoints',
        num_train_epochs=3,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        warmup_steps=500,
        weight_decay=0.01,
        logging_dir='./logs',
        logging_steps=10,
        evaluation_strategy='epoch',
        save_strategy='epoch',
        load_best_model_at_end=True,
        metric_for_best_model='accuracy'
    )
    
    # Initialize trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        tokenizer=tokenizer
    )
    
    # Train the model
    trainer.train()
    
    # Evaluate
    results = trainer.evaluate()
    
    # Save the model
    model_path = './trained_bias_model'
    trainer.save_model(model_path)
    tokenizer.save_pretrained(model_path)
    
    return model_path, results

def add_custom_training_data(file_path: str) -> List[Dict]:
    """Add custom training data from a JSON file"""
    if not os.path.exists(file_path):
        return []
    
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    return data

def main():
    print("🚀 Starting Bias Model Training")
    print("=" * 50)
    
    # Create training data
    print("📝 Creating training data...")
    texts, labels = create_training_data()
    
    # Add custom data if available
    custom_data = add_custom_training_data('custom_training_data.json')
    if custom_data:
        custom_texts = [item['text'] for item in custom_data]
        custom_labels = [item['label'] for item in custom_data]
        texts.extend(custom_texts)
        labels.extend(custom_labels)
        print(f"✅ Added {len(custom_data)} custom training examples")
    
    print(f"📊 Total training examples: {len(texts)}")
    print(f"📈 Label distribution: {dict(zip(*np.unique(labels, return_counts=True)))}")
    
    # Evaluate current model
    print("\n🔍 Evaluating current rule-based model...")
    current_results = evaluate_current_model(texts, labels)
    print(f"📊 Current model accuracy: {current_results['accuracy']:.3f}")
    print("📋 Classification Report:")
    print(current_results['classification_report'])
    
    # Train transformer model
    print("\n🤖 Training transformer model...")
    try:
        model_path, results = train_transformer_model(texts, labels)
        print(f"✅ Model trained and saved to: {model_path}")
        print(f"📊 Training results: {results}")
    except Exception as e:
        print(f"❌ Error training model: {e}")
        print("💡 Make sure you have enough GPU memory or try with a smaller model")
    
    # Create custom training data template
    template = {
        "training_examples": [
            {
                "text": "Example article text here...",
                "label": "Left|Center|Right",
                "source": "Optional source information",
                "notes": "Optional notes about why this is labeled as such"
            }
        ]
    }
    
    with open('custom_training_data_template.json', 'w') as f:
        json.dump(template, f, indent=2)
    
    print("\n📋 Created custom_training_data_template.json")
    print("💡 Add your own training examples to improve the model!")
    print("\n🎯 Next steps:")
    print("1. Add more training examples to custom_training_data.json")
    print("2. Run this script again to retrain the model")
    print("3. Update bias_model.py to use the trained model")

if __name__ == "__main__":
    main() 