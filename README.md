# AI Discovery Monitor

A tool that monitors your trusted AI blogs and Twitter accounts, discovers who they're reading/citing (2nd-degree sources), scores them for relevance, and recommends new sources to follow.

## How It Works

1. **Primary Sources**: You define trusted blogs and Twitter accounts to monitor
2. **Discovery**: The monitor fetches content from your primary sources
3. **Link Extraction**: Extracts URLs and mentions from their posts
4. **Scoring**: Evaluates 2nd-degree sources based on:
   - Relevance to your interests
   - How often they're cited by primary sources
   - How recently they've been active
5. **Recommendations**: Alerts you to promising new sources worth following

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Your Sources

Edit `config.yaml`:

```yaml
interests:
  - "AI agents"
  - "Large language models"
  - "AI safety"

primary_sources:
  blogs:
    - name: "Anthropic Blog"
      url: "https://www.anthropic.com/blog"

  twitter:
    - name: "Yann LeCun"
      handle: "ylecun"
```

### 3. Set Up Twitter API (Optional)

To monitor Twitter accounts, get a Bearer token:

1. Go to [Twitter Developer Portal](https://developer.twitter.com/en/portal/)
2. Create an app and get your Bearer Token
3. Set environment variable:

```bash
export TWITTER_BEARER_TOKEN="your_bearer_token_here"
```

Or add to `.env` file:

```
TWITTER_BEARER_TOKEN=your_bearer_token_here
```

## Usage

### Run Once

```bash
python monitor.py
```

This will:
1. Discover sources from your primary sources
2. Score them based on relevance and citation frequency
3. Output recommendations to `recommendations.md`

### Run Scheduled (Coming Soon)

With APScheduler integration:

```python
from apscheduler.schedulers.background import BackgroundScheduler
from monitor import AIDiscoveryMonitor
import asyncio

monitor = AIDiscoveryMonitor()
scheduler = BackgroundScheduler()

async def scheduled_run():
    await monitor.run_once()

scheduler.add_job(
    lambda: asyncio.run(scheduled_run()),
    'cron',
    hour=9,  # Run daily at 9 AM
    minute=0
)
scheduler.start()
```

## Configuration

### `config.yaml` Options

**Interests**
- List of topics you care about
- Used to score sources for relevance

**Primary Sources**
- Blogs: Define by name and RSS/blog URL
- Twitter: Define by name and @handle

**Recommendation Thresholds**
- `min_relevance_score`: 0-1 scale (e.g., 0.7 = 70% relevant)
- `min_citation_count`: How many times cited by primary sources
- `max_source_age_days`: Only recommend active sources

**Schedule**
- `frequency`: "hourly", "daily", or "weekly"
- `time`: Time to run (24-hour format, HH:MM)

**Notifications**
- `format`: "markdown", "json", or "text"
- `output_file`: Where to save recommendations

## Output

Recommendations are saved in your chosen format:

### Markdown (Default)
```markdown
# AI Discovery Recommendations

## ChatGPT Competitors
- **URL**: https://example.com
- **Type**: blog
- **Relevance Score**: 85%
- **Citations**: 3 times
- **Why recommend**: Good relevance: 0.85 | Cited 3 times by trusted sources
```

### JSON
```json
{
  "generated_at": "2024-11-16T09:00:00",
  "recommendations": [
    {
      "name": "ChatGPT Competitors",
      "url": "https://example.com",
      "relevance_score": 0.85,
      "reasoning": "..."
    }
  ]
}
```

## Database

The tool uses SQLite to track:
- Primary sources you're monitoring
- Discovered 2nd-degree sources
- Citation relationships
- Recommendation history

Database file: `discovery.db` (auto-created)

## File Structure

```
ai-discovery-monitor/
├── config.yaml           # Your configuration
├── monitor.py            # Main monitor loop
├── db.py                 # Database layer
├── fetchers.py           # Blog and Twitter fetchers
├── scoring.py            # Relevance scoring
├── notifications.py      # Output formatting
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## How Scoring Works

### Relevance Score (0-1)
- 40% based on source name matching your interests
- 60% based on content relevance

### Recommendation Logic
A source is recommended if it meets ALL of:
1. Relevance score ≥ threshold (e.g., 0.7)
2. Cited by ≥ N primary sources (e.g., 2+)
3. Been active in last N days (e.g., 90 days)

### Ranking
Sources are ranked by:
1. Relevance score (higher = better)
2. Citation count (more citations = better)

## Example Use Cases

### Daily AI News Monitor
Track tech blogs and AI researchers, find new resources mentioned by multiple trusted sources.

### Research Discovery
Monitor academic accounts, discover new papers and researchers in your field.

### Product Discovery
Track AI product communities, discover new tools your peers are using.

## Limitations

- Blog discovery requires RSS feeds or static URLs
- Twitter discovery requires valid API token
- Scoring is based on keyword matching (can be fine-tuned)
- No email notifications yet (future feature)

## Future Enhancements

- [ ] Email notifications
- [ ] Background scheduler integration
- [ ] Advanced NLP-based relevance scoring
- [ ] Duplicate detection (same content, different URLs)
- [ ] Source trust scores (based on accuracy history)
- [ ] Slack/Discord integration
- [ ] Web UI dashboard

## Troubleshooting

**No sources discovered**
- Check that RSS feeds are accessible
- Verify Twitter API token is valid
- Check your primary sources list in config

**Low relevance scores**
- Adjust your interests list
- Lower relevance score threshold in config
- Check that source names match your interests

**Twitter API errors**
- Verify Bearer token is set: `echo $TWITTER_BEARER_TOKEN`
- Check account has API access
- View rate limits in Twitter Developer Portal

## License

MIT
