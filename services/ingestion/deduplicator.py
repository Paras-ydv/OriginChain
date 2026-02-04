"""
Deduplication logic for articles.
Implements exact and near-duplicate detection.
"""

from typing import List, Dict, Set, Tuple
from collections import defaultdict
import logging

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from fuzzywuzzy import fuzz

from config import COSINE_SIMILARITY_THRESHOLD, FUZZY_MATCH_THRESHOLD
from utils import normalize_url

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExactDeduplicator:
    """Detects exact duplicates using URL matching."""
    
    @staticmethod
    def deduplicate(articles: List[Dict]) -> List[Dict]:
        """
        Remove exact duplicates by URL.
        
        Args:
            articles: List of article dictionaries
            
        Returns:
            Deduplicated list
        """
        seen_urls = set()
        unique_articles = []
        duplicates_removed = 0
        
        for article in articles:
            url = normalize_url(article.get('url', ''))
            
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_articles.append(article)
            else:
                duplicates_removed += 1
        
        logger.info(f"Exact deduplication: Removed {duplicates_removed} duplicates, "
                   f"{len(unique_articles)} unique articles remain")
        
        return unique_articles


class NearDeduplicator:
    """Detects near-duplicates using TF-IDF and fuzzy matching."""
    
    def __init__(
        self,
        cosine_threshold: float = COSINE_SIMILARITY_THRESHOLD,
        fuzzy_threshold: int = FUZZY_MATCH_THRESHOLD
    ):
        self.cosine_threshold = cosine_threshold
        self.fuzzy_threshold = fuzzy_threshold
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words='english',
            max_features=1000
        )
    
    def deduplicate(self, articles: List[Dict]) -> List[Dict]:
        """
        Remove near-duplicates using TF-IDF and fuzzy matching.
        
        Args:
            articles: List of article dictionaries
            
        Returns:
            Deduplicated list with best article from each duplicate group
        """
        if len(articles) <= 1:
            return articles
        
        # Build similarity groups
        duplicate_groups = self._find_duplicate_groups(articles)
        
        # Resolve each group to best article
        unique_articles = []
        processed_indices = set()
        duplicates_removed = 0
        
        for group in duplicate_groups:
            if any(idx in processed_indices for idx in group):
                continue
            
            # Select best article from group
            best_idx = self._select_best_article(articles, group)
            unique_articles.append(articles[best_idx])
            processed_indices.update(group)
            duplicates_removed += len(group) - 1
        
        # Add articles not in any duplicate group
        for idx, article in enumerate(articles):
            if idx not in processed_indices:
                unique_articles.append(article)
        
        logger.info(f"Near-duplicate detection: Removed {duplicates_removed} duplicates, "
                   f"{len(unique_articles)} unique articles remain")
        
        return unique_articles
    
    def _find_duplicate_groups(self, articles: List[Dict]) -> List[Set[int]]:
        """Find groups of duplicate articles."""
        n = len(articles)
        
        # Extract titles for comparison
        titles = [article.get('title', '') for article in articles]
        
        # Compute TF-IDF similarity
        try:
            tfidf_matrix = self.vectorizer.fit_transform(titles)
            similarity_matrix = cosine_similarity(tfidf_matrix)
        except ValueError:
            # Handle case where all titles are too similar or empty
            similarity_matrix = [[0] * n for _ in range(n)]
        
        # Build adjacency list of similar articles
        similar_pairs = []
        for i in range(n):
            for j in range(i + 1, n):
                is_similar = False
                
                # Check TF-IDF cosine similarity
                if similarity_matrix[i][j] >= self.cosine_threshold:
                    is_similar = True
                
                # Check fuzzy title match
                fuzzy_score = fuzz.ratio(titles[i], titles[j])
                if fuzzy_score >= self.fuzzy_threshold:
                    is_similar = True
                
                if is_similar:
                    similar_pairs.append((i, j))
        
        # Group connected components (transitively similar articles)
        groups = self._find_connected_components(n, similar_pairs)
        
        return groups
    
    @staticmethod
    def _find_connected_components(n: int, edges: List[Tuple[int, int]]) -> List[Set[int]]:
        """Find connected components in similarity graph."""
        # Build adjacency list
        adj = defaultdict(set)
        for i, j in edges:
            adj[i].add(j)
            adj[j].add(i)
        
        visited = set()
        components = []
        
        def dfs(node, component):
            visited.add(node)
            component.add(node)
            for neighbor in adj[node]:
                if neighbor not in visited:
                    dfs(neighbor, component)
        
        for node in range(n):
            if node not in visited:
                component = set()
                dfs(node, component)
                if len(component) > 1:  # Only add if it's a duplicate group
                    components.append(component)
        
        return components
    
    @staticmethod
    def _select_best_article(articles: List[Dict], group: Set[int]) -> int:
        """
        Select best article from duplicate group.
        Prioritizes: longest clean_text > most metadata > earliest publication
        
        Args:
            articles: All articles
            group: Indices of duplicate articles
            
        Returns:
            Index of best article
        """
        best_idx = None
        best_score = (-1, -1, float('inf'))  # (text_len, metadata_count, pub_timestamp)
        
        for idx in group:
            article = articles[idx]
            
            # Score based on clean_text length
            text_len = len(article.get('clean_text', ''))
            
            # Count available metadata fields
            metadata_count = sum([
                bool(article.get('author')),
                bool(article.get('published_at')),
                bool(article.get('raw_text')),
            ])
            
            # Parse publication time (earlier is better for tie-breaking)
            pub_time = article.get('published_at', '9999-12-31T23:59:59Z')
            
            score = (text_len, metadata_count, pub_time)
            
            if best_idx is None or score > best_score:
                best_idx = idx
                best_score = score
        
        return best_idx


class DuplicateResolver:
    """Main deduplication orchestrator."""
    
    def __init__(self):
        self.exact_dedup = ExactDeduplicator()
        self.near_dedup = NearDeduplicator()
    
    def deduplicate(self, articles: List[Dict]) -> List[Dict]:
        """
        Run full deduplication pipeline.
        
        Args:
            articles: List of article dictionaries
            
        Returns:
            Fully deduplicated list
        """
        logger.info(f"Starting deduplication on {len(articles)} articles")
        
        # Step 1: Remove exact duplicates
        articles = self.exact_dedup.deduplicate(articles)
        
        # Step 2: Remove near-duplicates
        articles = self.near_dedup.deduplicate(articles)
        
        logger.info(f"Deduplication complete: {len(articles)} unique articles")
        return articles
