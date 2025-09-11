# Agentic AI Platform

This repository contains tools and scripts for working with conversational AI datasets and models.

## Setup

1. Create the conda environment:
```bash
conda env create -f env.yml
```

2. Activate the environment:
```bash
conda activate agentic-ai-platform
```

## Available Datasets

### MultiWOZ 2.2 Dataset

The MultiWOZ 2.2 dataset is a large-scale multi-domain task-oriented dialogue dataset. It contains over 10,000 dialogues across 7 domains.

### PersonaChat Dataset

The PersonaChat dataset is a persona-conditioned chit-chat dialogue dataset where participants are assigned personas (character descriptions) to guide their responses. This dataset is useful for training conversational agents with consistent personalities.

### Download the Datasets

#### MultiWOZ 2.2
Run the download script:
```bash
python download_multiwz.py
```

This will:
- Download the MultiWOZ 2.2 dataset from Hugging Face
- Save it locally in the `data/multi_woz_v22` directory
- Display dataset information and statistics

#### PersonaChat
Run the download script:
```bash
python download_personachat.py
```

This will:
- Download the PersonaChat dataset from Hugging Face (not available on Kaggle)
- Save it locally in the `data/personachat` directory
- Display dataset information and statistics

### Loading the Datasets

After downloading, you can load the datasets in your Python code:

#### MultiWOZ 2.2
```python
from datasets import load_from_disk

# Load the dataset
dataset = load_from_disk('data/multi_woz_v22')

# Access different splits
train_data = dataset['train']
validation_data = dataset['validation'] 
test_data = dataset['test']

print(f"Training examples: {len(train_data)}")
print(f"Validation examples: {len(validation_data)}")
print(f"Test examples: {len(test_data)}")
```

#### PersonaChat
```python
from datasets import load_from_disk

# Load the dataset
dataset = load_from_disk('data/personachat')

# Access different splits
train_data = dataset['train']
validation_data = dataset['validation'] 
test_data = dataset['test']

print(f"Training examples: {len(train_data)}")
print(f"Validation examples: {len(validation_data)}")
print(f"Test examples: {len(test_data)}")
```

### Dataset Structures

#### MultiWOZ 2.2 Dataset Structure
The MultiWOZ 2.2 dataset contains:
- **Train split**: ~8,438 dialogues
- **Validation split**: ~1,000 dialogues  
- **Test split**: ~1,000 dialogues

Each dialogue contains:
- `dialogue_id`: Unique identifier
- `services`: List of domains involved
- `turns`: List of conversation turns with user and system utterances
- `metadata`: Additional information about the dialogue

#### PersonaChat Dataset Structure
The PersonaChat dataset contains:
- **Train split**: ~8,939 dialogues
- **Validation split**: ~1,000 dialogues  
- **Test split**: ~968 dialogues

Each dialogue contains:
- `personas`: List of persona sentences describing character traits
- `utterances`: List of conversation turns
- `candidates`: Optional response candidates for evaluation
- `id`: Unique dialogue identifier

## Requirements

- Python 3.9+
- Conda environment with dependencies specified in `env.yml`
- Internet connection for downloading datasets