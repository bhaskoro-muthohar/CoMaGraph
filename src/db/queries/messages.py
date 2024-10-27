class MessageQueries:
    CREATE_MESSAGE = """
    MATCH (t:Thread {id: $thread_id})
    CREATE (m:Message {
        id: $id,
        content: $content,
        created_at: datetime(),
        role: $role,
        embedding: $embedding,
        metadata: $metadata
    })-[:BELONGS_TO]->(t)
    WITH m, t
    MATCH (prev:Message)-[:BELONGS_TO]->(t)
    WHERE NOT EXISTS((prev)<-[:NEXT]-())
    CREATE (prev)-[:NEXT]->(m)
    RETURN m
    """

    GET_MESSAGE = """
    MATCH (m:Message {id: $id})
    RETURN m
    """

    GET_THREAD_MESSAGES = """
    MATCH (m:Message)-[:BELONGS_TO]->(t:Thread {id: $thread_id})
    RETURN m
    ORDER BY m.created_at
    """