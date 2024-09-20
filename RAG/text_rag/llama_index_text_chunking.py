import json
import os

from llama_index.core.node_parser import SemanticSplitterNodeParser
from llama_index.core import SimpleDirectoryReader

from llama_index_text_search_engine import text_create_search_index 
from openai_client_instantiate import instantiate_embeddings_client

def process_documents(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    embed_model_client = instantiate_embeddings_client()

    for doc_name in os.listdir(input_dir):
        doc_path = os.path.join(input_dir, doc_name)
        documents = SimpleDirectoryReader(input_files=[doc_path]).load_data()

        splitter = SemanticSplitterNodeParser(
            buffer_size=5, 
            breakpoint_percentile_threshold=85, 
            embed_model=embed_model_client,
            include_metadata=True, 
            include_prev_next_rel=True
        )

        nodes = splitter.get_nodes_from_documents(documents)
        #index nodes immediately after they are generated
        text_create_search_index(nodes)

        # save nodes locally for the individual document
        output_file_path = os.path.join(output_dir, f"{doc_name}_nodes.json")
        with open(output_file_path, 'w', encoding='utf-8') as f:
            json.dump([node.to_dict() for node in nodes], f, ensure_ascii=False, indent=4)
        
        print(f"Processed, indexed, and saved nodes for {doc_name} at {output_file_path}")

## Execution
# input_path = r"C:\Users\nicho\OneDrive\Desktop\HacX\Sandbox\data\documents\raw_text"
# output_path = r"C:\Users\nicho\OneDrive\Desktop\HacX\Sandbox\data\documents\output_chunks"
# process_documents(input_path, output_path)
