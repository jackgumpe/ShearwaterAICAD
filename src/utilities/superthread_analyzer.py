#!/usr/bin/env python3
"""
Superthread Analyzer for Conversation Analytics

This tool uses NLP topic modeling to cluster semantically similar conversation
threads into a small number of high-level "superthreads".
"""

import json
import logging
import re
from pathlib import Path
from typing import List, Dict, Any
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF
import nltk
from nltk.corpus import stopwords

# --- One-time setup for NLTK ---
try:
    stopwords.words('english')
except LookupError:
    print("Downloading NLTK stopwords...")
    nltk.download('stopwords')
# ---

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] {%(levelname)s} - %(message)s')
logger = logging.getLogger('SuperthreadAnalyzer')

class SuperthreadAnalyzer:
    """
    Analyzes defragmented conversation threads to create superthreads using NLP.
    """

    def __init__(self, defragmented_file: str, output_file: str, n_superthreads: int = 20):
        self.defragmented_path = Path(defragmented_file)
        self.output_path = Path(output_file)
        if not (1 < n_superthreads < 50):
            raise ValueError("Number of superthreads must be between 2 and 50.")
        self.n_superthreads = n_superthreads
        self.threads = []

    def _load_threads(self) -> bool:
        """Loads conversation threads from the Parquet file."""
        if not self.defragmented_path.exists():
            logger.error(f"Defragmented file not found: {self.defragmented_path}")
            return False
        
        try:
            df = pd.read_parquet(self.defragmented_path)
            # Re-hydrate the JSON string columns
            for col in ['messages', 'participants', 'context_shifts']:
                if col in df.columns:
                    df[col] = df[col].apply(json.loads)
            self.threads = df.to_dict('records')
            logger.info(f"Loaded {len(self.threads)} threads from {self.defragmented_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to load Parquet file: {e}")
            return False

    def _preprocess_text(self) -> List[str]:
        """Combines all messages in a thread and preprocesses the text."""
        thread_texts = []
        # Custom stopwords that are frequent but not meaningful for topic differentiation
        custom_stopwords = ['message', 'consolidated', 'true', 'original_count', 'time_window', 'keywords', 'contextid',
                            'updatedat', 'phases', 'timestamp', 'phase', 'data', 'length', 'domain', 'confidence',
                            'commandcount', 'routing', 'lease', 'context', 'activated', 'manager']

        for thread in self.threads:
            full_text = " ".join([msg.get('Message', '') for msg in thread['messages']])
            
            # --- Advanced Text Cleaning ---
            # Remove timestamps (e.g., 2025-10-15T22:07:49.2368354Z)
            full_text = re.sub(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z?', '', full_text)
            # Remove UUIDs
            full_text = re.sub(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', '', full_text, flags=re.IGNORECASE)
            # Remove non-alphanumeric characters and lowercase
            full_text = re.sub(r'[^a-zA-Z\s]', '', full_text).lower()
            
            # Tokenize and remove stopwords
            words = full_text.split()
            filtered_words = [word for word in words if word not in custom_stopwords and len(word) > 2]
            
            thread_texts.append(" ".join(filtered_words))
            
        return thread_texts

    def _perform_topic_modeling(self, texts: List[str]) -> tuple[Any, Any, Any]:
        """
        Uses TF-IDF and NMF to discover topics in the conversation texts.
        """
        logger.info("Performing topic modeling...")
        stop_words = list(stopwords.words('english'))
        
        # TF-IDF Vectorizer
        vectorizer = TfidfVectorizer(max_df=0.95, min_df=2, stop_words=stop_words)
        tfidf = vectorizer.fit_transform(texts)
        
        # Non-Negative Matrix Factorization (NMF) for topic modeling
        nmf_model = NMF(n_components=self.n_superthreads, random_state=42, max_iter=1000)
        nmf_model.fit(tfidf)
        
        feature_names = vectorizer.get_feature_names_out()
        logger.info("Topic modeling complete.")
        return nmf_model, feature_names, tfidf

    def _get_top_words_for_topics(self, model: Any, feature_names: List[str], n_top_words: int = 8) -> Dict[int, str]:
        """Creates a human-readable name for each topic (superthread)."""
        topic_names = {}
        for topic_idx, topic in enumerate(model.components_):
            top_words_indices = topic.argsort()[:-n_top_words - 1:-1]
            top_words = [feature_names[i] for i in top_words_indices]
            topic_names[topic_idx] = f"Topic {topic_idx + 1}: " + ", ".join(top_words)
        return topic_names

    def run(self) -> None:
        """Executes the full superthread analysis pipeline."""
        if not self._load_threads():
            return

        thread_texts = self._preprocess_text()
        nmf_model, feature_names, tfidf = self._perform_topic_modeling(thread_texts)
        topic_names = self._get_top_words_for_topics(nmf_model, feature_names)

        # Assign each thread to its dominant topic
        thread_topic_matrix = nmf_model.transform(tfidf)
        dominant_topics = thread_topic_matrix.argmax(axis=1)

        # Structure the output
        superthreads = {name: [] for name in topic_names.values()}
        for i, thread in enumerate(self.threads):
            topic_idx = dominant_topics[i]
            topic_name = topic_names[topic_idx]
            superthreads[topic_name].append(thread)
        
        # Remove empty superthreads
        final_superthreads = {k: v for k, v in superthreads.items() if v}

        logger.info(f"Clustered {len(self.threads)} threads into {len(final_superthreads)} superthreads.")
        
        # Write the output
        try:
            self.output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.output_path, 'w', encoding='utf-8') as f:
                json.dump(final_superthreads, f, indent=2, ensure_ascii=False)
            logger.info(f"Successfully wrote superthreads to {self.output_path}")
        except IOError as e:
            logger.error(f"Failed to write output file: {e}")

def main():
    """CLI entry point."""
    analyzer = SuperthreadAnalyzer(
        defragmented_file="conversation_logs/defragmented_sessions.parquet",
        output_file="conversation_logs/superthreads.json",
        n_superthreads=20
    )
    analyzer.run()

if __name__ == "__main__":
    main()
