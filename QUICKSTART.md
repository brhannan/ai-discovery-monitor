# Quick Start Guide

## 30-Second Setup

### 1. Install
```bash
cd ai-discovery-monitor
pip install -r requirements.txt
```

### 2. Configure (Optional)
Edit `config.yaml`:
- Add your interests (AI topics you care about)
- Add your primary sources (blogs and Twitter handles)

### 3. Run
```bash
python monitor.py
```

Check `recommendations.md` for results!

## What Happens

1. Fetches latest posts from your primary sources
2. Extracts links and mentions they reference
3. Scores those 2nd-degree sources by relevance
4. Recommends sources that meet your criteria

## Example Output

```
🔍 Starting discovery process...
📡 Discovering sources from primary sources...
✅ Discovered 45 potential sources

🎯 Scoring and filtering sources...
  ✨ GPT-4 Blog (NEW - score: 0.95)
  ✨ AI Safety News (NEW - score: 0.88)
  ↪️  ML Weekly (already tracked)

🏆 Finding sources to recommend...
   (min relevance: 70%, min citations: 2)

📬 Found 3 sources to recommend:

  • GPT-4 Blog
    └─ Good relevance: 0.95 | Cited 2 times by trusted sources

  • AI Safety News
    └─ Good relevance: 0.88 | Cited 3 times by trusted sources

✅ Done!
```

## Next Steps

- [ ] **Customize config.yaml** - Add your sources and interests
- [ ] **Set up Twitter API** (optional) - For Twitter account monitoring
  - Get Bearer token: https://developer.twitter.com/en/portal/
  - Set `TWITTER_BEARER_TOKEN` environment variable
- [ ] **Adjust thresholds** - Fine-tune relevance/citation requirements
- [ ] **Review recommendations.md** - Check what sources were recommended
- [ ] **Add to cron** (optional) - Run on a schedule

## Typical Results

After first run:
- ~20-100 potential sources discovered
- 2-10 sources that meet recommendation criteria
- ~1-3 strong recommendations to investigate

## Common Configs

### Fast-Moving News
```yaml
interests:
  - "AI news"
  - "startup news"
recommendation_thresholds:
  min_relevance_score: 0.6
  min_citation_count: 1
```

### Deep Research
```yaml
interests:
  - "machine learning"
  - "neural networks"
  - "AI research"
recommendation_thresholds:
  min_relevance_score: 0.8
  min_citation_count: 3
```

### Broad Coverage
```yaml
interests:
  - "AI"
  - "tech"
  - "products"
recommendation_thresholds:
  min_relevance_score: 0.5
  min_citation_count: 2
```

## Troubleshooting

**"No sources discovered"**
- Check that your primary sources are accessible
- Verify RSS feeds work (blogs)
- Confirm Twitter API token is set (for Twitter accounts)

**"No recommendations"**
- Lower `min_relevance_score` in config
- Lower `min_citation_count` threshold
- Add more primary sources to monitor

**Twitter API errors**
- Export your token: `export TWITTER_BEARER_TOKEN=your_token`
- Verify token is valid in Twitter Developer Portal

See full README.md for more details!
