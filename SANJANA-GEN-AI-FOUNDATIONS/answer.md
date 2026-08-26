# Question 1: The Vector Conflict

Yes, the similarity score between Sentence 1 and Sentence 2 was still relatively high even though the word "light" was used with different meanings. This happens because CountVectorizer follows the Bag-of-Words approach and only counts how many times each word appears in a sentence. Since both sentences contain the word "light", the vectorizer treats them as similar regardless of their actual meaning. As a result, it creates a false mathematical relationship between contextually different sentences.

# Question 2: The Context Blindspot

From a Data Science perspective, the Bag-of-Words approach is a major bottleneck because it ignores context, word order, and semantic meaning. When text is converted into static counts, all occurrences of a word receive the same representation regardless of the surrounding words. This makes it difficult for search engines and chatbots to understand user intent accurately. The linguistic property that is lost is contextual meaning, which is essential for natural language understanding.

# Question 3: The GenAI Architectural Fix

Modern Large Language Models such as GPT and LLaMA solve this problem using Context-Aware Embeddings generated through Masked Self-Attention mechanisms. Self-Attention allows each word to interact with surrounding words and learn its meaning based on context. Therefore, the word "light" receives different vector representations when referring to a healthy snack, a lightweight texture, or physical illumination. This enables LLMs to understand semantic meaning accurately and overcome the limitations of traditional Bag-of-Words models.
