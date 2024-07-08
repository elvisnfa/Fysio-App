import json

import matplotlib.pyplot as plt
from utils.logging import build_logger

from app.utils.database import Page

log = build_logger(__name__)

def total_complexity_scores_per_magazine(session):
    pages = session.query(Page).all()

    magazine_complexity_sums = {}

    for page in pages:
        complexity_scores = json.loads(page.complexity_scores)
        page_complexity_sum = sum(
            scores[0] for scores in complexity_scores if scores
        )
        magazine_complexity_sums[page.magazine_id] = page_complexity_sum \
            + magazine_complexity_sums.get(page.magazine_id, 0)

    for magazine_id, complexity_sum in magazine_complexity_sums.items():
        log.info(f"""
              Magazine id: {magazine_id},
              Total calculated complexity score: {complexity_sum}
        """)

    magazine_ids = list(magazine_complexity_sums.keys())
    complexity_sums = list(magazine_complexity_sums.values())

    plt.figure(figsize=(10, 5))
    bars = plt.bar(magazine_ids, complexity_sums, color='red')

    for bar in bars:
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            height,
            round(height, 2),
            va='bottom',
            ha='center',
            color='black'
        )

    plt.title('Complexity Bar Chart')
    plt.xlabel('Magazine id')
    plt.ylabel('Complexity Score')
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.xticks(rotation=45)
    plt.tight_layout()

    plt.show()