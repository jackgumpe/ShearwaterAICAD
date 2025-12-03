import json
import pandas as pd
import pyarrow as pa
import pyarrow.feather as feather
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF
from typing import Dict, List

class CheckpointCreator:
    """
    Reads conversation logs, performs topic modeling, and saves the
    enriched data as an Apache Arrow checkpoint file.
    """
    def __init__(self, log_dir: Path = Path("conversation_logs"), output_dir: Path = Path("checkpoints")):
        self.log_dir = log_dir
        self.output_dir = output_dir
        self.output_dir.mkdir(exist_ok=True)
        print(f"Checkpoint creator initialized. Logs from '{self.log_dir}', output to '{self.output_dir}'.")

    def load_logs(self, log_file_name: str = "current_session.jsonl") -> List[Dict]:
        """Loads conversation history from a JSONL log file."""
        log_file_path = self.log_dir / log_file_name
        if not log_file_path.exists():
            print(f"WARNING: Conversation log file not found at {log_file_path}")
            return []

        history = []
        with open(log_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    history.append(json.loads(line))
                except json.JSONDecodeError:
                    print(f"Skipping malformed JSON line: {line.strip()}")
        print(f"Loaded {len(history)} messages from {log_file_name}.")
        return history

    def create_topic_summary(self, documents: List[str], n_topics: int = 5, n_top_words: int = 3) -> tuple:
        """
        Performs topic modeling using TF-IDF and NMF to create summaries.
        """
        if not documents:
            return pd.Series(dtype=int), {}
        
        try:
            # 1. Vectorize text data
            vectorizer = TfidfVectorizer(max_df=0.95, min_df=1, stop_words='english')
            tfidf = vectorizer.fit_transform(documents)

            # Check if vectorization produced a valid matrix
            if tfidf.nnz == 0:
                print("WARNING: Vectorization resulted in an empty matrix. Skipping topic modeling.")
                return pd.Series(dtype=int), {}
            
            # 2. Apply Non-negative Matrix Factorization (NMF) for topic discovery
            nmf = NMF(n_components=n_topics, random_state=1, alpha_W=0.1, alpha_H=0.1, l1_ratio=0.5).fit(tfidf)
            
            # 3. Assign each document to a topic
            topic_assignments = pd.Series(nmf.transform(tfidf).argmax(axis=1))
            
            # 4. Generate topic titles
            feature_names = vectorizer.get_feature_names_out()
            topic_titles = {}
            for topic_idx, topic in enumerate(nmf.components_):
                top_words = [feature_names[i] for i in topic.argsort()[:-n_top_words - 1:-1]]
                topic_titles[topic_idx] = f"Topic {topic_idx}: " + ", ".join(top_words)
                
            print(f"Topic modeling complete. Identified {len(topic_titles)} topics.")
            for idx, title in topic_titles.items():
                print(f"  - {title}")
                
            return topic_assignments, topic_titles
        except Exception as e:
            print(f"WARNING: Topic modeling failed with error: {e}. Skipping.")
            return pd.Series(dtype=int), {}

    def run(self):
        """
        Executes the full checkpoint creation pipeline.
        """
        history = self.load_logs()
        if not history:
            print("No logs to process. Exiting.")
            return

        df = pd.DataFrame(history)

        # Extract message content for analysis, using the correct column 'Message'
        if 'Message' in df.columns:
            df['message_content'] = df['Message'].fillna('')
        else:
            print("WARNING: 'Message' column not found. Skipping topic modeling.")
            df['message_content'] = ''
        
        # Perform topic modeling only on messages with content
        docs_for_modeling = df[df['message_content'].str.len() > 0]
        topic_assignments, topic_titles = self.create_topic_summary(docs_for_modeling['message_content'].tolist())
        
        # Add topic information back to the main dataframe
        if not topic_assignments.empty:
            # Create a temporary index to align the topic assignments back to the original DataFrame
            docs_for_modeling = docs_for_modeling.copy()
            docs_for_modeling['topic_id'] = topic_assignments.values
            df = df.merge(docs_for_modeling[['topic_id']], left_index=True, right_index=True, how='left')
            df['topic_title'] = df['topic_id'].map(topic_titles)
        else:
            df['topic_id'] = None
            df['topic_title'] = None
        
        # Convert to Arrow Table and save
        table = pa.Table.from_pandas(df.drop(columns=['message_content'])) # Drop the temporary column
        output_file = self.output_dir / f"checkpoint_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.arrow"
        
        with pa.OSFile(str(output_file), 'wb') as sink:
            with pa.ipc.new_file(sink, table.schema) as writer:
                writer.write_table(table)
                
        print(f"Successfully created checkpoint file: {output_file}")


if __name__ == "__main__":
    # To run this script, the CWD should be the project root (ShearwaterAICAD)
    creator = CheckpointCreator(log_dir=Path("conversation_logs"))
    creator.run()
