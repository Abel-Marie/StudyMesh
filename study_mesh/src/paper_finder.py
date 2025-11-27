import arxiv
from datetime import datetime, timedelta

class PaperFinder:
    """Find and manage research papers from arXiv."""
    
    def __init__(self):
        self.client = arxiv.Client()
    
    def search_papers(self, query, max_results=5):
        """Search for papers on arXiv."""
        try:
            search = arxiv.Search(
                query=query,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.SubmittedDate
            )
            
            papers = []
            for result in self.client.results(search):
                papers.append({
                    "title": result.title,
                    "authors": ", ".join([author.name for author in result.authors]),
                    "abstract": result.summary,
                    "arxiv_id": result.entry_id.split("/")[-1],
                    "pdf_url": result.pdf_url,
                    "published_date": result.published.date().isoformat()
                })
            
            return papers
        except Exception as e:
            return []
    
    def get_daily_papers(self, topic, count=5):
        """Get daily recommended papers for a topic."""
        # Search for recent papers in the topic
        query = f"{topic} AND submittedDate:[{(datetime.now() - timedelta(days=7)).strftime('%Y%m%d')} TO {datetime.now().strftime('%Y%m%d')}]"
        
        return self.search_papers(query, max_results=count)
    
    def get_papers_by_category(self, category, max_results=10):
        """Get papers by arXiv category."""
        categories = {
            "AI": "cs.AI",
            "Machine Learning": "cs.LG",
            "Computer Vision": "cs.CV",
            "NLP": "cs.CL",
            "Robotics": "cs.RO",
            "Deep Learning": "cs.LG AND deep learning"
        }
        
        cat = categories.get(category, category)
        return self.search_papers(f"cat:{cat}", max_results=max_results)
