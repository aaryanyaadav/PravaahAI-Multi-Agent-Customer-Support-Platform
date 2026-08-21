def chunk_text(text: str):
    # Normalize newlines
    normalized = text.replace("\r\n", "\n")
    # Split by double newlines or lines containing only spaces
    raw_chunks = normalized.split("\n\n")
    
    chunks = []
    current_chunk = []
    
    for chunk in raw_chunks:
        stripped = chunk.strip()
        if not stripped:
            continue
    
        chunks.append(stripped)
        
    return chunks
