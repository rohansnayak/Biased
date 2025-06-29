# Fine-Tuning Guide for Bias Detection Model

## Overview

Your bias detection model is currently using rule-based analysis with keyword matching and sentiment analysis. To improve accuracy, you can fine-tune it with real training data.

## Current Model Capabilities

The enhanced model now includes:

1. **Enhanced Keyword Analysis**: Categorized political keywords (economic, social, environmental, healthcare)
2. **Contextual Sentiment Analysis**: Sentiment analysis with political context
3. **Loaded Language Detection**: Detection of emotional and judgmental language
4. **Confidence Scoring**: Indicates how confident the model is in its prediction

## Quick Test

First, test the current model:

```bash
cd ai
python test_bias_detection.py
```

This will run tests on sample articles and show you the current accuracy.

## Improving the Model

### 1. Add Training Data

Create a file called `custom_training_data.json` with your own examples:

```json
{
  "training_examples": [
    {
      "text": "Your article text here...",
      "label": "Left",
      "source": "CNN, Fox News, etc.",
      "notes": "Why this is labeled as Left/Right/Center"
    },
    {
      "text": "Another article text...",
      "label": "Right",
      "source": "Source name",
      "notes": "Explanation"
    }
  ]
}
```

### 2. Run Training

```bash
cd ai
python train_bias_model.py
```

This will:
- Evaluate the current model
- Train a new transformer model
- Save the trained model to `./trained_bias_model`

### 3. Use the Trained Model

Update `bias_model.py` to use your trained model:

```python
# In bias_model.py, update the PoliticalBiasAnalyzer class
def __init__(self, model_path: Optional[str] = None):
    self.model_path = model_path or './trained_bias_model'
    # ... rest of initialization
```

## Training Data Guidelines

### What Makes Good Training Data?

1. **Diverse Sources**: Include articles from various news sources
2. **Clear Labels**: Articles should have obvious political leanings
3. **Sufficient Length**: Articles should be at least 100-200 words
4. **Balanced Dataset**: Include roughly equal numbers of Left, Right, and Center examples

### Example Training Data Sources

**Left-leaning sources:**
- MSNBC
- CNN (some articles)
- The New York Times (editorial section)
- The Washington Post (editorial section)
- The Guardian (US edition)

**Right-leaning sources:**
- Fox News
- Breitbart
- The Daily Wire
- The Washington Times
- National Review

**Center/neutral sources:**
- Reuters
- Associated Press
- BBC News
- NPR (news reporting)
- PBS NewsHour

### Labeling Guidelines

**Left Bias Indicators:**
- Support for progressive policies
- Emphasis on social justice
- Climate change urgency
- Support for government intervention
- Focus on inequality and systemic issues

**Right Bias Indicators:**
- Support for free market policies
- Emphasis on traditional values
- Climate change skepticism
- Support for limited government
- Focus on individual responsibility

**Center/Neutral Indicators:**
- Balanced presentation of multiple viewpoints
- Factual reporting without opinion
- Bipartisan language
- Objective analysis
- Data-driven conclusions

## Advanced Fine-Tuning

### 1. Collect Real Articles

Use the web scraping functionality to collect articles:

```python
from backend.app import fetch_article_text

# Collect articles from known sources
sources = {
    'left': ['https://www.msnbc.com/...', 'https://www.cnn.com/...'],
    'right': ['https://www.foxnews.com/...', 'https://www.breitbart.com/...'],
    'center': ['https://www.reuters.com/...', 'https://www.ap.org/...']
}

for bias, urls in sources.items():
    for url in urls:
        text = fetch_article_text(url)
        if text:
            # Add to training data
            pass
```

### 2. Manual Review

Always manually review and label training data. Don't rely on source reputation alone - read the actual content.

### 3. Iterative Improvement

1. Train the model
2. Test on new articles
3. Identify incorrect predictions
4. Add those articles to training data with correct labels
5. Retrain
6. Repeat

## Troubleshooting

### Model Always Returns "Center"

This usually means:
1. **Insufficient training data**: Add more diverse examples
2. **Weak keywords**: The article doesn't contain strong political language
3. **Balanced content**: The article genuinely presents multiple viewpoints

### Model is Too Sensitive

If the model labels everything as biased:
1. Add more neutral/center examples to training data
2. Adjust the confidence thresholds
3. Reduce the weight of loaded language detection

### Model is Not Sensitive Enough

If the model misses obvious bias:
1. Add more examples with clear bias indicators
2. Increase the weight of keyword analysis
3. Add more loaded language patterns

## Performance Metrics

Track these metrics:
- **Accuracy**: Overall correct predictions
- **Precision**: How many predicted Left/Right articles were actually Left/Right
- **Recall**: How many actual Left/Right articles were correctly identified
- **F1 Score**: Balance between precision and recall

## Best Practices

1. **Regular Updates**: Retrain the model periodically with new data
2. **Validation Set**: Keep some articles aside for testing, don't use them for training
3. **Cross-Validation**: Use different subsets of data for training and validation
4. **Documentation**: Keep track of what changes improve performance
5. **Ethical Considerations**: Ensure your training data doesn't perpetuate existing biases

## Next Steps

1. Start with the test script to see current performance
2. Add 10-20 well-labeled articles to `custom_training_data.json`
3. Run the training script
4. Test the improved model
5. Iterate and improve

Remember: Bias detection is inherently subjective. Focus on creating a model that's consistent and transparent about its limitations. 