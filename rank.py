import argparse
import os
import sys

def main():
    parser = argparse.ArgumentParser(description="Redrob Candidate Discovery Ranking Pipeline")
    parser.add_argument("--candidates", required=True, help="Path to candidates.jsonl")
    parser.add_argument("--jd", required=False, help="Path to job_description.docx (optional, defaults to config if not set)")
    parser.add_argument("--out", required=True, help="Path to output submission.csv")
    
    args = parser.parse_args()
    
    # Set environment variables so config.py picks them up
    os.environ["REDROB_CANDIDATES_JSONL"] = os.path.abspath(args.candidates)
    if args.jd:
        os.environ["REDROB_JD_DOCX"] = os.path.abspath(args.jd)
        
    # We must assume the pre-processor has already been run and the embeddings are available.
    # The spec allows offline pre-computation.
    from redrob_pipeline import config
    from redrob_pipeline import rank_engine as ranker
    
    print(f"Ranking candidates from: {config.CANDIDATES_JSONL}")
    print(f"Outputting to: {args.out}")
    
    ranker.main(out_path=os.path.abspath(args.out))

if __name__ == "__main__":
    main()
