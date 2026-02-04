"""
Test data source that returns mock articles for testing.
Use this when GDELT/RSS are not accessible.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class MockNewsSource:
    """Mock news source for testing when APIs are unavailable."""
    
    def __init__(self):
        self.mock_data = self._generate_mock_articles()
    
    def search(
        self,
        query: str,
        max_records: int = 100,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Return mock articles matching the query."""
        
        # Split query into keywords and filter common words
        keywords = [word for word in query.lower().split() if len(word) > 2]
        articles = []
        
        # Parse date range
        start_dt = datetime.strptime(start_date, '%Y-%m-%d') if start_date else None
        end_dt = datetime.strptime(end_date, '%Y-%m-%d') if end_date else None
        
        for article in self.mock_data:
            # Check if ANY keyword matches (more flexible matching)
            article_text = (article['title'] + ' ' + article['raw_text']).lower()
            matches = sum(1 for keyword in keywords if keyword in article_text)
            
            # Require at least 30% of keywords to match
            if matches >= max(1, len(keywords) * 0.3):
                
                # Check date range
                if start_dt or end_dt:
                    pub_date = datetime.fromisoformat(article['published_at'].replace('Z', '+00:00'))
                    # Convert to naive datetime for comparison
                    pub_date_naive = pub_date.replace(tzinfo=None)
                    if start_dt and pub_date_naive < start_dt:
                        continue
                    if end_dt and pub_date_naive > end_dt.replace(hour=23, minute=59, second=59):
                        continue
                
                articles.append(article.copy())
                
                if len(articles) >= max_records:
                    break
        
        logger.info(f"MockSource: Fetched {len(articles)} articles for query '{query}'")
        return articles
    
    def _generate_mock_articles(self) -> List[Dict[str, Any]]:
        """Generate mock article data."""
        
        base_date = datetime.now()
        
        return [
            {
                'url': 'https://example.com/india-union-budget-2026-key-highlights',
                'title': 'India Union Budget 2026: Key Highlights and Major Announcements',
                'source_name': 'Economic Times India',
                'published_at': (base_date - timedelta(days=1)).strftime('%Y-%m-%dT10:30:00Z'),
                'author': 'Rajesh Kumar',
                'language': 'en',
                'raw_text': '''
                <html><body>
                <h1>India Union Budget 2026: Key Highlights</h1>
                <p>Finance Minister Nirmala Sitharaman presented the Union Budget 2026 today in Parliament, 
                outlining the government's fiscal roadmap for the upcoming year. The budget focuses on 
                infrastructure development, digital economy, and social welfare schemes.</p>
                
                <h2>Key Allocations:</h2>
                <ul>
                <li>Infrastructure: ₹10 lakh crores allocated for roads, railways, and ports</li>
                <li>Healthcare: 15% increase in health budget to strengthen public health infrastructure</li>
                <li>Education: ₹1.2 lakh crores for education sector with focus on digital learning</li>
                <li>Agriculture: New schemes announced for farmer welfare and crop insurance</li>
                </ul>
                
                <h2>Tax Proposals:</h2>
                <p>The budget proposes changes to income tax slabs, with increased exemption limits for 
                middle-class taxpayers. Corporate tax rates remain unchanged at 25% for domestic companies.</p>
                
                <p>The fiscal deficit is targeted at 4.5% of GDP, showing the government's commitment to 
                fiscal consolidation while supporting economic growth.</p>
                </body></html>
                '''
            },
            {
                'url': 'https://example.com/union-budget-2026-infrastructure-focus',
                'title': 'Union Budget 2026 Emphasizes Infrastructure and Green Energy',
                'source_name': 'Business Standard',
                'published_at': (base_date - timedelta(days=1)).strftime('%Y-%m-%dT14:15:00Z'),
                'author': 'Priya Sharma',
                'language': 'en',
                'raw_text': '''
                <html><body>
                <h1>Budget 2026: Green Energy and Infrastructure Take Center Stage</h1>
                <p>The Union Budget 2026 unveiled today marks a significant shift towards sustainable 
                development and infrastructure modernization. The Finance Minister announced ambitious 
                targets for renewable energy and transportation infrastructure.</p>
                
                <p>Major announcements include:</p>
                <ul>
                <li>₹2 lakh crores for renewable energy projects, including solar and wind power</li>
                <li>Electric vehicle incentives extended with additional ₹50,000 crores allocation</li>
                <li>New metro rail projects in 15 cities with combined budget of ₹3 lakh crores</li>
                <li>Green hydrogen mission launched with ₹30,000 crores initial funding</li>
                </ul>
                
                <p>Industry experts have welcomed the budget, calling it "forward-looking" and "growth-oriented" 
                while maintaining fiscal discipline.</p>
                </body></html>
                '''
            },
            {
                'url': 'https://example.com/india-budget-2026-healthcare-education',
                'title': 'Budget 2026: Major Boost for Healthcare and Education Sectors',
                'source_name': 'The Hindu',
                'published_at': (base_date - timedelta(days=2)).strftime('%Y-%m-%dT09:00:00Z'),
                'author': 'Anil Verma',
                'language': 'en',
                'raw_text': '''
                <html><body>
                <h1>Union Budget 2026: Social Sector Gets Priority</h1>
                <p>In a move aimed at strengthening India's social infrastructure, the Union Budget 2026 
                has allocated substantial funds for healthcare and education sectors.</p>
                
                <h2>Healthcare Initiatives:</h2>
                <ul>
                <li>10,000 new primary health centers to be established in rural areas</li>
                <li>Medical colleges in every district under mission Ayushman Bharat</li>
                <li>Free healthcare for senior citizens under enhanced Ayushman Bharat scheme</li>
                <li>₹25,000 crores for pandemic preparedness and vaccine research</li>
                </ul>
                
                <h2>Education Reforms:</h2>
                <ul>
                <li>New IITs and IIMs announced in underserved regions</li>
                <li>Digital infrastructure for schools in rural areas</li>
                <li>Skill development programs with focus on AI and emerging technologies</li>
                <li>Student loan interest subsidy for economically weaker sections</li>
                </ul>
                </body></html>
                '''
            },
            {
                'url': 'https://example.com/technology-innovation-budget-2026',
                'title': 'Technology and Innovation: Budget 2026 Analysis',
                'source_name': 'TechCrunch India',
                'published_at': (base_date - timedelta(days=0)).strftime('%Y-%m-%dT11:45:00Z'),
                'author': 'Sneha Patel',
                'language': 'en',
                'raw_text': '''
                <html><body>
                <h1>Budget 2026 Accelerates India's Digital Transformation</h1>
                <p>The Union Budget 2026 has unveiled a comprehensive roadmap for technology adoption 
                and innovation, positioning India as a global technology hub.</p>
                
                <p>Technology highlights include:</p>
                <ul>
                <li>₹75,000 crores for Digital India 2.0 initiative</li>
                <li>AI research centers in partnership with leading global institutions</li>
                <li>5G network expansion to cover 95% of the country by 2027</li>
                <li>Startup India program expansion with ₹20,000 crores corpus</li>
                <li>Semiconductor manufacturing incentives worth ₹50,000 crores</li>
                </ul>
                
                <p>The budget also proposes tax incentives for tech startups and R&D investments, 
                making it attractive for innovation-driven companies.</p>
                </body></html>
                '''
            },
            {
                'url': 'https://example.com/union-budget-agriculture-reforms',
                'title': 'Union Budget 2026: Farmers Get Relief with New Agricultural Schemes',
                'source_name': 'India Today',
                'published_at': (base_date - timedelta(days=1)).strftime('%Y-%m-%dT16:30:00Z'),
                'author': 'Vikram Singh',
                'language': 'en',
                'raw_text': '''
                <html><body>
                <h1>Budget 2026 Focuses on Agricultural Modernization</h1>
                <p>The Union Budget 2026 has introduced several farmer-centric schemes aimed at 
                doubling farm income and promoting sustainable agriculture.</p>
                
                <p>Key agricultural announcements:</p>
                <ul>
                <li>PM-KISAN direct benefit transfer increased to ₹8,000 per year</li>
                <li>Crop insurance coverage expanded with reduced premium</li>
                <li>₹1.5 lakh crores for irrigation and water conservation projects</li>
                <li>Organic farming incentives with certification support</li>
                <li>Cold storage and food processing infrastructure development</li>
                <li>Agricultural credit target raised to ₹20 lakh crores</li>
                </ul>
                
                <p>Farmer organizations have largely welcomed the budget, though some have called 
                for additional measures on minimum support prices.</p>
                </body></html>
                '''
            },
        ]
