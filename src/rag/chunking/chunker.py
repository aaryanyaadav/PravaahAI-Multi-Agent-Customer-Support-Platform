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
        
        # If it's a section header like "User Management FAQs" or "2. User Management Policy",
        # we can keep it as its own chunk, or attach it to the next chunk.
        # But split by double newlines is robust enough. Let's clean and append.
        chunks.append(stripped)
        
    return chunks
