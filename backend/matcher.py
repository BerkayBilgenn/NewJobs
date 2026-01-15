"""
Job Matcher Engine
Calculates match score between CV text and job descriptions using TF-IDF and Cosine Similarity.
"""

import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class JobMatcher:
    """
    Calculate match scores between CV and job descriptions.
    
    Uses TF-IDF (Term Frequency-Inverse Document Frequency) vectorization
    and Cosine Similarity to measure text similarity.
    
    Match Score Interpretation:
    - 80-100%: Excellent match (Green)
    - 50-79%: Good match (Yellow)
    - 0-49%: Weak match (Red)
    """
    
    def __init__(self):
        """Initialize the TF-IDF vectorizer with English stop words."""
        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            lowercase=True,
            max_features=5000,  # Limit vocabulary size for performance
            ngram_range=(1, 2)  # Include both unigrams and bigrams
        )
    
    def _preprocess_text(self, text: str) -> str:
        """
        Clean and normalize text for better matching.
        
        Args:
            text: Raw text from CV or job description
        
        Returns:
            Cleaned text string
        """
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'http\S+|www\S+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove special characters but keep spaces
        text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def calculate_match_score(self, cv_text: str, job_text: str) -> float:
        """
        Calculate similarity score between CV and job description.
        
        Args:
            cv_text: Full text extracted from the CV
            job_text: Job title + description text
        
        Returns:
            Match score as percentage (0-100)
        """
        # Preprocess both texts
        cv_clean = self._preprocess_text(cv_text)
        job_clean = self._preprocess_text(job_text)
        
        # Handle empty texts
        if not cv_clean or not job_clean:
            return 0.0
        
        try:
            # Create TF-IDF vectors for both documents
            # We need to fit on both documents together
            tfidf_matrix = self.vectorizer.fit_transform([cv_clean, job_clean])
            
            # Calculate cosine similarity between the two vectors
            # Result is a 2x2 matrix, we want the [0,1] element
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            # Convert to percentage (0-100)
            score = round(similarity * 100, 1)
            
            # Ensure score is within bounds
            return max(0.0, min(100.0, score))
            
        except Exception as e:
            print(f"Matching error: {e}")
            return 0.0
    
    def calculate_keyword_overlap(self, cv_text: str, job_text: str) -> float:
        """
        Alternative simple matching using keyword overlap.
        
        Useful when TF-IDF gives too low scores due to vocabulary mismatch.
        
        Args:
            cv_text: Full text extracted from the CV
            job_text: Job title + description text
        
        Returns:
            Overlap score as percentage (0-100)
        """
        cv_clean = self._preprocess_text(cv_text)
        job_clean = self._preprocess_text(job_text)
        
        if not cv_clean or not job_clean:
            return 0.0
        
        # Split into words (simple tokenization)
        cv_words = set(cv_clean.split())
        job_words = set(job_clean.split())
        
        # Remove very short words (likely not meaningful)
        cv_words = {w for w in cv_words if len(w) > 2}
        job_words = {w for w in job_words if len(w) > 2}
        
        if not job_words:
            return 0.0
        
        # Calculate Jaccard-like overlap
        # What percentage of job keywords appear in CV?
        overlap = len(cv_words.intersection(job_words))
        score = (overlap / len(job_words)) * 100
        
        return round(min(100.0, score), 1)
    
    def get_combined_score(self, cv_text: str, job_text: str) -> float:
        """
        Get a combined score using both TF-IDF and keyword overlap.
        
        This provides more robust matching by averaging both methods.
        
        Args:
            cv_text: Full text extracted from the CV
            job_text: Job title + description text
        
        Returns:
            Combined match score as percentage (0-100)
        """
        tfidf_score = self.calculate_match_score(cv_text, job_text)
        keyword_score = self.calculate_keyword_overlap(cv_text, job_text)
        
        # Weighted average: TF-IDF is more sophisticated, give it more weight
        combined = (tfidf_score * 0.6) + (keyword_score * 0.4)
        
        return round(combined, 1)


# For testing
if __name__ == "__main__":
    matcher = JobMatcher()
    
    # Sample CV text
    cv = """
    John Doe - Senior Software Engineer
    5 years of experience in Python, JavaScript, React, Node.js
    Built scalable microservices using FastAPI and Docker
    Machine Learning experience with TensorFlow and PyTorch
    Strong background in agile development and CI/CD pipelines
    """
    
    # Sample job descriptions
    jobs = [
        ("Senior Python Developer", "Looking for Python developer with FastAPI experience, microservices, Docker, CI/CD"),
        ("React Frontend Developer", "Need React developer for building user interfaces, CSS, JavaScript"),
        ("Data Scientist", "Machine learning, Python, TensorFlow, data analysis required"),
        ("Java Backend Engineer", "Java, Spring Boot, Oracle database, enterprise applications"),
    ]
    
    print("Match Scores:")
    print("-" * 50)
    
    for title, desc in jobs:
        job_text = f"{title} {desc}"
        score = matcher.calculate_match_score(cv, job_text)
        keyword = matcher.calculate_keyword_overlap(cv, job_text)
        combined = matcher.get_combined_score(cv, job_text)
        
        print(f"\n{title}")
        print(f"  TF-IDF Score: {score}%")
        print(f"  Keyword Overlap: {keyword}%")
        print(f"  Combined Score: {combined}%")
