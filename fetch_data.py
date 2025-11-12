import praw
import pandas as pd

# ✅ Initialize Reddit API (read-only mode)
reddit = praw.Reddit(
    client_id="tY3GccLHBECP073MenpcJw",
    client_secret="tV5rYyw8MLwhTGyiW6IUWYAR1Tdp5g",
    user_agent="reddit-sna-ai by Rakshitha"
)
reddit.read_only = True  # Important for safe data fetching

def fetch_subreddit(subreddit_name, limit=200):
    """Fetch posts from a given subreddit."""
    posts = []
    try:
        subreddit = reddit.subreddit(subreddit_name)
        for post in subreddit.hot(limit=limit):
            posts.append({
                "id": post.id,
                "title": post.title,
                "score": post.score,
                "num_comments": post.num_comments,
                "author": str(post.author),
                "created_utc": post.created_utc,
                "url": post.url,
                "subreddit": subreddit_name
            })
        print(f"✅ Fetched {len(posts)} posts from r/{subreddit_name}")
    except Exception as e:
        print(f"❌ Error fetching from r/{subreddit_name}: {e}")
    return posts


if __name__ == "__main__":
    # You can change the subreddits here
    subreddits = ["ArtificialInteligence", "MachineLearning" , "learnmachinelearning"]  

    all_posts = []
    for sub in subreddits:
        print(f"\n📡 Fetching data from r/{sub}...")
        all_posts.extend(fetch_subreddit(sub, limit=200))

    if len(all_posts) > 0:
        df = pd.DataFrame(all_posts)
        df.to_csv("rakshitha_data.csv", index=False)
        print("\n✅ Data collection complete! Saved to rakshitha_data.csv")
        print(df.head())
    else:
        print("\n⚠️ No data fetched. Try again later or use different subreddits.")
